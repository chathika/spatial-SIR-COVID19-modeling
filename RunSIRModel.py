import pandas as pd
from argparse import ArgumentParser
from tqdm import tqdm
from random import randint
import networkx as nx
import os 
from glob import glob

from src.network_loader import NetworkLoader
from src.epidemic_simulator import EpidemicSimulator
from src.plot_results import PlotResults

def simulate_all_networks(args, tot_pop = 111):
    nl = NetworkLoader(tot_pop)
    all_results = pd.DataFrame()
    for idx, scenario in tqdm(list(nl.networks.iterrows()), desc='Progress'):
        sim = EpidemicSimulator(scenario['Graph'],round(scenario['PopMul']*111))
        for SAR in np.arange(float(args.SARmin), float(args.SARmax), float(args.SARstep)):
            res = sim.simulate(SAR = round(SAR,2), reps= 10)
            res['GraphID'] = idx
            res['Strategy'] = scenario['Strategy']
            res['PopMul'] = scenario['PopMul']
            res['ProbBreak'] = scenario['ProbBreak']
            all_results = all_results.append(res, ignore_index=True)

    all_results.to_csv(f'output/allsims_{args.SARmin}_{args.SARmax}_{args.SARstep}.csv', index=False, float_format='%g')

    sc = {}
    for idx, scenario in tqdm(list(nl.networks.iterrows()), desc='Progress'):
        graph = scenario['Graph']
        sc[idx] = {} 
        for node, centrality in nx.degree_centrality(graph).items():
            sc[idx][int(node)] = centrality

    sc = pd.DataFrame(sc).T.reset_index().melt(id_vars = ['index']).dropna()
    sc.columns = ['GraphID', 'Node', 'Centrality']
    sc = sc.set_index(['GraphID', 'Node'])
    sc = sc[~sc.index.duplicated()]


    #cont = pd.DataFrame()
    for path in tqdm(glob('output/allsims_*.csv')):
        all_results = pd.read_csv(path)
        all_results = all_results.set_index(['GraphID','Node'])
        all_results['centrality'] = sc.reindex(all_results.index).Centrality.fillna(0)
        all_results.to_csv(f'output/allsims.csv', float_format='%g', mode='a', header= not os.path.exists('output/allsims.csv'))
        #cont = cont.append(all_results, ignore_index=True)


    #all_results.to_csv(f'output/allsims_{args.SARmin}_{args.SARmax}_{args.SARstep}.csv', index=False, float_format='%g',mode='a')


def plot_results(args):
    df = pd.read_csv('output/allsims.csv')
    plotter = PlotResults(df)
    plotter.plot_popmul_vs_infratio()

def plot_centrality_risk(args):
    df = pd.read_csv('output/allsims.csv')
    plotter = PlotResults(df)
    plotter.plot_centrality_risk()

ACTIONS = {
    'simulate' : simulate_all_networks, 
    'plot' : plot_results
}
if __name__=='__main__':
    parser = ArgumentParser()
    parser.add_argument('action')
    parser.add_argument('--SARmin')
    parser.add_argument('--SARmax')
    parser.add_argument('--SARstep')
    args = parser.parse_args()
    ACTIONS[args.action](args)