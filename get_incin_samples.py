import sys, numpy as np, pandas as pd
sys.path.insert(0, sys.argv[1])
from fpmodel.inputs import Params, load_workbook
from fpmodel.pathways import run_pathway, IMPACTS
data = load_workbook(sys.argv[1] + '/assumptions_v2.xlsx')
P = Params(data, 'A_HWC', 'PTFE', 10000, seed=42)
cost, imp, ind, prod, stack = run_pathway(P, data, 'PTFE')
tc = sum(cost.values()); ti = sum(imp.values())
df = pd.DataFrame(ti, columns=IMPACTS); df.insert(0, 'cost_USD_per_t', tc)
df.to_csv('./incin_PTFE_HWC_samples.csv', index=False)
print(df.median().to_dict())
