import itertools, os, sqlite3
import pandas as pd
import requests
from pydantic import ValidationError
from models import RayRow

API = os.getenv("API_URL")  # e.g. https://your-project.vercel.app ; unset = run the API in-process
if not API:
    from fastapi.testclient import TestClient
    from app import app
    client = TestClient(app)


def extract(params):
    r = requests.get(f"{API}/render", params=params, timeout=60) if API else client.get("/render", params=params)
    r.raise_for_status()
    return r.json()


def transform(payload, run_id):
    good, bad = [], []
    for row in payload["rays"]:
        try:
            good.append({**RayRow.model_validate(row).model_dump(), **payload["camera"], "run_id": run_id})
        except ValidationError as e:
            bad.append({**row, "error": e.errors()[0]["msg"], "run_id": run_id})
    return good, bad


def main():
    os.makedirs("data", exist_ok=True)
    good, bad = [], []
    for run_id, (y, x, fov) in enumerate(itertools.product([0.5, 1, 2, 4], [-2, 0, 2], [50, 90])):
        g, b = transform(extract({"cam_x": x, "cam_y": y, "cam_z": 3, "fov": fov, "size": 32}), run_id)
        good += g
        bad += b
    df = pd.DataFrame(good).drop_duplicates(["run_id", "pixel_x", "pixel_y"])
    with sqlite3.connect("data/rays.db") as con:
        df.to_sql("rays", con, if_exists="replace", index=False)  # re-running never duplicates rows
    pd.DataFrame(bad).to_csv("data/rejected.csv", index=False)
    print(f"loaded {len(df)} rows, rejected {len(bad)} ({len(bad) / (len(df) + len(bad)):.2%})")


if __name__ == "__main__":
    main()
