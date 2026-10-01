from draw import *
fig,ax=canvas(16,7.6)
ax.text(8,7.3,'Indicadores cuantitativos del problema (valores verificados en fuente citable)',fontsize=14,fontweight='bold',color=AZ,ha='center')
cards=[
 ('Seriamente\nen peligro','Estado de vitalidad del\nquechua wanka','MINCUL, BDPI','#8B2E2E'),
 ('0 de 3','variedades de quechua de la\nLínea 1812 son la wanka','MINCUL, mayo 2026','#8B2E2E'),
 ('1962','año de la última cifra de\nhablantes del shawsha wanka\n(64 años de antigüedad)','Ethnologue / SIL','#8A5A00'),
 ('8 PDF · 679 pp.','del corpus sin índice ni\nbuscador común','Corpus de la PoC (Doc. 6)','#2E5496'),
 ('11,6 %','de las páginas sin capa\nde texto (79 de 679):\ninvisibles al Ctrl+F','Medido en la PoC','#2E5496'),
 ('0 de 50','estudios de IA en quechua\ny aimara con RAG\nconsolidado','Puraca Ytusaca, 2026','#5B6F2A'),
 ('1 de 47','estudios de RAG en educación\ncon dominio «lengua»','Swacha y Gracel, 2025','#5B6F2A'),
 ('Por medir','tiempo de una consulta manual\n(AS-IS) frente a la del sistema','Medición propuesta con\ndocentes de EIB (HT-02)','#777777'),
]
W,H=3.6,2.9
for i,(big,txt,src,col) in enumerate(cards):
    r,c=divmod(i,4); x=0.4+c*3.85; y=3.75-r*3.35
    ax.add_patch(FancyBboxPatch((x,y),W,H,boxstyle='round,pad=0,rounding_size=0.12',fc='white',ec=col,lw=2))
    ax.add_patch(Rectangle((x,y+H-0.12),W,0.12,fc=col,ec=col))
    ax.text(x+W/2,y+H-0.8,big,fontsize=19 if len(big)<12 else 15,fontweight='bold',color=col,ha='center',va='center',linespacing=1.0)
    ax.text(x+W/2,y+1.05,txt,fontsize=9.8,ha='center',va='center',linespacing=1.3)
    ax.text(x+W/2,y+0.22,src,fontsize=7.8,ha='center',va='center',style='italic',color='#555555')
fig.savefig('v_kpis.png',dpi=200);print('ok')
