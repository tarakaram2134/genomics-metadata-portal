#!/bin/bash
set -e

echo "Waiting for database..."
sleep 5

echo ""
echo "Checking whether database is initialized..."
if PGPASSWORD="${POSTGRES_PASSWORD:-${DB_PASSWORD}}" psql \
    -h "${POSTGRES_HOST:-${DB_HOST:-postgres}}" \
    -p "${POSTGRES_PORT:-${DB_PORT:-5432}}" \
    -U "${POSTGRES_USER:-${DB_USER:-genomics_user}}" \
    -d "${POSTGRES_DB:-${DB_NAME:-genomics_portal}}" \
    -tAc "SELECT to_regclass('public.patients');" | grep -q patients; then
    echo "Database already initialized. Skipping schema init."
else
    echo "Initializing database..."
    python -m scripts.init_db
fi

echo ""
echo "Checking if synthetic data exists..."

if [ ! -f /app/data/raw/sample_metadata/patients.tsv ]; then
    echo "Synthetic data not found. Generating..."
    python -m scripts.generate_synthetic_data
else
    echo "Synthetic data already exists. Skipping generation."
fi

echo ""
echo "Ingesting samples..."
python -m scripts.ingest_samples

echo ""
echo "Registering sequencing runs..."
python -m scripts.register_sequencing_run

echo ""
echo "Registering pipeline runs..."
python -m scripts.register_pipeline_run

echo ""
echo "Registering file assets..."
python -m scripts.register_file_assets

echo ""
echo "Ingesting QC results..."
python -m scripts.ingest_qc_results

echo ""
echo "Ingesting variant summaries..."
python -m scripts.ingest_variant_summaries

echo ""
echo "Starting Streamlit..."
exec streamlit run streamlit_app/Home.py --server.port=8501 --server.address=0.0.0.0