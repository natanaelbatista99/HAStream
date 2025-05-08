from .micro_cluster import Vertex

class Edge():

    def __init__(self, v1 : Vertex, v2 : Vertex, dist : float):
        self.m_vertex1 = v1
        self.m_vertex2 = v2
        self.m_weight  = dist

    def compareTo(self, other):
        return self.m_weight < other.m_weight

    def getWeight(self):
        return self.m_weight

    def getVertex1(self):
        return self.m_vertex1

    def getVertex2(self):
        return self.m_vertex2

    def getAdjacentVertex(self, v):
        if v != self.m_vertex1:
            return self.m_vertex1
        else:
            return self.m_vertex2

    def setVertex1(self, v : Vertex):
        self.m_vertex1 = v

    def setVertex2(self, v : Vertex):
        self.m_vertex2 = v

    def setVertices(self, v1, v2):
        self.m_vertex1 = v1
        self.m_vertex2 = v2

    def graphVizString(self):
        return "M.add_edge(\"" + self.m_vertex1.getGraphVizVertexString() + "\",\"" + self.m_vertex2.getGraphVizVertexString() + "\",weight= " + str(self.m_weight) +")"

    def setEdgeWeight(self, weight):
        self.m_weight = weight