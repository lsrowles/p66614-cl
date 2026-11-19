import json, numpy as np, pandas as pd, matplotlib
import matplotlib.ticker
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
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
M='./'
ILC,CRC,INC='#7B68A6','#5B8C5A','#4F81BD'
cats=['AP','GWP','EFW','EP','HTC','HTNC','ODP','PMFP','MIR']
lab={'AP':'Acidification','GWP':'Global\nwarming','EFW':'Freshwater\necotoxicity','EP':'Eutrophication','HTC':'Human tox.\n(cancer)',
     'HTNC':'Human tox.\n(non-cancer)','ODP':'Ozone\ndepletion','PMFP':'Particulate\nmatter','MIR':'Max. incr.\nreactivity'}
# --- data (per kg composite)
cost=pd.read_excel(M+'P66614_Cl_ground_credit.xlsx',sheet_name='cost').total_cost.values
gross=pd.read_excel(M+'P66614_Cl_ground_credit.xlsx',sheet_name='impacts_PTFE')
net=pd.read_excel(M+'P66614_Cl_ground_credit.xlsx',sheet_name='impacts_net_of_credit')
inc=pd.read_csv('./incin_PTFE_HWC_samples.csv')*0.9/1000   # per kg composite (PTFE content)
cost_net=pd.read_excel(M+'P66614_Cl_ground_credit.xlsx',sheet_name='cost_net_of_credit').total_cost_net_of_credit.values
S={'IL process':(cost,gross,ILC),'IL process + PTFE credit':(cost_net,net,CRC),'Incineration (HWC)':(inc.cost_USD_per_t.values,inc,INC)}
fig=plt.figure(figsize=(7.2,9.6))
# (a) cost vs GWP KDE
ax=fig.add_axes([0.09,0.6954,0.36,0.2550])
xg=np.linspace(np.log10(100),np.log10(250),220); yg=np.linspace(-60,100,220); X,Y=np.meshgrid(xg,yg)
for name,(c,imp,col) in list(S.items())[:2]:
    lx=np.log10(c); gy=imp['GWP'].values
    idx=np.random.default_rng(1).choice(len(lx),3000,replace=False)
    k=gaussian_kde(np.vstack([lx[idx],gy[idx]])); Z=k(np.vstack([X.ravel(),Y.ravel()])).reshape(X.shape)
    zs=np.sort(Z.ravel())[::-1]; cs=np.cumsum(zs)/zs.sum()
    QS=(0.95,0.75,0.50,0.25,0.05)                      # probability mass enclosed by each region
    lv=[zs[min(np.searchsorted(cs,q),len(zs)-1)] for q in QS]
    for k_,(lev,alp) in enumerate(zip(lv,(0.12,0.22,0.34,0.48,0.65))):
        ax.contourf(X,Y,Z,levels=[lev,Z.max()],colors=[col],alpha=alp)
    ax.plot(np.median(lx),np.median(gy),'o',ms=4,mfc='white',mec=col,mew=1.2)
    ax.plot([],[],'s',ms=7,color=col,alpha=0.6,label=name)
ax.axhline(0,color='0.5',lw=0.6)
tk=[100,125,150,175,200,250]; ax.set_xticks(np.log10(tk)); ax.set_xticklabels([str(t) for t in tk]); ax.set_xlim(np.log10(105),np.log10(240)); ax.set_ylim(-60,100)
ax.set_xlabel('Cost (USD/kg composite)'); ax.set_ylabel('GWP (kg CO$_2$-eq/kg composite)')
ax.legend(loc='upper left',fontsize=6.5,frameon=False,handlelength=1)
ax.text(-0.2,1.04,'(a)',transform=ax.transAxes,fontweight='bold',fontsize=9)
if ax.name!='polar': ticks(ax,True)
# (b) spider: each category normalized to the largest scenario median
ax=fig.add_axes([0.6,0.6883,0.33,0.2338],projection='polar')
th=np.linspace(0,2*np.pi,len(cats),endpoint=False); th2=np.r_[th,th[0]]
med={n:np.array([np.median(imp[c].values) for c in cats]) for n,(_,imp,_) in S.items()}
mx=np.max(np.clip(np.vstack(list(med.values())),0,None),axis=0)   # largest positive median per category
RMIN=-0.6
ax.set_theta_zero_location('N'); ax.set_theta_direction(-1)
for n,(_,_,col) in S.items():
    v=med[n]/mx; vc=np.clip(v,RMIN,1); vv=np.r_[vc,vc[0]]
    ax.plot(th2,vv,color=col,lw=1.4); ax.fill(th2,vv,color=col,alpha=0.10)
    for t_,a_,b_ in zip(th,v,vc):
        if a_<RMIN:
            ax.plot(t_,b_,marker='o',ms=5,mfc='white',mec=col,mew=1.2)
            ax.text(t_,RMIN+0.33,'off scale\n(net credit)',fontsize=5.5,color=col,ha='center',va='center')
