from draw import *
fig,ax=canvas(16,9)
ax.text(8,8.7,'Matriz integradora de trazabilidad C1 → C6',fontsize=15,fontweight='bold',color=AZ,ha='center')
ax.text(8,8.32,'Cada competencia recibe la salida de la anterior y entrega un artefacto verificable a la siguiente',fontsize=10,ha='center',color='#444444',style='italic')
cards=[
 ('C1 · Análisis del problema','AG-T08 / AG-C08','#1F3864',
  'Material publicado no consultable;\nwanka «seriamente en peligro»',
  'BPMN AS-IS (F1–F6) · SIPOC\nIshikawa · árbol · 5 Porqués\nKPIs · matriz de restricciones',
  'Problema cuantificado y acotado'),
 ('C2 · Conocimientos de ingeniería','AG-I07','#2E5496',
  'Problema y restricciones de C1',
  'RF/RNF (IA: RF-05, 06, 08, 14–16)\nUmbral τ, recall, F1 (no accuracy)\nMatrices tecnológicas ponderadas',
  'Requisitos y tecnologías justificadas'),
 ('C3 · Ingeniero y sociedad','AG-I01 / AG-I02','#5B6F2A',
  'Requisitos y dominio de C2',
  'Stakeholders I-01…I-09 · LPDP\nMatriz ética de la IA · CARE\nImpactos y riesgo residual',
  'Salvaguarda de abstención como\nrequisito ético'),
 ('C4 · Gestión del proyecto','PMBOK 7 + Scrum','#8A5A00',
  'Alcance técnico y restricciones éticas',
  'Tailoring Scrum · 4 sprints\nE-01…E-11 · HU con Given/When/Then\nRoadmap 3 PMV · DoD-1…DoD-10',
  'Plan incremental priorizado'),
 ('C5 · Herramientas modernas','AG-I11','#6A3D8F',
  'Plan de C4',
  'Ecosistema en 7 categorías\nGit/GitHub · pytest · SonarQube\nMatriz de limitaciones',
  'Entorno técnico configurado\ny medido'),
 ('C6 · PoC + arquitectura','multiatributo','#8B2E2E',
  'IA de C2 + historias de C4\n+ herramientas de C5',
  'PoC: 0 FP con τ · Go con condiciones\nHexagonal 4 capas · 5 patrones\nPMV1 ejecutable + video',
  'PMV1 en GitHub con evidencias'),
]
W,H=4.6,3.55
pos=[(0.45,4.2),(5.7,4.2),(10.95,4.2),(0.45,0.25),(5.7,0.25),(10.95,0.25)]
for (t,sub,col,ent,art,sal),(x,y) in zip(cards,pos):
    ax.add_patch(FancyBboxPatch((x,y),W,H,boxstyle='round,pad=0,rounding_size=0.12',fc='white',ec=col,lw=2,zorder=2))
    ax.add_patch(FancyBboxPatch((x,y+H-0.62),W,0.62,boxstyle='round,pad=0,rounding_size=0.12',fc=col,ec=col,lw=2,zorder=3))
    ax.text(x+0.18,y+H-0.31,t,fontsize=12,fontweight='bold',color='white',va='center',zorder=4)
    ax.text(x+W-0.15,y+H-0.31,sub,fontsize=9,color='white',va='center',ha='right',zorder=4)
    rows=[('Entrada',ent,y+H-1.05),('Artefactos',art,y+H-2.0),('Salida',sal,y+0.42)]
    for lab,txt,yy in rows:
        ax.text(x+0.18,yy,lab,fontsize=9.8,fontweight='bold',color=col,va='center',zorder=4)
        ax.text(x+1.35,yy,txt,fontsize=9.8,va='center',zorder=4,linespacing=1.35)
    ax.plot([x+0.15,x+W-0.15],[y+0.78,y+0.78],color='#DDDDDD',lw=1,zorder=3)
for a,b in [(0,1),(1,2),(3,4),(4,5)]:
    x1=pos[a][0]+W; x2=pos[b][0]; yy=pos[a][1]+H/2
    arrow(ax,(x1+0.05,yy),(x2-0.05,yy),lw=2.2)
arrow(ax,(13.25,4.18),(2.75,3.82),rad=0.0,lw=2.2,color='#555555')
fig.savefig('v_integradora.png',dpi=200);print('ok')
