from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import Base, engine, get_session
from . import models, schemas, nlp_rules

app = FastAPI(title="RoadSenseAI Backend", version="0.1.0")

# CORS so React frontend can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- Dummy authentication: single test user ---
async def get_current_user(session: AsyncSession = Depends(get_session)) -> models.User:
    # For MVP we auto-login a single demo user.
    stmt = select(models.User).where(models.User.email == "demo@roadsense.ai")
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        user = models.User(email="demo@roadsense.ai", name="Demo User")
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user

# Healthcheck
@app.get("/api/health")
async def health():
    return {"status": "ok"}

# Submit incident + generate guidance
@app.post("/api/incidents", response_model=schemas.IncidentResponse)
async def create_incident(
    payload: schemas.IncidentCreate,
    session: AsyncSession = Depends(get_session),
    user: models.User = Depends(get_current_user),
):
    if not payload.description.strip():
        raise HTTPException(status_code=400, detail="Description cannot be empty.")

    legal_articles, explanation, recommendation, what_to_say = nlp_rules.analyze_incident(
        payload.description
    )

    incident = models.Incident(
        description=payload.description,
        user_id=user.id,
        legal_articles=";".join(legal_articles),
        explanation=explanation,
        recommendation=recommendation,
        what_to_say=what_to_say,
    )
    session.add(incident)
    await session.commit()
    await session.refresh(incident)

    return schemas.IncidentResponse(
        id=incident.id,
        description=incident.description,
        created_at=incident.created_at,
        legal_articles=incident.legal_articles.split(";"),
        explanation=incident.explanation,
        recommendation=incident.recommendation,
        what_to_say=incident.what_to_say,
    )

# List recent incidents (history)
@app.get("/api/incidents", response_model=list[schemas.IncidentResponse])
async def list_incidents(
    session: AsyncSession = Depends(get_session),
    user: models.User = Depends(get_current_user),
):
    stmt = (
        select(models.Incident)
        .where(models.Incident.user_id == user.id)
        .order_by(models.Incident.created_at.desc())
        .limit(20)
    )
    result = await session.execute(stmt)
    incidents = result.scalars().all()
    response = []
    for inc in incidents:
        response.append(
            schemas.IncidentResponse(
                id=inc.id,
                description=inc.description,
                created_at=inc.created_at,
                legal_articles=inc.legal_articles.split(";"),
                explanation=inc.explanation,
                recommendation=inc.recommendation,
                what_to_say=inc.what_to_say,
            )
        )
    return response
