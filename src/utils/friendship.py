import os
from os.path import join
import json
from utils.preprocess import JSONLoader
import networkx as nx

class Friendship(nx.Graph):
    '''
    Friendship Network.
    This is a child of nx.Graph where each node has additional attribute of 'influence'
    '''
    
    def __init__(self):
        super().__init__()
    
    def init_influence(self):
        dc = nx.degree_centrality(self)
        nx.set_node_attributes(self, name='influence', values=dc)

class GraphBuilder(JSONLoader):
    
    def __init__(self, json_file, dir_data):
        super().__init__(json_file, dir_data, fields = ['user_id','friends'])
        
    def build_graph(self, n_samples = 100, print_every = 10000, verbose = True, calculate_influence = False):
        '''
        Incrementally build a friendship network
        
        Args:
            n_samples (int): the number of json user objects to use. -1 to use all samples.
        '''
        
        G = Friendship()

        with open(self.dir_json) as f:
            for i, line in enumerate(f):
                if i % print_every == 0 and verbose:
                    print('[%i] N(nodes): %i' % (i ,len(G.nodes())))
                    print('[%i] N(edges): %i' % (i, len(G.edges())))
                    if i!= 0:
                        print('[%i] N(nodes)/N(edges): %.4f' % (i, len(G.nodes()) / len(G.edges())))
                    print()
                if i >= n_samples:
                    break
                json_line = json.loads(line)
                user_id = json_line['user_id']
                friends = json_line['friends']
                edges = [(user_id, target) for target in friends]
                G.add_edges_from(edges)
         
        if calculate_influence:
            print('Calculating Influence...')
            G.init_influence()
            
        return G
    
