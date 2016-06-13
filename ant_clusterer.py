import sys
import numpy as np
import matplotlib.pyplot as plt
import random as rand
import time
from scipy.io import arff
from ant import ant
from reactor import reactor

class ant_clusterer:
    def __init__(self, data, num_iterations, kp, kc, alpha, number_ants, alpha1, s ):
        self.data = data
        self.num_iterations = int(num_iterations)
        self.kp = float(kp)
        self.kc = float(kc)
        self.alpha = float(alpha)
        self.number_ants = int(number_ants)
        self.alpha1 = float(alpha1)
        self.s = int(s)
        self.reactors = []
        self.ants = []
        self.start_reactor_index = int(0)
        self.similarity_sum = float(0)
        
    def initialize(self):
        # create all data in numpy.array without last element (lable)
        new_data = []
        for datum in range(0,len(data)):
            new_data.append([])
            for element in range(0,len(data[datum]) - 1):
                new_data[datum].append(data[datum][element])
        
        self.data = np.array([np.array(datum) for datum in new_data])          
        
        num_data = self.data.size / self.data[0].size      
        
        # random amount of reactor K <= number of data
        k = rand.randint(1, num_data)       
        
        # create reactors
        for i in range(0, k):
            self.reactors.append(reactor(self.alpha))
        
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
            for tmp in self.ants:
                #if unloaeded check number of objects
                if tmp.get_load_state() == False:
                    # if more than one datum take most dissimilar
                    if (self.reactors[tmp.reactor_num].get_reactor_length() > 1):
                        # before taking the datum, check if reactors can be combined
                        for reactor_index in range(0,len(self.reactors)):
                            if(reactor_index != tmp.reactor_num and self.reactors[reactor_index].get_reactor_length() > 0):
                                reactor_sim = self.reactor_similarity(self.reactors[tmp.reactor_num].get_reactor_center(), self.reactors[reactor_index].get_reactor_center())
                                
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
                                        #print("reactor combined", tmp.reactor_num, reactor_index)
                                        self.combine_reactors(tmp.reactor_num, reactor_index)
                                        
                                
                        # find most dissimilar object
                        sim, dissim_index = self.reactors[tmp.reactor_num].find_most_dissimilar()
                                                
                        # calculate probability to pick up
                        prob = self.kp / (self.kp + sim)
                        prob = prob * prob
                        ran = rand.random()
                        
                        # and take it 
                        if(ran < prob):
                            tmp.pick_object(self.reactors[tmp.reactor_num].pop_obj(dissim_index))
                           
                    #if only one object in this reactor then take it
                    elif (self.reactors[tmp.reactor_num].get_reactor_length() == 1):
                        tmp.pick_object(self.reactors[tmp.reactor_num].pop_obj(0))
                
                elif tmp.isloaded == True:
                    # put carried datum only to reactor with more than one object
                    if(self.reactors[tmp.reactor_num].get_reactor_length() > 1):
                        self.reactors[tmp.reactor_num].push_obj(tmp.put_object())

                        # check if reactors can be combined
                        for reactor_index in range(0,len(self.reactors)):
                            if(reactor_index != tmp.reactor_num and self.reactors[reactor_index].get_reactor_length() > 0):
                                reactor_sim = self.reactor_similarity(self.reactors[tmp.reactor_num].get_reactor_center(), self.reactors[reactor_index].get_reactor_center())
                                
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
                                        #print("reactor combined", tmp.reactor_num, reactor_index)
                                        self.combine_reactors(tmp.reactor_num, reactor_index)
                                             
                        
                        # find most dissimilar object
                        sim, dissim_index = self.reactors[tmp.reactor_num].find_most_dissimilar()
                                                
                        # calculate probability to pick up
                        prob = self.kp / (self.kp + sim)
                        prob = prob * prob
                        ran = rand.random()
                        
                        if(ran < prob):
                            tmp.pick_object(self.reactors[tmp.reactor_num].pop_obj(dissim_index))

            # end for all ants => one Iteration done
            # delete all reactor with no data
            self.reactors = [react for react in self.reactors if react.get_reactor_length() != 0]                    
                
            # move ants to next reactor  
            for tmp in self.ants:
                #ran = (tmp.reactor_num + 1) % len(self.reactors) 
                ran = rand.randint(0, len(self.reactors) - 1)
                if(ran == tmp.reactor_num):
                    ran = (ran + 1) % len(self.reactors) 
                #print("move ant",tmp.reactor_num, ran ) 
                tmp.move_to_reactor(ran)
                            
            # after self.s steps create new reactor with all loaded objects
            if(iteration %  (self.s) == 0 or iteration == self.num_iterations - 1):
                react = reactor(self.alpha)
                for tmp in self.ants:
                    if(tmp.isloaded == True):
                        react.push_obj(tmp.put_object())
                if(react.get_reactor_length() > 0):
                    self.reactors.append(react)
                #print("new reactor created", iteration, react.get_reactor_length(), "num_reactors", len(self.reactors))
                                        
            # Terminate if difference between two iterations is small enough
#            if (self.compare_iterations() == True):
#                break
                
        # end M Iterations            
        return self.lable_reactor_data()
        
        
    def compare_iterations(self):
        # calc current value of iteration (sum all similarities)
        sim_sum = 0.0
        for react in self.reactors:
            if(react.get_reactor_length() > 1):
                sim_sum = sim_sum + react.get_similarity_mean()
                
        # calc difference between this and last iteration
        diff = abs(sim_sum - self.similarity_sum)
        
        if(sim_sum > 0):
            self.similarity_sum = sim_sum        
        
        if(diff < 0.00001):
            return True
            
        else:
            return False
        
        
#    def print_data_amount(self):
#        data_amount = 0
#        for n in range(0, len(self.reactors) ):
#            data_amount = data_amount + self.reactors[n].get_reactor_length()
#            
#        for tmp in self.ants:
#            if tmp.isloaded == True:
#                data_amount = data_amount + 1
#        print("data_amount", data_amount)
        
        
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
    
    def lable_reactor_data(self):
        labled_data = []
        lables = []
        lable_num = 0
        # each reactor is one cluster
        for react in self.reactors:
            # store data and lables in same order
            for datum in range(0, react.get_reactor_length()):
                labled_data.append(react.pop_obj(0))
                lables.append(lable_num)
            lable_num = lable_num + 1
            
        return (labled_data, lables)
    

########################### main ################################
if __name__ == "__main__":
    #data, meta = arff.loadarff('./Dataset/iris2.arff')
    data, meta = arff.loadarff(sys.argv[1])       

    #                      (data, num_iterations, kp, kc, alpha, number_ants, alpha1, s )
    #cluster = ant_clusterer(data, 2500, 0.05, 0.4, 5, 20, 0.3, 100)
    cluster = ant_clusterer(data, sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])
    cluster.initialize()
    labled_data, lables = cluster.iterations()
    
    lables = np.array([np.array(datum) for datum in lables])
    
    colors = np.array([x for x in 'bgrcmykbgrcmykbgrcmykbgrcmyk'])
    colors = np.hstack([colors] * 20)
        
    plt.scatter([i[0] for i in labled_data], [i[1] for i in labled_data], color=colors[lables].tolist(), s=10)
        
    plt.show()
