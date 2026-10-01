import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon, FancyArrowPatch
plt.rcParams['font.family']='DejaVu Sans'
AZ='#1F3864'; AZ2='#2E5496'
def canvas(w,h):
    fig=plt.figure(figsize=(w,h),dpi=200); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,w); ax.set_ylim(0,h); ax.axis('off'); return fig,ax
def pkg(ax,x,y,w,h,title,fc,ec='#444444',fs=11,tabw=None):
    tabw=tabw or min(w*0.6, 0.12*len(title)+0.4)
    ax.add_patch(Rectangle((x,y+h),tabw,0.28,fc=fc,ec=ec,lw=1.2,zorder=1))
    ax.text(x+0.1,y+h+0.14,title,fontsize=fs,fontweight='bold',va='center',zorder=3)
    ax.add_patch(Rectangle((x,y),w,h,fc=fc,ec=ec,lw=1.2,zorder=1))
def box(ax,x,y,w,h,text,fc='white',ec='#777777',fs=9,bold_first=False,align='center',lw=1,z=2,round_=True):
    if round_: ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=0.08',fc=fc,ec=ec,lw=lw,zorder=z))
    else: ax.add_patch(Rectangle((x,y),w,h,fc=fc,ec=ec,lw=lw,zorder=z))
    lines=text.split('\n')
    if bold_first:
        n=len(lines); lh=fs/72*1.35
        y0=y+h/2+(n-1)*lh/2
        for i,l in enumerate(lines):
            xx=x+w/2 if align=='center' else x+0.12
            ax.text(xx,y0-i*lh,l,fontsize=fs,ha=align if align!='left' else 'left',va='center',fontweight='bold' if i==0 else 'normal',zorder=z+1)
    else:
        xx=x+w/2 if align=='center' else x+0.12
        ax.text(xx,y+h/2,text,fontsize=fs,ha='center' if align=='center' else 'left',va='center',zorder=z+1,linespacing=1.35)
def arrow(ax,p1,p2,label=None,dashed=False,head='-|>',color='#333333',lw=1.3,rad=0,fs=8.5,loff=(0,0.12),z=4,hollow=False):
    st='Simple,head_length=8,head_width=6'
    a=FancyArrowPatch(p1,p2,arrowstyle=head if not hollow else '-|>',mutation_scale=14,color=color,lw=lw,
        linestyle=(0,(5,3)) if dashed else '-',connectionstyle=f'arc3,rad={rad}',zorder=z)
    if hollow: a.set_facecolor('white')
    ax.add_patch(a)
    if label:
        mx=(p1[0]+p2[0])/2+loff[0]; my=(p1[1]+p2[1])/2+loff[1]
        ax.text(mx,my,label,fontsize=fs,ha='center',va='center',style='italic',color='#222222',
                bbox=dict(fc='white',ec='none',pad=1),zorder=z+1)
