from draw import *
fig,ax=canvas(16,8.4)
ax.text(8,8.1,'Ecosistema de herramientas en siete categorías y su incorporación por PMV',fontsize=14,fontweight='bold',color=AZ,ha='center')
cats=[
 ('1 · Ingeniería y modelado','#1F3864',[('PlantUML · Graphviz','PMV1'),('Matplotlib (figuras)','PMV1'),('BPMN 2.0 (notación)','PMV1')]),
 ('2 · Desarrollo y DevOps','#2E5496',[('Python 3.12 · VS Code','PMV1'),('FastAPI · Streamlit','PMV1'),('Git · GitHub · Actions','PMV1'),('Claude Code (agentes)','PMV1'),('Flutter','PMV3')]),
 ('3 · Datos, IA y predicción','#5B6F2A',[('Ollama · Qwen3.5-4B','PMV1'),('scikit-learn (TF-IDF)','PMV1'),('Google Colab (PoC)','PoC'),('pandas · scikit-learn (RF-14–16)','PMV2'),('llama.cpp · Qwen3.5-0.8B','PMV3')]),
 ('4 · Gestión del proyecto','#8A5A00',[('GitHub Projects','PMV1'),('Markdown SDD (docs/)','PMV1')]),
 ('5 · Calidad de software','#6A3D8F',[('pytest · pytest-cov','PMV1'),('pytest-bdd (Gherkin)','PMV1'),('SonarQube Cloud / local','PMV1'),('Postman · Newman','PMV1'),('ruff · pip-audit','PMV1')]),
 ('6 · Rendimiento y seguridad','#8B2E2E',[('Medición propia de latencia','PMV1'),('k6 / OWASP ZAP','no aplica*')]),
 ('7 · Datos del corpus','#555555',[('pypdf','PMV1'),('Tesseract (medición)','PoC'),('Manifiesto YAML · JSONL','PMV1'),('sqlite-vec · ONNX','PMV2')]),
]
colsx=[0.3,4.2,8.1,12.0]; W=3.7
pcol={'PMV1':'#2E5496','PMV2':'#B7882F','PMV3':'#5B8C3A','PoC':'#777777','no aplica*':'#8B2E2E'}
pos=[(0,7.6),(1,7.6),(2,7.6),(3,7.6),(0,3.9),(1,3.9),(2,3.9)]
for (t,col,items),(ci,ytop) in zip(cats,pos):
    x=colsx[ci]; h=0.55+len(items)*0.55
    ax.add_patch(FancyBboxPatch((x,ytop-h),W,h,boxstyle='round,pad=0,rounding_size=0.1',fc='white',ec=col,lw=1.8))
    ax.add_patch(FancyBboxPatch((x,ytop-0.5),W,0.5,boxstyle='round,pad=0,rounding_size=0.1',fc=col,ec=col))
    ax.text(x+0.15,ytop-0.25,t,fontsize=10.5,fontweight='bold',color='white',va='center')
    for k,(tool,p) in enumerate(items):
        yy=ytop-0.82-k*0.55
        ax.text(x+0.18,yy,tool,fontsize=9.5,va='center')
        ax.text(x+W-0.15,yy,p,fontsize=8.3,va='center',ha='right',fontweight='bold',color='white',bbox=dict(boxstyle='round,pad=0.25',fc=pcol[p],ec='none'))
ax.text(12.0,3.5,'* k6 y OWASP ZAP se orientan a servicios\nconcurrentes expuestos en red; el sistema es\nde uso individual y escucha solo en 127.0.0.1.\nSe declara como limitación (C5), no se oculta.',fontsize=8.8,va='top',color='#8B2E2E',style='italic',linespacing=1.4)
ax.text(12.0,1.55,'Cambio respecto del Documento 5: el análisis\nestático se excluyó por proporción; se\nincorpora SonarQube porque la evaluación\nlo exige y el código ya es mayor (CHG-05).',fontsize=8.8,va='top',color='#333333',linespacing=1.4)
fig.savefig('v_ecosistema.png',dpi=200);print('ok')
