from draw import *
import numpy as np
fig,ax=canvas(16,9)
ax.text(8,8.65,'Vista hexagonal — canales de entrada, puertos y adaptadores de salida del PMV1',fontsize=14,fontweight='bold',color=AZ,ha='center')
cx,cy=8,4.25
def hexa(r,fc,ec,lw=1.5,z=1):
    pts=[(cx+r*np.cos(np.radians(a)),cy+r*0.93*np.sin(np.radians(a))) for a in range(0,360,60)]
    ax.add_patch(Polygon(pts,closed=True,fc=fc,ec=ec,lw=lw,zorder=z))
hexa(4.45,'#FFF6E5','#B7882F')
hexa(3.45,'#EAF3FB','#2E5496')
hexa(1.45,'#E8F5E9','#2E7D32')
ax.text(cx,cy+0.62,'DOMINIO',fontsize=11,fontweight='bold',ha='center',color='#2E7D32')
ax.text(cx,cy-0.15,'EvaluadorConfianza (τ)\nVerificadorFormaLiteral\nDepuradorConsulta · Segmentador\nConsulta · Fragmento · Respuesta',fontsize=7.0,ha='center',va='center',linespacing=1.4)
ax.text(cx,cy+2.6,'APLICACIÓN',fontsize=11,fontweight='bold',ha='center',color=AZ2)
ax.text(cx,cy+2.2,'ConsultarCorpusUseCase · IngestarDocumentoUseCase · …   ·   RespuestaFactory',fontsize=7.8,ha='center')
ax.text(cx,cy+3.75,'ADAPTADORES',fontsize=11,fontweight='bold',ha='center',color='#8A5A00')
ax.text(cx,cy-3.85,'INFRAESTRUCTURA: contenedor.py inyecta cada adaptador en su puerto · config.py (τ = 0,41)',fontsize=8.2,ha='center',color='#8B2E2E')
# input ports on left boundary of application hex
ins=[('ConsultarCorpusPort',1.1),('IngestarDocumentoPort',0.35),('GestionarFuentesPort',-0.4),('ConsultarHistorialPort',-1.15)]
for name,dy in ins:
    x=cx-3.05; y=cy+dy
    ax.add_patch(plt.Circle((x,y),0.11,fc='white',ec=AZ2,lw=1.6,zorder=5))
    ax.text(x+0.2,y,name,fontsize=7.3,va='center',zorder=6)
outs=[('IndiceRecuperacionPort',1.3),('GeneradorTextoPort',0.65),('TraductorPort',0.0),('RepositorioConsultasPort',-0.65),('ExtraccionDocumentalPort',-1.3)]
for name,dy in outs:
    x=cx+3.05; y=cy+dy
    ax.add_patch(plt.Circle((x,y),0.11,fc='white',ec=AZ2,lw=1.6,zorder=5))
    ax.text(x-0.2,y,name,fontsize=7.3,va='center',ha='right',zorder=6)
# adapters in (on outer ring left)
ain=[('REST · FastAPI\n4 controladores',1.5),('CLI\nindexar · evaluar',0.1),('MCP (desarrollo)\nsolo lectura',-1.3)]
for t,dy in ain:
    box(ax,cx-4.75,cy+dy-0.35,1.45,0.7,t,fc='#FFFDF7',ec='#B7882F',fs=7.6,bold_first=True,z=6)
aout=[('IndiceHibridoLexico\nTF-IDF palabras+caracteres',1.5),('OllamaGenerador\nQwen3.5-4B',0.5),('TraductorSLM\nsolo la consulta',-0.5),('Repositorios\nsesión · manifiesto',-1.5)]
for t,dy in aout:
    box(ax,cx+3.25,cy+dy-0.33,1.55,0.66,t,fc='#FFFDF7',ec='#B7882F',fs=7.2,bold_first=True,z=6)
# external actors
box(ax,0.3,cy+1.0,2.1,0.9,'Usuario\nnavegador · Streamlit',fc='#F2F2F2',fs=8.5,bold_first=True)
box(ax,0.3,cy-0.45,2.1,0.75,'Terminal\nequipo de proyecto',fc='#F2F2F2',fs=8.5,bold_first=True)
box(ax,0.3,cy-1.75,2.1,0.75,'Agente de código\n(Claude Code)',fc='#F2F2F2',fs=8.5,bold_first=True)
arrow(ax,(2.4,cy+1.45),(cx-4.75,cy+1.5),'HTTP',fs=7.5)
arrow(ax,(2.4,cy-0.07),(cx-4.75,cy+0.1))
arrow(ax,(2.4,cy-1.37),(cx-4.75,cy-1.3),'stdio',fs=7.5)
ext=[('Índice en memoria\nfragmentos.jsonl',cy+1.5),('Ollama · Qwen3.5-4B\nGPU o CPU local',cy+0.5),('Ollama · Qwen3.5-4B\ntraducción EN→ES',cy-0.5),('Memoria de sesión\nMANIFIESTO.yaml',cy-1.5)]
for t,y in ext:
    box(ax,13.6,y-0.36,2.1,0.72,t,fc='#F2F2F2',fs=7.9,bold_first=True)
    arrow(ax,(cx+4.8,y),(13.6,y))
ax.text(1.25,cy+2.55,'Canales (lado conductor)',fontsize=9.5,fontweight='bold',ha='center',color='#444444')
ax.text(14.6,cy+2.55,'Sistemas externos\n(lado conducido)',fontsize=9.5,fontweight='bold',ha='center',color='#444444')
ax.text(2.1,0.35,'○ puerto (interfaz)   ▭ adaptador (implementación)\nCada canal tiene su adaptador de entrada y\ninvoca un puerto de entrada, nunca el caso de uso concreto.',fontsize=7.8,ha='center',va='center',color='#333333',linespacing=1.45)
fig.savefig('v_hexagono.png',dpi=200); print('ok')
