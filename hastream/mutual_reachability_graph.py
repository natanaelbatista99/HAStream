import time
import copy
import itertools
import sys
import numpy as np

from sklearn.neighbors import KDTree
from .abstract_graph import AbstractGraph
from .micro_cluster import Vertex, MicroCluster
from .neighbour import Neighbour

class MutualReachabilityGraph(AbstractGraph):
    def __init__(self, graph, mcs : MicroCluster, mpts, timestamp):
        super().__init__()
        self.mpts      = mpts
        self.G         = graph
        self.timestamp = timestamp

        for mc in mcs:
            v = Vertex(mc, timestamp)
            mc.setVertexRepresentative(v)
            self.G.add_node(v)
        
        start = time.time()
        self.computeCoreDistance()
        end   = time.time()
        print(">tempo para computar coreDistanceDB: ", end - start, end='\n')

    def getKnngGraph(self):
        return self.knng
       
    def buildGraph(self):
        seen = set()

        for idx1, v1 in enumerate(self.G.nodes):
            for idx2, v2 in enumerate(self.G.nodes):
                pair = (idx1, idx2)

                if idx1 >= idx2 or pair in seen:
                    continue
                
                seen.add(pair)
                mrd = self.getMutualReachabilityDistance(v1, v2)
                self.G.add_edge(v1, v2, weight = mrd)

            
    def computeCoreDistance(self):
        coords = [[v for k, v in vx.getMicroCluster().getCenter(self.timestamp).items()] for vx in self.G.nodes]
        kdtree = KDTree(coords)

        # mpts: valor fixo para a distância do m-ésimo vizinho
        dists, _       = kdtree.query(coords, k = self.mpts + 1)
        core_distances = dists[:, -1]  # Pega a distância do m-ésimo vizinho

        # Atualiza os objetos Vertex no grafo com a core distance
        for vertex, core_dist in zip(self.G.nodes, core_distances):
            vertex.setCoreDistance(core_dist)

    def getMutualReachabilityDistance(self, v1, v2):
        return max(v1.getCoreDistance(), max(v2.getCoreDistance(), v1.getDistance(v2)))
    
    def getmpts(self):
        return self.m_mpts