"""Importa respostas anonimizadas de CSV para o banco da demonstração."""

import argparse
import csv
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import select  # noqa: E402

from backend.database import SessionLocal  # noqa: E402
from backend.models import Assessment, Submission  # noqa: E402
from backend.seed import seed_database  # noqa: E402


REQUIRED_COLUMNS = {
    "assessment_code",
    "participant_code",
    "client",
    "instructor",
    "score",
    "submitted_at",
}


def import_csv(path: Path) -> int:
    seed_database()
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Colunas ausentes: {', '.join(sorted(missing))}")
        rows = list(reader)

    inserted = 0
    with SessionLocal() as db:
        assessments = {item.code: item for item in db.scalars(select(Assessment)).all()}
        for row in rows:
            assessment = assessments.get(row["assessment_code"].strip())
            if not assessment:
                raise ValueError(f"Avaliação desconhecida: {row['assessment_code']}")
            score = float(row["score"].replace(",", "."))
            if not 0 <= score <= 100:
                raise ValueError(f"Nota fora do intervalo 0–100: {score}")
            db.add(
                Submission(
                    assessment_id=assessment.id,
                    participant_code=row["participant_code"].strip(),
                    client=row["client"].strip(),
                    instructor=row["instructor"].strip(),
                    score=score,
                    submitted_at=datetime.fromisoformat(row["submitted_at"].strip()),
                )
            )
            inserted += 1
        db.commit()
    return inserted


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="Arquivo CSV anonimizado")
    args = parser.parse_args()
    print(f"{import_csv(args.csv)} registros importados.")

