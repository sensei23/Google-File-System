import os
import random

class Location_Manager():
    def __init__(self):
        FILE_LOC = os.path.join(os.path.dirname(__file__), "locations")
        with open(FILE_LOC, "r") as f:
            self.locations = f.read().splitlines()
        #location format: "x y"
        self.locations = [tuple(map(int, loc.split())) for loc in self.locations]
        self.num_locations = len(self.locations)

    def get_location(self):
        idx = random.randint(0, self.num_locations - 1)
        return self.locations[idx]
    
    def get_distance(self, loc1, loc2):
        #return euclidean distance
        return ((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)**0.5

# loc_man = Location_Manager()
# print(loc_man.get_location())