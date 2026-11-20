import networkx as nx, numpy as np
from gcn_leiden.datasets import _PYG_LOADERS
from gcn_leiden.prior import detect_communities
print(f"{'dataset':9} {'n':>6} {'comps':>6} {'aislados':>8} {'%gigante':>8} {'k_louv':>7} {'comps_enteras':>13} {'k_en_gigante':>12} {'k_ref':>5}")
for name in ['cora','citeseer','pubmed','cocs','amac','amap','film','wikics']:
    data=_PYG_LOADERS[name]('datasets_pyg')[0]
    G=nx.Graph(); G.add_nodes_from(range(data.num_nodes))
    G.add_edges_from((int(a),int(b)) for a,b in data.edge_index.t().tolist() if a!=b)
    comps=list(nx.connected_components(G)); giant=max(comps,key=len)
    iso=sum(1 for c in comps if len(c)==1)
    comms=detect_communities(G,"louvain",1.0,0)
    compsets=set(frozenset(c) for c in comps)
    whole=sum(1 for c in comms if frozenset(c) in compsets)
    ingiant=sum(1 for c in comms if next(iter(c)) in giant)
    kref=len(set(data.y.tolist()))
    print(f"{name:9} {G.number_of_nodes():6d} {len(comps):6d} {iso:8d} {100*len(giant)/G.number_of_nodes():7.1f}% {len(comms):7d} {whole:13d} {ingiant:12d} {kref:5d}")
