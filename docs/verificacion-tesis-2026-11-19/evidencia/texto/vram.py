import pandas as pd
R='/Users/omar/Developer/me/gcn-leiden/results'
N={'pubmed':19717,'cocs':18333,'amac':13752,'cophysics':34493}
for ds,n in N.items():
    d=pd.read_csv(f'{R}/runs_{ds}.csv'); d=d[d.seed.between(0,4)]
    nn=n*n*4/2**20
    for m,g in d.groupby('method'):
        v=g.vram_peak_mb.mean()
        print(ds,m,'vram MiB',round(v,1),'ratio to n^2 fp32',round(v/nn,3))
    print(ds,'n^2 fp32 MiB',round(nn,1))
n=34493; print('physics n^2*4 GiB', n*n*4/2**30, 'x4.33 GiB', 4.33*n*n*4/2**30, 'L4 24GB in GiB', 24e9/2**30)
