import numpy as np

SPHERES = [((0.0, 1.0, -4.0), 1.0, 0.9), ((2.0, 0.6, -5.0), 0.6, 0.6), ((-2.0, 0.8, -3.5), 0.8, 0.4)]
NAMES = ["sky", "sphere_1", "sphere_2", "sphere_3", "floor"]
LIGHT = np.array([5.0, 8.0, 2.0])
TARGET = np.array([0.0, 0.8, -4.0])


def trace(cam_x=0.0, cam_y=2.0, cam_z=3.0, fov=60.0, size=40):
    """Shoot size*size rays from the camera; return per-ray results as arrays."""
    o = np.array([cam_x, cam_y, cam_z], float)
    f = TARGET - o
    f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1, 0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    s = np.tan(np.radians(fov) / 2)
    px, py = (a.ravel() for a in np.meshgrid(np.arange(size), np.arange(size)))
    d = f + ((2 * (px + .5) / size - 1) * s)[:, None] * r + ((1 - 2 * (py + .5) / size) * s)[:, None] * u
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    n = len(px)
    best, obj = np.full(n, np.inf), np.zeros(n, int)
    normal, albedo = np.zeros((n, 3)), np.zeros(n)
    for i, (c, rad, alb) in enumerate(SPHERES, 1):   # the quadratic from our maths
        c = np.array(c)
        oc = o - c
        hb = d @ oc
        disc = hb ** 2 - (oc @ oc - rad ** 2)
        with np.errstate(invalid="ignore"):
            t = -hb - np.sqrt(disc)
        ok = (disc >= 0) & (t > 1e-4) & (t < best)
        best[ok], obj[ok], albedo[ok] = t[ok], i, alb
        normal[ok] = ((o + t[:, None] * d)[ok] - c) / rad
    with np.errstate(divide="ignore", invalid="ignore"):   # floor plane y = 0
        t = -o[1] / d[:, 1]
    ok = (d[:, 1] < 0) & (t > 1e-4) & (t < best)
    best[ok], obj[ok], albedo[ok], normal[ok] = t[ok], 4, 0.5, [0, 1, 0]
    hit = obj > 0
    p = o + np.where(hit, best, 0)[:, None] * d
    l = LIGHT - p
    l /= np.linalg.norm(l, axis=1, keepdims=True)
    lam = np.clip((normal * l).sum(1), 0, 1)
    bright = np.clip(np.where(hit, 0.1 + 0.9 * lam * albedo, 0.1), 0, 1)
    return dict(pixel_x=px, pixel_y=py, obj=obj, hit=hit,
                distance=np.where(hit, best, np.nan), brightness=bright, normal=normal)


def render(**kw):
    """Same as trace(), but as a list of JSON-friendly dicts (one per ray)."""
    t = trace(**kw)
    rows = []
    for k in range(len(t["pixel_x"])):
        h = bool(t["hit"][k])
        nx, ny, nz = (round(float(v), 4) for v in t["normal"][k])
        rows.append({"pixel_x": int(t["pixel_x"][k]), "pixel_y": int(t["pixel_y"][k]), "hit": h,
                     "surface": NAMES[t["obj"][k]],
                     "distance": round(float(t["distance"][k]), 4) if h else None,
                     "brightness": round(float(t["brightness"][k]), 4), "nx": nx, "ny": ny, "nz": nz})
    return rows
