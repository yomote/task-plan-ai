import argparse
import json

import yaml

from ai.task_plan_agent import TaskPlanAgent


def main():
    parser = argparse.ArgumentParser(description="Generate a plan.")
    parser.add_argument(
        "--input",
        help="Input file for the plan generation. Format: YAML",
        required=True,
    )
    parser.add_argument(
        "--adoption-score",
        type=int,
        default=60,
        choices=range(0, 101),
        help="Adoption score for the plan (0-100)",
    )
    parser.add_argument(
        "--num-iterations",
        type=int,
        default=3,
        choices=range(1, 11),
        help="Number of iterations for the plan refinement",
    )
    args = parser.parse_args()

    with open(args.input) as f:
        data = yaml.safe_load(f)
    yaml_str = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

    agent = TaskPlanAgent(args)
    result = agent.generate_plan(yaml_str)

    print("Plan Result:")

    with open("plan.mw", "w") as f:
        f.write(result["plan_result"].schedule)

    with open("meta.json", "w") as f:
        json.dump(
            [task.model_dump() for task in result["plan_result"].tasks],
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("Plan generated successfully.")


if __name__ == "__main__":
    main()
