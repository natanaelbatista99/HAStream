from collections import defaultdict, deque

class SuperAdjacencyList:
    def __init__(self):
        self.m_adjacencyList = defaultdict(list)

    def addEdge(self, vertex, edge):
        
        if vertex not in self.m_adjacencyList:
            self.m_adjacencyList[vertex] = deque()
            self.m_adjacencyList[vertex].append(edge)
            return
        edges = self.m_adjacencyList[vertex]
        if (edge.getWeight() < edges[0].getWeight()):
            edges.appendleft(edge)
        else:
            edges.append(edge)
            

    def removeEdge(self, vertex):
        del self.m_adjacencyList[vertex]

    def getAdjacentVertices(self):
        return self.m_adjacencyList.keys()

    def getEdgeWithSmallestWeight(self, vertex):
        edges = self.m_adjacencyList[vertex]
        if not edges:
            return None
        res = min(edges, key=lambda edge: edge.getWeight())
        return res

    def getAdjacentEdges(self):
        all_edges = []
        for edges in self.m_adjacencyList.values():
            all_edges.extend(edges)
        return all_edges

    def getEdgesTo(self, vertex):
        return self.m_adjacencyList[vertex]

    def clear(self):
        self.m_adjacencyList = defaultdict(list)