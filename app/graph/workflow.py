from langgraph.graph import StateGraph, END

from app.state.content_state import ContentState
from app.graph.nodes import create_nodes

from app.graph.routing import (
    route_after_input,
    route_after_research,
    route_after_research_relevance,
    route_after_writer_state,
    route_after_editor_state,
    route_after_editor,
    route_after_fact_checker_state,
    route_after_fact_checker,
    route_after_output,
)


def build_workflow(
    llm,
    checkpointer=None,
    interrupt_before=None
):

    nodes = create_nodes(llm)

    graph = StateGraph(ContentState)

    # ---------------------------------------------------------
    # Add nodes
    # ---------------------------------------------------------

    graph.add_node(
        "input_guardrail",
        nodes["input_guardrail"]
    )

    graph.add_node(
        "researcher",
        nodes["researcher"]
    )

    graph.add_node(
        "research_guardrail",
        nodes["research_guardrail"]
    )

    # NEW: Research Relevance Guardrail
    graph.add_node(
        "research_relevance_guardrail",
        nodes["research_relevance_guardrail"]
    )

    graph.add_node(
        "writer_state_guardrail",
        nodes["writer_state_guardrail"]
    )

    graph.add_node(
        "writer",
        nodes["writer"]
    )

    graph.add_node(
        "editor_state_guardrail",
        nodes["editor_state_guardrail"]
    )

    graph.add_node(
        "editor",
        nodes["editor"]
    )

    graph.add_node(
        "fact_checker_state_guardrail",
        nodes["fact_checker_state_guardrail"]
    )

    graph.add_node(
        "fact_checker",
        nodes["fact_checker"]
    )

    graph.add_node(
        "output_guardrail",
        nodes["output_guardrail"]
    )

    graph.add_node(
        "metrics_finalizer",
        nodes["metrics_finalizer"]
    )

    # ---------------------------------------------------------
    # Entry point
    # ---------------------------------------------------------

    graph.set_entry_point(
        "input_guardrail"
    )

    # ---------------------------------------------------------
    # Input Guardrail routing
    # ---------------------------------------------------------

    graph.add_conditional_edges(
        "input_guardrail",
        route_after_input,
        {
            "researcher": "researcher",
            "end": "metrics_finalizer",
        },
    )

    # ---------------------------------------------------------
    # Researcher → Research Guardrail
    # ---------------------------------------------------------

    graph.add_edge(
        "researcher",
        "research_guardrail"
    )

    # ---------------------------------------------------------
    # Research Guardrail routing
    # ---------------------------------------------------------

    graph.add_conditional_edges(
        "research_guardrail",
        route_after_research,
        {
            "research_relevance_guardrail":
                "research_relevance_guardrail",

            "end":
                "metrics_finalizer",
        },
    )

    # ---------------------------------------------------------
    # Research Relevance Guardrail routing
    # ---------------------------------------------------------

    graph.add_conditional_edges(
        "research_relevance_guardrail",
        route_after_research_relevance,
        {
            "researcher":
                "researcher",

            "writer_state_guardrail":
                "writer_state_guardrail",

            "end":
                "metrics_finalizer",
        },
    )

    # ---------------------------------------------------------
    # Writer State Guardrail routing
    # ---------------------------------------------------------

    graph.add_conditional_edges(
        "writer_state_guardrail",
        route_after_writer_state,
        {
            "writer": "writer",
            "end": "metrics_finalizer",
        },
    )

    # ---------------------------------------------------------
    # Writer → Editor State Guardrail
    # ---------------------------------------------------------

    graph.add_edge(
        "writer",
        "editor_state_guardrail"
    )

    # ---------------------------------------------------------
    # Editor State Guardrail routing
    # ---------------------------------------------------------

    graph.add_conditional_edges(
        "editor_state_guardrail",
        route_after_editor_state,
        {
            "editor": "editor",
            "end": "metrics_finalizer",
        },
    )

    # ---------------------------------------------------------
    # Editor decision routing
    # ---------------------------------------------------------

    graph.add_conditional_edges(
        "editor",
        route_after_editor,
        {
            "writer":
                "writer",

            "fact_checker_state_guardrail":
                "fact_checker_state_guardrail",

            "end":
                "metrics_finalizer",
        },
    )

    # ---------------------------------------------------------
    # Fact Checker State Guardrail routing
    # ---------------------------------------------------------

    graph.add_conditional_edges(
        "fact_checker_state_guardrail",
        route_after_fact_checker_state,
        {
            "fact_checker":
                "fact_checker",

            "end":
                "metrics_finalizer",
        },
    )

    # ---------------------------------------------------------
    # Fact Checker decision routing
    # ---------------------------------------------------------

    graph.add_conditional_edges(
        "fact_checker",
        route_after_fact_checker,
        {
            "writer":
                "writer",

            "output_guardrail":
                "output_guardrail",

            "end":
                "metrics_finalizer",
        },
    )

    # ---------------------------------------------------------
    # Final Output Guardrail
    # ---------------------------------------------------------

    graph.add_conditional_edges(
        "output_guardrail",
        route_after_output,
        {
            "end":
                "metrics_finalizer",
        },
    )

    # ---------------------------------------------------------
    # Metrics Finalizer → END
    # ---------------------------------------------------------

    graph.add_edge(
        "metrics_finalizer",
        END
    )

    # ---------------------------------------------------------
    # Compile workflow
    # ---------------------------------------------------------

    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=interrupt_before
    )