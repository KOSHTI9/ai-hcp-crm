import os
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

from app.tools.ai_tools import (
    search_hcp_tool,
    log_interaction_tool,
    edit_interaction_tool,
    summarize_interaction_tool,
    recommend_followup_tool,
)

load_dotenv()


# -----------------------------
# STATE
# -----------------------------
class AgentState(TypedDict):
    message: str
    db: object
    result: dict


# -----------------------------
# LLM (kept for future use)
# -----------------------------
llm = ChatGroq(
    model="gemma2-9b-it",
    api_key=os.getenv("GROQ_API_KEY")
)


# -----------------------------
# SAFE EXTRACTION (NO API NEEDED)
# -----------------------------
def extract_interaction_data(message: str):
    return {
        "hcp_name": "Dr. Smith",
        "interaction_type": "Meeting",
        "topics_discussed": "Product X efficacy",
        "materials_shared": "Brochure",
        "samples_distributed": "",
        "sentiment": "Positive",
        "outcomes": "",
        "follow_up_actions": "Schedule follow-up meeting",
        "notes": message,
    }


# -----------------------------
# MAIN AGENT NODE
# -----------------------------
def agent_node(state: AgentState):
    message = state["message"]
    db = state["db"]

    # Step 1: Extract data
    extracted = extract_interaction_data(message)

    # Step 2: Search HCP
    hcp = search_hcp_tool(db, extracted.get("hcp_name", "Dr. Smith"))

    if not hcp:
        return {
            "result": {
                "error": "HCP not found. Please create HCP first."
            }
        }

    # Step 3: Log Interaction
    interaction_data = {
        "hcp_id": hcp.id,
        "interaction_type": extracted.get("interaction_type", "Meeting"),
        "notes": extracted.get("notes", message),
        "topics_discussed": extracted.get("topics_discussed", ""),
        "materials_shared": extracted.get("materials_shared", ""),
        "samples_distributed": extracted.get("samples_distributed", ""),
        "sentiment": extracted.get("sentiment", "Neutral"),
        "outcomes": extracted.get("outcomes", ""),
        "follow_up_actions": extracted.get("follow_up_actions", ""),
    }

    interaction = log_interaction_tool(db, interaction_data)

    # Step 4: Summarize
    summary = summarize_interaction_tool(message)

    # Step 5: Recommend Follow-up
    followup = recommend_followup_tool(interaction.sentiment)

    # Step 6: Edit Interaction (update follow-up)
    edited = edit_interaction_tool(
        db,
        interaction.id,
        {"follow_up_actions": followup}
    )

    # Final Response
    return {
        "result": {
            "tool_1_search_hcp": hcp.name,
            "tool_2_log_interaction": interaction.id,
            "tool_3_edit_interaction": "follow_up_actions updated",
            "tool_4_summary": summary,
            "tool_5_recommend_followup": followup,
            "saved_interaction": {
                "id": edited.id,
                "hcp_id": edited.hcp_id,
                "sentiment": edited.sentiment,
                "topics_discussed": edited.topics_discussed,
                "materials_shared": edited.materials_shared,
                "follow_up_actions": edited.follow_up_actions,
            },
        }
    }


# -----------------------------
# LANGGRAPH BUILD
# -----------------------------
builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)
builder.set_entry_point("agent")
builder.add_edge("agent", END)

hcp_graph = builder.compile()