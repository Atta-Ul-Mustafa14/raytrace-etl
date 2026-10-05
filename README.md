# Ray tracing ETL + EDA pipeline

A mini ray tracer exposed as an API; an ETL pipeline pulls ray data from it, validates it with Pydantic,
cleans it with pandas, loads it into SQLite, and an EDA script analyses it.

    raytracer.py   ray-sphere / ray-floor maths      app.py   FastAPI API + serves public/
    models.py      Pydantic validation rules          etl.py   Extract -> Transform -> Load
    eda.py         4 EDA questions + charts           public/  live dashboard

## Run locally
    python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
    pip install -r requirements-dev.txt
    python etl.py          # creates data/rays.db and data/rejected.csv
    python eda.py          # creates eda_output/eda.png
    uvicorn app:app --reload   # dashboard at http://127.0.0.1:8000 , API docs at /docs

## Deploy (GitHub + Vercel)
1. Push this folder to your group's GitHub repo.
2. vercel.com -> Add New Project -> import the repo -> Deploy (FastAPI is auto-detected, no config needed).
3. Open the Vercel URL for the dashboard, and /docs for the API.
4. To run the ETL against the live API: `API_URL=https://your-project.vercel.app python etl.py`
