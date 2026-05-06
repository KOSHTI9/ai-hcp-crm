
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.agents.hcp_agent import hcp_graph

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import HCP, Interaction

class ChatRequest(BaseModel):
    message: str

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-HCP CRM Backend")

app = FastAPI(title="AI-HCP CRM Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend and database are running successfully"}


@app.post("/hcps")
def create_hcp(name: str, specialty: str = "", location: str = "", db: Session = Depends(get_db)):
    hcp = HCP(name=name, specialty=specialty, location=location)
    db.add(hcp)
    db.commit()
    db.refresh(hcp)
    return hcp


@app.get("/hcps")
def get_hcps(db: Session = Depends(get_db)):
    return db.query(HCP).all()


@app.post("/interactions")
def create_interaction(
    hcp_id: int,
    notes: str,
    interaction_type: str = "Meeting",
    topics_discussed: str = "",
    materials_shared: str = "",
    samples_distributed: str = "",
    sentiment: str = "Neutral",
    outcomes: str = "",
    follow_up_actions: str = "",
    db: Session = Depends(get_db),
):
    interaction = Interaction(
        hcp_id=hcp_id,
        notes=notes,
        interaction_type=interaction_type,
        topics_discussed=topics_discussed,
        materials_shared=materials_shared,
        samples_distributed=samples_distributed,
        sentiment=sentiment,
        outcomes=outcomes,
        follow_up_actions=follow_up_actions,
    )

    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


@app.get("/interactions")
def get_interactions(db: Session = Depends(get_db)):
    return db.query(Interaction).all()

@app.post("/agent/chat")
def agent_chat(request: ChatRequest, db: Session = Depends(get_db)):
    result = hcp_graph.invoke({
        "message": request.message,
        "db": db,
        "result": {}
    })
    return result["result"]

