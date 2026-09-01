from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(160))
    equipment: Mapped[str] = mapped_column(String(120))
    form_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    passing_score: Mapped[float] = mapped_column(Float, default=70.0)
    submissions: Mapped[list["Submission"]] = relationship(back_populates="assessment")
    questions: Mapped[list["Question"]] = relationship(back_populates="assessment", order_by="Question.order")


class Question(Base):
    """Pergunta de multipla escolha de uma prova interna (nao-Microsoft Forms).
    Conteudo tecnico reaproveitado de material de treinamento real, mas
    reescrito com alternativas proprias (distratores) -- sem nome de
    participante real nem marca/logo da empresa."""

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), index=True)
    order: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(String(500))
    options: Mapped[list] = mapped_column(JSON)
    correct_index: Mapped[int] = mapped_column(Integer)
    assessment: Mapped["Assessment"] = relationship(back_populates="questions")


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), index=True)
    participant_code: Mapped[str] = mapped_column(String(40), index=True)
    client: Mapped[str] = mapped_column(String(100), index=True)
    instructor: Mapped[str] = mapped_column(String(100), index=True)
    score: Mapped[float] = mapped_column(Float)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    assessment: Mapped[Assessment] = relationship(back_populates="submissions")

