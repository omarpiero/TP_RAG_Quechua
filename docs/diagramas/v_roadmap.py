from draw import *
import datetime as dt, matplotlib.dates as md
D=lambda s: md.date2num(dt.date.fromisoformat(s))
fig,ax=plt.subplots(figsize=(16,7.2),dpi=200)
rows=[
 ('PMV1 · Sprint 1 — ingesta, índice, arnés','2026-09-08','2026-09-28','2026-09-08','2026-10-02','#2E5496','Meta: 100 % en la exposición'),
 ('PMV1 · Sprint 2 — recuperación, τ, generación, UI','2026-09-29','2026-10-19','2026-09-08','2026-10-02','#2E5496','Adelantado e integrado al Sprint 1'),
 ('PMV2 · Sprint 3 — analítica predictiva y artefactos','2026-10-20','2026-11-09',None,None,'#B7882F','Pendiente'),
 ('PMV3 · Sprint 4 — app móvil sin conexión','2026-11-10','2026-11-30',None,None,'#5B8C3A','Pendiente'),
 ('Transversal — procedencia y licencias del corpus','2026-09-08','2026-11-30',None,None,'#999999','En curso'),
 ('Transversal — documentación y sustentación','2026-09-08','2026-11-30',None,None,'#999999','En curso'),
]
n=len(rows)
for i,(lab,p0,p1,r0,r1,col,est) in enumerate(rows):
    y=n-1-i
    ax.barh(y+0.18,D(p1)-D(p0)+1,left=D(p0),height=0.28,color='white',edgecolor=col,hatch='///',lw=1.2)
    if r0: ax.barh(y-0.16,D(r1)-D(r0)+1,left=D(r0),height=0.34,color=col)
    elif 'Transversal' in lab: ax.barh(y-0.16,D('2026-09-24')-D(p0)+1,left=D(p0),height=0.34,color=col)
    ax.text(D('2026-12-02'),y,est,va='center',fontsize=9.5,fontweight='bold',color=col)
for d,t in [('2026-10-02','Exposición U-II\nPMV1 (sem. 28-09)'),('2026-10-19','Hito 1 previsto\n(Doc. 4)'),('2026-11-09','Hito 2'),('2026-11-30','Hito 3')]:
    ax.axvline(D(d),color='#8B2E2E' if 'U-II' in t else '#777777',ls='--',lw=1.2)
    ax.text(D(d),n-0.35,t,ha='center',va='bottom',fontsize=8.5,color='#8B2E2E' if 'U-II' in t else '#555555')
ax.axvline(D('2026-09-24'),color='#2E7D32',lw=1.5); ax.text(D('2026-09-24'),-0.9,'hoy\n24-09',ha='center',fontsize=8,color='#2E7D32')
ax.axvspan(D('2026-10-05'),D('2026-10-19'),color='#FFF6E5',zorder=0)
ax.text(D('2026-10-12'),-0.75,'ventana liberada:\ninicio anticipado del PMV2\n(decisión del equipo)',ha='center',fontsize=7.8,color='#8A5A00')
ax.set_yticks(range(n)); ax.set_yticklabels([r[0] for r in rows][::-1],fontsize=9.5)
ax.xaxis.set_major_locator(md.WeekdayLocator(byweekday=0)); ax.xaxis.set_major_formatter(md.DateFormatter('%d-%m'))
ax.set_xlim(D('2026-09-06'),D('2026-12-20')); ax.set_ylim(-1.2,n+0.2)
ax.tick_params(axis='x',labelsize=8)
for s in ['top','right']: ax.spines[s].set_visible(False)
ax.grid(axis='x',color='#EEEEEE')
from matplotlib.patches import Patch
ax.legend(handles=[Patch(fc='white',ec='#555555',hatch='///',label='Línea base (Documento 4)'),Patch(fc='#2E5496',label='Real / reprogramado')],loc='upper right',bbox_to_anchor=(1.0,-0.07),ncol=2,frameon=False,fontsize=9)
ax.set_title('Roadmap de los tres PMV — línea base frente a estado actual (base para GitHub Projects)',fontsize=13.5,fontweight='bold',color=AZ,pad=34)
fig.tight_layout(); fig.savefig('v_roadmap.png',dpi=200);print('ok')
