import numpy as np
import random as rand
import time
from scipy.io import arff

class ant:
    def __init__(self):
        self.isloaded = False
        self.loaded_object = None
        self.reactor_num = 0
        
    def pick_object(self, object_to_pick):
        if (self.loaded_object == None):
            self.loaded_object = object_to_pick
            self.isloaded = True
    
    def put_object(self):
        tmp = self.loaded_object
        self.loaded_object = None
        self.isloaded = False
        return tmp
        
    def get_load_state(self):
        return self.isloaded
        
    def move_to_reactor(self, num_reactor):
        self.reactor_num = num_reactor
        
    def print_state(self):
        print("isloaded", self.isloaded," object: ", self.loaded_object," reactor: ", self.reactor_num)


class reactor:
    def __init__(self, alpha):
        self.item_sim_list = [] #[sim, obj]
        self.has_changed = False
        self.has_center_changed = False
        self.alpha = alpha
        self.center = None
        
    def obj_average_similarity(self, object_index):
        object1 = self.item_sim_list[object_index][1]
        dist = 0
        summe = 0
        for object2_index in range(0,len(self.item_sim_list)):
            if(object_index != object2_index):
                dist = self.distance(object1, self.item_sim_list[object2_index][1]) 
                summe = summe + 1 - np.sqrt(dist / self.alpha)

        similarity = 1/(len(self.item_sim_list) - 1) * summe
        
        if(similarity < 0):
            similarity = 0
        
        self.item_sim_list[object_index][0] = similarity
        return similarity
        
    def distance(self, object1, object2):
        distance = 0
        for i in range(0,len(object1)):
            distance1dim = object1[i] - object2[i]
            distance = distance + distance1dim * distance1dim
        distance = np.sqrt(distance)
        return distance        
        
    def get_reactor_length(self):
        return len(self.item_sim_list)        
        
    def get_reactor_center(self):
        if (self.has_center_changed == True):
            self.center = self.item_sim_list[0][1]
            for n in range(1, len(self.item_sim_list)):
                self.center = self.center + self.item_sim_list[n][1]
            self.center = self.center / len(self.item_sim_list)
            self.has_center_changed = False
        return self.center
        
    def push_obj(self, obj):
        self.item_sim_list.append([0, obj])
        self.has_changed = True
        self.has_center_changed = True
        
    def pop_obj(self, obj_index):
        self.has_changed = True
        self.has_center_changed = True
        return self.item_sim_list.pop(obj_index)[1]
        
    #returns similarity and index in reactor
    def find_most_dissimilar(self):
        min_index = 0
        min_sim = 100
        # calulate only if item was added or removed          
        if(self.has_changed == True):            
            for object_index in range(0, len(self.item_sim_list)):
                sim = self.obj_average_similarity(object_index)
                if(sim < min_sim):
                    min_sim = sim
                    min_index = object_index
            self.has_changed = False
        # else search object with minimum similarity
        else:
            for object_index in range(0, len(self.item_sim_list)):
                if(self.item_sim_list[object_index][0] < min_sim):
                    min_sim = self.item_sim_list[object_index][0]
                    min_index = object_index
            
        return(min_sim, min_index)
    

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
        
        # create all data in numpy.array without last element
        new_data = []
        for datum in range(0,len(data)):
            new_data.append([])
            for element in range(0,len(data[datum]) - 1):
                new_data[datum].append(data[datum][element])
        
        self.data = np.array([np.array(datum) for datum in new_data])          
        
        # random amount of reactor K <= number of data
        k = rand.randint(1, num_data)
        print(k)        
        
        # create reactors
        for i in range(0, k):
            self.reactors.append([])
        print(len(self.reactors))
        
        # assign data at random to reactors
        for x in self.data:
            k = rand.randint(0, len(self.reactors) - 1)
            self.reactors[k].append(x)
            
        #create ants
        for i in range(0, self.number_ants):
            tmp = ant()
            self.ants.append(tmp)
            
        #choose reactor to start with and init all ants
        self.start_reactor_index = rand.randint(0, len(self.reactors) - 1)
        for tmp in self.ants:
            tmp.reactor_num = self.start_reactor_index
        
    def iterations(self):
        print(self.start_reactor_index)
        
        for i in range(0, self.num_iterations):
            for tmp in self.ants:
                #if unloaeded check number of objects
                if tmp.get_load_state() == False:
                    # if more than one take most dissimilar
                    if (len(self.reactors[tmp.reactor_num]) > 1):
                        # check if reactors can be combined
                        for reactor_index in range(0,len(self.reactors)):
                            if(reactor_index != tmp.reactor_num & len(self.reactors[reactor_index]) > 0):
                                reactor_sim = self.reactor_similarity(self.reactors[tmp.reactor_num], self.reactors[reactor_index])
                                #print("reactor_sim",reactor_sim)
                                
                                # calculate combine_probability
                                combine_prob = 0
                                if(reactor_sim >= self.kc):
                                    combine_prob = 1
                                else:
                                    combine_prob = 2 * reactor_sim
                                
                                # check if combine
                                if combine_prob > 0:
                                    ran = rand.random()
                                    if(ran < combine_prob):
                                        self.combine_reactors(tmp.reactor_num, reactor_index)
                                        
                                
                        # make similarity list
                        similarity_list = []
                        for object_index in range(0, len(self.reactors[tmp.reactor_num])):
                            sim = self.average_similarity(tmp.reactor_num, object_index)
                            similarity_list.append([sim, object_index])
                        similarity_list.sort()
                        # most dissimilar object is now first
                        
                        # calculate probability to pick up
                        prob = self.kp / (self.kp + similarity_list[0][0])
                        prob = prob * prob
                        ran = rand.random()
                        
                        if(ran < prob):
                            #print("picked up")
                            tmp.pick_object(self.reactors[tmp.reactor_num].pop(similarity_list[0][1]))
                            #del self.reactors[tmp.reactor_num][similarity_list[0][1]]
                            
                        #print("similarity",similarity_list[0], "rest length: ", len(self.reactors[tmp.reactor_num]))
                            
                    #if only one object then take it
                    if (len(self.reactors[tmp.reactor_num]) == 1):
                        tmp.pick_object(self.reactors[tmp.reactor_num].pop(0))
                        #del self.reactors[tmp.reactor_num][0]
                        #maybe destroy reactor cause no data is in and will be
                        #del self.reactors[tmp.reactor_num]
                  
                
                if tmp.isloaded == True:
                    # put only to reactor with more than one object
                    if(len(self.reactors[tmp.reactor_num]) > 1):
                        self.reactors[tmp.reactor_num].append(tmp.put_object())

                        # check if reactors can be combined
                        for reactor_index in range(0,len(self.reactors)):
                            if(reactor_index != tmp.reactor_num & len(self.reactors[reactor_index]) > 0):
                                reactor_sim = self.reactor_similarity(self.reactors[tmp.reactor_num], self.reactors[reactor_index])
                                #print("reactor_sim",reactor_sim)
                                
                                # calculate combine_probability
                                combine_prob = 0
                                if(reactor_sim >= self.kc):
                                    combine_prob = 1
                                else:
                                    combine_prob = 2 * reactor_sim
                                
                                # check if combine
                                if combine_prob > 0:
                                    ran = rand.random()
                                    if(ran < combine_prob):
                                        self.combine_reactors(tmp.reactor_num, reactor_index)
                                                
                        
                        # and pick most dissimilar with prob
                        similarity_list = []
                        for object_index in range(0, len(self.reactors[tmp.reactor_num])):
                            sim = self.average_similarity(tmp.reactor_num, object_index)
                            similarity_list.append([sim, object_index])
                        similarity_list.sort()
                        # most dissimilar object is now first
                        
                        # calculate probability to pick up
                        prob = self.kp / (self.kp + similarity_list[0][0])
                        prob = prob * prob
                        ran = rand.random()
                        
                        if(ran < prob):
                            #print("picked up")
                            #print(tmp.isloaded)
                            tmp.pick_object(self.reactors[tmp.reactor_num].pop(similarity_list[0][1]))
                            #print(tmp.isloaded)
                            #del self.reactors[tmp.reactor_num][similarity_list[0][1]]
                            
                        #print("similarity",similarity_list[0], "rest length: ", len(self.reactors[tmp.reactor_num]))
                
            # end for all ants => one Iteration done
            # delete all reactor with no data

            self.reactors = [react for react in self.reactors if len(react) != 0]                    
                
            # move ants to next reactor  
            for tmp in self.ants:
                ran = rand.randint(0, len(self.reactors) - 1)
                tmp.move_to_reactor(ran)                
                
            # debug message