ax.set_ylim(RMIN,1.05); ax.set_yticks([0,0.5,1]); ax.set_yticklabels(['0','0.5','1'],fontsize=6,color='0.4')
ax.plot(np.linspace(0,2*np.pi,200),np.zeros(200),color='k',lw=0.8)
ax.set_xticks(th); ax.set_xticklabels([lab[c] for c in cats],fontsize=6.5)
ax.tick_params(axis='x',pad=9); ax.set_rlabel_position(20)
from matplotlib.lines import Line2D
ax.legend([Line2D([],[],color=c_,lw=1.6) for c_ in (ILC,CRC,INC)],list(S.keys()),loc='upper center',bbox_to_anchor=(0.5,-0.12),ncol=3,fontsize=6.3,frameon=False,handlelength=1.5,columnspacing=1)
ax.text(-0.22,1.14,'(b)',transform=ax.transAxes,fontweight='bold',fontsize=9)
if ax.name!='polar': ticks(ax,False)
# (c) cost vs reuse cycles
ax=fig.add_axes([0.09,0.3483,0.36,0.2408])
ns=[1,2,3,4,5,6,8,10,12,15,20,25,30,35,40]
q=np.array([pd.read_excel(f'{M}reuse/g_{n}.xlsx',sheet_name='cost').total_cost.quantile([.05,.5,.95]).values for n in ns])
ax.fill_between(ns,q[:,0],q[:,2],color=ILC,alpha=0.18,lw=0,label='5-95%'); ax.plot(ns,q[:,1],color=ILC,lw=1.6,label='median')
ax.axhline(q[4,1],color='0.4',ls=':',lw=0.9); ax.text(39,q[4,1]+3,'main analysis (5 cycles)',ha='right',fontsize=6.5,style='italic',color='0.35')
ax.text(1.6,q[0,1],f'{q[0,1]:.0f}',fontsize=7,color=ILC,va='center'); ax.text(40,q[-1,1]-9,f'{q[-1,1]:.0f}',fontsize=7,color=ILC,ha='right')
ax.set_xlim(1,40); ax.set_xlabel('Reuse cycles'); ax.set_ylabel('Cost (USD/kg composite)')
ax.legend(loc='upper right',fontsize=6.5,frameon=False); ax.text(-0.2,1.04,'(c)',transform=ax.transAxes,fontweight='bold',fontsize=9)
if ax.name!='polar': ticks(ax,True)
# (d) break-even with virgin PTFE footprint
ax=fig.add_axes([0.6,0.3483,0.36,0.2408])
gg=gross.GWP.values; INCG=np.median(inc.GWP); yld=0.92; GTFE=138.0
sp=np.linspace(0,1,101)
netq=np.array([np.percentile(gg-yld*s_*GTFE,[5,50,95]) for s_ in sp])
ax.axvspan(50,80,color='0.93',lw=0,zorder=0); ax.text(65,63,'assumed\nrange',ha='center',va='top',fontsize=6.3,color='0.35')
ax.fill_between(sp*100,netq[:,0],netq[:,2],color=CRC,alpha=0.2,lw=0,label='IL net, 5-95%')
ax.plot(sp*100,netq[:,1],color=CRC,lw=1.6,label='IL net, median')
ax.axhline(INCG,color=INC,lw=1.2,ls='--',label='incineration')
be=(np.median(gg)-INCG)/(yld*GTFE)*100
ax.plot([be],[INCG],'o',ms=4,mfc='white',mec=CRC,mew=1.2); ax.text(be-2,INCG+6,f'break-even ~{be:.0f}%',ha='right',fontsize=6.5,color=CRC)
ax.axhline(0,color='k',lw=0.5); ax.set_xlim(0,100); ax.set_ylim(-80,90)
ax.set_xlabel('Recovered PTFE displacing virgin PTFE (%)'); ax.set_ylabel('Net IL GWP (kg CO$_2$-eq/kg composite)')
ax.legend(loc='lower left',fontsize=6.3,frameon=False); ax.text(-0.2,1.04,'(d)',transform=ax.transAxes,fontweight='bold',fontsize=9)
if ax.name!='polar': ticks(ax,True)
from matplotlib.colors import LinearSegmentedColormap
SP=pd.read_excel(M+'P66614_Cl_ground.xlsx',sheet_name='sensitivity_PTFE',index_col=0).dropna(how='all')
cols=['cost','AP','GWP','EFW','EP','HTC','HTNC','ODP','PMFP','MIR']; SP=SP[cols]
keep=SP.abs().max(axis=1).sort_values(ascending=False); keep=keep[keep>0.05].index[:10]
names={'filtration_time':'Filtration time','vacuum_pump_power':'Vacuum pump power','grinding_power':'Grinding mill power',
 'HCL_cost':'HCl price','NaOH_cost':'NaOH price','acetone_cost':'Acetone price','acetone_recovery':'Acetone recovery',
 'acid_liquor_HCl_fraction':'Residual HCl in liquor','heating_efficiency':'Heating efficiency','NaOH_amount':'NaOH dose',
 'acetone_amount':'Acetone dose','P66614_Cl_amount':'[P$_{66614}$][Cl] dose','HCL_amount':'HCl dose','recovery_fraction':'IL recovery'}
