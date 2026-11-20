import pandas as pd, numpy as np, glob, os
H='/Users/omar/Developer/me/gcn-leiden/results/history'
def summ(paths):
    q=[];qf=[]
    for p in paths:
        h=pd.read_csv(p); qp=-h.loss/1e-3; q.append(qp.max()); qf.append(qp.iloc[-1])
    return f'n={len(paths)} Qmax mean {np.mean(q):.3f}±{np.std(q,ddof=1):.3f} final {np.mean(qf):.3f}'
for m in ['leiden','louvain']:
    print('main film',m, summ(sorted(glob.glob(f'{H}/history_film/gcn-{m}_film_seed[0-4].csv'))))
    for sub in sorted(os.listdir(f'{H}/history_recal_film')):
        print('  recal',sub,m, summ(sorted(glob.glob(f'{H}/history_recal_film/{sub}/gcn-{m}_film_seed[0-4].csv'))))
mx=max(abs(pd.read_csv(p).loss).max() for p in glob.glob(f'{H}/history_film/gcn-leiden_film_seed[0-4].csv')); print('max |loss| leiden film', mx, 'Q', mx/1e-3)
