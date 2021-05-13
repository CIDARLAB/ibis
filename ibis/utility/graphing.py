import matplotlib.pyplot as plt
import networkx as nx


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