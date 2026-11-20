P=/Users/omar/Developer/me/gcn-leiden/.venv/bin/python
W=/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/reverif
cd $W
for d in cora citeseer film amap wikics amac cocs pubmed; do
  $P $W/prior_cv.py $d '[["louvain","modularity",0.3],["leiden","modularity",0.3],["louvain","modularity",1.0],["leiden","modularity",1.0]]' >> $W/cv_out.jsonl 2>> $W/cv_err.txt
done
for d in sbm_1000_5 sbm_5000_10 sbm_10000_20; do
  $P $W/prior_cv.py $d '[["louvain","modularity",1.0],["leiden","modularity",1.0],["leiden","cpm",0.0275],["louvain","modularity",0.3],["leiden","modularity",0.3]]' >> $W/cv_out.jsonl 2>> $W/cv_err.txt
done
echo DONE >> $W/cv_out.jsonl
