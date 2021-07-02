'''
--------------------------------------------------------------------------------
Description:

Roadmap:

Written by W.R. Jackson <wrjackso@bu.edu>, DAMP Lab 2020
--------------------------------------------------------------------------------
'''
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns


def plot_graph(
        input_graph: nx.DiGraph,
        save_file: bool = False,
        output_filename: str = f"test.jpg",
        filtered_graph: nx.Graph = None,
):
    """

    Args:
        graph_type:
        save_file:
        output_filename:
        filtered_graph:

    Returns:

    """
    graph = filtered_graph if filtered_graph is not None else input_graph
    # pos = nx.bipartite_layout(graph, graph.nodes, align='horizontal')
    # pos = nx.spring_layout(graph)
    nx.draw(
        graph,
        arrowsize=20,
        verticalalignment='bottom',
        # node_color=node_colors,
    )
    if not save_file:
        plt.show()
    else:
        plt.savefig(output_filename)


def plot_cell_edgelist(
        input_edgelist_fp: str,
        save_file: bool = False,
        output_filename: str = 'test.jpg',
):
    original_network = False
    g = nx.read_edgelist(input_edgelist_fp)
    plt.figure(num=None, figsize=(15, 15), dpi=80)
    img_path = "nor_gate.png"
    img_list = []
    nor_img = mpimg.imread(img_path)
    for _ in g.nodes():
        img_list.append(nor_img)
    positions = nx.nx_agraph.graphviz_layout(g, prog='dot')
    # Calculate the number of ranks in here so you can figure out how many
    # colors you need...
    y_pos = sorted(list({position[1] for position in positions.values()}))
    sns.color_palette('Set2', len(y_pos))
    colors = [y_pos.index(position[1]) for position in positions.values()]
    plt.title('MD5 Hash Boolean Logic Network', fontsize=30, ha='center')
    if original_network:
        nx.draw(
            g,
            pos=positions,
            node_color=colors,
            with_labels=True,
            horizontalalignment='left',
            verticalalignment='bottom',
            alpha=0.6,
        )
        plt.draw()
        plt.savefig('original_network.jpg')
        return
    # I'm going to rotate the graph so it makes more sense in terms of an
    # electrical circuit.
    flip_xy_pos = {}
    flipped_pos = {node: (-y, x) for (node, (x, y)) in positions.items()}
    nx.draw_networkx_edges(g, pos=flipped_pos, alpha=0.7)
    nx.draw(
        g,
        pos=flipped_pos,
        node_color=colors,
        with_labels=False,
        horizontalalignment='left',
        verticalalignment='bottom',
        alpha=0.5,
    )
    # plt.imshow(nor_img)
    ax = plt.gca()
    fig = plt.gcf()
    trans = ax.transData.transform
    trans2 = fig.transFigure.inverted().transform
    imsize = 0.05  # this is the image size
    for index, n in enumerate(g.nodes()):
        (x, y) = flipped_pos[n]
        xx, yy = trans((x, y))  # figure coordinates
        xa, ya = trans2((xx, yy))  # axes coordinates
        print(f'{xa=}')
        print(f'{ya=}')
        print(f'{imsize=}')
        print(f'{xa - imsize / 2.0=}')
        print(f'{ya - imsize / 2.0=}')
        a = plt.axes([(xa / 0.7975) - 0.17, (ya / 0.805) - 0.155, imsize, imsize])
        a.imshow(img_list[index])
        a.set_aspect('equal')
        a.axis('off')
    # plt.show()
    plt.draw()
    plt.savefig('with_gates.jpg')
