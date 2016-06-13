import numpy as np

class reactor:
    def __init__(self, alpha):
        self.item_sim_list = [] #[sim, datum]
        self.has_changed = True
        self.has_center_changed = True
        self.alpha = alpha
        self.center = None
        
    # find similarity to all other data in this reactor
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
        
        self.item_sim_list[object_index][0] = similarity
        return similarity
        
    # euclidian distance of two datapoints
    def distance(self, object1, object2):
        distance = 0
        for i in range(0,len(object1)):
            distance1dim = object1[i] - object2[i]
            distance = distance + distance1dim * distance1dim
        distance = np.sqrt(distance)
        return distance        
        
    def get_reactor_length(self):
        return len(self.item_sim_list)        
        
    # calculate mean of all data for this reactor
    def get_reactor_center(self):
        if (self.has_center_changed == True):
            self.center = self.item_sim_list[0][1]
            for n in range(1, len(self.item_sim_list)):
                self.center = self.center + self.item_sim_list[n][1]
            self.center = self.center / len(self.item_sim_list)
            self.has_center_changed = False
        return self.center
        
    # take datum in reactor
    def push_obj(self, obj):
        self.item_sim_list.append([0, obj])
        self.has_changed = True
        self.has_center_changed = True
        
    # remove datum from reactor
    def pop_obj(self, obj_index):
        self.has_changed = True
        self.has_center_changed = True
        return self.item_sim_list.pop(obj_index)[1]

    # returns mean_similarity 
    def get_similarity_mean(self):
        sim_sum = 0.0
        if(self.has_changed == True):
            self.find_most_dissimilar()
        
        for object_index in range(0, len(self.item_sim_list)):
            if (self.item_sim_list[object_index][0] > 0):
                sim_sum = sim_sum + self.item_sim_list[object_index][0]
        
        sim_sum = sim_sum / self.get_reactor_length()
        return sim_sum
        
    #returns similarity of most dissimilar datum and its index in reactor
    def find_most_dissimilar(self):
        min_index = 0
        min_sim = 100
        # update similarity only if item was added or removed          
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
        
        # limit negativ similarity to 0
        if(min_sim < 0):
            min_sim = 0
            
        return(min_sim, min_index)
