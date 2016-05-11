__author__ = 'nacho'

import random
from constants import *

class cell:
    def __init__(self):
        self.hab=[]

        self.food=[0]*OMNI

        a=random.randint(0,2)
        if a==1:
            self.grow_food()



    def has_food(self,type):
        if type==OMNI:
            t=(i>0 for i in self.food)
            return any(t)
        else:
            try:
                return self.food[type]>0
            except:
                # If type does not exist, the bug cannot feed
                return 0

    def grow_food(self,type=HERB,value=FOODPACK):
        self.food[type]=value

    def consume_food(self,type):
        if type==OMNI:
            f=sum(self.food)
            for i in range(0,len(self.food)):
                self.food[i]=0
        else:
            f=self.food[type]
            self.food[type]=0
        return f

    def set_hab(self,val):
        self.hab.append(val)

    def del_hab(self,val):
        self.hab.remove(val)

    def is_hab(self):
        return len(self.hab)>0

