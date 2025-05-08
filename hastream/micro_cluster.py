import math

from abc import ABCMeta

class SuperVertex():
    s_idCounterSuperVertex = 0

    def __init__(self, c):
        self.m_id        = SuperVertex.s_idCounterSuperVertex
        SuperVertex.s_idCounterSuperVertex += 1
        self.m_component = c
        self.m_vertices  = set(self.m_component.getVertices())
        self.m_visited   = False


    def getVertices(self):
        return self.m_vertices

    def visited(self) -> bool:
        return self.m_visited

    def setVisited(self):
        self.m_visited = True

    def resetVisited(self):
        self.m_visited = False

    def getID(self):
        return self.m_id

    def compareID(self, other: 'SuperVertex'):
        return self.m_id == other.m_id

    def isSuperVertex(self):
        return True

    def containsVertex(self, v):
        return v in self.m_vertices

    def getComponent(self):
        return self.m_component
    
class Vertex():
    
    s_idCounter = 0

    def __init__(self, mc, timestamp, id=None):
        self.m_id          = id if id is not None else Vertex.s_idCounter
        Vertex.s_idCounter += 1
        self.m_mc          = mc
        self.timestamp     = timestamp
        
        if self.m_mc is not None:
            self.m_mc.setVertexRepresentative(self)
            
        self.m_visited            = False
        self.m_coreDistanceObject = None
        self.m_lrd                = -1
        self.m_coreDist           = 0
        
    def getMicroCluster(self):
        return self.m_mc

    def getCoreDistance(self):
        if self.m_coreDist == 0:
            return -1
        return self.m_coreDist

    def setCoreDist(self, coreDistValue):
        self.m_coreDist = coreDistValue

    def setCoreDistance(self, coreDistObj):
        self.m_coreDistanceObject = coreDistObj

    def String(self):
        return f"({self.m_mc.getCenter()})"

    def getGraphVizVertexString(self):
        return f"vertex{self.m_id}"

    def getGraphVizString(self):
        return f"{self.getGraphVizVertexString()} [label='{self}';cdist={self.getCoreDistance()}]"

    def getDistanceToVertex(self, other):
        return self.m_mc.getCenterDistance(other.getMicroCluster())
    '''
    def getDistanceRep(self, vertex):
        x1 = self.distance(self.m_mc.getCenter(), vertex.getMicroCluster().getCenter())
        
        return x1
    '''
    def getDistance(self, vertex):
        if self.m_mc.getStaticCenter() is None or vertex.getMicroCluster().getStaticCenter() is None:
            return self.getDistanceToVertex(vertex)
        
        return self.distance(self.m_mc.getCenter(self.timestamp), vertex.getMicroCluster().getCenter(self.timestamp))

    def distance(self, v1, v2):
        distance = 0
        for i in range(len(v1)):
            d = v1[i] - v2[i]
            distance += d * d
        return math.sqrt(distance)

    def setCoreDistChanged(self):
        self.m_changeCoreDist = True

    def resetCoreDistChanged(self):
        self.m_changeCoreDist = False

    def hasCoreDistChanged(self):
        return self.m_changeCoreDist

    def visited(self):
        return self.m_visited

    def setVisited(self):
        self.m_visited = True

    def resetVisited(self):
        self.m_visited = False

    def getID(self):
        return self.m_id

    def compareID(self,  other: "Vertex"):
        return self.m_id == other.m_id

