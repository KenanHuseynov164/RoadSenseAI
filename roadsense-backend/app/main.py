from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import Base, engine, get_session
from . import models, schemas, nlp_rules
from fastapi import FastAPI, Depends, HTTPException, Header
from jose import jwt
from .auth_utils import (
    hash_password, verify_password, create_access_token, decode_token
)
from .schemas import UserRegister, UserLogin, TokenResponse


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

async def get_current_user(
    authorization: str = Header(None),
    session: AsyncSession = Depends(get_session)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = authorization.split(" ")[1]
    user_id = decode_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    stmt = select(models.User).where(models.User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

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

@app.post("/auth/register")
async def register_user(
    payload: UserRegister,
    session: AsyncSession = Depends(get_session),
):
    # Check if user exists
    stmt = select(models.User).where(models.User.email == payload.email)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        provider="local"
    )

    session.add(new_user)
    await session.commit()
    return {"message": "User registered successfully"}


@app.post("/auth/login", response_model=TokenResponse)
async def login_user(
    payload: UserLogin,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(models.User).where(models.User.email == payload.email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)

