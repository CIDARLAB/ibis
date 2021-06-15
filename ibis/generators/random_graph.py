import copy
import random
from typing import (
    List,
)

import imageio
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
import tqdm
from PIL import (
    Image,
)
from networkx.drawing.nx_agraph import graphviz_layout

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


# ------------ Random Graph based on Ranks traversing left to right ------------
def generate_random_rank_graph(
        input_num: int,
        output_num: int,
        minimum_nodes_per_rank: int,
        maximum_nodes_per_rank: int,
        minimum_ranks: int,
        maximum_ranks: int,
        max_exit_degree: int = 2,
        edge_propensity: float = 15,
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
            print(new_nodes)
            try:
                prior_nodes = [y for x, y in g.nodes(data=True) if y['rank'] == j - 1]
            except KeyError:
                continue
            start_node_counter = node_counter
            for node in range(new_nodes):
                print(2)
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
                while True:
                    lucky_child = random.choice(
                        range(
                            start_node_counter,
                            end_node_counter,
                        )
                    )
                    lucky_degree = g.in_degree(lucky_child)
                    print(f'{lucky_degree}')
                    if type(lucky_degree) == int:
                        if g.in_degree(lucky_child) < max_exit_degree:
                            break
                    else:
                        break
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
            copy_nodes = copy.deepcopy(prior_nodes)
            for i in range(start_node_counter, end_node_counter):
                if not copy_nodes:
                    while True:
                        prior_node = random.choice(
                            prior_nodes,
                        )
                        prior_degree = g.in_degree(prior_node)
                        if type(prior_degree) == int:
                            if g.in_degree(prior_node) < max_exit_degree:
                                break
                        else:
                            break
                    g.add_edge(prior_node['handle'], i)
                else:
                    random.shuffle(copy_nodes)
                    prior_node = copy_nodes.pop()
                    g.add_edge(prior_node['handle'], i)
                # if random.randint(0, 100) < edge_propensity:
                #     if len(list(g.edges(prior_node['handle']))) < max_exit_degree:
                #         random_next_node = random.randint(start_node_counter, end_node_counter)
                #         g.add_edge(prior_node['handle'], random_next_node)
            # But due to the nature of the graph we can't have any orphaned
            # parents either.
            while prior_nodes:
                random.shuffle(prior_nodes)
                while True:
                    lucky_child = random.choice(
                        range(
                            start_node_counter,
                            end_node_counter,
                        )
                    )
                    # print(f'{g.in_degree(lucky_child)=}')
                    # print(f'{prior_nodes}')
                    if g.in_degree(lucky_child) < max_exit_degree:
                        # print(f'{g.in_degree(lucky_child)=}')
                        # print(f'{max_exit_degree=}')
                        break
                lucky_parent = prior_nodes.pop()
                g.add_edge(lucky_parent['handle'], lucky_child)

    return g


def degree_check(graph, node, maximum_degree):
    if (graph.in_degree(node) + graph.out_degree(node)) > maximum_degree:
        return False
    return True


# ----------------- Random Graph in more of a tree like format -----------------
def generate_random_tree_graph(
        input_nodes: int = 3,
        output_nodes: int = 2,
        total_nodes: int = 20,
        input_chance: int = 5,
        output_chance: int = 5,
        edge_propensity: int = 25,
):
    '''
    Our constraints:

        - Each graph contains 3-5 input vertices, 1-2 output vertex, and the
            rest primitive vertices
        - Each primitive vertex has a degree of 2 or 3
        - Two vertices with two edges cannot be neighbors
        - No self-loops, cycles, or parallel edges are allowed.
        - Each primitive vertex has a path from at least one of the input vertices,
            as well as a path to the output vertex.
        - The output vertex has variable logic states under different combinations
            of input states.
        - The final graph is connected.

    '''

    def total_exit_condition():
        criteria = [
            total_node_count >= total_nodes,
            input_node_count >= input_nodes,
            output_node_count >= output_nodes,
        ]
        return all(criteria)

    def inputs_available():
        return not input_node_count >= input_nodes

    def outputs_available():
        return not output_node_count >= output_nodes

    g = nx.DiGraph()
    center_point = 100
    x_delta_modifier = 25
    y_delta_modifier = 100
    y_start = 400
    # -------------------------------- COUNTERS --------------------------------
    rank_count = 0
    input_node_count = 0
    output_node_count = 0
    total_node_count = 0
    node_streak = 0
    # ------------------------------- ROOT NODE --------------------------------
    root_node = PartitionNode()
    g.add_node(
        total_node_count,
        node_type="input",
        rank=rank_count,
        handle=total_node_count,
        pos=(center_point, y_start),
        **root_node.return_as_dict(),
    )
    input_node_count += 1
    total_node_count += 1
    # --------------------- ADDITIONAL ROOT LEVEL INPUTS -----------------------
    if random.randint(0, 100) < input_chance:
        input_node = PartitionNode()
        g.add_node(
            total_node_count,
            node_type="input",
            rank=rank_count,
            handle=total_node_count,
            pos=(center_point + x_delta_modifier, y_start),
            **input_node.return_as_dict(),
        )
        input_node_count += 1
        total_node_count += 1
    current_rank_nodes = [y for x, y in g.nodes(data=True) if y['rank'] == rank_count]
    demarc_point = len(current_rank_nodes) / 2
    for index, node_ref in enumerate(current_rank_nodes):
        polarity = -1 if index <= demarc_point else 1
        distance = len(current_rank_nodes) - index
        x_position = (x_delta_modifier * polarity * distance) + center_point
        y_position = y_start - (rank_count * y_delta_modifier)
        g.nodes[node_ref['handle']]['pos'] = (x_position, y_position)
    rank_count += 1
    # --------------------------- PRIMITIVE LAYERS -----------------------------
    while not total_exit_condition():
        # We might be adding an input node, which does not necessitate an
        # ancestor.
        if inputs_available():
            if random.randint(0, 100) < input_chance:
                input_node = PartitionNode()
                g.add_node(
                    total_node_count,
                    node_type="input",
                    rank=rank_count,
                    handle=total_node_count,
                    pos=(0, 0),
                    **input_node.return_as_dict(),
                )
                input_node_count += 1
                total_node_count += 1
        # We first ensure that every prior node that is not an output node
        # has a child.
        prior_nodes = [y for x, y in g.nodes(data=True) if y['rank'] == rank_count - 1 and y['node_type'] != 'output']
        edge_copy = copy.deepcopy(prior_nodes)
        random.shuffle(prior_nodes)
        for prior_node in prior_nodes:
            if outputs_available():
                if random.randint(0, 100) < output_chance:
                    output_node = PartitionNode()
                    g.add_node(
                        total_node_count,
                        node_type="output",
                        rank=rank_count,
                        handle=total_node_count,
                        pos=(0, 0),
                        **output_node.return_as_dict(),
                    )
                    g.add_edge(prior_node['handle'], total_node_count)
                    output_node_count += 1
                    total_node_count += 1
                    continue
            primitive_node = PartitionNode()
            g.add_node(
                total_node_count,
                node_type="middle",
                rank=rank_count,
                handle=total_node_count,
                pos=(0, 0),
                **primitive_node.return_as_dict(),
            )
            g.add_edge(prior_node['handle'], total_node_count)
            if random.randint(0, 100) < edge_propensity + (edge_propensity * node_streak):
                random_counter = 0
                while True:
                    random.shuffle(edge_copy)
                    lucky_node = edge_copy.pop()
                    if g.in_degree(lucky_node['handle']) + g.out_degree(lucky_node['handle']) < 3:
                        g.add_edge(lucky_node['handle'], total_node_count)
                        break
                    if random_counter > 15:
                        break
                    random_counter += 1
                    node_streak = 0
            else:
                node_streak += 1
            total_node_count += 1
        # Given the tree like structure of the wanted output,
        # we reorder the positions of the ranked nodes to create a waterfall effect downward.
        current_rank_nodes = [y for x, y in g.nodes(data=True) if y['rank'] == rank_count]
        demarc_point = len(current_rank_nodes) / 2
        for index, node_ref in enumerate(current_rank_nodes):
            polarity = -1 if index <= demarc_point else 1
            distance = len(current_rank_nodes) - index
            predecessor = list(g.predecessors(node_ref['handle']))
            if predecessor:
                ancestor_x, ancestor_y = g.nodes[predecessor[0]]['pos']
            else:
                ancestor_x = center_point
            if len(current_rank_nodes) == 1:
                x_position = center_point
            else:
                x_position = (x_delta_modifier * polarity * distance) + center_point
            y_position = y_start - (rank_count * y_delta_modifier)
            g.nodes[node_ref['handle']]['pos'] = (x_position, y_position)
        rank_count += 1
    return g


# ------------------------ NAIEVE PARTITIONING ATTEMPTS ------------------------
def recursive_droplet_search(inner_graph, input_droplet):
    pi = 'partition_index'
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
        INPUT_NUM = random.randint(2, 4)

        MIN_NODES = random.randint(2, 3)
        MAX_NODES = MIN_NODES + random.randint(0, 1)

        OUTPUT_NUM = random.randint(2, 3)

        MIN_RANKS = 15
        MAX_RANKS = 30
        o = generate_random_rank_graph(
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
    g = generate_random_tree_graph()
    labels = {}
    # Then we create an implicit ordering based on these locations
    for node_index in list(g.nodes):
        labels[node_index] = g.nodes[node_index]['handle']
    pos_list = []
    for node in g.nodes(data=True):
        pos_list.append(node[1]['pos'])
    color_list = []
    color_lookup = sns.color_palette('deep', 3)
    color_dict = {
        'input': 0,
        'middle': 1,
        'output': 2,

    }
    for node in g.nodes(data=True):
        color_index = color_dict[node[1]['node_type']]
        print(color_index)
        color = color_lookup[color_index]
        color_list.append(color)
    nx.nx_agraph.write_dot(g, 'test.dot')

    plt.figure(3, figsize=(12, 12))
    nx.draw(
        g,
        pos=pos_list,
        labels=labels,
        node_color=color_list,
    )
    plt.show()

# if __name__ == '__main__':
#     test_num = 10
#     INPUT_NUM = random.randint(0, 2)
#
#     MIN_NODES = INPUT_NUM + random.randint(-1, 3)
#     MAX_NODES = MIN_NODES + random.randint(0, 1)
#
#     OUTPUT_NUM = random.randint(MAX_NODES - 2, MAX_NODES - 1)
#
#     MIN_RANKS = 10
#     MAX_RANKS = 15
#     o = generate_random_rank_graph(
#         input_num=INPUT_NUM,
#         output_num=OUTPUT_NUM,
#         minimum_nodes_per_rank=MIN_NODES,
#         maximum_nodes_per_rank=MAX_NODES,
#         minimum_ranks=MIN_RANKS,
#         maximum_ranks=MAX_RANKS,
#     )
#     pos_list = []
#     for node in o.nodes(data=True):
#         pos_list.append(node[1]['pos'])
#     color_list = []
#     color_lookup = sns.color_palette('deep', MAX_RANKS)
#     for node in o.nodes(data=True):
#         color = color_lookup[int(node[1]['rank'])]
#         color_list.append(color)
#     plt.figure(3, figsize=(12, 12))
#     nx.draw(
#         o,
#         pos=pos_list,
#         node_color=color_list,
#     )
#     # plt.show()
#     plt.savefig(f'testcase_{test_num}.png')
#     nx.write_edgelist(o, path=f'testcase_{test_num}.edgelist')
