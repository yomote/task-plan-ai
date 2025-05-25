import json
from textwrap import dedent
from typing import Dict, Optional, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from ai.datamodels import ReviewResult, State

PROMPT = """\
あなたは **ソフトウェア開発プロジェクトのアジャイルコーチ** です。
入力として以下を受け取り、プロジェクト計画のレビューを行います。
1. Markwhen 形式のスケジュール
2. タスク一覧
3. 前回レビューからの改善点（もしあれば）

・出力はすべて日本語にしてください。

{extra_section}

# 評価観点
1. 適切にタスク分解できているか
2. スケジュールが現実的か
3. リスクが適切に考慮されているか
4. 成果物が明確に定義されているか

# スコア算出ルール
- 初期値 **100** から減点方式
  • **LOW**     1件につき  5 点減点  
  • **MEDIUM**  1件につき 10 点減点  
  • **HIGH**    1件につき 20 点減点  
- score が 0 未満になった場合は 0 とする
- 小数点以下は四捨五入し、**整数 (0-100)** で返す

<INPUT>
<SCHEDULE>
{schedule}
</SCHEDULE>
<TASKS>
{tasks}
</TASKS>
</INPUT>
"""


class Reviewer:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.prompt = PromptTemplate(
            template=PROMPT,
            input_variables=["extra_section", "schedule", "tasks"],
        )

    def _build_extra_section(
        self, prev_score: Optional[int], prev_issues: Optional[list[Any]]
    ) -> str:
        if prev_score is None or prev_issues is None:
            return ""  # 初回 ⇒ 空文字を返す

        return dedent(
            f"""\
           # 前回レビュー情報
           <PREV_SCORE>{prev_score}</PREV_SCORE>

           <PREVIOUS_ISSUES>
           {json.dumps(prev_issues, indent=2, ensure_ascii=False)}
           </PREVIOUS_ISSUES>

           以下のルールで差分減点を行ってください。
           - 依然残っている issue → 減点を維持
           - 解消された issue → 同点数を加点
           - 新規 issue       → 減点
       """
        )

    def invoke(self, state: State) -> ReviewResult:
        extra_section = self._build_extra_section(
            prev_score=state.review_result.score if state.review_result else None,
            prev_issues=state.review_result.issues if state.review_result else None,
        )
        assert state.plan_result is not None, "plan_result must not be None"

        chain = self.prompt | self.llm.with_structured_output(ReviewResult)
        raw_result = chain.invoke(
            {
                "extra_section": extra_section,
                "schedule": state.plan_result.schedule,
                "tasks": state.plan_result.tasks,
            }
        )
        return ReviewResult.model_validate(raw_result)