#            print("iteratio",i)
#            print("num reactors", len(self.reactors))
#            data_amount = 0
#            for n in range(0, len(self.reactors) ):
#                data_amount = data_amount + len(self.reactors[n])
#                #print("iteration: ", i, " reactor ", n, "num Data: ", len(self.reactors[n]))
#            
#            
#            
#            
#            for tmp in self.ants:
#                #tmp.print_state()
#                if tmp.isloaded == True:
#                    data_amount = data_amount + 1
#            print("data_amount", data_amount)
        # end M Iterations
        for i in range(len(self.reactors)):
            print("reactor ",i , "size:", len(self.reactors[i])  )
            print(self.reactors[i])
        # after M Iterations all Ants with dataobject build one new reactor
        # if too much reactors combine some (done in every step)
        # Terminate if difference between two Iterations is low enough
        
    
# calculate average similarity
    def average_similarity(self, reactor_num, object_index):
        reactor = self.reactors[reactor_num]
        object1 = reactor[object_index]
        dist = 0
        summe = 0
        for object2_index in range(0,len(reactor)):
            if(object_index != object2_index):
                dist = self.distance(reactor[object_index], reactor[object2_index]) 
                #print("dist",dist)
                summe = summe + 1 - np.sqrt(dist / self.alpha)
        
        #print("sum",summe)
        similarity = 1/(len(reactor) - 1) * summe
        
        if(similarity < 0):
            similarity = 0
        
        return similarity
        
    def distance(self, object1, object2):
        distance = 0
        for i in range(0,len(object1)):
            distance1dim = object1[i] - object2[i]
            distance = distance + distance1dim * distance1dim
        distance = np.sqrt(distance)
        return distance
    
    def reactor_similarity(self, reactor1, reactor2):
        # find reactorcenters (mean value)

        xyz1 = reactor1[0]
        for n in range(1, len(reactor1)):
            xyz1 = xyz1 + reactor1[n]
        xyz1 = xyz1 / len(reactor1)     
        
        xyz2 = reactor2[0]
        for n in range(1, len(reactor2)):
            xyz2 = xyz2 + reactor2[n]
        xyz2 = xyz2 / len(reactor2) 

        # measure distance
        dist = self.distance(xyz1, xyz2)
                
        # calculate similarity
        sim = 1 - dist / self.alpha1
        return sim

    def combine_reactors(self, num_reactor1, num_reactor2):
        for i in range(0,len(self.reactors[num_reactor2])):
            self.reactors[num_reactor1].append(self.reactors[num_reactor2].pop())
    #number_of_data = data.size
    #init()
    #dataprojection()
    #pack_ants()
    #iteration()
    #lable_list = 0
    #return lable_list
    

########################### main ################################
data, meta = arff.loadarff('./Dataset/iris.arff')



#new_data = []
#for datum in range(0,len(data)):
#    new_data.append([])
#    for element in range(0,len(data[datum]) - 1):
#        new_data[datum].append(data[datum][element])
#        
#new_data = np.array([np.array(datum) for datum in new_data])        

start = time.clock()
#                      (data, num_iterations, kp, kc, alpha, number_ants, alpha1, s )
cluster = ant_clusterer(data, 500, 0.1, 0.4, 1.5, 20, 0.3, 3)
cluster.initialize()
cluster.iterations()

end = time.clock()
print("time needed", end - start)
#new_data = []
#for datum in range(0,len(data)):
#    new_data.append([])
#    for element in range(0,len(data[datum]) - 1):
#        new_data[datum].append(data[datum][element])
#        
#data = np.array([np.array(datum) for datum in new_data]) 
#
#react = reactor(1.5)
#
#for i in range(10):
#    print(data[i])
#    react.push_obj(data[i])
#    
#print(react.find_most_dissimilar())  
#print(react.get_reactor_center())  
#    
#for i in range(react.get_reactor_length()):
#    print(react.pop_obj(0))

