"""
State definitions for LangGraph Stock AI Agents.
"""
from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator


class AgentTraceItem(TypedDict):
    agent: str
    action: str
    summary: str
    timestamp: str


class StockAgentState(TypedDict, total=False):
    # ==========================================
    # INPUT DATA
    # ==========================================
    ticker: str
    company_name: str
    price: Any
    score: Any
    category: str
    fair_value: Any
    mos: Any
    metrics: str
    signals: str
    business_summary: str
    raw_data: Optional[Dict[str, Any]]

    # ==========================================
    # DYNAMIC TOOL RESULTS
    # ==========================================
    tool_results: Dict[str, Any]

    # ==========================================
    # SUB-AGENT INTERMEDIATE ANALYSES
    # ==========================================
    valuation_analysis: str
    risk_analysis: str
    structured_valuation: Optional[Dict[str, Any]]
    structured_risk: Optional[Dict[str, Any]]

    # ==========================================
    # FINAL CIO SYNTHESIS (Markdown & Structured)
    # ==========================================
    final_analysis: str
    structured_report: Optional[Dict[str, Any]]
    conviction_score: Optional[float]
    investment_classification: Optional[str]

    # ==========================================
    # AGENT REASONING TRACE (Observability)
    # Uses operator.add to collect trace events across graph nodes
    # ==========================================
    agent_trace: Annotated[List[Dict[str, Any]], operator.add]
