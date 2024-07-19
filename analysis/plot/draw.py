import networkx as nx 
from networkx.drawing.nx_agraph import graphviz_layout

from .args import pargs

def draw_subtitle(text:str, ax, pad:int=0):
    ax.set_title(f"{text}", 
                 fontsize=pargs.tfont - 2, 
                 fontweight='bold', 
                 pad=pad)

def draw_graph(G, ax, cmap=None, emap=None):
    G.graph['rankdir'] = "TB"
    G.graph['ranksep'] = "0.03"

    A = nx.nx_agraph.to_agraph(G)
    A.layout(prog='dot')
    A.write(f"analysis/graphs/{G.name}.dot")

    pos = graphviz_layout(G, prog='dot')
    nx.draw(G, 
            pos, 
            node_color=cmap, 
            edge_color=emap,
            node_size=pargs.size, 
            with_labels=True, 
            ax=ax, 
            font_size=pargs.nfont)

    # plt.tight_layout()
    return pos
