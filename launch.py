"""
Central File
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget


import os
import sys
from math import sqrt


sticky_buffer = 30 #px
sticky_width = 140




class click_interface(QtWidgets.QGraphicsScene):
    """
        This object is used for keeping track of what the mouse is up to and drawing things on the window 
    """
    def __init__(self, parent:QtWidgets.QGraphicsView, master:QtWidgets.QMainWindow):
        QtWidgets.QGraphicsScene.__init__(self, parent)

        self.parent = parent
        self.master = master

        self._mode = 0
        
        """
        Modes! 
            0 - waiting
            1 - placing blue sticky 
            2 - placing yellow sticky 
            3 - placing salmon sticky
            4 - placing twine 
            5 - first bit of twine placed, placing second end 
            6 - moving sticky
        """
        self._ghost_pixmap = None
        self._shadow_pixmap = None

        self._mouse_shift = (0,0)

        self._placed_stickies = []

        self._sticky_starts = []
        self._sticky_ends = []
        self._placed_pins = []

        self._selected_sticky_index = None

        self._thread_start_pin = None
        self._thread_start = QtCore.QPointF(0,0)
        self._thread_preview = None

        self.back = self.addPixmap(cork)
        self.back.setZValue(0)

        self._primary_mouse = QtCore.Qt.MouseButton.LeftButton
        self._secondary_mouse = QtCore.Qt.MouseButton.RightButton

        self._pin_shift = QtCore.QPointF(0.5*sticky_width+ sticky_buffer, 30)

    def set_mouse_shift(self, loc:tuple):
        # loc should be a length-2 tuple specifying the amount by which we need to shift the drawing of the ghost pixmap 
        self._mouse_shift = loc

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        mouse_loc = event.scenePos()
        if self._mode==0:
            if self._ghost_pixmap is not None:
                self.removeItem(self._ghost_pixmap)
                self._ghost_pixmap = None
            if self._shadow_pixmap is not None:
                self.removeItem(self._shadow_pixmap)
                self._shadow_pixmap = None
            if self._thread_preview is not None:
                self._thread_preview.erase()
                self._thread_preview = None
        elif self._mode==1:
            if self._ghost_pixmap is None:
                self._shadow_pixmap = self.addPixmap(shadow)
                self._ghost_pixmap = self.addPixmap(blue_sticky)
        elif self._mode==2:
            if self._ghost_pixmap is None:
                self._ghost_pixmap = self.addPixmap(yellow_sticky)
                self._shadow_pixmap = self.addPixmap(shadow)
        elif self._mode==3:
            if self._ghost_pixmap is None:
                self._ghost_pixmap = self.addPixmap(salmon_sticky)
                self._shadow_pixmap = self.addPixmap(shadow)
        elif self._mode==4:
            # shimmy the thread preview over
            if self._ghost_pixmap is None:
                self._ghost_pixmap = self.addPixmap(twine_preview)
                self._ghost_pixmap.setZValue(30)
            self._ghost_pixmap.setPos(mouse_loc)
        elif self._mode==5:
            # draw the thread preview 
            if self._thread_preview is not None:
                self._thread_preview.erase()
            self._thread_preview = Link(self._thread_start, mouse_loc, self)
        elif self._mode == 6:
            if self._selected_sticky_index is None:
                self._mode = 0

            if self._shadow_pixmap is None:
                self._shadow_pixmap = self.addPixmap(shadow)
                self._shadow_pixmap.setZValue(29)

            self._shadow_pixmap.setPos( mouse_loc.x() -self._mouse_shift[0]-10, mouse_loc.y() - self._mouse_shift[1] +10)
            self._placed_stickies[self._selected_sticky_index].setPos( mouse_loc.x() -self._mouse_shift[0], mouse_loc.y() - self._mouse_shift[1] )
            self._placed_stickies[self._selected_sticky_index].setZValue(30)

        if self._mode in [1,2,3]:
            self._ghost_pixmap.setPos( mouse_loc.x() -self._mouse_shift[0], mouse_loc.y() - self._mouse_shift[1] )
            self._shadow_pixmap.setPos( mouse_loc.x() -self._mouse_shift[0]-10, mouse_loc.y() - self._mouse_shift[1] +10)
            self._ghost_pixmap.setZValue(30)
            self._shadow_pixmap.setZValue(29)

    def set_mode(self, index:int):
        self._mode = index

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        if self._mode == 0:
            # check if there's a sticky underneath this, but only if we're not placing! 
            mouse_loc = event.scenePos()
            index_count = 0
            for entry in self._placed_stickies:
                index_count += 1
                obj_loc = entry.scenePos()
                mouse_shift = (mouse_loc.x()-obj_loc.x(), mouse_loc.y()-obj_loc.y())

                in_x = mouse_shift[0] > sticky_buffer and mouse_shift[0] < sticky_width+sticky_buffer
                in_y = mouse_shift[1] > sticky_buffer and mouse_shift[1] < sticky_width+sticky_buffer
                if (in_x and in_y):
                    self._selected_sticky_index = self._placed_stickies.index(entry)
                    self.set_mouse_shift(mouse_shift)
                    self._mode = 6
                    break
        elif self._mode==4:
            # look for a pin near where we click 
            for entry in self._placed_pins:
                dist =  event.scenePos() - entry.scenePos() - self._pin_shift
                disp = sqrt(dist.x()**2 + dist.y()**2)
                print("displacement {}".format(disp))
                if disp<20:
                    self._mode = 5
                    self._thread_start =  entry.scenePos() + self._pin_shift
                    self._thread_start_pin = entry
                    if self._ghost_pixmap is not None:
                        self.removeItem(self._ghost_pixmap)
                        self._ghost_pixmap = None
                        break
                
            
        elif self._mode==5:  # place a piece of twine
            for entry in self._placed_pins:
                dist =  event.scenePos() - entry.scenePos() - self._pin_shift
                disp = sqrt(dist.x()**2 + dist.y()**2)
                if disp<20:
                    self._mode = 0
                    #find the start pin
                    
                    new_link = Link(self._thread_start, entry.scenePos()+ self._pin_shift , self)
                    end_index = self._placed_pins.index(entry)
                    start_index = self._placed_pins.index(self._thread_start_pin)
                    self._sticky_starts[start_index][self._thread_start_pin] = new_link
                    self._sticky_ends[end_index][entry] = new_link

                    if self._thread_preview is not None:
                        self._thread_preview.erase()
                    self._thread_preview=None



                    break

    def mouseReleaseEvent( self, event: QtWidgets.QGraphicsSceneMouseEvent)->None:
        if self._mode in [1,2,3]:
            # finish doing it! 
            if self._mode==1:
                new_sticky = self.addPixmap(blue_sticky)
            elif self._mode == 2:
                new_sticky = self.addPixmap(yellow_sticky)
            elif self._mode == 3:
                new_sticky = self.addPixmap(salmon_sticky)
            else:
                raise ValueError()
                new_sticky = self.addPixmap(blue_sticky)

            new_pin = self.addPixmap(sticky_pin)
            new_pin.setPos( event.scenePos().x()-self._mouse_shift[0], event.scenePos().y()-self._mouse_shift[1] )
            new_pin.setZValue(20)
            self._placed_pins.append(new_pin)
            new_sticky.setPos(event.scenePos().x()-self._mouse_shift[0], event.scenePos().y()-self._mouse_shift[1])
            new_sticky.setZValue(10)
            self._placed_stickies.append(new_sticky)

            # we'll use these to keep the links updated 
            self._sticky_starts.append({})
            self._sticky_ends.append({})

            self.set_mode(0)
        if self._mode==6:
            self.removeItem(self._shadow_pixmap)
            self._shadow_pixmap = None
            self._placed_pins[self._selected_sticky_index].setPos( event.scenePos().x()-self._mouse_shift[0], event.scenePos().y()-self._mouse_shift[1] )
            self._placed_stickies[self._selected_sticky_index].setZValue(10)
            self._mode = 0

            # update the twine starting from this pin
            start_keys = list(self._sticky_starts[self._selected_sticky_index].keys())
            for key in range(len(start_keys)):
                old_start = self._sticky_starts[self._selected_sticky_index][start_keys[key]].start
                self._sticky_starts[self._selected_sticky_index][start_keys[key]].erase()
                new_link = Link(old_start, QtCore.QPointF( event.scenePos().x()-self._mouse_shift[0], event.scenePos().y()-self._mouse_shift[1])+self._pin_shift, self)
                self._sticky_starts[self._selected_sticky_index][start_keys[key]] = new_link


            end_keys = list(self._sticky_starts[self._selected_sticky_index].keys())
            for key in range(len(end_keys)):
                old_end = self._sticky_ends[self._selected_sticky_index][end_keys[key]].end
                self._sticky_ends[self._selected_sticky_index][end_keys[key]].erase()
                new_link = Link(QtCore.QPointF( event.scenePos().x()-self._mouse_shift[0], event.scenePos().y()-self._mouse_shift[1])+self._pin_shift, old_end, self)
                self._sticky_ends[self._selected_sticky_index][end_keys[key]] = new_link

            self._selected_sticky_index = None

    def mouseDoubleClickEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent)->None:
        return


# open the gui
class main_window(QMainWindow):
    """"
    Main Menu Gui creator! 
    """
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        self.ui = central_gui()
        self.ui.setupUi(self)

        self.interface = click_interface(self.ui.graphicsView, self)
        self.ui.graphicsView.setMouseTracking(True)
        self.ui.graphicsView.setScene(self.interface)
        
        self.ui.bluesticky.mousePressEvent = self.click_bluesticky
        self.ui.yellowsticky.mousePressEvent = self.click_yellowsticky
        self.ui.salmonsticky.mousePressEvent = self.click_salmonsticky
        self.ui.thread_lbl.mousePressEvent = self.click_thread

        self.ui.bluesticky.mouseReleaseEvent = self.release_bluesticky
        self.ui.yellowsticky.mouseReleaseEvent = self.release_yellowsticky
        self.ui.salmonsticky.mouseReleaseEvent = self.release_salmonsticky
        self.ui.thread_lbl.mouseReleaseEvent = self.release_thread
        

    def _click_sticky(self, event:QtGui.QMouseEvent, button_pos, sticky_id):
        bs_pos = self.ui.bluesticky.pos()

        mouse_pos = event.windowPos()
        mouse_shift = ( mouse_pos.x() - button_pos.x() , mouse_pos.y() - button_pos.y())
        in_x = mouse_shift[0] > sticky_buffer and mouse_shift[0] < sticky_width+sticky_buffer
        in_y = mouse_shift[1] > sticky_buffer and mouse_shift[1] < sticky_width+sticky_buffer

        # get relative position of mouse click in label 
        if in_x and in_y:
            if sticky_id==1:
                self.ui.bluesticky.setPixmap(blue_press)
            elif sticky_id==2:
                self.ui.yellowsticky.setPixmap(blue_press)
            else:
                self.ui.salmonsticky.setPixmap(blue_press)

            self.interface.set_mode(sticky_id)
            self.interface.set_mouse_shift(mouse_shift)
            

    def release_bluesticky(self, event:QtGui.QMouseEvent):
        self.ui.bluesticky.setPixmap(blue_sticky)
    def release_yellowsticky(self, event:QtGui.QMouseEvent):
        self.ui.yellowsticky.setPixmap(yellow_sticky)
    def release_salmonsticky(self, event:QtGui.QMouseEvent):
        self.ui.salmonsticky.setPixmap(salmon_sticky)

    def click_salmonsticky(self, event:QtGui.QMouseEvent):
        bs_pos = self.ui.salmonsticky.pos()
        self._click_sticky(event, bs_pos, 3)

    def click_yellowsticky(self, event:QtGui.QMouseEvent):
        bs_pos = self.ui.yellowsticky.pos()
        self._click_sticky(event, bs_pos, 2)

    def click_bluesticky(self, event:QtGui.QMouseEvent):
        # sticky buffer of 30 px, 142 px wide/tall
        bs_pos = self.ui.bluesticky.pos()
        self._click_sticky(event, bs_pos, 1)

    def click_thread(self, event:QtGui.QMouseEvent):
        self.interface.set_mode(4)

    def release_thread(self, event:QtGui.QMouseEvent):
        self.ui.thread_lbl.setPixmap(thread)

app = QApplication(sys.argv)
from objects import yellow_sticky, blue_sticky, salmon_sticky
from objects import blue_press
from objects import sticky_pin, cork, shadow, thread, twine_preview
from guis import central_gui
from objects import Link
app_instance = main_window()


# quit button
if __name__=="__main__":
    # make sure the base saves folder exists 

    app_instance.show()
    sys.exit(app.exec_())