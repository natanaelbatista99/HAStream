from .abstract_graph import AbstractGraph

class MinimalSpaningTree(AbstractGraph):
    def __init__(self, graph):
        super().__init__()
        self.m_inputGraph = graph

    def buildGraph(self):
        for i, (u,v,w) in enumerate(self.m_inputGraph.edges(data='weight')):
            self.addVertex(u)
            self.addVertex(v)
            self.addEdge(u,v,w)
    
    def getEdgeWithMinWeight(self, available):
        fromVertex = toVertex = edge = None
        dist = float('inf')
        
        for v in available:            
            for e in self.m_inputGraph.adjacencyList(v).values():
                other = e.getAdjacentVertex(v)
                if e.getWeight() < dist and other not in available:
                    fromVertex = v
                    toVertex = other
                    edge = e
                    dist = e.getWeight()

        return fromVertex, toVertex, edge

    @staticmethod
    def getEmptyMST():
        return MinimalSpaningTree(None)

    def getTotalWeight(self):
        edges = set()
        
        for v in self.m_graph.getVertices():
            for e in self.adjacencyList[v].values():
                edges.add(e)

        res = 0
        for e in edges:
            res += e.getWeight()
            
        return res