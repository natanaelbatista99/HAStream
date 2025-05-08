from collections import defaultdict, deque
from .super_adjacency_list import SuperAdjacencyList

class SuperAbstractGraph:
    def __init__(self):
        self.m_graph = defaultdict(SuperAdjacencyList)
        self.m_globalIDCounter = 0

    def addVertex(self, vertex):
        if vertex in self.m_graph:
            return False
        self.m_graph[vertex] = SuperAdjacencyList()
        return True

    def addEdge(self, vertex1, vertex2, edge):
        if vertex1 not in self.m_graph or vertex2 not in self.m_graph:
            raise KeyError("One vertex or both are missing")
        self.adjacencyList(vertex1).addEdge(vertex2, edge)
        self.adjacencyList(vertex2).addEdge(vertex1, edge)

    def removeEdge(self, vertex1, vertex2):
        if vertex1 not in self.m_graph or vertex2 not in self.m_graph:
            raise KeyError("One vertex or both are missing")
        self.adjacencyList(vertex1).removeEdge(vertex2)
        self.adjacencyList(vertex2).removeEdge(vertex1)

    def removeVertex(self, vertex):
        del self.m_graph[vertex]

    def buildGraph(self):
        pass

    def getEdge(self, vertex1, vertex2):
        if vertex1 not in self.m_graph or vertex2 not in self.m_graph:
            raise KeyError("One vertex or both are missing")
        edges = self.adjacencyList(vertex1).getEdgesTo(vertex2)
        if edges is None or len(edges) == 0:
            raise KeyError("There are no edges between these vertices.")
        return edges

    def getVertices(self):
        if self.isEmpty():
            return None
        return self.m_graph.keys()

    def getAdjacentEdges(self, vertex):
        adjacentEdges = self.adjacencyList(vertex).getAdjacentEdges()
        if adjacentEdges is None:
            raise KeyError("This is an isolated vertex")
        return adjacentEdges

    def containsVertex(self, vertex):
        return vertex in self.m_graph

    def containsEdge(self, vertex1, vertex2):
        if vertex1 not in self.m_graph or vertex2 not in self.m_graph:
            raise KeyError("One vertex or both are missing")
        return self.adjacencyList(vertex1).getEdgesTo(vertex2) is not None

    def __iter__(self):
        return iter(self.m_graph.keys())

    def numVertices(self):
        return len(self.m_graph)

    def isEmpty(self):
        return len(self.m_graph) == 0

    def getNextID(self):
        self.m_globalIDCounter += 1
        return self.m_globalIDCounter

    def adjacencyList(self, vertex):
        return self.m_graph[vertex]