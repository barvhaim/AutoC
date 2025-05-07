from langgraph.graph import StateGraph
from backend.pipeline.state import PipelineState
from backend.pipeline.nodes import (
    html_extractor_node,
    keywords_extractor_node,
    qna_extractor_node,
    iocs_extractor_node,
    mitre_ttp_classifier_node,
)
from backend.pipeline.node_types import (
    HTML_EXTRACTOR_NODE,
    KEYWORDS_EXTRACTOR_NODE,
    QNA_EXTRACTOR_NODE,
    IOCS_EXTRACTOR_NODE,
    MITRE_CLASSIFIER_NODE,
)


def build_graph():
    flow = StateGraph(PipelineState)

    flow.add_node(HTML_EXTRACTOR_NODE, html_extractor_node)
    flow.add_node(KEYWORDS_EXTRACTOR_NODE, keywords_extractor_node)
    flow.add_node(QNA_EXTRACTOR_NODE, qna_extractor_node)
    flow.add_node(IOCS_EXTRACTOR_NODE, iocs_extractor_node)
    flow.add_node(MITRE_CLASSIFIER_NODE, mitre_ttp_classifier_node)

    flow.set_entry_point(HTML_EXTRACTOR_NODE)

    return flow.compile()
