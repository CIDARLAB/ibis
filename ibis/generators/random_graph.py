import copy
import random
from typing import (
    List,
)

import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns

import imageio
from PIL import (
    Image,
)
import tqdm
from matplotlib.patches import Rectangle

valid_repressor_names = [
    'AmeR',
    'BetI',
    'BM3R1',
    'HlyIIR',
    'IcaRA',
    'LitR',
    'LmrA',
    'PhlF',
    'PsrA',
    'QacR',
    'SrpR',
]
rbs_letter_range = [65, 90]
rbs_integer_range = [1, 4]
ymin_range = [0.003, 0.2]
ymax_range = [0.5, 6.9]
k_range = [0.01, 0.23]
n_range = [1.8, 4.0]
top_graph = None
action_bar = None
graph_figure = None
used_rbs_names: List = []


class PartitionNode:

    def __init__(self, cell_index=None):
        self.repressor_name: str = None
        self.rbs: float = None
        self.y_min: float = None
        self.y_max: float = None
        self.k: float = None
        self.n: float = None
        self.cell_index: str = cell_index

    def randomize(self):

        def _get_random(input_nums: List[int]):
            lst_type = type(input_nums[0])
            if lst_type == int:
                return random.randint(input_nums[0], input_nums[1])
            if lst_type == float:
                return round(random.uniform(input_nums[0], input_nums[1]), 3)

        # Select from 'OK' Repressor Names
        self.repressor_name = random.choice(valid_repressor_names)
        # RBS Generation. This puts an upper bound of unique node generation of
        # about 26 x 4
        self.rbs = 'IDK'
        # while True:
        #     rbs_letter = chr(_get_random(rbs_letter_range))
        #     rbs_number = _get_random(rbs_integer_range)
        #     proposed_rbs = f'{rbs_letter}{rbs_number}'
        #     if proposed_rbs not in used_rbs_names:
        #         used_rbs_names.append(proposed_rbs)
        #         self.rbs = proposed_rbs
        #         break
        self.y_min = _get_random(ymin_range)
        self.y_max = _get_random(ymax_range)
        self.k = _get_random(k_range)
        self.n = _get_random(n_range)

    def return_as_dict(self):
        return {
            'repressor_name': self.repressor_name,
            'rbs': self.rbs,
            'y-min': self.y_min,
            'y-max': self.y_max,
            'k': self.k,
            'n': self.n,
        }


def generate_random_graph(
        input_num: int,
        output_num: int,
        minimum_nodes_per_rank: int,
        maximum_nodes_per_rank: int,
        minimum_ranks: int,
        maximum_ranks: int,
):
    g = nx.DiGraph()
    # We assume that we start with one input.
    total_ranks = minimum_ranks + (random.randint(0, 32767) % (maximum_ranks - minimum_ranks + 1))
    node_counter = 0
    for j in range(total_ranks):
        # We assume our initial layer are inputs. This is not necessarily true.
        new_nodes = minimum_nodes_per_rank + (
                random.randint(0, 32767) % (maximum_nodes_per_rank - minimum_nodes_per_rank + 1))
        # --------------------------- START OF GRAPH ---------------------------
        if not j:
            new_nodes = input_num
            for node in range(new_nodes):
                input_node = PartitionNode()
                input_node.randomize()
                g.add_node(
                    node_counter,
                    node_type="input",
                    rank=j,
                    handle=node_counter,
                    pos=(10 * j + 10, 10 * node * 10),
                    **input_node.return_as_dict(),
                )
                node_counter += 1
        # --------------------------- END OF GRAPH -----------------------------
        elif j == total_ranks - 1:
            new_nodes = output_num
            try:
                prior_nodes = [y for x, y in g.nodes(data=True) if y['rank'] == j - 1]
            except KeyError:
                continue
            start_node_counter = node_counter
            for node in range(new_nodes):
                output_node = PartitionNode()
                output_node.randomize()
                g.add_node(
                    node_counter,
                    node_type="output",
                    rank=j,
                    handle=node_counter,
                    pos=(10 * j + 10, 10 * node * 10),
                    **output_node.return_as_dict(),
                )
                node_counter += 1
            end_node_counter = node_counter
            # Should be the latest node
            for i in range(start_node_counter, end_node_counter):
                prior_node = random.choice(prior_nodes)
                g.add_edge(prior_node['handle'], i)
            while prior_nodes:
                random.shuffle(prior_nodes)
                lucky_child = random.choice(
                    range(
                        start_node_counter,
                        end_node_counter,
                    )
                )
                lucky_parent = prior_nodes.pop()
                g.add_edge(lucky_parent['handle'], lucky_child)
        # ------------------------- MIDDLE OF GRAPH ----------------------------
        else:
            try:
                prior_nodes = [y for x, y in g.nodes(data=True) if y['rank'] == j - 1]
            except KeyError:
                continue
            start_node_counter = node_counter
            for node in range(new_nodes):
                middle_node = PartitionNode()
                middle_node.randomize()
                g.add_node(
                    node_counter,
                    node_type="middle",
                    rank=j,
                    handle=node_counter,
                    pos=(10 * j + 10, 10 * node * 10),
                    **middle_node.return_as_dict(),
                )
                node_counter += 1
            end_node_counter = node_counter
            # Ensure that everyone has an ancestor...
            for i in range(start_node_counter, end_node_counter):
                prior_node = random.choice(prior_nodes)
                g.add_edge(prior_node['handle'], i)
            # But due to the nature of the graph we can't have any orphaned
            # parents either.
            while prior_nodes:
                random.shuffle(prior_nodes)
                lucky_child = random.choice(
                    range(
                        start_node_counter,
                        end_node_counter,
                    )
                )
                lucky_parent = prior_nodes.pop()
                g.add_edge(lucky_parent['handle'], lucky_child)

    return g

