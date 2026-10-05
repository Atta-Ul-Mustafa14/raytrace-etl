import os, sqlite3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_sql("select * from rays", sqlite3.connect("data/rays.db"))
print(df.shape, "\nMissing values:\n", df.isna().sum(), "\n", df.describe().T)
df["hit"] = df["hit"].astype(bool)  # SQLite stores booleans as 0/1
os.makedirs("eda_output", exist_ok=True)
fig, ax = plt.subplots(2, 2, figsize=(12, 8))
df.groupby("cam_y").hit.mean().plot(marker="o", ax=ax[0, 0], title="Q1: hit rate vs camera height")
share = df.groupby(["fov", "surface"]).size().unstack()
share.div(share.sum(axis=1), axis=0).plot.bar(stacked=True, ax=ax[0, 1], title="Q2: what the camera sees, by FOV")
df[df.hit].boxplot(column="distance", by="surface", ax=ax[1, 0])
ax[1, 0].set_title("Q3: hit distance by surface")
df.groupby(["cam_x", "surface"]).brightness.mean().unstack().plot.bar(ax=ax[1, 1], title="Q4: brightness by camera x")
plt.suptitle("")
plt.tight_layout()
plt.savefig("eda_output/eda.png", dpi=120)
print("\nHit rate by camera height:\n", df.groupby("cam_y").hit.mean().round(3))
