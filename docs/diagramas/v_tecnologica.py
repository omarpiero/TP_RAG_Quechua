from draw import *
import numpy as np
fig,axs=plt.subplots(2,3,figsize=(16,8),dpi=200)
fig.suptitle('Matrices de decisión ponderadas — puntaje total sobre 5 (Documentos 0, 4 y 5)',fontsize=14,fontweight='bold',color=AZ,y=0.985)
groups=[
 ('Estilo de arquitectura',[('Hexagonal',4.65),('Event-driven',3.10),('Microservicios',2.80)]),
 ('Enfoque de desarrollo',[('Ágil',4.60),('Híbrido',4.40),('Predictivo',2.50)]),
 ('Marco de trabajo',[('Scrum',4.65),('Scrumban',4.15),('Kanban',3.65),('XP',3.30)]),
 ('Generador de escritorio',[('Qwen3.5-4B',4.80),('Qwen3.5-9B',4.40),('Gemma 3 4B',4.25),('Llama 3.2 3B',4.25)]),
 ('Motor de inferencia (escritorio)',[('Ollama',4.80),('llama.cpp',4.65),('MediaPipe LLM',3.85),('ExecuTorch',3.40)]),
 ('Almacén vectorial (móvil)',[('sqlite-vec',4.70),('ChromaDB',4.15),('FAISS',3.85),('Qdrant',3.10)]),
]
for ax,(t,items) in zip(axs.flat,groups):
    names=[n for n,_ in items][::-1]; vals=[v for _,v in items][::-1]
    cols=['#C9D6E8']*(len(vals)-1)+['#1F3864']
    ax.barh(names,vals,color=cols,height=0.6)
    for i,v in enumerate(vals): ax.text(v+0.05,i,f'{v:.2f}'.replace('.',','),va='center',fontsize=10,fontweight='bold' if i==len(vals)-1 else 'normal')
    ax.set_xlim(0,5.6); ax.set_title(t,fontsize=11.5,fontweight='bold',color=AZ2)
    ax.tick_params(axis='y',labelsize=10); ax.tick_params(axis='x',labelsize=8)
    for s in ['top','right']: ax.spines[s].set_visible(False)
fig.text(0.5,0.015,'Criterios comunes: adecuación técnica, ajuste a recursos (8 GB VRAM), integración, costo y licencia, operación sin conexión, curva de aprendizaje, madurez. La opción elegida aparece en azul oscuro; llama.cpp (4,65) se adopta para el móvil y ChromaDB para escritorio en el diseño original.',ha='center',fontsize=9,style='italic',color='#444444')
fig.tight_layout(rect=[0,0.04,1,0.95])
fig.savefig('v_tecnologica.png',dpi=200);print('ok')
