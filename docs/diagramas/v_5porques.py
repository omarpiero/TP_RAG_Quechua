from draw import *
fig,ax=canvas(16,8.6)
ax.text(8,8.3,'Análisis de los 5 Porqués — de la falla observada a la causa raíz',fontsize=14,fontweight='bold',color=AZ,ha='center')
steps=[
 ('Falla observada','Un docente de EIB no obtiene una forma wanka con su documento y página de origen, aunque el material ya fue publicado.','#8B2E2E'),
 ('¿Por qué? 1','La búsqueda es literal (Ctrl+F) y documento por documento; la variación ortográfica hace fallar la coincidencia exacta (F2, F4).','#A0522D'),
 ('¿Por qué? 2','El material oficial se publica como PDF individuales, sin índice unificado ni buscador común; parte está escaneado sin capa de texto (F1, F3).','#8A5A00'),
 ('¿Por qué? 3','No existe un corpus digital procesable de la variedad wanka ni herramientas de PLN construidas para ella.','#5B6F2A'),
 ('¿Por qué? 4','La infraestructura de PLN del quechua se concentra en las variedades sureñas: 0 de 50 estudios revisados reportan la recuperación aumentada como categoría consolidada [Puraca, 2026].','#2E5496'),
 ('¿Por qué? 5 · causa raíz','Variedad de bajos recursos y baja prioridad institucional: «seriamente en peligro», fuera de la Línea 1812 y con cifras de hablantes de 2002 y 1962.','#1F3864'),
]
x0=0.4; y=7.55; w=9.5; h=0.95
for i,(lab,txt,col) in enumerate(steps):
    xx=x0+i*0.42
    ax.add_patch(FancyBboxPatch((xx,y-h),2.3,h,boxstyle='round,pad=0,rounding_size=0.08',fc=col,ec=col,zorder=2))
    ax.text(xx+1.15,y-h/2,lab,fontsize=9.6,fontweight='bold',color='white',ha='center',va='center',zorder=3)
    ax.add_patch(FancyBboxPatch((xx+2.3,y-h),w-2.3,h,boxstyle='round,pad=0,rounding_size=0.08',fc='white',ec=col,lw=1.5,zorder=2))
    import textwrap
    ax.text(xx+2.45,y-h/2,'\n'.join(textwrap.wrap(txt,92)),fontsize=9.4,va='center',zorder=3,linespacing=1.35)
    if i<len(steps)-1: arrow(ax,(xx+1.15,y-h-0.02),(xx+1.15+0.42,y-h-0.28),lw=1.6)
    y-=1.18
# intervention
ax.add_patch(FancyBboxPatch((12.5,0.55),3.3,6.6,boxstyle='round,pad=0,rounding_size=0.12',fc='#E8F5E9',ec='#2E7D32',lw=2,zorder=2))
ax.text(14.15,6.6,'Intervención que se\nderiva del análisis',fontsize=11,fontweight='bold',color='#2E7D32',ha='center',va='center')
ax.text(14.15,3.6,'Indexar lo ya publicado\ny recuperarlo por\nsimilitud, no por\ncoincidencia exacta.\n\nMostrar la forma\nliteral con documento\ny página.\n\nAbstenerse cuando el\ncorpus no la respalda.\n\nRAG, no ajuste fino:\nno hay corpus para\nentrenar.',fontsize=10.2,ha='center',va='center',linespacing=1.35)
arrow(ax,(12.05,1.15),(12.48,1.15),lw=2.2,color='#2E7D32')
fig.savefig('v_5porques.png',dpi=200);print('ok')
