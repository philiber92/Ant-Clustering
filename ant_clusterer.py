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
        if (self.isloaded == False):
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
        self.has_changed = True
        self.has_center_changed = True
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

        anzahl = len(self.item_sim_list) - 1
        faktor = 1.0 /anzahl
        similarity = summe * (faktor) 
        
#        if(similarity < 0):
#            similarity = 0
        
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

    def get_similarity_sum(self):
        sim_sum = 0
        if(self.has_changed == True):
            self.find_most_dissimilar()
        
        for object_index in range(0, len(self.item_sim_list)):
            sim_sum = sim_sum + self.item_sim_list[object_index][0]
        
        return sim_sum
        
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
        
        if(min_sim < 0):
            min_sim = 0
            
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
        self.similarity_sum = 0
        #self.ant_reactor_index = []
        
    def initialize(self):
        # create all data in numpy.array without last element
        new_data = []
        for datum in range(0,len(data)):
            new_data.append([])
            for element in range(0,len(data[datum]) - 1):
                new_data[datum].append(data[datum][element])
        
        self.data = np.array([np.array(datum) for datum in new_data])          
        
        num_data = self.data.size / self.data[0].size       
        print("num data", num_data)
        
        # random amount of reactor K <= number of data
        k = rand.randint(1, num_data)
        print(k)        
        
        # create reactors
        for i in range(0, k):
            self.reactors.append(reactor(self.alpha))
        print(len(self.reactors))
        
        # assign data at random to reactors
        for x in self.data:
            k = rand.randint(0, len(self.reactors) - 1)
            self.reactors[k].push_obj(x)
            
        #create ants
        for i in range(0, self.number_ants):
            tmp = ant()
            self.ants.append(tmp)
            
        #choose reactor to start with and init all ants
        self.start_reactor_index = rand.randint(0, len(self.reactors) - 1)
        for tmp in self.ants:
            tmp.reactor_num = self.start_reactor_index
        
    def iterations(self):
        
        for iteration in range(0, self.num_iterations):
            #print("iteration", iteration)
            for tmp in self.ants:
                #if unloaeded check number of objects
                if tmp.get_load_state() == False:
#                    print("is unloaded")
#                    tmp.print_state()
#                    self.print_data_amount()
                    # if more than one take most dissimilar
                    if (self.reactors[tmp.reactor_num].get_reactor_length() > 1):
                        # before, check if reactors can be combined
                        for reactor_index in range(0,len(self.reactors)):
                            if(reactor_index != tmp.reactor_num and self.reactors[reactor_index].get_reactor_length() > 0):
                                reactor_sim = self.reactor_similarity(self.reactors[tmp.reactor_num].get_reactor_center(), self.reactors[reactor_index].get_reactor_center())
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
                                        print("reactor combined", tmp.reactor_num, reactor_index)
                                        self.combine_reactors(tmp.reactor_num, reactor_index)
                                        
                                
                        # find most dissimilar object
                        sim, dissim_index = self.reactors[tmp.reactor_num].find_most_dissimilar()
                                                
                        # calculate probability to pick up
                        prob = self.kp / (self.kp + sim)
                        prob = prob * prob
                        ran = rand.random()
                        
                        if(ran < prob):
                            #print("took: ", sim, dissim_index, "from:", tmp.reactor_num)
                            tmp.pick_object(self.reactors[tmp.reactor_num].pop_obj(dissim_index))
                           
                    #if only one object then take it
                    elif (self.reactors[tmp.reactor_num].get_reactor_length() == 1):
                        #print("took: ", 1, "from:", tmp.reactor_num)
                        tmp.pick_object(self.reactors[tmp.reactor_num].pop_obj(0))
                        
                  
                
                elif tmp.isloaded == True:
