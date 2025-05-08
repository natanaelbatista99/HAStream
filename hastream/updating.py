
from .micro_cluster import SuperVertex, Vertex
from .neighbour import Neighbour
from .component import Component
from .edge import Edge
from .mutual_reachability_graph import MutualReachabilityGraph
from .minimal_spaning_tree import MinimalSpaningTree
from .super_complete_graph import SuperCompleteGraph
from .super_minimal_spaning_tree import SuperMinimalSpaningTree

class Updating:
    def __init__(self, mrg: MutualReachabilityGraph, mst : MinimalSpaningTree):
        self.m_mrg = mrg
        self.m_mst = mst
        self.m_globalReplacementEdge = None
    
    def getMST(self):
        return self.m_mst
    
    def getMRG(self):
        return self.m_mrg
    
    def insert(self, mc):
        # Create new vertex for the new microcluster and insert it to the MRG
        insert = Vertex(mc)

        # Update the "adjacency matrix" of the mutual reachability graph
        # Furthermore generate candidates whose core-distance has changed and update them
        updatedObjects = self.computeAndCheckCoreDistance(insert, self.m_mrg.getVertices(), self.m_mrg.getMinPts())

        # Edge insertion i.e. edge's weight has decreased
        vertices = self.m_mrg.getVertices()
        # Update the corresponding row in the adjacency matrix
        for w in updatedObjects:
            for adj in self.m_mrg.adjacencyList(w).keys():
                max = self.m_mrg.getMutualReachabilityDistance(w, adj)
                if w != adj:
                    self.m_mrg.getEdge(w, adj).setEdgeWeight(max)

            # Fake vertex
            self.edgeInsertionMST(w)

        # Update the Mutual Reachability Graph, i.e. add new Vertex and the corresponding edges
        self.m_mrg.addVertex(insert)
        self.updateMRG_Ins(insert)

        # Vertex insertion into MST
        self.vertexInsertionMST(insert)
        return self.m_mst
    
    def computeAndCheckCoreDistance(self, vertex, vertices, minPts):
        vertexList = [vertex]
        candidateSet = []
        neighbours = []
        
        
        self.computeNeighbourhoodAndCandidates(vertex, neighbours, candidateSet, vertexList, minPts)
        neighbours.sort(key=lambda n: n.getDistance(), reverse = False)
        self.computeNeighbourhoodAndCandidates(vertex, neighbours, candidateSet, vertices, minPts)
        neighbours.sort(key=lambda n: n.getDistance(), reverse = False)

        coreDist = neighbours[len(neighbours) - 1]
        vertex.setCoreDistance(coreDist)

        i = 0
        while i < len(candidateSet):            
            candidate = candidateSet[i]
            neighbours = []
            self.computeNeighbourhoodAndCandidates(candidate, neighbours, None, vertexList, minPts)
            neighbours.sort(key=lambda n: n.getDistance(), reverse = False)
            self.computeNeighbourhoodAndCandidates(candidate, neighbours, None, vertices, minPts)
            neighbours.sort(key=lambda n: n.getDistance(), reverse = False)

            coreDist = neighbours[len(neighbours) - 1]
            if coreDist.getDistance() < candidate.getCoreDistance():
                candidate.setCoreDistance(coreDist)
                i += 1
            else:
                del candidateSet[i]

        return candidateSet
    
    def computeNeighbourhoodAndCandidates(self, vertex, lista, candidateSet, vertices, minPts):
        k = minPts - 1
        for v in vertices:
            dist = vertex.getDistance(v)
            if candidateSet is not None and dist < v.getCoreDistance():
                candidateSet.append(v)

            if len(lista) < minPts:
                lista.append(Neighbour(v, dist))
            else:
                kth = lista[k]
                if dist < kth.getDistance():
                    lista.append(Neighbour(v, dist))
                    if kth.getDistance() != lista[k].getDistance():
                        for last in range(len(lista) - 1, k, -1):
                            del lista[last]
    
    def edgeInsertionMST(self, w):
        # Generate the fake vertex to insert
        z = Vertex(None, -1)
        self.m_mrg.addVertex(z)
        # Create fake vertex with edges with the weights from MRG
        edge = None
        assert len(self.m_mst.getVertices()) == len(self.m_mrg.getVertices()) - 1
        for v in self.m_mst.getVertices():
            if v == w:
                edge = Edge(z, v, -1)
            else:
                edge = Edge(z, v, self.m_mrg.getEdge(w, v).getWeight())

            assert edge is not None
            self.m_mrg.addEdge(z, v, edge)

        newMSTedges = []
        self.m_globalReplacementEdge = None

        # Get a random vertex to represent the root of the MST
        first = None
        iterator = iter(self.m_mst)
        if iterator.hasNext():
            first = iterator.next()
            if first == w and iterator.hasNext():
                first = iterator.next()
            else:
                # This can only happen when the MRG was empty and a vertex was added.
                # Since that vertex is the only existing vertex in the MRG, it represents the MST
                # TODO: Single insertion of vertex in empty MST
                pass

        assert first != w

        for v in self.m_mrg.getVertices():
            v.resetVisited()

        self.updateMST_Ins(first, z, newMSTedges)
        newMSTedges.append(self.m_globalReplacementEdge)

        assert len(newMSTedges) == len(self.m_mst.getVertices())

        # Update MST adjacency lists
        self.m_mst.clearAdjacencyLists()

        correctMSTedges = []
        for e in newMSTedges:
            vertex1 = e.getVertex1()
            vertex2 = e.getVertex2()
            if vertex1 != z and vertex2 != z:
                self.m_mst.addEdge(vertex1, vertex2, e)
                correctMSTedges.append(e)
            else:
                v = e.getAdjacentVertex(z)
                if v == w:
                    # Do nothing --> remove the edge to the fake vertex
                    pass
                else:
                    replacement = self.m_mrg.getEdge(w, v)
                    assert replacement.getWeight() == e.getWeight()
                    self.m_mst.addEdge(w, v, replacement)
                    correctMSTedges.append(replacement)

        assert len(correctMSTedges) == len(self.m_mst.getVertices()) - 1

        # Remove fake node from m_mrg
        for v in self.m_mrg.getVertices():
            self.m_mrg.removeEdge(z, v)
        self.m_mrg.removeVertex(z)

        assert not self.m_mrg.containsVertex(z)
        assert not self.m_mst.containsVertex(z)
    
    def updateMST_Ins(self, r, z, edges):
        r.setVisited()
        m = self.m_mrg.getEdge(z, r)  # z.getEdgeTo(r)
        adjacentVertices = self.m_mst.adjacencyList(r).keys()
        for w in adjacentVertices:
            if not w.visited():
                self.updateMST_Ins(w, z, edges)
                wr = self.m_mrg.getEdge(w, r)  # w.getEdgeTo(r)
                k = None
                h = None
                aux = 0
                aux3 = 0
                
                if type(self.m_globalReplacementEdge.getWeight()) == float:
                    aux = self.m_globalReplacementEdge.getWeight()
                else:
                    aux = self.m_globalReplacementEdge.getWeight().getWeight()
                    
                if type(wr.getWeight()) == float:
                    aux3 = wr.getWeight()
                else:
                    aux3 = wr.getWeight().getWeight()
                
                if aux > aux3:
                    k = self.m_globalReplacementEdge
                    h = wr
                else:
                    k = wr
                    h = self.m_globalReplacementEdge
                edges.append(h)
                
                
                
                if type(k.getWeight()) == float:
                    aux1 = k.getWeight()
                else:
                    aux1 = k.getWeight().getWeight()
                
                if type(m.getWeight()) == float:
                    aux2 = m.getWeight()
                else:
                    aux2 = m.getWeight().getWeight()
                    
                if aux1 < aux2:
                    m = k
        self.m_globalReplacementEdge = m

    def updateMRG_Ins(self, vertex):
        vertices = self.m_mrg.getVertices()

        for v in vertices:
            # No self loops
            if vertex != v:
                max = self.m_mrg.getMutualReachabilityDistance(vertex, v)
                edge = Edge(vertex, v, max)
                self.m_mrg.addEdge(vertex, v, edge)
                self.m_mrg.addEdge(v, vertex, edge)

        assert self.m_mrg.controlNumEdgesCompleteGraph()
    
    def vertexInsertionMST(self, insert):
        newMSTedges = []
        self.m_globalReplacementEdge = None

        first = None
        iterator = iter(self.m_mst)
        if next(iterator):
            first = next(iterator)
            if first == insert and iterator.hasNext():
                first = iterator.next()
            else:
                # TODO: Handle the case when the MRG was empty and a vertex was added
                pass
        assert first != insert

        for v in self.m_mrg.getVertices():
            v.resetVisited()

        self.updateMST_Ins(first, insert, newMSTedges)
        newMSTedges.append(self.m_globalReplacementEdge)

        assert len(newMSTedges) == len(self.m_mst.getVertices())

        self.m_mst.clearAdjacencyLists()
        self.m_mst.addVertex(insert)

        for e in newMSTedges:
            vertex1 = e.getVertex1()
            vertex2 = e.getVertex2()
            self.m_mst.addEdge(vertex1, vertex2, e)
    
    def getAffectedNeighborhood2(self, query, vertices):
        neighbors = set()
        dist = -1.0
        for v in vertices:
            dist = v.getDistance(query)
            if v.getCoreDistance() >= dist:
                neighbors.add(v)
        return neighbors
    def getAffectedNeighborhood(self, vertex):
        affectedNeighbours = set()

        affectedNeighbours.update(self.getAffectedNeighborhood2(vertex, self.m_mrg.getVertices()))
        
        if vertex in affectedNeighbours:
            affectedNeighbours.remove(vertex)
            print(vertex)

        queue = []
        queue.extend(affectedNeighbours)

        while queue:
            first = queue.pop(0)

            neighbours = self.getAffectedNeighborhood2(first, self.m_mrg.getVertices())
            neighbours.remove(vertex)

            for v in neighbours:
                if v not in affectedNeighbours:
                    affectedNeighbours.add(v)
                    queue.append(v)

        assert vertex not in affectedNeighbours

        return affectedNeighbours
                                  
    def delete(self, mc):
        assert mc.getVertexRepresentative() != None, "Vertex reference is missing"
        toDelete = mc.getVertexRepresentative()

        if len(self.m_mrg.getVertices()) - 1 <= self.m_mrg.getMinPts():
            self.m_mst = None
            return None

        affectedNeighbours = self.getAffectedNeighborhood(toDelete)

        self.updateMRG_Del(toDelete)
        for affected in affectedNeighbours:
            self.updateCoreDistance(affected, self.m_mrg.getVertices(), self.m_mrg.getMinPts())

        for affected in affectedNeighbours:
            edges = self.m_mrg.getAdjacentEdges(affected)
            for e in edges:
                adjacent = e.getAdjacentVertex(affected)
                max_val = self.m_mrg.getMutualReachabilityDistance(affected, adjacent)
                if e.getWeight() < max_val:
                    e.setEdgeWeight(max_val)

        for w in affectedNeighbours:
            for adj in self.m_mrg.adjacencyList(w).keys():
                max_val = self.m_mrg.getMutualReachabilityDistance(w, adj)
                if w != adj:
                    self.m_mrg.getEdge(w, adj).setEdgeWeight(max_val)

        mst_components = self.removeFromMST_Del(toDelete, affectedNeighbours)

        superVertices = set()
        for c in mst_components:
            superVertices.add(SuperVertex(c))

        assert len(mst_components) == len(superVertices)

        self.m_mst = self.updateMST_Del(superVertices)

        return self.m_mst
                                  
    def updateMRG_Del(self, v):
        toRemove = set()
        toRemove.update(self.m_mrg.adjacencyList(v).values())
        for edge in toRemove:
            self.m_mrg.removeEdge2(edge)
        self.m_mrg.removeVertex(v)

    def updateCoreDistance(self, vertex, vertices, minPts):
        lista = []

        dist = -1.0
        for v in vertices:
            dist = vertex.getDistance(v)
            lista.append(Neighbour(v, dist))

        assert lista.size() == len(vertices)

        coreDist = lista[minPts - 1]
        vertex.setCoreDistance(coreDist)
    
    def removeFromMST_Del(self, toDelete, affectedNeighbours):
        components = set()
        startVertices = set()

        toRemove = set()
        print(self.m_mst.getAdjacentEdges(toDelete).values())
        toRemove.update(self.m_mst.getAdjacentEdges(toDelete).values())

        for edge in toRemove:
            self.m_mst.removeEdge2(edge)
            startVertices.add(edge.getAdjacentVertex(toDelete))
        self.m_mst.removeVertex(toDelete)

        for v in affectedNeighbours:
            toRemove.clear()
            toRemove.update(self.m_mst.getAdjacentEdges(v))

            adjVertices = set()
            for edge in toRemove:
                adj = edge.getAdjacentVertex(v)
                adjVertices.add(adj)
                self.m_mst.removeEdge2(edge)

            for adj in adjVertices:
                startVertices.add(adj)

            startVertices.add(v)

        for startVertex in startVertices:
            newComponent = True
            for c in components:
                if c.containsVertex(startVertex):
                    newComponent = False
                    break
            if newComponent:
                debug = Component(startVertex, self.m_mst, True)
                components.add(debug)

        self.assertNumVertices(components, self.m_mst.numVertices())

        return components

    def assertNumVertices(self, components, numVertices):
        sum_numVertices = 0
        pairwiseDifferent = True
        for c in components:
            sum_numVertices += c.numVertices()
            for other in components:
                if c != other:
                    pairwiseDifferent &= not c.compareByVertices(other)

        return pairwiseDifferent and sum_numVertices == numVertices
    
    def updateMST_Del(self, superVertices):
        scgraph = SuperCompleteGraph(superVertices, self.m_mrg)
        scgraph.buildGraph()
        new_mst = SuperMinimalSpaningTree(scgraph)
        new_mst.buildGraph()
        return new_mst