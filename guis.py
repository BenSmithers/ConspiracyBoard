from PyQt5 import QtWidgets, QtCore

from objects import yellow_sticky, blue_sticky, salmon_sticky
from objects import thread

class central_gui(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1080, 720)
        MainWindow.setWindowTitle(QtCore.QCoreApplication.translate("MainWindow", "Conspiracy Board"))

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # where we add the stickies! 
        self.toolPane = QtWidgets.QVBoxLayout()
        self.toolPane.setObjectName("toolPane")
        

        self.bluesticky = QtWidgets.QLabel()
        self.bluesticky.setObjectName("bluesticky")
        self.bluesticky.setPixmap(blue_sticky)
        self.toolPane.addWidget(self.bluesticky)

        self.salmonsticky = QtWidgets.QLabel()
        self.salmonsticky.setObjectName("salmonsticky")
        self.salmonsticky.setPixmap(salmon_sticky)
        self.toolPane.addWidget(self.salmonsticky)

        self.yellowsticky = QtWidgets.QLabel()
        self.yellowsticky.setObjectName("yellowsticky")
        self.yellowsticky.setPixmap(yellow_sticky)
        self.toolPane.addWidget(self.yellowsticky)

        self.thread_lbl = QtWidgets.QLabel()
        self.thread_lbl.setObjectName("thread_lbl")
        self.thread_lbl.setPixmap(thread)
        self.toolPane.addWidget(self.thread_lbl)

        self.spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.toolPane.addItem(self.spacerItem)

        self.horizontalLayout.addLayout(self.toolPane)


        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget) # <--- this is the screen
        self.graphicsView.setObjectName("graphicsView") 
        self.horizontalLayout.addWidget(self.graphicsView)

        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)