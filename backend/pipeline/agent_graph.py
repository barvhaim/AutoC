"""LangGraph workflow using agents"""

from langgraph.graph import StateGraph
from backend.pipeline.state import PipelineState
from backend.pipeline.agent_nodes import (
    html_extractor_agent_node,
    parallel_analysis_agent_node,
    enrichment_agent_node,
    mitre_agent_node,
)
from backend.pipeline.node_types import (
    HTML_EXTRACTOR_NODE,
    IOCS_EXTRACTOR_NODE,
    MITRE_TTP_CLASSIFIER_NODE,
)


def build_agent_graph():
    """Build LangGraph workflow with agents

    This creates a hybrid architecture that combines:
    - LangGraph for workflow orchestration
    - Agents for intelligent task execution
    - Parallel processing for independent tasks

    Workflow:
    1. HTML_EXTRACTOR_NODE: Parser Agent extracts content
    2. parallel_analysis: Keywords, IOC, QnA agents run concurrently
    3. IOCS_EXTRACTOR_NODE: Enrichment Agent enriches IOCs
    4. MITRE_TTP_CLASSIFIER_NODE: MITRE Agent classifies techniques
    """
    flow = StateGraph(PipelineState)

    # Add agent-enabled nodes
    flow.add_node(HTML_EXTRACTOR_NODE, html_extractor_agent_node)
    flow.add_node("parallel_analysis", parallel_analysis_agent_node)
    flow.add_node(IOCS_EXTRACTOR_NODE, enrichment_agent_node)
    flow.add_node(MITRE_TTP_CLASSIFIER_NODE, mitre_agent_node)

    # Set entry point
    flow.set_entry_point(HTML_EXTRACTOR_NODE)

    return flow.compile()
