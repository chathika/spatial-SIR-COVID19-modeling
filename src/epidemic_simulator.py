from random import choices

from networkx import Graph
import pandas as pd

class EpidemicSimulator:

    def __init__(self, G : Graph, tot_pop : int):
        self._G = G
        self._tot_pop = tot_pop
        self._sim_results = {}
        self._recovereds = []
        self._susceptibles = []
        self._infection_probs = []


    def simulate(self, SAR, I0 = 1, reps = 1) -> pd.DataFrame:
        """
        Performs monte carlo simulations on provided network at Rt
        """
        assert 0 < SAR < 1
        sim_results = []
        for rep in range(reps):
            infection_prob = dict(zip(self._G.nodes, [[] for _ in range(len(self._G.nodes))]))

            recovered = []
            infecteds = [] if list(self._G.nodes) == [] else list(set(choices(list(self._G.nodes), k=I0)))
            susceptibles = [] if list(self._G.nodes) == [] else [n for n in self._G.nodes if n not in infecteds]
            while len(infecteds) > 0:
                for i in infecteds:
                    contacts = self._G.neighbors(i)
                    susceptible_contacts = [c for c in contacts if c in susceptibles]
                    if len(susceptible_contacts) > 0:
                        secondary_inf_count = int(round(SAR * len(susceptible_contacts)))
                        exposed_contacts = list(set(choices(list(susceptible_contacts), k = secondary_inf_count)))
                        for sc in susceptible_contacts:
                            infection_prob[sc].append(len(exposed_contacts)/len(susceptible_contacts))
                        susceptibles = [s for s in susceptibles if s not in exposed_contacts]
                        infecteds.extend(exposed_contacts)
                    infecteds.remove(i)
                    recovered.append(i)
            for r in recovered:
                sim_results.append([SAR, I0, rep, r, 'R', infection_prob[r]])
            for s in susceptibles:
                sim_results.append([SAR, I0, rep, s, 'S', infection_prob[s]])
            for i in range(self._tot_pop):
                sim_results.append([SAR, I0, rep, 2000+i, 'S', []])
        return pd.DataFrame(sim_results, 
                        columns=['SAR', 'I0', 'Rep', 'Node', 'State', 'Infection Risks'])
        
    @property
    def recovereds(self):
        return self._recovereds

    @property
    def susceptibles(self):
        return self._susceptibles

    @property
    def infection_probs(self):
        return self._infection_probs

        

        