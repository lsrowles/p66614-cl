import json, numpy as np, pandas as pd, matplotlib
import matplotlib.ticker
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
def ticks(ax,mirror):
    """left/bottom ticks cross the axis; top/right ticks point inward (mirror panels only)"""
    ax.tick_params(axis='both',which='major',direction='inout',length=5,top=False,right=False)
    ax.tick_params(axis='both',which='minor',direction='inout',length=3,top=False,right=False)
    if mirror:
        sx=ax.secondary_xaxis('top'); sx.set_xticks(ax.get_xticks()); sx.tick_params(direction='in',length=3,labeltop=False)
        sy=ax.secondary_yaxis('right'); sy.set_yticks(ax.get_yticks()); sy.tick_params(direction='in',length=3,labelright=False)
        sx.xaxis.set_minor_locator(matplotlib.ticker.NullLocator()) if ax.get_xscale()!='log' else None
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','Liberation Sans','DejaVu Sans'],
 'font.size':8,'axes.linewidth':0.8,'svg.fonttype':'none','pdf.fonttype':42,'mathtext.default':'regular'})
R=json.load(open('./results.json')); g=R['ground']; b=R['bulk']
cats=['ODP','GWP','EFW','HTNC','PMFP','HTC','AP','MIR','EP']
lab={'ODP':'Ozone depletion','GWP':'Global warming','EFW':'Freshwater ecotoxicity','HTNC':'Human tox. (non-cancer)',
 'PMFP':'Particulate matter','HTC':'Human tox. (cancer)','AP':'Acidification','MIR':'Max. incremental reactivity','EP':'Eutrophication'}
cats=sorted(cats,key=lambda c:g['ratio_'+c][1])
BETTER,WORSE='#3D7A72','#A9544B'; OM,EN,CAP='#7B68A6','#E3AE3F','#C9505B'
fig=plt.figure(figsize=(7.2,3.6))
# (a)
ax=fig.add_axes([0.20,0.18,0.36,0.70])
y=np.arange(len(cats))[::-1]
for yi,c in zip(y,cats):
    lo,m,hi=g['ratio_'+c]; col=BETTER if m<1 else WORSE
    ax.barh(yi,m,0.62,color=col,left=0); ax.errorbar(m,yi,xerr=[[m-lo],[hi-m]],color='0.2',capsize=2,lw=0.8)
    ax.plot(b['ratio_'+c][1],yi,marker='D',ms=3.5,mfc='white',mec='0.15',mew=0.8,ls='none',zorder=5)
    ax.text(hi*1.25,yi,f'{m:.2g}×' if m<10 else f'{m:.0f}×',va='center',fontsize=7,color=col)
ax.set_xscale('log'); ax.set_xlim(0.1,3000); ax.axvline(1,color='k',ls='--',lw=0.9)
ax.set_yticks(y); ax.set_yticklabels([lab[c] for c in cats]); ax.set_xlabel('IL impact / incineration impact')
ax.text(0.92,len(cats)-0.35,'better',ha='right',fontsize=7,color=BETTER,style='italic')
ax.text(1.1,len(cats)-0.35,'worse',ha='left',fontsize=7,color=WORSE,style='italic')
ax.set_ylim(-0.6,len(cats)-0.1)
ax.plot([],[],marker='D',ms=3.5,mfc='white',mec='0.15',ls='none',label='bulk composite')
ax.add_patch(plt.Rectangle((0,0),0,0,color=WORSE,label='ground composite (5-95%)'))
ax.legend(loc='upper center',bbox_to_anchor=(0.5,-0.13),ncol=2,fontsize=7,frameon=False,handlelength=1)
ax.text(-0.5,1.06,'(a)',transform=ax.transAxes,fontweight='bold',fontsize=9)
if ax.name!='polar': ticks(ax,True)
# (b)
ax=fig.add_axes([0.62,0.18,0.35,0.70])
for yi,c in zip(y,cats):
    o=g['OM_impacts'][c]*100; e=g['energy_impacts'][c]*100; k=g['capital_impacts'][c]*100
    ax.barh(yi,o,0.75,color=OM); ax.barh(yi,e,0.75,left=o,color=EN); ax.barh(yi,k,0.75,left=o+e,color=CAP)
    ax.text(o/2,yi,f'{o:.0f}',ha='center',va='center',color='white',fontsize=7)
    ax.text(o+e/2,yi,f'{e:.0f}',ha='center',va='center',color='0.15',fontsize=7)
ax.set_xlim(0,100); ax.set_yticks(y); ax.set_yticklabels([]); ax.set_ylim(-0.6,len(cats)-0.1)
ax.set_xlabel('Contribution to IL impact (%)'); ax.set_xticks([0,25,50,75,100])
h=[plt.Rectangle((0,0),1,1,color=cc) for cc in (OM,EN,CAP)]
ax.legend(h,['Operation & maintenance','Energy','Capital'],loc='upper center',bbox_to_anchor=(0.5,-0.13),ncol=3,fontsize=7,frameon=False,handlelength=1)
ax.text(-0.08,1.06,'(b)',transform=ax.transAxes,fontweight='bold',fontsize=9)
if ax.name!='polar': ticks(ax,False)
for ext in ('png','svg','pdf'): fig.savefig(f'./FigureS10.{ext}',dpi=300,bbox_inches='tight')
