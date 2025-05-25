from typing import Any
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from ai.datamodels import State
from ai.planner import Planner
from ai.reviewer import Reviewer


class TaskPlanAgent:
    def __init__(self, args):
        self.graph = self._create_graph()
        self.planner = Planner(llm=ChatOpenAI(model="gpt-4o", temperature=0.0))
        self.reviewer = Reviewer(llm=ChatOpenAI(model="gpt-4o", temperature=0.0))

        self.args = args

    def _create_graph(self) -> CompiledStateGraph:
        graph = StateGraph(State)
        graph.add_node("plan", self._plan_node)
        graph.add_node("review", self._review_node)
        graph.set_entry_point("plan")

        graph.add_edge("plan", "review")
        graph.add_conditional_edges(
            "review",
            lambda state: state.review_result.score >= self.args.adoption_score,
            {True: END, False: "plan"},
        )

        return graph.compile()

    def _plan_node(self, state: State) -> dict[str, Any]:
        plan_result = self.planner.invoke(state)
        return {"plan_result": plan_result}

    def _review_node(self, state: State) -> dict[str, Any]:
        review_result = self.reviewer.invoke(state)
        return {"review_result": review_result}

    def generate_plan(self, context: str) -> dict[str, Any]:
        compiled = self._create_graph()
        state = State(planning_context=context)

        result = compiled.invoke(state)

        return result
