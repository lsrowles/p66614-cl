"""Virgin-PTFE GWP at which the IL route matches incineration once the recovered PTFE is credited.
Usage: python break_even.py IL_GWP INCIN_GWP  (both kg CO2-eq per kg composite)"""
import sys
il, inc = (float(sys.argv[1]), float(sys.argv[2])) if len(sys.argv) > 2 else (63.3, 4.5)
yield_ptfe = 0.92
for s in (1.0, 0.8, 0.65, 0.5):
    print(f'substitution {s:.2f}: break-even virgin PTFE GWP = {(il - inc) / (yield_ptfe * s):.0f} kg CO2-eq/kg')
