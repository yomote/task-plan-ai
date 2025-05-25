from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from typing import Optional

from ai.datamodels import PlanResult, State
from ai.reviewer import ReviewResult


PROMPT = """\
あなたは **プロジェクト計画の専門家** です。

・出力はすべて日本語にしてください。
・入力として、プロジェクトの計画コンテキストと、必要に応じて前回の出力やレビュー結果を受け取ります。
・レビュー結果がある場合は、必ず改善点を反映した計画を生成してください。

{input_section}

# 出力要件
1. timeline.mw  
   ◆ 先頭にヘッダー `--- ... ---` を入れる  
      - 常に `title:` と `timezone: Asia/Tokyo` を含める  
      - `#tag:` の色設定は YAML に tags が 3 つ以上ある場合のみ追加  
      - vertical-lines は YAML の `options.verticalLines` がある場合のみ追加  
   ◆ イベント行の書式 … <YYYY-MM-DD> / <n days>: <タスク名> #<tag> !Task<n>  
   ◆ 依存行、グループ行、マイルストーンは必要時だけ生成  
   ◆ 期間は “n days” を使用。  

2. meta.json — tasks 配列 (id, description, tag, outputs, risks, estimate_days)

3. review_answer (optional)
# 例
   - レビュー結果がある場合は、何を改善したかを記載
    - レビュー結果がない場合は、空文字列を返す

# few-shot 例
<EXAMPLE>
---
title: 認証基盤 PoC
timezone: Asia/Tokyo
#design: aquamarine
---
2025-06-01 / 5 days: 要件整理 #design !Task1
after !Task1 7 days: 設計ドキュメント作成 #design !Task2
</EXAMPLE>
"""


class Planner:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["input_section"],
            template=PROMPT,
        )

    def _build_input_section(
        self,
        planning_context: str,
        previous_output: Optional[PlanResult] = None,
        review_result: Optional[ReviewResult] = None,
    ) -> str:
        blocks: list[str] = []

        if previous_output:
            blocks.append(
                f"<PREVIOUS_OUTPUT>\n{previous_output.model_dump_json(indent=2)}\n</PREVIOUS_OUTPUT>"
            )

        if review_result:
            blocks.append(
                f"<REVIEW>\n{review_result.model_dump_json(indent=2)}\n</REVIEW>"
            )

        blocks.append(f"<INPUT>\n{planning_context}\n</INPUT>")

        return "\n\n".join(blocks)

    def invoke(self, state: State) -> PlanResult:
        input_section = self._build_input_section(
            planning_context=state.planning_context,
            previous_output=state.plan_result if state.plan_result else None,
            review_result=state.review_result if state.review_result else None,
        )

        chain = self.prompt | self.llm.with_structured_output(PlanResult)
        raw_output = chain.invoke(
            {
                "input_section": input_section,
            }
        )
        return PlanResult.model_validate(raw_output)
