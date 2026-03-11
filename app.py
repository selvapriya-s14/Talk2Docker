from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from agent.agent_loop import run_agent_turn
from rag.retriever import Retriever


def main() -> None:
    console = Console()
    console.print("Talk2Docker v2 - local agent")

    base_dir = Path(__file__).resolve().parent
    retriever = Retriever(base_dir / "rag" / "docker_docs", base_dir / "memory")

    while True:
        user_input = Prompt.ask("Talk2Docker")
        if user_input.strip().lower() in {"exit", "quit"}:
            break

        result = run_agent_turn(user_input, retriever)
        console.print(result["display"])


if __name__ == "__main__":
    main()
