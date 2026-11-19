import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','Liberation Sans'],'font.size':7,'svg.fonttype':'none','pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(7.2,5.4)); ax.set_xlim(0,100); ax.set_ylim(0,76); ax.axis('off')
F=5.8
OM,EN,CAP,INC,GR='#7B68A6','#E3AE3F','#C9505B','#4F81BD','0.55'
def box(x,y,w,h,t,fc='white',ec='0.2',ls='-',fs=6.5,bold=False,tc='0.1'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.25,rounding_size=0.8',fc=fc,ec=ec,lw=0.9,ls=ls))
    ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=fs,fontweight='bold' if bold else 'normal',color=tc,linespacing=1.15)
def arr(x1,y1,x2,y2,c='0.25',ls='-'):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=7,color=c,lw=0.8,ls=ls,shrinkA=0,shrinkB=0))
# boundaries
ax.add_patch(FancyBboxPatch((14,38),84,36,boxstyle='round,pad=0,rounding_size=1.5',fc='#F3F0F8',ec=OM,lw=1.2,ls='--'))
ax.text(15.5,72,'(a) IL process boundary (gate-to-gate, lab scale)',fontsize=7.5,fontweight='bold',color=OM,va='top')
ax.add_patch(FancyBboxPatch((14,9),84,25,boxstyle='round,pad=0,rounding_size=1.5',fc='#EEF3F9',ec=INC,lw=1.2,ls='--'))
ax.text(15.5,32.5,'(b) Incineration boundary (companion model, hazardous waste combustion)',fontsize=7.5,fontweight='bold',color=INC,va='top')
# feed
box(1,52,10.4,8,'Fe-PTFE\ncomposite\n(1 kg)',fc='0.93',bold=True,fs=F)
box(1,17,10.4,8,'Fe-PTFE\ncomposite\n(1 kg)',fc='0.93',bold=True,fs=F)
# IL chain
F=5.8
box(16.5,55,10,7,'Grinding\n(ground case)',fs=F); box(30,55,13,7,'IL extraction\n90 °C, hotplate',fs=F); box(46.5,55,10,7,'Vacuum\nfiltration',fs=F)
box(60,61,17,7,'Acetone wash + drying\n(acetone recovered by\nrotary evaporation)',fs=F); box(60,48,17,7,'NaOH regeneration\nof Fe-loaded IL',fs=F)
box(84,61,12.5,7,'Recovered\nPTFE-rich solid',fc='#E4F1E4',fs=F); box(84,48,12.5,7,'Fe-oxide\nsolid',fc='#E4F1E4',fs=F)
box(30,40.5,13,6,'Acidic liquor:\nNaOH neutralization',fs=F); box(60,40.5,17,5.5,'Wastewater treatment',fs=F)
arr(11.4,56,16.5,58.5); arr(26.9,58.5,30,58.5); arr(43.4,58.5,46.5,58.5); arr(56.9,60.5,60,64); arr(56.9,56.5,60,52)
arr(77.4,64.5,84,64.5); arr(77.4,51.5,84,51.5)
arr(60,49.5,40,54.6,c=OM,ls='--'); ax.text(51.5,47.3,'IL recycled; makeup\nfor measured losses',fontsize=5.3,color=OM,ha='center')
arr(51.5,55,40,46.9); arr(43.4,43.5,60,43.3); arr(68.5,48,68.5,46.3)
ax.text(36.5,63.8,'IL, HCl, H$_2$O$_2$',fontsize=5.5,ha='center',color='0.3'); arr(36.5,63,36.5,62.4)
# incineration chain
box(16.5,17,12,8,'Transport to\npermitted facility',fs=F); box(32,17,14,8,'Rotary kiln\n~1100 °C\n(natural gas)',fs=F); box(50,17,14,8,'Wet lime\nscrubbing (APC)',fs=F)
box(68,22.5,14,5.5,'Stack emissions\n(CO$_2$, CF$_4$, HF)',fs=F); box(68,12.5,14,5.5,'APC residue\nto landfill',fs=F); box(86,17,10.5,7,'No material\nrecovered',fc='#F6E3E3',fs=F)
arr(11.4,21,16.5,21); arr(28.5,21,32,21); arr(46,21,50,21); arr(64,22.5,68,24.5); arr(64,19.5,68,15.5); arr(82,21,86,20.5,c=GR,ls=':')
# legend of included cost/impact elements
ax.text(1,6.5,'Included in both LCA and comparative LCC:',fontsize=6.5,fontweight='bold')
items=[(OM,'reagents and consumables (O&M)'),(EN,'electricity and fuel (energy)'),(CAP,'process equipment (capital)'),('0.5','aqueous waste treatment / APC residue')]
for k,(c,t) in enumerate(items):
    ax.add_patch(plt.Rectangle((1+k*25,2),1.6,2,color=c)); ax.text(3.2+k*25,3,t,fontsize=5.6,va='center')
ax.text(1,0.3,'Excluded from both: composite production, buildings, HVAC, lighting, and credits for recovered PTFE and Fe oxide. Labor and transport are included for incineration only (companion model).',fontsize=5.4,color='0.3',va='bottom')
for ext in ('png','svg','pdf'): fig.savefig(f'FigureS9.{ext}',dpi=300,bbox_inches='tight')
