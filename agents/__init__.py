"""
Stock AI Agents Multi-Agent System Package.
Orchestrated using LangGraph with specialized sub-agents, quantitative tools, and Pydantic structured schemas.
"""
from agents.graph import build_stock_agent_graph, StockAgentRunner
from agents.state import StockAgentState
from agents.schemas import (
    ValuationAnalysisSchema,
    RiskAnalysisSchema,
    CIOInvestmentReport
)
from agents.tools import (
    peer_benchmark_tool,
    financial_distress_tool,
    dividend_sustainability_tool
)

__all__ = [
    "build_stock_agent_graph",
    "StockAgentRunner",
    "StockAgentState",
    "ValuationAnalysisSchema",
    "RiskAnalysisSchema",
    "CIOInvestmentReport",
    "peer_benchmark_tool",
    "financial_distress_tool",
    "dividend_sustainability_tool"
]
