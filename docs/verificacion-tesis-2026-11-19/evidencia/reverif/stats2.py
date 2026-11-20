exec(open("/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/reverif/common.py").read())
for ds in ["sbm_1000_5","sbm_5000_10","sbm_10000_20"]:
    for kind in ["recal","validate"]:
        df=load(f"runs_{kind}_{ds}.csv")
        print("==",kind,ds)
        for key,s in df.groupby(["method","prior_objective","resolution","beta","filter_variant"]):
            print(f"{str(key):60s} n={len(s)} seeds={sorted(s.seed)} k={sorted(s.k.unique())} k0={sorted(s.k0.unique())} ep={sorted(s.epochs.unique())}| NMI {ms(s.nmi)} ARI {ms(s.ari)} Q {ms(s.q)} DBI {ms(s.dbi)} | pNMI {ms(s.peak_nmi)} pARI {ms(s.peak_ari)}")
