from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from raytracer import render, trace

app = FastAPI(title="Ray tracer API")


@app.get("/render")
def render_endpoint(cam_x: float = Query(0.0, ge=-6, le=6), cam_y: float = Query(2.0, ge=0.2, le=8),
                    cam_z: float = Query(3.0, ge=0, le=8), fov: float = Query(60.0, ge=20, le=120),
                    size: int = Query(40, ge=8, le=80)):
    cam = {"cam_x": cam_x, "cam_y": cam_y, "cam_z": cam_z, "fov": fov, "size": size}
    return {"camera": cam, "rays": render(**cam)}


@app.get("/experiment")
def experiment():
    out = []
    for y in (0.5, 1, 2, 3, 4, 6):
        t = trace(0, y, 3, 60, 24)
        out.append({"cam_y": y, "hit_rate": round(float(t["hit"].mean()), 3)})
    return out


public = Path(__file__).parent / "public"
if public.is_dir():
    app.mount("/", StaticFiles(directory=public, html=True), name="public")
