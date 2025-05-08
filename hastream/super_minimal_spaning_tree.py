from .minimal_spaning_tree import MinimalSpaningTree

class SuperMinimalSpaningTree(MinimalSpaningTree):

    def __init__(self, graph):
        super().__init__(graph)
        self.m_inputGraph = graph

    def buildGraph(self):
        vertexQueue = set()
        edgeQueue = []
        
        # Select any node as the first node
        iterator = iter(self.m_inputGraph)
        first    = None

        if iterator:
            first = next(iterator)
        else:
            return

        vertexQueue.add(first)

        while len(vertexQueue) != len(self.m_inputGraph.getVertices()):
            fromVertex, toVertex, edge = self.getEdgeWithMinWeight(vertexQueue)
            edgeQueue.append(edge)
            vertexQueue.add(toVertex)

        for sv in vertexQueue:
            for v in sv.getVertices():
                self.addVertex(v)

        for edge in edgeQueue:
            vertex1 = edge.getVertex1()
            vertex2 = edge.getVertex2()
            self.addEdge(vertex1, vertex2, edge)

        for sv in self.m_inputGraph.getVertices():
            c     = sv.getComponent()
            edges = c.getEdges()

            for edge in edges:
                vertex1 = edge.getVertex1()
                vertex2 = edge.getVertex2()
                self.addEdge(vertex1, vertex2, edge)

    def getEdgeWithMinWeight(self, available):
        fromVertex = None
        toVertex   = None
        edge       = None
        dist       = float('inf')

        for v in available:
            adjList     = self.m_inputGraph.adjacencyList(v)
            adjVertices = adjList.getAdjacentVertices()

            for adjacentV in adjVertices:
                e = adjList.getEdgeWithSmallestWeight(adjacentV)

                if e.getWeight() < dist and adjacentV not in available:
                    fromVertex = v
                    toVertex   = adjacentV
                    edge       = e
                    dist       = e.getWeight()

        return fromVertex, toVertex, edge

    @staticmethod
    def getEmptyMST():
        return SuperMinimalSpaningTree()