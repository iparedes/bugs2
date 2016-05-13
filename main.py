__author__ = 'nacho'

import sys
import pygame, os
from pygame.locals import *
from ocempgui.draw import Draw
from ocempgui.widgets import *
from ocempgui.widgets.Constants import *

import bug
import world
from constants import *

class GUI:
    def __init__(self):
        # upper corner of the map shown in display
        self.coords=(0,0)
        # renderer
        self.re=None

        # Controls main loop
        self.GO=True
        self.TERMINATE=False

        self.RUNNING=False
        self.STEP=False
        # Shows the map
        self.SCREEN=True

        l=self.preload('./prog')
        B=bug.bug()
        B.compile(l)
        self.W=world.world()
        self.W.add_hab(B,(10,20))

        self.go_gui()
        self.draw_board()

        while self.GO and not self.TERMINATE:
            self.proc_events()
            if self.RUNNING or self.STEP:
                self.GO=self.W.cycle()
                if self.SCREEN:
                    self.draw_board()

            if self.STEP:
                self.STEP=False

            self.screen.blit(self.re.screen,self.re.topleft)
            pygame.display.update()


    def go_gui(self):
        pygame.init()
        # Main Window
        self.screen=pygame.display.set_mode((WINWIDTH,WINHEIGHT))
        self.screen.fill((100,100,100))

        # Controls surface
        self.re=Renderer()
        surfcontrols=pygame.Surface((WINWIDTH,WINHEIGHT))
        self.re.screen=surfcontrols
        self.re.topleft=(0,0)
        self.re.color=100,100,100

        # Right frame contains the controls
        frright=VFrame()
        frright.border=BORDER_RAISED
        frright.align=ALIGN_TOP

        # Subframe with buttons
        frplay=HFrame()
        frplay.align=ALIGN_LEFT
        frright.minsize=CONTROLWIDTH,CONTROLHEIGHT

        self.btn_play=ImageButton("./images/play.png")
        self.btn_play.connect_signal(SIG_CLICKED,self._toggle_pause)
        frplay.add_child(self.btn_play)

        self.btn_step=ImageButton("./images/step.png")
        self.btn_step.connect_signal(SIG_CLICKED,self._step)
        frplay.add_child(self.btn_step)

        self.btn_stop=ImageButton("./images/stop.png")
        self.btn_stop.connect_signal(SIG_CLICKED,self._stop)
        frplay.add_child(self.btn_stop)

        # Frame with world's status info
        frstatus=VFrame()
        frstatus.align=ALIGN_LEFT
        #
        self.label_cycle=Label("Cycle: "+str(self.W.cycles))
        self.label_bugs=Label("Bugs: "+str(len(self.W.habs)))
        frstatus.add_child(self.label_cycle)
        frstatus.add_child(self.label_bugs)

        frright.add_child(frplay)
        frright.add_child(frstatus)
        frright.topleft=(MAPWIDTH,0)

        self.re.add_widget(frright)

        frhbar=HFrame()
        frhbar.align=ALIGN_LEFT
        frhbar.set_border(BORDER_NONE)
        self.hscroll=HScrollBar(MAPWIDTH,(MAPWIDTH-TILESWIDTH)+MAPWIDTH)
        self.hscroll.connect_signal(SIG_VALCHANGED,self._hscroll_change)
        frhbar.add_child(self.hscroll)
        frhbar.topleft=(0,MAPHEIGHT)
        #hscroll.topleft=(0,MAPHEIGHT)
        self.re.add_widget(frhbar)

        self.screen.blit(self.re.screen,self.re.topleft)
        pygame.display.flip()


        # #hscroll=HScrollBar(BOARDSIZE-TILESWIDTH,BOARDSIZE-TILESWIDTH)
        # #self.screen.blit(self.re.screen,self.re.topleft)
        #
        # # Draws the controls surface
        # self.re.topleft=0,0
        # self.screen.blit(self.re.screen,(0,0))
        # #pygame.draw.rect(self.screen,(0,255,0),(0,0,50,50))
        # #pygame.display.flip()
        #
        # #self.re.start()

    def draw_board(self):
        f1=self.coords[0]
        c1=self.coords[1]
        f2=f1+TILESHEIGHT
        c2=c1+TILESWIDTH

        if f2>=BOARDSIZE:
            f2=BOARDSIZE
            f1=f2-TILESHEIGHT
        if c2>=BOARDSIZE:
            c2=BOARDSIZE
            c1=c2-TILESHEIGHT

        for y in range(f1,f2):
            for x in range(c1,c2):
                a=self.W.board.cell((x,y))
                if a.is_hab():
                    id=a.hab[0]
                    color=self.W.habs[id].color
                elif a.has_food(CARN):
                    color=RED
                elif a.has_food(HERB):
                    color=GREEN
                else:
                    color=BROWN
                pygame.draw.rect(self.re.screen,color,((y-f1)*TILESIZE,(x-c1)*TILESIZE,TILESIZE,TILESIZE))
                rect=Draw.draw_rect(TILESIZE,TILESIZE,color)
                # Draws each tile in the board
                self.screen.blit(rect,((y-f1)*TILESIZE,(x-c1)*TILESIZE))

    def proc_events(self):
        events=pygame.event.get()
        for event in events:
            if event.type==QUIT:
                pygame.quit()
                sys.exit()
            if event.type==MOUSEBUTTONDOWN:
                # Watchout swap rows,cols to match x,y
                # ToDo FIX offset
                y,x=event.pos
                if (x<MAPHEIGHT) and (y<MAPWIDTH):
                    mx=x/TILESIZE
                    my=y/TILESIZE
                    cell=self.W.board.cell((mx,my))
                    if cell.is_hab():
                        id=cell.hab
                        for ident in id:
                            l=self.W.habs[ident].bug.decompile()
                            print "================="
                            for i in l:
                                print i
                            print "================="
                    print str(mx)+","+str(my)

        # WATCH HERE
        self.re.distribute_events(*events)



    def preload(self,fich):
        L=[]
        with open(fich,'r') as f:
            for line in f:
                for word in line.split():
                    L.append(word)
        return L

    def _toggle_pause(self):
        self.RUNNING=not self.RUNNING
        if self.RUNNING:
            self.btn_play.set_picture('./images/pause.png')
        else:
            self.btn_play.set_picture('./images/play.png')

    def _step(self):
        self.STEP=True

    def _stop(self):
        self.TERMINATE=True

    def _hscroll_change(self):

        c=(int(self.hscroll.value),self.coords[1])
        self.coords=c
        self.draw_board()


if __name__ == "__main__":
    G=GUI()
