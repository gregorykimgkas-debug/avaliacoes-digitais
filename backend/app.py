from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
import os

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import Assessment, Question, Submission
from .seed import seed_database


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"


@asynccontextmanager
async def lifespan(_: FastAPI):
    seed_database()
    yield


app = FastAPI(
    title="Avaliações Digitais — API demonstrativa",
    description="API acadêmica com dados anonimizados.",
    version="1.0.0",
    lifespan=lifespan,
)


class SubmissionInput(BaseModel):
    assessment_code: str
    participant_code: str = Field(min_length=3, max_length=40)
    client: str = Field(min_length=2, max_length=100)
    instructor: str = Field(min_length=2, max_length=100)
    score: float = Field(ge=0, le=100)
    submitted_at: datetime | None = None


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "avaliacoes-digitais"}


@app.get("/api/assessments")
def assessments(db: Session = Depends(get_db)):
    rows = db.scalars(select(Assessment).order_by(Assessment.title)).all()
    return [
        {
            "code": row.code,
            "title": row.title,
            "equipment": row.equipment,
            "form_url": row.form_url,
            "passing_score": row.passing_score,
            "has_exam": len(row.questions) > 0,
        }
        for row in rows
    ]


@app.get("/api/assessments/{code}/exam")
def get_exam(code: str, db: Session = Depends(get_db)):
    assessment = db.scalar(select(Assessment).where(Assessment.code == code))
    if not assessment:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    if not assessment.questions:
        raise HTTPException(status_code=404, detail="Esta avaliação não possui prova interna")
    return {
        "code": assessment.code,
        "title": assessment.title,
        "equipment": assessment.equipment,
        "passing_score": assessment.passing_score,
        "questions": [
            {"id": q.id, "order": q.order, "text": q.text, "options": q.options}
            for q in assessment.questions
        ],
    }


class ExamAnswer(BaseModel):
    question_id: int
    selected_index: int = Field(ge=0)


class ExamSubmission(BaseModel):
    participant_name: str = Field(min_length=2, max_length=100)
    client: str = Field(min_length=2, max_length=100, default="Demonstração")
    instructor: str = Field(min_length=2, max_length=100, default="Instrutor demonstrativo")
    answers: list[ExamAnswer]


@app.post("/api/assessments/{code}/exam")
def submit_exam(code: str, payload: ExamSubmission, db: Session = Depends(get_db)):
    assessment = db.scalar(select(Assessment).where(Assessment.code == code))
    if not assessment:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    questions = {q.id: q for q in assessment.questions}
    if not questions:
        raise HTTPException(status_code=400, detail="Esta avaliação não possui prova interna")

    correct = 0
    for answer in payload.answers:
        question = questions.get(answer.question_id)
        if question is not None and answer.selected_index == question.correct_index:
            correct += 1
    total = len(questions)
    score = round(correct / total * 100, 1)

    item = Submission(
        assessment_id=assessment.id,
        participant_code=payload.participant_name,
        client=payload.client,
        instructor=payload.instructor,
        score=score,
        submitted_at=datetime.now(),
    )
    db.add(item)
    db.commit()

    return {
        "score": score,
        "correct": correct,
        "total": total,
        "status": "Aprovado" if score >= assessment.passing_score else "Reprovado",
    }


@app.get("/api/dashboard")
def dashboard(
    assessment: str | None = Query(default=None),
    client: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = select(Submission, Assessment).join(Assessment)
    if assessment:
        query = query.where(Assessment.code == assessment)
    if client:
        query = query.where(Submission.client == client)
    rows = db.execute(query.order_by(Submission.submitted_at.desc())).all()

    values = [row.Submission.score for row in rows]
    approved = sum(row.Submission.score >= row.Assessment.passing_score for row in rows)
    total = len(rows)
    by_assessment: dict[str, dict] = {}
    for row in rows:
        key = row.Assessment.code
        bucket = by_assessment.setdefault(
            key,
            {"code": key, "title": row.Assessment.title, "scores": [], "approved": 0},
        )
        bucket["scores"].append(row.Submission.score)
        bucket["approved"] += row.Submission.score >= row.Assessment.passing_score

    grouped = [
        {
            "code": item["code"],
            "title": item["title"],
            "responses": len(item["scores"]),
            "average": round(sum(item["scores"]) / len(item["scores"]), 1),
            "approval_rate": round(item["approved"] / len(item["scores"]) * 100, 1),
        }
        for item in by_assessment.values()
    ]
    return {
        "summary": {
            "responses": total,
            "average": round(sum(values) / total, 1) if total else 0,
            "approved": approved,
            "failed": total - approved,
            "approval_rate": round(approved / total * 100, 1) if total else 0,
        },
        "by_assessment": sorted(grouped, key=lambda item: item["title"]),
        "clients": sorted({row.Submission.client for row in rows}),
        "submissions": [
            {
                "participant": row.Submission.participant_code,
                "assessment": row.Assessment.title,
                "client": row.Submission.client,
                "instructor": row.Submission.instructor,
                "score": row.Submission.score,
                "status": "Aprovado" if row.Submission.score >= row.Assessment.passing_score else "Reprovado",
                "submitted_at": row.Submission.submitted_at.isoformat(),
            }
            for row in rows
        ],
    }


@app.post("/api/submissions", status_code=201)
def create_submission(
    payload: SubmissionInput,
    x_api_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    expected_key = os.getenv("ADMIN_API_KEY", "troque-por-uma-chave-segura")
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Chave de integração inválida")
    assessment = db.scalar(select(Assessment).where(Assessment.code == payload.assessment_code))
    if not assessment:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    item = Submission(
        assessment_id=assessment.id,
        participant_code=payload.participant_code,
        client=payload.client,
        instructor=payload.instructor,
        score=payload.score,
        submitted_at=payload.submitted_at or datetime.now(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "status": "registrado"}


app.mount("/assets", StaticFiles(directory=FRONTEND / "assets"), name="assets")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(FRONTEND / "index.html")


@app.get("/prova/{code}", include_in_schema=False)
def prova_page(code: str):
    return FileResponse(FRONTEND / "prova.html")
