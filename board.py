__author__ = 'nacho'

import cell

class board:
    def __init__(self,width,height):
        """
        width=x coordinate
        height=y coordinate
        :param width:
        :param height:
        :return:
        """
        self.height=height
        self.width=width
        self.b=[[cell.cell() for x in range(width)] for x in range(height)]


    def cell(self,pos):
        return self.b[pos[0]][pos[1]]