class MicroCluster(metaclass=ABCMeta):

    s_idCounter = 0
    
    def __init__(self, x, timestamp, decaying_factor):

        self.x = x

        self.db_id           = MicroCluster.s_idCounter        
        self.last_edit_time  = timestamp
        self.creation_time   = timestamp
        self.decaying_factor = decaying_factor

        self.N              = 1
        self.linear_sum     = x
        self.squared_sum    = {i: (x_val * x_val) for i, x_val in x.items()}        
        self.m_staticCenter = [];

    def getID(self):
        return self.db_id

    def setID(self, id):
        self.db_id = id
    
    def calc_cf1(self, fading_function):
        cf1 = []        
        for key in self.linear_sum.keys():
            val_ls = self.linear_sum[key]
            cf1.append(fading_function * val_ls)
        return cf1
    
    def calc_cf2(self, fading_function):
        cf2 = []        
        for key in self.squared_sum.keys():
            val_ss = self.squared_sum[key]
            cf2.append(fading_function * val_ss)
        return cf2

    def calc_weight(self):
        return self._weight()
    
    def getN(self):
        return self.N

    def getWeight(self, timestamp):
        return self.N * self.fading_function(timestamp - self.last_edit_time)
        
    def getCenter(self, timestamp):
        ff = self.fading_function(timestamp - self.last_edit_time)
        weight = self.getWeight(timestamp)
        center = {key: (ff * val) / weight for key, val in self.linear_sum.items()}
        
        return center
    '''
    def getRadius(self, timestamp):        
        x1  = 0
        x2  = 0
        res = 0
        
        ff     = self.fading_function(timestamp - self.last_edit_time)
        weight = self.getWeight(timestamp)
        
        for key in self.linear_sum.keys():
            val_ls = self.linear_sum[key]
            val_ss = self.squared_sum[key]
            
            x1  = 2 * (val_ss * ff) * weight
            x2  = 2 * (val_ls * ff)**2
            tmp = (x1 - x2)
                        
            if tmp <= 0.0:
                tmp = 1/10 * 1/10
            
            diff = (tmp / (weight * (weight - 1))) if (weight * (weight - 1)) > 0.0 else 0.1
            
            res += math.sqrt(diff) if diff > 0 else 0

        return (res / len(self.linear_sum)) * 1.5  #redius factor
        #return res
    '''
    def getRadius(self, timestamp):        
        ff  = self.fading_function(timestamp - self.last_edit_time)
        w   = self.getWeight(timestamp)        
        cf1 = self.calc_cf1(ff)
        cf2 = self.calc_cf2(ff)        
        res = 0      
        
        for i in range(len(self.linear_sum)):
            x1 = cf2[i] / w
            x2 = math.pow(cf1[i]/w , 2)
            
            tmp = x1 - x2
            
            res += math.sqrt(tmp) if tmp > 0 else (1/10 * 1/10)
            
        #1.8            
        return (res / len(cf1)) * 1.8
        
    def add(self, x):        
        self.N += 1
        
        for key, val in x.items():
            self.linear_sum[key]  += val
            self.squared_sum[key] += val * val
            
    def insert(self, x, timestamp):
        if(self.last_edit_time != timestamp):
            self.fade(timestamp)
        
        self.last_edit_time = timestamp
        
        self.add(x)
    
    def fade(self, timestamp):
        ff = self.fading_function(timestamp - self.last_edit_time)
        
        self.N *= ff
        
        for key, val in self.linear_sum.items():            
            self.linear_sum[key]  *= ff
            self.squared_sum[key] *= ff
        
    def merge(self, cluster):
        self.N += cluster.N
        
        for key in cluster.linear_sum.keys():
            try:
                self.linear_sum[key]  += cluster.linear_sum[key]
                self.squared_sum[key] += cluster.squared_sum[key]
            except KeyError:
                self.linear_sum[key]  = cluster.linear_sum[key]
                self.squared_sum[key] = cluster.squared_sum[key]
                
        if self.last_edit_time < cluster.creation_time:
            self.last_edit_time = cluster.creation_time
            
    def fading_function(self, time):
        return 2 ** (-self.decaying_factor * time)
    
    def setVertexRepresentative(self, v : Vertex): 
        self.m_vertexRepresentative = v

    def getVertexRepresentative(self):
        return self.m_vertexRepresentative
    
    def getStaticCenter(self):
        return self.m_staticCenter

    def setStaticCenter(self, timestamp):
        self.m_staticCenter = self.getCenter(timestamp).copy()
        
    def hasCenterChanged(self,percentage, refEpsilon, timestamp):
        distance = self.getCenterDistance(self.m_staticCenter, timestamp)
        if(distance > percentage * refEpsilon):
            return True
        return False
    def getCenterDistance(self, instance, timestamp):
        distance = 0.0
        center = self.getCenter(timestamp)
        for i in range(len(instance)):
            d = center[i] - instance[i]
            distance += d * d
        return math.sqrt(distance)