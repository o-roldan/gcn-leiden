"""Step 1 (design graphs only): two pre-registered corrections of the
cross-view agreement criterion.

    A  attenuation correction:  A*(γ) = ARI(L_γ, KM_k) / sqrt(R_X(k) · R_T(γ))
         R_X(k): mean pairwise ARI among k-means runs (seeds 0-4)
         R_T(γ): mean pairwise ARI among Leiden runs (seeds 0-4), giant comp.
    B  AMI instead of ARI:      B(γ) = mean_s AMI(L_γ, KM_s)

Fixed setup: same γ grid, k >= 3, L_γ = Leiden seed 123 (thesis prior),
k-means on TF-IDF + L2 rows, n_init=3, seeds 0-4. Decision = plain argmax,
no tie-break. Labels are used ONLY for the evaluation column (ARI of L_γ).
Pass condition: the chosen γ gives ARI(prior) >= that of γ = 0.3.
"""

import itertools
import sys

import networkx as nx
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import adjusted_mutual_info_score as ami
from sklearn.metrics import adjusted_rand_score as ari
from sklearn.preprocessing import normalize

from gcn_leiden.datasets import load_dataset
from gcn_leiden.prior import detect_communities

GAMMAS = [0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0]
SEEDS = range(5)


def giant_labels(graph, giant, gamma, seed):
    comms = detect_communities(graph, "leiden", gamma, seed, "modularity")
    index = {v: c for c, nodes in enumerate(comms) for v in nodes}
    return np.array([index[v] for v in giant])


def mean_pairwise_ari(parts):
    return float(np.mean([ari(a, b) for a, b in itertools.combinations(parts, 2)]))


for dataset in sys.argv[1:]:
    data = load_dataset(dataset)
    graph = nx.from_numpy_array(data.adj)
    giant = np.array(sorted(max(nx.connected_components(graph), key=len)))
    y = data.label[giant]
    x = normalize(TfidfTransformer().fit_transform(data.feat[giant]))

    rows = []
    for gamma in GAMMAS:
        part = giant_labels(graph, giant, gamma, 123)
        k = np.unique(part).size
        if k < 3:
            continue
        kms = [KMeans(n_clusters=k, n_init=3, random_state=s).fit_predict(x)
               for s in SEEDS]
        r_x = mean_pairwise_ari(kms)
        r_t = mean_pairwise_ari([giant_labels(graph, giant, gamma, s) for s in SEEDS])
        raw = float(np.mean([ari(part, km) for km in kms]))
        rel = r_x * r_t
        rows.append(dict(
            gamma=gamma, k=k, raw=raw, r_x=r_x, r_t=r_t,
            a_star=raw / np.sqrt(rel) if rel > 0 else float("nan"),
            b_ami=float(np.mean([ami(part, km) for km in kms])),
            ari_prior=ari(y, part)))

    print(f"\n== {dataset}: giant {giant.size}/{graph.number_of_nodes()} nodes")
    print(f"{'gamma':>6} {'k':>4} {'ARI vistas':>10} {'R_X':>6} {'R_T':>6} "
          f"{'A* (A)':>7} {'AMI (B)':>8} {'ARI prior':>10}")
    for r in rows:
        print(f"{r['gamma']:>6} {r['k']:>4} {r['raw']:>10.3f} {r['r_x']:>6.3f} "
              f"{r['r_t']:>6.3f} {r['a_star']:>7.3f} {r['b_ami']:>8.3f} "
              f"{r['ari_prior']:>10.3f}")
    base = next(r for r in rows if r["gamma"] == 0.3)
    best = max(rows, key=lambda r: r["ari_prior"])
    for name, key in (("raw (antes)", "raw"), ("A: atenuación", "a_star"),
                      ("B: AMI", "b_ami")):
        valid = [r for r in rows if not np.isnan(r[key])]
        pick = max(valid, key=lambda r: r[key])
        verdict = "PASA" if pick["ari_prior"] >= base["ari_prior"] else "NO PASA"
        print(f"  {name:14s} elige γ={pick['gamma']:<5} k={pick['k']:<3} "
              f"ARI prior={pick['ari_prior']:.3f}  vs γ=0.3: "
              f"{base['ari_prior']:.3f}  -> {verdict}")
    print(f"  (mejor posible: γ={best['gamma']} k={best['k']} "
          f"ARI prior={best['ari_prior']:.3f})")
