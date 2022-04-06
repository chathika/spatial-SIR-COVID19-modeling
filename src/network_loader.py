import os
import sys
import glob
from pathlib import Path

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns

class NetworkLoader:

    def __init__(self, tot_pop):
        self.filenames = glob.glob("output/output_*.csv")
        self._tot_pop = tot_pop
        graphs = []
        strategies = []
        pop_muls = []
        break_probs = []
        for filename in self.filenames:
            network_info = self._load_network(filename)
            graphs.append(network_info[0])
            strategies.append(network_info[1])
            pop_muls.append(network_info[2])
            break_probs.append(network_info[3])

        self._networks = pd.DataFrame({"Graph": graphs, "Strategy": strategies, "PopMul": pop_muls, "ProbBreak": break_probs})
        colors = {
            'I':[[0.05,0.25],[0.05,0.5],[0.05,0.75],[0.05,1.0],[0.05,1.25],[0.05,1.5],[0.05,1.75],[0.05,2.0],[0.1,0.25],[0.1,0.5],[0.1,0.75],[0.2,0.25]],
            'II' :[[0.1,1.0],[0.1,1.25],[0.1,1.5],[0.1,1.75],[0.1,2.0],[0.2,0.5],[0.2,0.75],[0.25,0.25],[0.25,0.5],[0.3,0.25],[0.3,0.5],[0.35,0.25],[0.4,0.25],[0.45,0.25]],
            'III'  :[[0.2,1.0],[0.25,0.75],[0.3,0.75],[0.35,0.5],[0.4,0.5],[0.45,0.25]]
        }
        self._networks['class'] = self._networks.apply(lambda x: 'I' if [x['ProbBreak'],x['PopMul']] in colors['I'] else ('II' if [x['ProbBreak'],x['PopMul']] in colors['II'] else 'III'), axis=1)

    def _load_network(self, fn: str):
        cts = pd.read_csv(fn, names=["Time","A","B", "place"], skiprows=1)
        bname = Path(fn).stem.replace('output','offices')
        fpath = Path(Path(fn).parent.absolute(), f'{bname}.csv')
        nodes = pd.read_csv(fpath, names=["Agent","Office"], skiprows=1)
        cts["A"] = cts.A.apply(lambda x: int(x[1:]))
        cts["B"] = cts.B.apply(lambda x: int(x[:-1]))
        pop_mul = float(fn.split("_")[1])
        break_prob = float(fn.split("_")[2])
        strategy = fn.split("_")[3]
        G = nx.from_pandas_edgelist(cts, source="A", target="B", edge_attr=True)        
        nodes.columns = [c.replace(' ','') for c in nodes.columns]
        if nodes.Agent[~nodes.Agent.isin(G.nodes)].unique().shape[0] + len(G.nodes) != nodes.Agent.shape[0]:
            print('Break Prob', break_prob, 'PopMul',pop_mul, 'Missing', nodes.Agent[~nodes.Agent.isin(G.nodes)].unique().shape[0], 'Have', len(G.nodes), 'From', nodes.Agent.shape[0])
        for i in nodes.Agent[~nodes.Agent.isin(G.nodes)]:
            G.add_node(i)
        offices = dict(zip(G.nodes, [nodes[nodes.Agent == node].Office.iloc[0] for node in G.nodes]))
        nx.set_node_attributes(G, offices, 'office')
        return G, strategy, pop_mul, break_prob

    @property
    def networks(self):
        return self._networks

    def same_office_contacts(self):
        val = self._networks.copy()
        val['ratio_same_office_contacts'] = self._networks.Graph.apply(lambda n: 0 if len(list(n.edges)) == 0 else sum([1 for edge in n.edges if n.nodes[edge[0]]['office']==n.nodes[edge[1]]['office']]) / len(n.edges))
        return val

    def room_dist(self):
        self._networks['cens'] = self._networks.Graph.apply(lambda G: nx.degree_centrality(G))
        room_cens = []
        self._networks.apply(lambda scenario: [room_cens.append([scenario.Strategy, scenario.PopMul, scenario.ProbBreak, scenario['class'], scenario.Graph.nodes(data=True)[node]['office'],scenario.cens[node]]) for node in scenario.cens], axis = 1)
        return pd.DataFrame(data=room_cens, columns=['Strategy', 'PopMul', 'ProbBreak', 'Class', 'Office', 'Centrality'])

"""
centrality = pd.DataFrame()
contacts = pd.DataFrame()
for fn in filenames:
    cts = pd.read_csv(os.path.join(fn),names=["source","target"],delimiter=",")
    cts["Strategy"] = fn.split("_")[2]
    counts = cts.groupby(["source","target"]).count()
    edges = counts[counts.Strategy>=60].reset_index()[["source","target"]].drop_duplicates()   
    print(edges)
    edges["Strategy"] = fn.split("_")[2]
    edges["Occupancy Scale (1=Expected)"] = fn.split("_")[1] 
    contacts = contacts.append(edges)
    G = nx.from_pandas_edgelist(edges)
    c = pd.DataFrame.from_dict(nx.degree_centrality(G),orient="index").rename(columns={0:"centrality"})
    c["Strategy"] = fn.split("_")[2]
    c["Occupancy Scale (1=Expected)"] = fn.split("_")[1]
    centrality = centrality.append(c)
    #Gcc = G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[0])
    pos = nx.spring_layout(G)
    plt.axis("off")
    nx.draw_networkx_nodes(G, pos, node_size=20)
    nx.draw_networkx_edges(G, pos, alpha=0.4)
    params="_".join([fn.split("_")[2],fn.split("_")[1]])
    plt.savefig(f"net_{params}.png")
    plt.show()

"""