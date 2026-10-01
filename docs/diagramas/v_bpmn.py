from draw import *
fig,ax=canvas(17,8.2)
ax.text(8.5,7.95,'Proceso AS-IS de consulta de material en quechua wanka — notación BPMN 2.0',fontsize=14,fontweight='bold',color=AZ,ha='center')
# pool
X0,X1=0.3,16.8
lanes=[('Docente EIB /\nestudiante /\ninvestigador',4.5,7.45,'#F4F9FE'),('Repositorios\nde material\n(MINEDU, BQW, web)',2.6,4.5,'#FFFBF2'),('Fuentes no\nespecíficas\n(traductor, hablante)',0.3,2.6,'#FDF3F2')]
ax.add_patch(Rectangle((X0,0.3),0.55,7.15,fc='#DCE6F1',ec='#444444',lw=1.4))
ax.text(X0+0.27,3.87,'Consulta de un término o contenido en quechua wanka',rotation=90,ha='center',va='center',fontsize=9,fontweight='bold')
for name,y0,y1,fc in lanes:
    ax.add_patch(Rectangle((X0+0.55,y0),1.35,y1-y0,fc='#EEF2F7',ec='#444444',lw=1.1))
    ax.text(X0+1.22,(y0+y1)/2,name,rotation=90,ha='center',va='center',fontsize=8.2,linespacing=1.2)
    ax.add_patch(Rectangle((X0+1.9,y0),X1-X0-1.9,y1-y0,fc=fc,ec='#444444',lw=1.1))
def task(x,y,t,w=1.75,h=0.8):
    box(ax,x-w/2,y-h/2,w,h,t,fc='white',ec='#2E5496',fs=7.6,lw=1.3,z=5); return (x,y,w,h)
def gw(x,y,label,s=0.36,above=False):
    ax.add_patch(Polygon([(x,y+s),(x+s,y),(x,y-s),(x-s,y)],fc='#FFF6E5',ec='#8A5A00',lw=1.4,zorder=5))
    ax.text(x,y,'×',fontsize=12,ha='center',va='center',zorder=6,color='#8A5A00')
    if above: ax.text(x,y+s+0.12,label,fontsize=7.4,ha='center',va='bottom',zorder=6)
    else: ax.text(x+s*0.5+0.05,y-s-0.08,label,fontsize=7.4,ha='left',va='top',zorder=6)
def ev(x,y,end=False,label=None):
    ax.add_patch(plt.Circle((x,y),0.24,fc='#E8F5E9' if not end else '#FDECEA',ec='#2E7D32' if not end else '#8B2E2E',lw=1.4 if not end else 3,zorder=5))
    if label: ax.text(x,y-0.36,label,fontsize=7.2,ha='center',va='top',zorder=6)
def flow(p,q,lab=None,rad=0,loff=(0,0.12)):
    arrow(ax,p,q,lab,lw=1.1,fs=7.2,rad=rad,loff=loff,z=4)
def fail(x,y,t):
    ax.text(x,y,t,fontsize=7.3,color='#8B2E2E',fontweight='bold',ha='center',va='center',zorder=7,
            bbox=dict(boxstyle='round,pad=0.25',fc='#FDECEA',ec='#8B2E2E',lw=1))
yA=6.1; yB=3.55; yC=1.45
ev(2.75,yA,label='Necesidad\nde consulta')
task(4.3,yA,'Buscar material\nen fuentes\nconocidas')
task(4.3,yB,'Descargar PDF\nsin catálogo ni\nbuscador común')
fail(4.3,2.85,'F1 dispersión documental')
task(6.35,yA,'Abrir los\ndocumentos\nuno por uno')
gw(8.05,yA,'¿Tiene capa\nde texto?')
task(9.75,6.75,'Búsqueda literal\n(Ctrl+F) con la\nforma supuesta',h=0.78)
fail(9.75,7.33,'F2 literal · F4 ortografía')
task(9.75,5.25,'Revisar página\npor página',h=0.7)
fail(9.75,4.72,'F3 escaneado sin texto')
gw(11.55,yA,'¿Encuentra\nel dato?')
task(13.3,yA,'Copiar el dato\nsin documento\nni página')
fail(13.3,6.85,'F5 sin trazabilidad')
ev(15.3,yA,end=True,label='Dato sin\nfuente')
task(11.55,yC,'Recurrir a traductor\ngenérico o a un\nhablante disponible',w=1.95)
gw(13.3,yC,'¿Obtiene\nrespuesta?',above=True)
task(15.0,yC+0.05,'Adoptar forma de\nvariedad sureña',w=1.6,h=0.7)
fail(15.0,0.62,'F6 homogeneización')
ev(16.35,2.35,end=True,label='')
ax.text(16.35,2.72,'Forma no\nwanka',fontsize=7,ha='center',va='bottom')
ev(13.3,0.62,end=True)
ax.text(12.9,0.62,'Consulta\nabandonada',fontsize=7,ha='right',va='center')
flow((2.99,yA),(3.42,yA)); flow((4.3,yA-0.4),(4.3,yB+0.4)); flow((5.17,yB+0.1),(6.35,yA-0.4),rad=0.25)
flow((7.22,yA),(7.69,yA)); flow((8.05,yA+0.36),(8.87,6.75),'sí',rad=-0.25,loff=(0.05,0.25))
flow((8.05,yA-0.36),(8.87,5.25),'no',rad=0.25,loff=(0.05,-0.28))
flow((10.62,6.75),(11.55,yA+0.36),rad=-0.25); flow((10.62,5.25),(11.55,yA-0.36),rad=0.25)
flow((11.91,yA),(12.42,yA),'sí',loff=(0,0.14)); flow((14.17,yA),(15.06,yA))
flow((11.55,yA-0.36),(11.55,yC+0.4),'no',loff=(-0.18,0.3))
flow((12.52,yC),(12.94,yC)); flow((13.66,yC),(14.2,yC+0.05),'sí',loff=(0,0.14))
flow((15.8,yC+0.2),(16.2,2.2),rad=0.2); flow((13.3,yC-0.36),(13.3,0.86),'no',loff=(0.18,0))
fig.savefig('v_bpmn.png',dpi=200);print('ok')