mm=SP.loc[keep].fillna(0).values.T   # rows: outputs, cols: inputs
cmap=LinearSegmentedColormap.from_list('pg',['#3B1F5C','#9C88C2','#F2F2F2','#8FC98A','#1E5631'])
ax=fig.add_axes([0.16,0.07,0.70,0.21])
im=ax.imshow(mm,cmap=cmap,vmin=-1,vmax=1,aspect='auto')
for i_ in range(mm.shape[0]):
    for j_ in range(mm.shape[1]):
        if abs(mm[i_,j_])>=0.1: ax.text(j_,i_,f'{mm[i_,j_]:.2f}'.replace('0.','.'),ha='center',va='center',fontsize=5.5,color='white' if abs(mm[i_,j_])>0.6 else '0.1')
ax.set_yticks(range(len(cols))); ax.set_yticklabels(['Cost']+cols[1:],fontsize=6.5)
ax.set_xticks(range(len(keep))); ax.set_xticklabels([names.get(k,k) for k in keep],rotation=30,ha='right',fontsize=6.5)
ax.set_xticks(np.arange(-.5,len(keep)),minor=True); ax.set_yticks(np.arange(-.5,len(cols)),minor=True)
ax.grid(which='minor',color='white',lw=0.6); ax.tick_params(which='minor',length=0)
cb=fig.colorbar(im,ax=ax,fraction=0.03,pad=0.02); cb.set_label("Spearman's ρ",fontsize=7); cb.ax.tick_params(labelsize=6.5)
ax.text(-0.11,1.06,'(e)',transform=ax.transAxes,fontweight='bold',fontsize=9)
if ax.name!='polar': ticks(ax,False)
for ext in ('png','svg','pdf'): fig.savefig(f'./Figure6.{ext}',dpi=300,bbox_inches='tight')
print('break-even',be,'meds',{n:dict(zip(cats,np.round(v,6))) for n,v in med.items()})