def recursive_droplet_search(inner_graph, input_droplet):
    pi = 'partition_index'
    partition_index = None
    input_neighbors = list(nx.neighbors(inner_graph, input_droplet['handle']))
    neighbor_list = copy.deepcopy(input_neighbors)
    while input_neighbors:
        random.shuffle(input_neighbors)
        _selected_node_index = input_neighbors.pop()
        _selected_node = inner_graph.nodes()[_selected_node_index]
        if pi in _selected_node:
            partition_index = _selected_node[pi]
            print(f'A-{partition_index=}')
            return partition_index
    while True:
        successor_list = copy.deepcopy(neighbor_list)
        while successor_list:
            random.shuffle(successor_list)
            _selected_node_index = successor_list.pop()
            _selected_node = inner_graph.nodes()[_selected_node_index]
            partition_index = recursive_droplet_search(
                inner_graph=inner_graph,
                input_droplet=_selected_node,
            )
            print(f'D-{partition_index=}')
            if partition_index:
                print(f'B-{partition_index=}')
                return partition_index
    print(f'C-{partition_index}')


def generate_fake_partition(input_graph: nx.DiGraph, partition_num: int):
    pi = 'partition_index'

    # We take in the graph and the partition number.
    # We have some sort of high level check to see if there are more partitions
    # than nodes, for example.
    # Once that's done we'll start with the first node and traverse both in x and y.
    # This takes this form of going to nodes in the same rank as themselves and
    # other nodes that are at least spatially aligned. There could be a notion
    # of nodes requiring to be within a degree of each other, but I think that will
    # be confusing visually from people, even if it doesn't represent the biological
    # reality.
    if len(input_graph.nodes) < partition_num:
        raise RuntimeError(
            f'Cannot partition network into more partitions than node.'
        )
    # We assume that we need to pick nodes to occupy each partition to ensure
    # that all partitions at least have one node and some distribution across
    # the network.
    pi = 'partition_index'
    current_node = input_graph.nodes()[1]
    partition_points = {}
    for i in range(partition_num):
        current_node[pi] = i
        partition_points[i] = current_node['handle']
        current_node = random.choice(input_graph.nodes())
        while hasattr(current_node, pi):
            current_node = random.choice(input_graph.nodes())
    # We've seeded our network with our partition points, and now we need to
    # grow them out. For this initial pass I'm just going to see what's up,
    # by we probably need some sort of cognizance of overlap of the area of the
    # partition.
    # Let's call this a droplet merge. Think of a bead of water absorbing other
    # beads of water.
    undirected_graph = input_graph.to_undirected()
    for droplet_node in input_graph.nodes(data=True):
        if pi not in droplet_node[1]:
            # We recursively move through our edges looking for someone who's
            # already in a partition.
            thing = recursive_droplet_search(
                inner_graph=undirected_graph,
                input_droplet=droplet_node[1],
            )
            print(f'{thing=}')
            droplet_node[1][pi] = thing
    return input_graph

