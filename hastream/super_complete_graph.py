from .super_abstract_graph import SuperAbstractGraph

class SuperCompleteGraph(SuperAbstractGraph):
    def __init__(self, superVertices, sourcegraph):
        super().__init__()
        self.m_supervertices = list(superVertices)
        self.m_sourcegraph   = sourcegraph

    def buildGraph(self):
        for i in range(len(self.m_supervertices)):
            sv_i = self.m_supervertices[i]

            if not self.containsVertex(sv_i):
                self.addVertex(sv_i)

            for j in range(i + 1, len(self.m_supervertices)):
                sv_j = self.m_supervertices[j]

                if not self.containsVertex(sv_j):
                    self.addVertex(sv_j)

                min_edge = None
                dist     = float('inf')

                for v in sv_i.getVertices():
                    for u in sv_j.getVertices():
                        e = self.m_sourcegraph.getEdge(v, u)
                        
                        w = 0
                        
                        if type(e.getWeight()) == float:
                            w = e.getWeight()
                        else:
                            w = e.getWeight().getWeight()

                        if w < dist:
                            min_edge = self.m_sourcegraph.getEdge(v, u)
                            dist     = e.getWeight()

                assert min_edge is not None
                self.addEdge(sv_i, sv_j, min_edge) 