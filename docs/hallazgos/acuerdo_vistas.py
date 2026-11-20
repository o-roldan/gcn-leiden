"""Exploratory test (Cora, design graph): does the cross-view agreement
criterion track the ARI of the prior partition?

For each resolution gamma of the Leiden prior (RBConfiguration, run on the
whole graph, seed 123 as in the thesis), take the communities inside the
giant component (k_gamma of them) and compare them with spherical k-means
(TF-IDF + L2 rows) on the raw features X with the same k, averaged over
several k-means seeds:

    agreement(gamma) = mean_s ARI( Leiden_gamma , kmeans_s(X, k_gamma) )

Gammas with k_gamma < 3 are excluded (k = 1 gives ARI = 1 trivially).
Labels are used ONLY to evaluate the criterion afterwards (ARI of the
Leiden partition against the classes); they never choose gamma.
"""

import sys

import networkx as nx
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import adjusted_rand_score as ari
from sklearn.metrics import normalized_mutual_info_score as nmi
from sklearn.preprocessing import normalize

from gcn_leiden.datasets import load_dataset
from gcn_leiden.prior import detect_communities

DATASET = sys.argv[1] if len(sys.argv) > 1 else "cora"
GAMMAS = [0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0]
KMEANS_SEEDS = range(5)


def ranks(values):
    order = np.argsort(values)
    r = np.empty(len(values))
    r[order] = np.arange(len(values))
    return r


def spearman(a, b):
    return float(np.corrcoef(ranks(np.asarray(a)), ranks(np.asarray(b)))[0, 1])


data = load_dataset(DATASET)
graph = nx.from_numpy_array(data.adj)
giant = np.array(sorted(max(nx.connected_components(graph), key=len)))
y = data.label[giant]
x = normalize(TfidfTransformer().fit_transform(data.feat[giant]))
print(f"{DATASET}: giant component {giant.size}/{graph.number_of_nodes()} "
      f"nodes, {np.unique(y).size} classes in it\n")

rows = []
print(f"{'gamma':>6} {'k':>4} {'agreement':>16} {'ARI prior':>10} "
      f"{'NMI prior':>10} {'ARI kmeans':>11}")
for gamma in GAMMAS:
    communities = detect_communities(graph, "leiden", gamma, 123, "modularity")
    index = {v: c for c, nodes in enumerate(communities) for v in nodes}
    part = np.array([index[v] for v in giant])
    k = np.unique(part).size
    if k < 3:
        print(f"{gamma:>6} {k:>4}   excluded (k < 3)")
        continue
    agree, km_true = [], []
    for seed in KMEANS_SEEDS:
        km = KMeans(n_clusters=k, n_init=3, random_state=seed).fit_predict(x)
        agree.append(ari(part, km))
        km_true.append(ari(y, km))
    row = dict(gamma=gamma, k=k, agree=np.mean(agree), agree_sd=np.std(agree),
               ari_prior=ari(y, part), nmi_prior=nmi(y, part),
               ari_km=np.mean(km_true))
    rows.append(row)
    print(f"{gamma:>6} {k:>4} {row['agree']:>9.3f}±{row['agree_sd']:.3f} "
          f"{row['ari_prior']:>10.3f} {row['nmi_prior']:>10.3f} "
          f"{row['ari_km']:>11.3f}")

agree = [r["agree"] for r in rows]
truth = [r["ari_prior"] for r in rows]
best_crit = rows[int(np.argmax(agree))]
best_true = rows[int(np.argmax(truth))]
print(f"\nSpearman(agreement, ARI prior) over {len(rows)} gammas: "
      f"{spearman(agree, truth):.2f}")
print(f"criterion picks gamma={best_crit['gamma']} (k={best_crit['k']}, "
      f"ARI prior={best_crit['ari_prior']:.3f})")
print(f"best ARI prior at gamma={best_true['gamma']} (k={best_true['k']}, "
      f"ARI prior={best_true['ari_prior']:.3f})")
floor = best_crit["agree"] - best_crit["agree_sd"]
rule = max((r for r in rows if r["agree"] >= floor), key=lambda r: r["gamma"])
print(f"1-sd rule (largest gamma with agreement >= {floor:.3f}) picks "
      f"gamma={rule['gamma']} (k={rule['k']}, ARI prior={rule['ari_prior']:.3f})")
print(f"thesis prior gamma=0.3 -> ARI prior="
      f"{next(r['ari_prior'] for r in rows if r['gamma'] == 0.3):.3f}")
