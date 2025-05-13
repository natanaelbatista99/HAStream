from .node import Node
from .edge import Edge
from .minimal_spaning_tree import MinimalSpaningTree
from .dendrogram_component import DendrogramComponent

class Dendrogram:
    def __init__(self, mst: MinimalSpaningTree, min_cluster_size: int, timestamp):        
        assert len(mst.getVertices()) > 0
        Node.resetStaticLabelCounter()

        self.m_components     = []
        self.m_minClusterSize = min_cluster_size
        first                 = None
        it                    = iter(mst.getVertices())
        self.timestamp        = timestamp
        
        if next(it):
            first = next(it)

        assert first is not None

        self.m_mstCopy = DendrogramComponent(first, mst, True)
        
        self.m_root = Node(self.m_mstCopy.getVertices())
        
        self.spurious_1 = 0
        self.spurious_gr2 = 0
        
        self.m_mstCopy.setNodeRepresentitive(self.m_root)
        self.m_components.append(self.m_mstCopy)

    def build(self):
        self.experimental_build()

    def compare(self, n1: Node):
        return n1.getScaleValue()

    def clusterSelection(self):
        selection = []

        # Step 1
        leaves = self.getLeaves(self.m_root)
        
        for leaf in leaves:
            leaf.setPropagatedStability(leaf.computeStability())

        # Special case
        if len(leaves) == 1 and leaves[0] == self.m_root:
            selection.append(self.m_root)
            return selection

        queue = []
        for leaf in leaves:
            if leaf.getParent() is not None and leaf.getParent() not in queue:
                queue.append(leaf.getParent())
        
        queue.sort(key=self.compare)

        # Step 2
        while queue and queue[0] != self.m_root:
            current = queue[0]
            current_stability = current.computeStability()
            s = sum(child.getPropagatedStability() for child in current.getChildren())
            if current_stability < s:
                current.setPropagatedStability(s)
                current.resetDelta()
            else:
                current.setPropagatedStability(current_stability)
            queue.remove(current)
            if current.getParent() not in queue and current.getParent() is not None:
                queue.append(current.getParent())
            queue.sort(key=self.compare)

        # get clustering selection
        selection_queue = self.m_root.getChildren().copy()
        self.m_root.resetDelta()

        while selection_queue:
            current = selection_queue.pop(0)
            if not current.isDiscarded():
                selection.append(current)
            else:
                selection_queue.extend(current.getChildren())

        return selection

    @staticmethod
    def getLeaves(node: Node):
        res = []
        queue = [node]

        while queue:
            n = queue.pop(0)

            if len(n.getChildren()) > 0:
                queue.extend(n.getChildren())
            elif len(n.getChildren()) == 0:
                res.append(n)
            #queue.pop(0)

        return res
    
    def experimental_build(self):
    
        # Get set of edges with the highest weight
        
        next = self.m_mstCopy.getNextSetOfHeighestWeightedEdges()

        # return if no edge available
        if next is None:
            return

        # repeat until all edges are processed
        while next is not None:
                        
            # copy edges into "queue"
            highestWeighted = []
            highestWeighted.extend(next)

            # Mapping of a component onto it's subcomponents, resulting from splitting
            splittingCandidates = {}

            # search components which contains one of the edges which the highest weight
            for edge in highestWeighted:
                i = 0
                while i < len(self.m_components):
                    current = self.m_components[i]

                    if current.containsEdge2(edge):
                        tmp = [current]
                        splittingCandidates[current] = tmp

                        self.m_components.pop(i)
                    else:
                        i += 1

            # Split these components
            for current in splittingCandidates.keys():  # Nodes
                if len(highestWeighted) == 0:
                    break

                currentNode = current.getNode()  # get the DendrogramComponent node to access the internal DBs
                
                highest = highestWeighted[0].getWeight()
                if isinstance(highest, Edge):
                    highest = (highestWeighted[0].getWeight()).getWeight()
                    
                
                current.getNode().setScaleValue(highest)  # epsilon
        
                subComponents = splittingCandidates[current]  # get TMP

                # Info: call by reference with "subComponent".
                # Effect: After calling splitting(), the subComponent List contains the subcomponents
                # which are created by removing the edges from the whole component
                toRemove = self.splitting(subComponents, highestWeighted)

                for item in toRemove:
                    highestWeighted.remove(item)

                spuriousList = []

                # Computing the Matrix Dh for HAI
                # computingMatrixDhHAI(numberDB, current, splittingCandidates.get(current));
                for c in splittingCandidates[current]:  # scrolls through the list of splitting Components (HAI)
                    numPoints = 0.0
                    count     = 0

                    for v in c.getVertices():
                        numPoints += v.getMicroCluster().getWeight(self.timestamp)
                        count     += 1

                    if numPoints >= self.m_minClusterSize or count >= self.m_minClusterSize:
                        spuriousList.append(c)

                if len(spuriousList) == 1:
                    self.spurious_1 += 1

                    # cluster has shrunk
                    replacementComponent = spuriousList.pop(0)

                    replacementComponent.setNodeRepresentitive(currentNode)

                    assert len(spuriousList) == 0

                    # add component to component list for further processing
                    self.m_components.append(replacementComponent)

                elif len(spuriousList) > 1:
                    
                    self.spurious_gr2 += 1

                    for c in spuriousList:
                        # generate new child node with currentNode as parent node
                        child = Node(c.getVertices())

                        child.setParent(currentNode)

                        # add child to parent
                        currentNode.addChild(child)
                        c.setNodeRepresentitive(child)

                        # add new components to component list for further processing
                        self.m_components.append(c)
                        
                        child.setScaleValue(highest)

            # update set of heighest edges
            next = self.m_mstCopy.getNextSetOfHeighestWeightedEdges()

    def splitting(self, c, edges):
        to_remove = []
        for edge in edges:
            i = 0
            while i < len(c):
                current = c[i]
                if current.containsEdge2(edge):
                    to_remove.append(edge)
                    v1, v2 = edge.getVertex1(), edge.getVertex2()
                    if v1 == v2:
                        current.removeEdge(edge)
                    else:
                        c.pop(i)
                        c.extend(current.splitComponent(edge))
                    break
                else:
                    i += 1
        return to_remove