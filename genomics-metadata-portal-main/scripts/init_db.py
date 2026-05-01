import os
import subprocess
from pathlib import Path

from app.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
SQL_DIR = BASE_DIR / "sql"


def run_sql_file(sql_file: Path) -> None:
    logger.info("Applying SQL file: %s", sql_file.name)

    env = os.environ.copy()
    env["PGPASSWORD"] = env.get("POSTGRES_PASSWORD") or env.get("DB_PASSWORD", "")

    command = [
        "psql",
        "-h",
        env.get("POSTGRES_HOST") or env.get("DB_HOST", "postgres"),
        "-p",
        str(env.get("POSTGRES_PORT") or env.get("DB_PORT", "5432")),
        "-U",
        env.get("POSTGRES_USER") or env.get("DB_USER", "genomics_user"),
        "-d",
        env.get("POSTGRES_DB") or env.get("DB_NAME", "genomics_portal"),
        "-v",
        "ON_ERROR_STOP=1",
        "-f",
        str(sql_file),
    ]

    result = subprocess.run(command, cwd=BASE_DIR, env=env, check=False)

    if result.returncode != 0:
        raise RuntimeError(f"Failed to apply {sql_file.name}")

    logger.info("Applied SQL file successfully: %s", sql_file.name)


def main() -> None:
    logger.info("Initializing database from SQL files")

    sql_files = [
        "001_schema.sql",
        "002_constraints_indexes.sql",
        "003_seed_reference_data.sql",
    ]

    optional_sql = SQL_DIR / "004_provenance_association_alignment.sql"
    if optional_sql.exists():
        sql_files.append("004_provenance_association_alignment.sql")

    for sql_name in sql_files:
        run_sql_file(SQL_DIR / sql_name)

    logger.info("Database initialization complete")


if __name__ == "__main__":
    main()