#                    print("is loaded")
#                    tmp.print_state()
#                    self.print_data_amount()
                    # put only to reactor with more than one object
                    if(self.reactors[tmp.reactor_num].get_reactor_length() > 1):
                        self.reactors[tmp.reactor_num].push_obj(tmp.put_object())

                        # check if reactors can be combined
                        for reactor_index in range(0,len(self.reactors)):
                            if(reactor_index != tmp.reactor_num and self.reactors[reactor_index].get_reactor_length() > 0):
                                reactor_sim = self.reactor_similarity(self.reactors[tmp.reactor_num].get_reactor_center(), self.reactors[reactor_index].get_reactor_center())
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
                                        print("reactor combined", tmp.reactor_num, reactor_index)
                                        self.combine_reactors(tmp.reactor_num, reactor_index)
                                             
                        
                        # find most dissimilar object
                        sim, dissim_index = self.reactors[tmp.reactor_num].find_most_dissimilar()
                                                
                        # calculate probability to pick up
                        prob = self.kp / (self.kp + sim)
                        prob = prob * prob
                        ran = rand.random()
                        
                        if(ran < prob):
                            #print("took: ", sim, dissim_index, "from:", tmp.reactor_num)
                            tmp.pick_object(self.reactors[tmp.reactor_num].pop_obj(dissim_index))
                        
#                tmp.print_state() 
#                self.print_data_amount()
#                print("")
            # end for all ants => one Iteration done
            # delete all reactor with no data

            self.reactors = [react for react in self.reactors if react.get_reactor_length() != 0]                    
                
            # move ants to next reactor  
            for tmp in self.ants:
                ran = (tmp.reactor_num + 1) % len(self.reactors) 
                #ran = rand.randint(0, len(self.reactors) - 1)
                #print("move ant",tmp.reactor_num, ran ) 
                tmp.move_to_reactor(ran)
                            
            # after some steps create new reactor with all loaded objects
            if(iteration %  (self.s) == 0 or iteration == self.num_iterations - 1):
                react = reactor(self.alpha)
                for tmp in self.ants:
                    if(tmp.isloaded == True):
                        react.push_obj(tmp.put_object())
                if(react.get_reactor_length() > 0):
                    self.reactors.append(react)
                print("new reactor created", iteration, react.get_reactor_length())
                                        
                
            #self.compare_iterations()
        # end M Iterations
                
        print("iteratio",iteration)
        self.print_data_amount()                
                
        for i in range(len(self.reactors)):
            print("reactor ",i , "size:", self.reactors[i].get_reactor_length()  )
            print(self.reactors[i].item_sim_list)
            print("")
        # after M Iterations all Ants with dataobject build one new reactor
        # if too much reactors combine some (done in every step)
        # Terminate if difference between two Iterations is low enough
        
    def compare_iterations(self):
        # calc current value of iteration (sum all similarities)
        sim_sum = 0
        for react in self.reactors:
            if(react.get_reactor_length() > 1):
                sim_sum = sim_sum + react.get_similarity_sum()
        #print("compare iter: sim_sum ", sim_sum)  
                
        # calc difference between this and last iteration
        diff = abs(sim_sum - self.similarity_sum)
        #print("compare iter: diff ", diff, sim_sum, self.similarity_sum)
        
        if(sim_sum > 0):
            self.similarity_sum = sim_sum        
        
        if(diff < 0.00001):
            print("small diff between iterations")
            return True
            
        else:
            return False
        
        
    def print_data_amount(self):
        #print("num reactors", len(self.reactors))
        data_amount = 0
        for n in range(0, len(self.reactors) ):
            data_amount = data_amount + self.reactors[n].get_reactor_length()
            
        for tmp in self.ants:
            #tmp.print_state()
            if tmp.isloaded == True:
                data_amount = data_amount + 1
        print("data_amount", data_amount)
        
    def distance(self, object1, object2):
        distance = 0
        for i in range(0,len(object1)):
            distance1dim = object1[i] - object2[i]
            distance = distance + distance1dim * distance1dim
        distance = np.sqrt(distance)
        return distance
    
    def reactor_similarity(self, center1, center2):
        # measure distance
        dist = self.distance(center1, center2)
                
        # calculate similarity
        sim = 1 - dist / self.alpha1
        return sim

    def combine_reactors(self, num_reactor1, num_reactor2):
        for i in range(0, self.reactors[num_reactor2].get_reactor_length()):
            self.reactors[num_reactor1].push_obj(self.reactors[num_reactor2].pop_obj(0))
    

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
cluster = ant_clusterer(data, 15000, 0.05, 0.3, 1.5, 20, 0.3, 1000)
cluster.initialize()
cluster.iterations()

end = time.clock()
print("time needed", end - start)


