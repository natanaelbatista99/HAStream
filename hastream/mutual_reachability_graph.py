import time

from .abstract_graph import AbstractGraph
from .micro_cluster import Vertex, MicroCluster
from .neighbour import Neighbour

class MutualReachabilityGraph(AbstractGraph):
    def __init__(self, G, mcs : MicroCluster, minPts, timestamp):
        super().__init__()
        self.m_minPts  = minPts
        self.G         = G
        self.timestamp = timestamp

        for mc in mcs:
            v = Vertex(mc, timestamp)
            mc.setVertexRepresentative(v)
            self.G.add_node(v)
        
        start = time.time()
        self.computeCoreDistance(G, minPts)
        end   = time.time()
        #print(">tempo para computar coreDistanceDB",end - start, end='\n')

    def getKnngGraph(self):
        return self.knng
       
    def buildGraph(self):
        for v1 in self.G:            
            for v2 in self.G:
                if v1 != v2:
                    mrd = self.getMutualReachabilityDistance(v1, v2)
                    self.G.add_edge(v1, v2, weight = mrd)
        
        self.buildGraph1()
        
    def buildGraph1(self):
        for i, (u,v,w) in enumerate(self.G.edges(data='weight')):
            self.addVertex(u)
            self.addVertex(v)
            self.addEdge(u,v,w)
            
    def computeCoreDistance(self, vertices, minPts):
        for current in vertices:
            neighbours      = self.getNeighbourhood(current, vertices)
            minPtsNeighbour = neighbours[minPts - 1]
            
            current.setCoreDistance(minPtsNeighbour)

    def getNeighbourhood(self, vertex, vertices):
        neighbours = []
        
        for v in vertices:
            if v != vertex:
                neighbour = Neighbour(v, vertex.getDistance(v))
                neighbours.append(neighbour)
                
        neighbours.sort(key=lambda x: x.getDistance(), reverse=False)
        
        return neighbours

    def getMutualReachabilityDistance(self, v1, v2):
        return max(v1.getCoreDistance(), max(v2.getCoreDistance(), v1.getDistance(v2)))
    
    def getMinPts(self):
        return self.m_minPts