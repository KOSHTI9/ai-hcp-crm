from sqlalchemy.orm import Session
from app.models import HCP, Interaction


def search_hcp_tool(db: Session, name: str):
    hcp = db.query(HCP).filter(HCP.name.ilike(f"%{name}%")).first()
    return hcp


def log_interaction_tool(db: Session, data: dict):
    interaction = Interaction(**data)
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


def edit_interaction_tool(db: Session, interaction_id: int, updates: dict):
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        return None

    for key, value in updates.items():
        if hasattr(interaction, key):
            setattr(interaction, key, value)

    db.commit()
    db.refresh(interaction)
    return interaction


def summarize_interaction_tool(notes: str):
    return f"Summary: {notes}"


def recommend_followup_tool(sentiment: str):
    if sentiment.lower() == "positive":
        return "Schedule a follow-up meeting and share additional clinical data."
    if sentiment.lower() == "negative":
        return "Plan a re-engagement visit with objection-handling material."
    return "Send additional product information and follow up next week."
