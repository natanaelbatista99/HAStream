class Node:
    s_label = 0

    def __init__(self, c):
        self.m_vertices = set(c)
        self.m_children = []
        self.m_delta = True
        self.m_label = Node.s_label
        Node.s_label += 1
        self.m_parent = None
        self.m_scaleValue = 0
        

    def computeStability(self) -> float:
        if self.m_parent is None:
            return float('nan')

        eps_max = self.m_parent.m_scaleValue
        eps_min = self.m_scaleValue        
        
        if eps_max == 0:
            eps_max = 0.0000000001
        if eps_min == 0:
            eps_min = 0.0000000001
        
        self.m_stability = len(self.m_vertices) * ((1 / eps_min) - (1 / eps_max))

        return self.m_stability

    def addChild(self, child: "Node"):
        self.m_children.append(child)

    def getChildren(self):
        return self.m_children

    def setParent(self, parent):
        self.m_parent = parent

    def getParent(self):
        return self.m_parent

    def setScaleValue(self, scaleValue):
        self.m_scaleValue = scaleValue

    def getScaleValue(self):
        return self.m_scaleValue

    def getVertices(self):
        return self.m_vertices

    def setDelta(self):
        self.m_delta = True

    def resetDelta(self):
        self.m_delta = False

    def isDiscarded(self):
        return not self.m_delta

    def getStability(self) -> float:
        return self.m_stability

    def getPropagatedStability(self) -> float:
        return self.m_propagatedStability

    def setPropagatedStability(self, stability):
        self.m_propagatedStability = stability

    @staticmethod
    def resetStaticLabelCounter():
        Node.s_label = 0

    #def __str__(self):
    #    return self.getDescription()

    def getDescription(self):
        return f'N={len(self.m_vertices)},SV={self.m_scaleValue},SC={self.m_stability}'

    def getOutputDescription(self):
        return f'{len(self.m_vertices)},{self.m_scaleValue},{self.m_stability}'

    def getGraphVizNodeString(self):
        return f'node{self.m_label}'

    def getGraphVizEdgeLabelString(self):
        return f'[label="{self.m_scaleValue}"];'

    def getGraphVizString(self):
        return f'{self.getGraphVizNodeString()} [label="Num={len(self.m_vertices)}[SV,SC,D]:{{{self.m_scaleValue}; {self.m_stability}; {self.m_delta}}}""];'

    def setVertices(self, vertices ):
        self.m_vertices = set(vertices)