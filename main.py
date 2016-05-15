__author__ = 'nacho'

import sys
import logging
import pygame, os
import codecs
import datetime
#import pickle
from pygame.locals import *
from ocempgui.draw import Draw
from ocempgui.widgets import *
from ocempgui.widgets.Constants import *
from operator import attrgetter

import bug
import world
from constants import *

logger = logging.getLogger('bugs')
hdlr=logging.FileHandler('./bugs.log')
formatter = logging.Formatter('%(asctime)s - %(module)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

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
        # Enables clicks on the map
        self.MAPENABLED=True
        # Selected bug
        self.SELECTEDBUG=None

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

            self.label_cycle.set_text("Cycle: "+str(self.W.cycles))
            self.label_bugs.set_text("Bugs: "+str(len(self.W.habs)))

            if self.SELECTEDBUG!=None and self.SELECTEDBUG in self.W.habs:
                hab=self.W.habs[self.SELECTEDBUG]
                bicho=hab.bug
                pos=hab.pos
                self.label_bugid.set_text("Bug Id: "+bicho.id)
                self.label_bugage.set_text("Age: "+str(bicho.age))
                self.label_bugenergy.set_text("Energy: "+str(bicho.energy()))
                self.label_bugpos.set_text("("+str(pos[0])+","+str(pos[1])+")")
                self.label_buginstr.set_text(bicho.last_executed)
            else:
                self.label_bugid.set_text("Bug Id: ")
                self.label_bugage.set_text("Age: ")
                self.label_bugenergy.set_text("Energy: ")
                self.label_bugpos.set_text("")
                self.label_buginstr.set_text("")

            self.screen.blit(self.re.screen,self.re.topleft)
            pygame.display.update()

        L=self.W.graveyard
        M=[x.bug for x in self.W.habs.values()]
        N=L+M
        totpop=len(N)
        print "The world ended at "+str(self.W.cycles)+" cycles."
        print "A total of "+str(totpop)+" bugs lived during this time."
        if totpop>0:
            oldest=max(L+M,key=attrgetter('age'))
            print "Oldest bug:"
            print "Id: "+oldest.id
            print "Age: "+str(oldest.age)
            print "Maxpop: "+str(self.W.maxpop)
            l=oldest.decompile()
            print l


    def go_gui(self):
        pygame.init()

        base.GlobalStyle.styles["default"]["font"]["name"] = "calibrib.ttf"
        base.GlobalStyle.styles["default"]["font"]["size"] = 14

        # Main Window
        self.screen=pygame.display.set_mode((WINWIDTH,WINHEIGHT))
        self.screen.fill((100,100,100))

        # Controls surface
        self.re=Renderer()
        surfcontrols=pygame.Surface((WINWIDTH,WINHEIGHT))
        self.re.screen=surfcontrols
        self.re.topleft=(0,0)
        self.re.color=100,100,100

        # Subframe with vertical scrollbar
        frvbar=VFrame()
        frvbar.align=ALIGN_TOP
        frvbar.set_border(BORDER_NONE)
        self.vscroll=VScrollBar(MAPHEIGHT,(MAPHEIGHT+BOARDSIZE-TILESHEIGHT))
        self.vscroll.connect_signal(SIG_VALCHANGED,self._vscroll_change)
        frvbar.add_child(self.vscroll)
        frvbar.topleft=(MAPWIDTH,0)
        #hscroll.topleft=(0,MAPHEIGHT)

        #frright.add_child(frvbar)
        self.re.add_widget(frvbar)

        frcontrols=VFrame()
        frcontrols.align=ALIGN_TOP

        # Subframe with buttons
        frplay=HFrame()
        frplay.align=ALIGN_LEFT


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

        # Frame with selected bug info
        frselbug=VFrame()
        frselbug.align=ALIGN_TOP

        self.label_bugid=Label("Bug Id: ")
        self.label_bugage=Label("Age: ")
        self.label_bugenergy=Label("Energy: ")
        self.label_bugpos=Label("")
        self.label_buginstr=Label("")
        frselbug.children=self.label_bugid,self.label_bugage,self.label_bugenergy,self.label_bugpos,self.label_buginstr

        # Frame with sow control
        frosow=VFrame(Label("Sow Rate"))
        frosow.align=ALIGN_TOP

        # Slider
        self.sowslider=HScale(0,len(self.W.sowratevalues)-1)
        self.sowslider.connect_signal (SIG_VALCHANGED, self._update_sowrate,)
        # Sets the initial position of the slider
        self.sowslider.value=self.W.sowratevalues.index(self.W.sowrate)
        frosow.add_child(self.sowslider)
        
        # Frame with file buttons
        frfile=HFrame()
        frfile.align=ALIGN_LEFT
        tafile=Table(2,2)
        frfile.add_child(tafile)
        
        self.btn_loadbug=ImageButton("./images/loadbug.png")
        self.btn_loadbug.connect_signal(SIG_CLICKED,self._loadbug)
        tafile.add_child(0,0,self.btn_loadbug)
        #frfile.add_child(self.btn_loadbug)

        self.btn_loadworld=ImageButton("./images/loadworld.png")
        self.btn_loadworld.connect_signal(SIG_CLICKED,self._loadworld)
        tafile.add_child(0,1,self.btn_loadworld)
        #frfile.add_child(self.btn_loadworld)

        self.btn_savebug=ImageButton("./images/savebug.png")
        self.btn_savebug.connect_signal(SIG_CLICKED,self._savebug)
        tafile.add_child(1,0,self.btn_savebug)
        #frfile.add_child(self.btn_savebug)
        
        self.btn_saveworld=ImageButton("./images/saveworld.png")
        self.btn_saveworld.connect_signal(SIG_CLICKED,self._saveworld)
        tafile.add_child(1,1,self.btn_saveworld)
        #frfile.add_child(self.btn_saveworld)

        # frcontrols.add_child(frplay)
        # frcontrols.add_child(frstatus)
        # frcontrols.add_child(frselbug)
        # frcontrols.add_child(frosow)
        frcontrols.children=frplay,frstatus,frselbug,frosow,frfile


        # Right frame contains the controls
        frright=HFrame()
        frright.border=BORDER_NONE
        frright.align=ALIGN_TOP
        frright.topleft=(MAPWIDTH+frvbar.width,0)
        frright.minsize=CONTROLWIDTH,CONTROLHEIGHT

        frright.add_child(frcontrols)

        self.re.add_widget(frright)

        # Horizontal scroll bar
        frhbar=HFrame()
        frhbar.align=ALIGN_LEFT
        frhbar.set_border(BORDER_NONE)
        self.hscroll=HScrollBar(MAPWIDTH,(MAPWIDTH+BOARDSIZE-TILESWIDTH))
        self.hscroll.connect_signal(SIG_VALCHANGED,self._hscroll_change)
        frhbar.add_child(self.hscroll)
        frhbar.topleft=(0,MAPHEIGHT)
        #hscroll.topleft=(0,MAPHEIGHT)
        self.re.add_widget(frhbar)

        self.screen.blit(self.re.screen,self.re.topleft)
        pygame.display.flip()



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
                if self.MAPENABLED:
                    y,x=event.pos
                    if (x<MAPHEIGHT) and (y<MAPWIDTH):
                        mx=x/TILESIZE
                        my=y/TILESIZE
                        mx+=self.coords[1]
                        my+=self.coords[0]
                        cell=self.W.board.cell((mx,my))
                        if cell.is_hab():
                            id=cell.hab
                            for ident in id:
                                self.SELECTEDBUG=ident
                                l=self.W.habs[ident].bug.decompile()
                                print "================="
                                for i in l:
                                    print i
                                print "================="
                        print str(mx)+","+str(my)

        # WATCH HERE
        self.re.distribute_events(*events)



    def filewindow(self,item):
        """
        Draws a load file window for bugs and worlds
        :param item: Determines if it is a bug or world load. Values (0:bug, 1:world)
        :return:
        """
        # Disables map clicks
        self.MAPENABLED=False

        buttons = [Button ("#OK"), Button ("#Cancel")]
        buttons[0].minsize = 80, buttons[0].minsize[1]
        buttons[1].minsize = 80, buttons[1].minsize[1]
        results = [DLGRESULT_OK, DLGRESULT_CANCEL]

        dialog = FileDialog ("Select your file(s)", buttons, results)
        dialog.depth = 1 # Make it the top window.
        #dialog.topleft = 100, 20
        #dialog.filelist.selectionmode = SELECTION_MULTIPLE
        if item==0:
            dialog.connect_signal (SIG_DIALOGRESPONSE, self._set_bugfiles, dialog)
        elif item==1:
            dialog.connect_signal (SIG_DIALOGRESPONSE, self._set_worldfiles, dialog)
        return dialog

    def messWindow(self,message):
        # Disables map clicks
        self.MAPENABLED=False

        buttons = [Button ("OK")]
        results = [DLGRESULT_OK]
        dialog = GenericDialog ("Message", buttons, results)
        lbl = Label (message)
        dialog.content.add_child (lbl)
        dialog.connect_signal (SIG_DIALOGRESPONSE, self._close_messWindow, dialog)
        #dialog.topleft = 30, 30
        dialog.depth = 1
        return dialog

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
        v=int(self.hscroll.value)
        #print v
        c=(v,self.coords[1])
        self.coords=c

        self.draw_board()

    def _vscroll_change(self):
        v=int(self.vscroll.value)
        #print v
        c=(self.coords[0],v)
        self.coords=c
        self.draw_board()

    def _update_sowrate(self):
        v=int(self.sowslider.value)
        print v
        rate=self.W.sowratevalues[v]
        self.W.sowrate=rate

    def _loadbug(self):
        dialog=self.filewindow(0)
        self.re.add_widget(dialog)
        pygame.display.update()

    def loadbug(self,filename):
        B=bug.bug()
        file=open(filename,'rb')
        B.load(file)
        file.close()
        self.W.add_hab(B)

    def _loadworld(self):
        dialog=self.filewindow(1)
        self.re.add_widget(dialog)
        pygame.display.update()

    def loadworld(self,filename):
        X=world.world()
        file=open(filename,'rb')
        self.W=X.load(file)
        file.close()

    def _savebug(self):
        if self.SELECTEDBUG!=None and self.SELECTEDBUG in self.W.habs:
            bug=self.W.habs[self.SELECTEDBUG].bug
            fname="savebugs/"+bug.id+".bug"
            f=codecs.open(fname,'wb')
            #data_stringB=pickle.dumps(bug)
            bug.save(f)
            #f.write(data_stringB)
            f.close()
            win=self.messWindow("Bug "+bug.id+" saved.")
            self.re.add_widget(win)
            #self.draw_board()


    def _saveworld(self):
        a=datetime.datetime.now()
        name=a.strftime('%Y%m%d%H%M%S')
        fname="savebugs/"+name+".world"
        f=codecs.open(fname,'wb')
        self.W.save(f)
        f.close()
        win=self.messWindow("World "+name+" saved.")
        self.re.add_widget(win)

    def _close_messWindow(self,resp,dialog):
        dialog.destroy()
        self.draw_board()
        # Enables map clicks
        self.MAPENABLED=True

    def _set_bugfiles(self,result,dialog):
        string = ""
        if result == DLGRESULT_OK:
            fname=dialog.get_filenames()[0]
            self.loadbug(fname)
        dialog.destroy ()
        self.draw_board()
        # Enables map clicks
        self.MAPENABLED=True

    def _set_worldfiles(self,result,dialog):
        string=""
        if result == DLGRESULT_OK:
            fname=dialog.get_filenames()[0]
            self.loadworld(fname)
        dialog.destroy ()
        self.draw_board()
        # Enables map clicks
        self.MAPENABLED=True

if __name__ == "__main__":
    # W=world.world()
    # filename="savebugs/20160515194356.world"
    # file=open(filename,'rb')
    # A=W.load(file)
    # file.close()
    G=GUI()
