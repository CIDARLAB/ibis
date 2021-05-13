
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


if __name__ == '__main__':
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
