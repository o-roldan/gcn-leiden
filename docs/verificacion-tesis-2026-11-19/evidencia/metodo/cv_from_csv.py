import glob, os
import pandas as pd
R = "/Users/omar/Developer/me/gcn-leiden/results"
N = {"cora": 2708, "citeseer": 3327, "pubmed": 19717, "cocs": 18333, "cophysics": 34493,
     "amac": 13752, "amap": 7650, "film": 7600, "wikics": 11701,
     "sbm_1000_5": 1000, "sbm_5000_10": 5000, "sbm_10000_20": 10000}
frames = []
for f in sorted(glob.glob(f"{R}/runs_*.csv")):
    df = pd.read_csv(f); df["file"] = os.path.basename(f); frames.append(df)
df = pd.concat(frames)
df = df[df.method.str.startswith("gcn") & df.seed.isin(range(5))].copy()
cfg = df.config.str.split(";").apply(lambda kv: dict(x.split("=", 1) for x in kv))
for key in ("k0", "threshold", "beta", "resolution", "prior_objective", "prior_seed", "filter_variant"):
    df[key] = cfg.apply(lambda d: d.get(key))
df["k0"] = df.k0.astype(int); df["threshold"] = df.threshold.astype(float); df["beta"] = df.beta.astype(float)
df["n"] = df.dataset.map(N)
df["mean"] = df.n / df.k0
df = df[df.beta != 0]
df["cv"] = (df.threshold - df["mean"]) / df.beta / df["mean"]
g = df.groupby(["dataset", "method", "prior_objective", "resolution", "prior_seed"]).agg(
    k0=("k0", lambda s: sorted(set(s))), k=("k", lambda s: sorted(set(s))),
    cv_min=("cv", "min"), cv_max=("cv", "max"), files=("file", lambda s: sorted(set(s))))
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 80)
print(g.to_string())
