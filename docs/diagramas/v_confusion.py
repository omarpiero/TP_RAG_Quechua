from draw import *
import numpy as np
fig=plt.figure(figsize=(16,6.4),dpi=200)
fig.suptitle('Por qué el umbral no se elige por accuracy: dos políticas sobre las mismas 208 consultas (A+B con respaldo, C sin respaldo)',fontsize=12.5,fontweight='bold',color=AZ,y=0.97)
def cm(ax,vals,title,sub):
    col=np.array([['#D9EAD3','#FCE5CD'],['#F4CCCC','#D9EAD3']])
    lab=[['VP','FN'],['FP','VN']]; desc=[['responde con\nrespaldo','se abstiene\naunque hay respaldo'],['responde SIN\nrespaldo = alucinación','se abstiene\ncorrectamente']]
    for i in range(2):
        for j in range(2):
            ax.add_patch(Rectangle((j,1-i),1,1,fc=col[i][j],ec='#666666',lw=1.2))
            ax.text(j+0.5,1-i+0.62,f'{lab[i][j]} = {vals[i][j]}',ha='center',va='center',fontsize=15,fontweight='bold',color='#8B2E2E' if (i,j)==(1,0) and vals[1][0]>0 else '#222222')
            ax.text(j+0.5,1-i+0.3,desc[i][j],ha='center',va='center',fontsize=8.5)
    ax.set_xlim(-0.45,2); ax.set_ylim(-0.05,2.25); ax.axis('off')
    ax.text(0.5,2.08,'Responde',ha='center',fontsize=9.5,fontweight='bold'); ax.text(1.5,2.08,'Se abstiene',ha='center',fontsize=9.5,fontweight='bold')
    ax.text(-0.08,1.5,'Hay\nrespaldo\n(180)',ha='right',va='center',fontsize=9,fontweight='bold'); ax.text(-0.08,0.5,'Sin\nrespaldo\n(28)',ha='right',va='center',fontsize=9,fontweight='bold')
    ax.set_title(title+'\n'+sub,fontsize=10.5,fontweight='bold',pad=4)
a1=fig.add_axes([0.03,0.08,0.27,0.76]); cm(a1,[[180,0],[28,0]],'Política trivial: responder siempre','(referencia teórica)')
a2=fig.add_axes([0.33,0.08,0.27,0.76]); cm(a2,[[154,26],[0,28]],'Sistema con τ = 0,41','(medido en la prueba de concepto, Documento 6)')
a3=fig.add_axes([0.70,0.17,0.28,0.63])
mets=['Accuracy','Precisión','Recall','F1','Especificidad\n(abstención en C)']
triv=[180/208,180/208,1.0,2*(180/208)/(1+180/208),0.0]
sys=[(154+28)/208,1.0,154/180,2*1.0*(154/180)/(1+154/180),1.0]
y=np.arange(len(mets))[::-1]
a3.barh(y+0.2,triv,0.38,color='#E6B8B7',label='Responder siempre')
a3.barh(y-0.2,sys,0.38,color='#2E5496',label='τ = 0,41')
for yy,v in zip(y+0.2,triv): a3.text(v+0.01,yy,f'{v:.3f}'.replace('.',','),va='center',fontsize=8.5)
for yy,v in zip(y-0.2,sys): a3.text(v+0.01,yy,f'{v:.3f}'.replace('.',','),va='center',fontsize=8.5,color=AZ2,fontweight='bold')
a3.set_yticks(y); a3.set_yticklabels(mets,fontsize=9.5); a3.set_xlim(0,1.18); a3.legend(loc='upper center',bbox_to_anchor=(0.5,-0.08),ncol=2,fontsize=9,frameon=False)
for s in ['top','right']: a3.spines[s].set_visible(False)
a3.set_title('La política trivial obtiene 0,865 de accuracy y 0,928 de F1\ncon 28 alucinaciones: el criterio es FP = 0 en C',fontsize=9.8,fontweight='bold',color='#8B2E2E')
fig.savefig('v_confusion.png',dpi=200);print('ok')
