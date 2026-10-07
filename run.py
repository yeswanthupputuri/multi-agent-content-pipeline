import uuid

from langgraph.checkpoint.sqlite import SqliteSaver

from app.graph.workflow import build_workflow
from app.llm.local_qwen import LocalQwen


MODEL_PATH = (
    r"C:\Users\Yeswanth Upputuri\.cache\huggingface\hub"
    r"\models--Qwen--Qwen2.5-1.5B-Instruct"
    r"\snapshots\989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
)

CHECKPOINT_DB = "data/checkpoints/content_pipeline.db"


def main():

    print("=" * 60)
    print("MULTI-AGENT CONTENT PIPELINE")
    print("=" * 60)

    print("\nLoading local Qwen model...")

    llm = LocalQwen(MODEL_PATH)

    topic = input("\nEnter topic: ").strip()

    content_type = input(
        "Enter content type "
        "(e.g. technical article, social post): "
    ).strip()

    requirements = input(
        "Enter content requirements: "
    ).strip()

    if not topic:
        print("\nError: Topic is required.")
        return

    if not content_type:
        print("\nError: Content type is required.")
        return

    if not requirements:
        print("\nError: Requirements are required.")
        return

    thread_id = f"content_{uuid.uuid4().hex[:8]}"

    initial_state = {
        "topic": topic,
        "content_type": content_type,
        "requirements": requirements,
        "metrics": {
            "thread_id": thread_id
        },
    }

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    print("\nCreating workflow...")

    with SqliteSaver.from_conn_string(
        CHECKPOINT_DB
    ) as checkpointer:

        workflow = build_workflow(
            llm,
            checkpointer=checkpointer,
        )

        print("\nStarting content pipeline...")
        print("-" * 60)

        result = workflow.invoke(
            initial_state,
            config=config
        )

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)

    status = result.get("status")

    print(f"\nStatus: {status}")

    if status == "completed":

        print("\nFINAL CONTENT")
        print("-" * 60)
        print(result.get("draft", ""))
        print("-" * 60)

    else:

        print("\nWorkflow did not complete successfully.")

        print(
            f"\nReason: "
            f"{result.get('status', 'unknown')}"
        )

        errors = result.get("errors", [])

        if errors:
            print("\nErrors:")

            for error in errors:
                print(f"- {error}")

        editor_feedback = result.get(
            "editor_feedback",
            ""
        )

        if editor_feedback:
            print("\nLast Editor Feedback:")
            print("-" * 60)
            print(editor_feedback)

        draft = result.get(
            "draft",
            ""
        )

        if draft:
            print("\nLast Generated Draft:")
            print("-" * 60)
            print(draft)
            print("-" * 60)

    metrics = result.get("metrics", {})

    print("\nEXECUTION METRICS")
    print("-" * 60)

    print(
        f"Thread ID: {metrics.get('thread_id')}"
    )

    print(
        f"Execution time: "
        f"{metrics.get('execution_time_seconds')} seconds"
    )

    print(
        f"Revisions: "
        f"{metrics.get('revision_count')}"
    )

    print(
        f"Editor decisions: "
        f"{metrics.get('editor_decisions')}"
    )

    print(
        f"Fact-check decisions: "
        f"{metrics.get('fact_check_decisions')}"
    )

    print(
        f"Claims checked: "
        f"{metrics.get('claims_checked')}"
    )

    print(
        f"Errors: "
        f"{metrics.get('errors')}"
    )

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()