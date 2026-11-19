# [P66614][Cl] PTFE recovery: LCA and LCC (revised model)

Revision of the sustainability model for the Fe-PTFE ionic-liquid recovery manuscript.
Every change from the submitted model is commented in `P66614_Cl_corrected.py` with the reviewer comment it answers.

## Requirements
Python 3.10+, numpy, scipy, pandas, openpyxl, matplotlib, pydoe (`lhs.py` imports `pydoe`; the old `pyDOE` package was renamed).

## Run
```
SCENARIO=ground python P66614_Cl_corrected.py                       # base case: ground composite, 0.5 h
SCENARIO=bulk   python P66614_Cl_corrected.py                       # bulk composite, 48-72 h
SCENARIO=ground REUSE=10 OUTFILE=reuse/g_10.xlsx python P66614_Cl_corrected.py   # fixed reuse cycles (Fig. 6c uses 1-40)
SCENARIO=ground CREDIT=1 OUTFILE=P66614_Cl_ground_credit.xlsx python P66614_Cl_corrected.py   # recovered-PTFE credit
python break_even.py                                                # virgin-PTFE GWP at which IL matches incineration
```

## Key definitions
- Functional unit: 1 kg of Fe-PTFE composite treated (LCA and LCC). Reference flow: 0.450 g PTFE + 0.050 g Fe3O4 per batch.
- IL recovery: 0.95-0.98 per cycle (measured, Table S4); losses replaced each cycle.
- Fresh HCl and H2O2 every cycle; acetone recovered by rotary evaporation (80-95%, assumed) and replenished.
- Energy: hotplate (nameplate, charged once); grinding, vacuum filtration, rotary evaporation, and drying charged per batch.
- Waste: NaOH neutralization of residual HCl; acidic and alkaline liquors to average wastewater treatment (ecoinvent 3.10).
- Credit (sensitivity, CREDIT=1): recovered PTFE (0.92 kg/kg composite) displaces virgin PTFE at a substitution ratio of 0.5-0.8,
  using ecoinvent 3.10 market for tetrafluoroethylene (GLO, TRACI 2.1) as a proxy and a virgin PTFE price of 7.3-18.7 USD/kg.
- Rows marked ASSUMED in `assumptions.xlsx` are laboratory equipment estimates awaiting measured values.

## Figures
`fig6.py`, `figS9.py`, `figS10.py` regenerate the figures from the model outputs. `get_incin_samples.py` draws the
hazardous-waste-combustion Monte Carlo samples from the companion incineration model (fp_eol_v2; provisional baseline).
Figures use Arial when installed.
