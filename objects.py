import os
from math import sqrt, atan2, sin, cos, pi

from PyQt5 import QtGui, QtWidgets, QtCore

SEGMENT_LEN = 20.0

salmon_sticky = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'stickies','salmon.svg')).scaledToHeight(200)
blue_sticky = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'stickies','blue.svg')).scaledToHeight(200)
blue_press = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'stickies','blue_press.svg')).scaledToHeight(200)
shadow =  QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'stickies','shadow.svg')).scaledToHeight(200)

yellow_sticky = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'stickies','yellow.svg')).scaledToHeight(200)
sticky_pin = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'stickies','pin.svg')).scaledToHeight(200)
cork = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'stickies','cork.svg'))
thread =  QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'stickies','thread.svg')).scaledToHeight(200)
twine_preview =  QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'stickies','twine_preview.svg')).scaledToHeight(200)

# twine is 20 by 5
TWINE_SHIFT = -2.5
twine = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'stickies','twine.svg'))

deg = 180/pi

class Entry:
    def __init__(self, **kwargs):
        self.anchor = ()


class Link:
    """
        Abstract representation of a linkage between two Entry objects

        One entry is the "parent" and the other the "child": there is an inherint directionality to these linkages 
    """
    def __init__(self, start:QtCore.QPointF, end:QtCore.QPointF, scene : QtWidgets.QGraphicsScene,  **kwargs):
        self.start = start
        self.end = end
                
        displacement = end-start

        distance = sqrt(displacement.x()**2 + displacement.y()**2)
        unit_v = displacement/distance

        n_seg = int(( distance- 0.5*SEGMENT_LEN)/SEGMENT_LEN) + 1
        scale_f = distance/(n_seg*SEGMENT_LEN)

        theta = atan2(displacement.y(), displacement.x())
        rot_mat = [[cos(theta), sin(theta)], [-sin(theta), cos(theta)]]

        anchor_shift = [rot_mat[0][1]*TWINE_SHIFT, rot_mat[1][1]*TWINE_SHIFT]

        step_len = unit_v*SEGMENT_LEN*scale_f

        self._scene = scene
        self._segments = []
        for i_count in range(n_seg):
            new_entry = scene.addPixmap(twine)
            new_entry.setScale(scale_f)
            new_entry.setRotation(theta*deg)
            new_entry.setPos(start.x() + anchor_shift[0] + step_len.x()*i_count , start.y() + anchor_shift[1] + step_len.y()*i_count)
            new_entry.setZValue(15)
            self._segments.append(new_entry)

    def erase(self):
        for segment in self._segments:
            self._scene.removeItem(segment)
        self._segments = []