def reorder_for_partition_position(input_graph: nx.DiGraph, partition_num: int):
    # We'll assume a grid like structure.
    for i in range(partition_num):
        nodes_of_partition = []
        for node in input_graph.nodes(data=True):
            print(node[1]['partition_index'])
            if node[1]['partition_index'] == i:
                nodes_of_partition.append(node[1])

        for index, j in enumerate(nodes_of_partition):
            x_pos = index * 50
            y_pos = i % 3 * 50
            j['partiton_position'] = (x_pos, y_pos)
    return input_graph


def generate_visualization():
    write_list = []
    for i in tqdm.tqdm(range(15)):
        INPUT_NUM = random.randint(2, 5)
        OUTPUT_NUM = random.randint(1, 4)

        MIN_NODES = random.randint(2, 5)
        MAX_NODES = MIN_NODES + random.randint(1, 4)

        MIN_RANKS = 15
        MAX_RANKS = 30
        o = generate_random_graph(
            input_num=INPUT_NUM,
            output_num=OUTPUT_NUM,
            minimum_nodes_per_rank=MIN_NODES,
            maximum_nodes_per_rank=MAX_NODES,
            minimum_ranks=MIN_RANKS,
            maximum_ranks=MAX_RANKS,
        )
        # We need to be able to position by node positions
        # We then need to color by layer.
        # pos_list = [node['pos'] for node in o.nodes]
        pos_list = []
        for node in o.nodes(data=True):
            pos_list.append(node[1]['pos'])
        color_list = []
        color_lookup = sns.color_palette('deep', MAX_RANKS)
        for node in o.nodes(data=True):
            color = color_lookup[int(node[1]['rank'])]
            color_list.append(color)
        nx.draw(
            o,
            pos=pos_list,
            node_color=color_list,

        )
        out_handle = f'{i}.png'
        plt.savefig(out_handle)
        write_list.append(out_handle)
        plt.clf()
    draw_array = []
    time_delay = 15
    for write_fp in write_list:
        for frame_delay in range(time_delay):
            draw_array.append(Image.open(write_fp))
    imageio.mimsave(
        f'example_graphs.gif',
        draw_array,
    )


if __name__ == '__main__':
    MAX_RANKS = 10
    NUM_OF_PARTITIONS = 4
    o = generate_random_graph(
        input_num=2,
        output_num=1,
        minimum_nodes_per_rank=2,
        maximum_nodes_per_rank=3,
        minimum_ranks=5,
        maximum_ranks=MAX_RANKS,
    )
    # We need to be able to position by node positions
    # We then need to color by layer.
    # pos_list = [node['pos'] for node in o.nodes]
    f, ax = plt.subplots(1, 1, figsize=(8, 5))
    pos_list = []
    for node in o.nodes(data=True):
        pos_list.append(node[1]['pos'])
    color_list = []
    color_lookup = sns.color_palette('deep', MAX_RANKS)
    for node in o.nodes(data=True):
        color = color_lookup[int(node[1]['rank'])]
        color_list.append(color)
    nx.draw(
        o,
        pos=pos_list,
        node_color=color_list,
    )
    plt.show()
    plt.clf()
    o = generate_fake_partition(o, NUM_OF_PARTITIONS)
    reorder_for_partition_position(o, NUM_OF_PARTITIONS)
    part_pos = []
    for node in o.nodes(data=True):
        part_pos.append(node[1]['partiton_position'])
    part_color_list = []
    color_lookup = sns.color_palette('bright', NUM_OF_PARTITIONS)
    for node in o.nodes(data=True):
        color = color_lookup[int(node[1]['partition_index'])]
        part_color_list.append(color)
    nx.draw(
        o,
        pos=part_pos,
        node_color=color_list,
    )
    plt.show()
    plt.clf()
    nx.draw(
        o,
        pos=part_pos,
        node_color=part_color_list,
        alpha=0.6,
    )
    ax.add_patch(Rectangle((0, 0), 0.1, 0.1, linewidth=1, edgecolor='b', facecolor='none'))
    plt.show()

