from datetime import datetime

from sqlalchemy import func, select

from .database import Base, SessionLocal, engine
from .models import Assessment, Submission


ASSESSMENTS = [
    ("BR_CON_HP", "Britadores Cônicos HP", "Britador cônico", 70),
    ("BR_MAND_C", "Britadores de Mandíbulas Linha C", "Britador de mandíbulas", 70),
    ("MO_BOLAS", "Moinho de Bolas", "Moinho", 70),
    ("EQUIP_VIB", "Equipamentos Vibratórios", "Peneira vibratória", 70),
    ("MO_VERTMILL", "Moinho Vertical (Vertimill)", "Moinho vertical", 70),
]

SCORES = [
    ("BR_CON_HP", "ALU-001", "Cliente A", "Instrutor 1", 90, "2026-05-12T14:10:00"),
    ("BR_CON_HP", "ALU-002", "Cliente A", "Instrutor 1", 80, "2026-05-12T14:14:00"),
    ("BR_CON_HP", "ALU-003", "Cliente A", "Instrutor 1", 60, "2026-05-12T14:18:00"),
    ("BR_MAND_C", "ALU-004", "Cliente B", "Instrutor 2", 65, "2026-06-03T16:05:00"),
    ("BR_MAND_C", "ALU-005", "Cliente B", "Instrutor 2", 75, "2026-06-03T16:08:00"),
    ("MO_BOLAS", "ALU-006", "Cliente C", "Instrutor 1", 95, "2026-06-20T11:30:00"),
    ("MO_BOLAS", "ALU-007", "Cliente C", "Instrutor 1", 90, "2026-06-20T11:34:00"),
    ("MO_BOLAS", "ALU-008", "Cliente C", "Instrutor 1", 85, "2026-06-20T11:38:00"),
    ("EQUIP_VIB", "ALU-009", "Cliente D", "Instrutor 3", 70, "2026-07-08T15:20:00"),
    ("EQUIP_VIB", "ALU-010", "Cliente D", "Instrutor 3", 55, "2026-07-08T15:24:00"),
    ("MO_VERTMILL", "ALU-011", "Cliente E", "Instrutor 2", 88, "2026-08-16T10:11:00"),
    ("MO_VERTMILL", "ALU-012", "Cliente E", "Instrutor 2", 92, "2026-08-16T10:14:00"),
]


def seed_database() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(func.count()).select_from(Assessment)):
            return
        items = {}
        for code, title, equipment, passing_score in ASSESSMENTS:
            item = Assessment(
                code=code,
                title=title,
                equipment=equipment,
                passing_score=passing_score,
            )
            db.add(item)
            items[code] = item
        db.flush()
        for code, participant, client, instructor, score, date in SCORES:
            db.add(
                Submission(
                    assessment_id=items[code].id,
                    participant_code=participant,
                    client=client,
                    instructor=instructor,
                    score=score,
                    submitted_at=datetime.fromisoformat(date),
                )
            )
        db.commit()

