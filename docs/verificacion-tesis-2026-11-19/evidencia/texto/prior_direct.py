import sys, time, numpy as np, networkx as nx
from gcn_leiden.datasets import load_dataset
from gcn_leiden.prior import detect_communities, filter_by_size
jobs=[('cora',0.3,'modularity',['louvain','leiden']),('citeseer',0.3,'modularity',['louvain','leiden']),
      ('wikics',0.3,'modularity',['louvain','leiden']),('amap',0.3,'modularity',['louvain','leiden']),
      ('film',1.0,'modularity',['louvain','leiden']),
      ('sbm_1000_5',1.0,'modularity',['louvain','leiden']),('sbm_1000_5',0.3,'modularity',['louvain','leiden']),('sbm_1000_5',0.0275,'cpm',['leiden']),
      ('sbm_5000_10',1.0,'modularity',['louvain','leiden']),('sbm_5000_10',0.3,'modularity',['louvain','leiden']),
      ('sbm_10000_20',1.0,'modularity',['louvain','leiden']),('sbm_10000_20',0.0275,'cpm',['leiden'])]
cache={}
for ds,res,obj,meths in jobs:
    if ds not in cache:
        t=time.time(); data=load_dataset(ds); g=nx.from_numpy_array(data.adj); cache={ds:(data,g)}
        print(f'# {ds}: n={data.num_nodes} nx_nodes={g.number_of_nodes()} edges={g.number_of_edges()} isolated={nx.number_of_isolates(g)} ({time.time()-t:.0f}s)',flush=True)
    data,g=cache[ds]
    for m in meths:
        comms=detect_communities(g,m,res,123,obj)
        sizes=np.array([len(c) for c in comms],float)
        cover=sum(len(c) for c in comms); uni=len(set().union(*comms))
        T5=sizes.mean()+0.5*sizes.std()
        print(f'{ds} {m} {obj} g={res}: k0={len(comms)} sum_sizes={int(cover)} union={uni} mu={sizes.mean():.3f} cv={sizes.std()/sizes.mean():.4f} T(b=0.5)={T5:.2f} sizes_top={sorted(sizes.astype(int))[-5:]}',flush=True)
