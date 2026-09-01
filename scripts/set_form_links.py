"""Atualiza os links públicos do Microsoft Forms a partir de um JSON."""

import argparse
import json
from pathlib import Path
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import select  # noqa: E402

from backend.database import SessionLocal  # noqa: E402
from backend.models import Assessment  # noqa: E402
from backend.seed import seed_database  # noqa: E402


ALLOWED_HOSTS = {"forms.office.com", "forms.microsoft.com"}


def update_links(path: Path) -> int:
    links = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(links, dict):
        raise ValueError("O arquivo deve conter um objeto código: URL")
    seed_database()
    updated = 0
    with SessionLocal() as db:
        assessments = {item.code: item for item in db.scalars(select(Assessment)).all()}
        for code, url in links.items():
            if code not in assessments:
                raise ValueError(f"Avaliação desconhecida: {code}")
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
                raise ValueError(f"Link inválido para {code}: use uma URL HTTPS do Microsoft Forms")
            assessments[code].form_url = url
            updated += 1
        db.commit()
    return updated


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json", type=Path, help="Arquivo JSON com os links")
    args = parser.parse_args()
    print(f"{update_links(args.json)} links atualizados.")

