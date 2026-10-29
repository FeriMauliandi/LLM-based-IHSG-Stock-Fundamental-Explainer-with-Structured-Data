"""
LangGraph Multi-Agent Workflow Orchestration for Stock AI Agents.
Graph Architecture:
  START
    ↓
  [tool_execution_node] (Dynamic Quantitative Diagnostics)
    ↓
  [valuation_agent_node] (Senior Valuation & Efficiency Analyst)
    ↓
  [risk_agent_node] (Solvency & Downside Risk Officer)
    ↓
  [synthesis_agent_node] (Chief Investment Officer / Final Synthesis)
    ↓
  END
"""
import os
from typing import Dict, Any, Optional

from langgraph.graph import StateGraph, START, END
from agents.state import StockAgentState
from agents.subagents import (
    tool_execution_node,
    valuation_agent_node,
    risk_agent_node,
    synthesis_agent_node
)


def create_stock_agent_graph():
    """
    Membangun dan mengompilasi StateGraph multi-agent LangGraph.
    """
    workflow = StateGraph(StockAgentState)

    # Tambahkan Node Agen
    workflow.add_node("tool_engine", tool_execution_node)
    workflow.add_node("valuation_agent", valuation_agent_node)
    workflow.add_node("risk_agent", risk_agent_node)
    workflow.add_node("synthesis_agent", synthesis_agent_node)

    # Definisikan Alur Eksekusi (Graph Edges)
    workflow.add_edge(START, "tool_engine")
    workflow.add_edge("tool_engine", "valuation_agent")
    workflow.add_edge("valuation_agent", "risk_agent")
    workflow.add_edge("risk_agent", "synthesis_agent")
    workflow.add_edge("synthesis_agent", END)

    return workflow.compile()


class StockAgentRunner:
    """
    Runner wrapper yang menyediakan antarmuka kompatibel dengan LangChain chain.
    - .invoke(inputs) -> mengembalikan teks string final (drop-in replacement)
    - .invoke_full(inputs) -> mengembalikan dict lengkap berisi trace & tool_results
    """
    def __init__(self):
        self.graph = create_stock_agent_graph()

    def invoke_full(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "dummy" or "your_groq_api_key" in api_key.lower():
            return {
                "final_analysis": (
                    "⚠️ **API Key Groq belum dikonfigurasi.**\n\n"
                    "Untuk mengaktifkan arsitektur Multi-Agent AI (Valuation Agent, Risk Officer, CIO):\n"
                    "1. Buka file `.env` di folder proyek\n"
                    "2. Masukkan `GROQ_API_KEY=gsk_...` (gratis di [console.groq.com/keys](https://console.groq.com/keys))\n"
                    "3. Muat ulang aplikasi Anda."
                ),
                "agent_trace": [],
                "tool_results": {}
            }

        initial_state: StockAgentState = {
            "ticker": inputs.get("ticker", ""),
            "company_name": inputs.get("company_name", ""),
            "price": inputs.get("price"),
            "score": inputs.get("score"),
            "category": inputs.get("category", ""),
            "fair_value": inputs.get("fair_value", ""),
            "mos": inputs.get("mos", ""),
            "metrics": inputs.get("metrics", ""),
            "signals": inputs.get("signals", ""),
            "business_summary": inputs.get("business_summary", ""),
            "raw_data": inputs.get("raw_data"),
            "agent_trace": []
        }

        result = self.graph.invoke(initial_state)
        return result

    def invoke(self, inputs: Dict[str, Any]) -> str:
        """
        Backwards-compatible call: mengembalikan string Markdown analisis final.
        """
        full_res = self.invoke_full(inputs)
        return full_res.get("final_analysis", "Gagal memproses analisis multi-agent.")


def build_stock_agent_graph():
    """Factory helper untuk inisialisasi workflow runner."""
    return StockAgentRunner()
