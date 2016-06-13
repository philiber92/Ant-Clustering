
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
