import numpy as np
import random as rand
from scipy.io import arff

class ant:
    def __init__(self):
        self.isloaded = False
        self.loaded_object = None
        self.reactor_num = 0
        
    def pick_object(self, object_to_pick):
        if (self.loaded_object != None):
            self.loaded_object = object_to_pick
            self.isloaded = True
    
    def put_object(self):
        tmp = self.loaded_object
        self.loaded_object = None
        self.isloaded = False
        return tmp
        
    def move_to_reactor(self, num_reactor):
        self.reactor_num = num_reactor
    

class ant_clusterer:
    def __init__(self, data, num_iterations, kp, kc, alpha, number_ants, alpha1, s ):
        self.data = data
        self.num_iterations = num_iterations
        self.kp = kp
        self.kc = kc
        self.alpha = alpha
        self.number_ants = number_ants
        self.alpha1 = alpha1
        self.s = s
        self.reactors = []
        self.ants = []
        self.start_reactor_index = 0
        #self.ant_reactor_index = []
        
    def initialize(self):
        num_data = self.data.size
        print(num_data)
        # random amount of reactor K <= number of data
        k = rand.randint(1, num_data/10)
        print(k)
        # create reactors
        for i in range(0,k):
            self.reactors.append([]) #= np.ndarray((k), int)
        print(len(self.reactors))
        
        # assign data at random to reactors
        for x in data:
            k = rand.randint(1, len(self.reactors) - 1)
            self.reactors[k].append(x)
            
        #create ants
        for i in range(0, self.number_ants):
            tmp = ant()
            self.ants.append(tmp)
            
        #choose reactor to start with and init all ants
        self.start_reactor_index = rand.randint(1, len(self.reactors) - 1)
        for tmp in self.ants:
            tmp.reactor_num = self.start_reactor_index
        
    def iterations(self):
        print(self.start_reactor_index)
        
        for i in range(0, self.num_iterations):
            for tmp in self.ants:
                #if unloaeded check number of objects
                if tmp.isloaded == False:
                    # if more than one take most dissimilar
                    if (len(self.reactors[tmp.reactor_num]) > 1):
                        #print(self.reactors[tmp.reactor_num])
                        similarity_list = []
                        for object_index in range(len(self.reactors[tmp.reactor_num])):
                            sim = self.average_similarity(tmp.reactor_num, object_index)
                            similarity_list.append([sim, object_index])
                        similarity_list.sort()
                        # most dissimilar object is now first
                        
                        # calculate probability to pick up
                        prob = self.kp / (self.kp + similarity_list[0][0])
                        prob = prob * prob
                        ran = rand.random()
                        
                        if(ran < prob):
                            print("picked up")
                            tmp.pick_object(self.reactors[tmp.reactor_num][similarity_list[0][1]])
                            del self.reactors[tmp.reactor_num][similarity_list[0][1]]
                            
                        print("similarity",similarity_list[0], "rest length: ", len(self.reactors[tmp.reactor_num]))
                            
                    #if only one object then take it
                    if (len(self.reactors[tmp.reactor_num]) == 1):
                        tmp.pick_object(self.reactors[tmp.reactor_num][0])
                # for all ants 
                # at reactor with only one object pick it
                # if they have no object loaded pick the one with lowest similarity with a probability
                # if they are loaded drop it and pick the one with lowest similarity
                # and move to other reactor
        
    
# calculate average similarity
    def average_similarity(self, reactor_num, object_index):
        reactor = self.reactors[reactor_num]
        object1 = reactor[object_index]
        dist = 0
        summe = 0
        for object2 in reactor:
            if(object1 != object2):
                dist = self.distance(object1, object2) 
                #print("dist",dist)
                summe = summe + 1 - np.sqrt(dist / self.alpha)
        
        #print("sum",summe)
        similarity = 1/(len(reactor) - 1) * summe
        
        if(similarity < 0):
            similarity = 0
        
        return similarity
        
    def distance(self, object1, object2):
        distance = 0
        for i in range(0,len(object1) - 1):
            #print(object1[i],"-",object2[i], "=",object1[i]-object2[i])
            distance1dim = object1[i] - object2[i]
            distance = distance + distance1dim * distance1dim
        distance = np.sqrt(distance)
        return distance
    
    #number_of_data = data.size
    #init()
    #dataprojection()
    #pack_ants()
    #iteration()
    #lable_list = 0
    #return lable_list
    

########################### main ################################
data, meta = arff.loadarff('./Dataset/D31.arff')

#print("data: ")
#print(data)
#print("meta: ")
#print(meta)
#                      (data, num_iterations, kp, kc, alpha, number_ants, alpha1, s )
cluster = ant_clusterer(data, 1, 0.1, 0.15, 10, 20, 0.4, 3)
cluster.initialize()
cluster.iterations()