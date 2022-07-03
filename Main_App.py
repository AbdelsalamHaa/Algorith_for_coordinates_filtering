import sys
import traceback
import os

import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog,QVBoxLayout,QLabel,QScrollArea,QWidget
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap , QImage
from KMLProcessor import *
from PyQt5.QtCore import QThread,pyqtSignal,pyqtSlot,Qt


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure



class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)



class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        loadUi(r"./gui/gui.ui", self)


        self.btn_select_file.clicked.connect(self.on_clicked_select_file)
        self.scrollArea.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.layout = QVBoxLayout(self.scrollAreaWidgetContents)

        self.p = ProcessKML()
        self.p.updateUi_signal.connect(self.updateUI)




    def on_clicked_select_file(self):
        self.remove_all_ui()
        path = QFileDialog.getOpenFileName(self, 'Open a file', '',
                                           'All Files (*.kml)')

        self.folderpath = path[0]
        self.p.set_path(self.folderpath)
        self.p.start()


    @pyqtSlot(list,list,list,float,str)
    def updateUI(self,f_d,d,thr,distance_travelled,method):
        try:
           sc = MplCanvas(self, width=5, height=4, dpi=100)
           sc.axes.plot(d,label="Original Signal")
           sc.axes.plot(f_d,label = "Filtered Signal")
           sc.axes.plot(thr,label = "Filtering Threshold")
           sc.axes.legend()
           sc.axes.set_xlabel("Index")
           sc.axes.set_ylabel("Distance in km")
           sc.axes.set_title(f"Filtered Signal Using {method} Method")
           # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
           toolbar = NavigationToolbar(sc, self)


           self.layout.addWidget(toolbar)
           self.layout.addWidget(sc)

           self.te_outpu.appendPlainText(f"Using {method} method = {round(distance_travelled,3)} km")

        except :
            traceback.print_exc()


    def remove_all_ui(self):
        number_of_labels = self.layout.count()
        for i in range(number_of_labels - 1, -1, -1):
            l = self.layout.itemAt(i)
            l.widget().setParent(None)
        self.te_outpu.clear()

class ProcessKML(QThread):
    updateUi_signal = pyqtSignal(list, list,list,float,str)
    def __init__(self):
        super(ProcessKML, self).__init__()


    def set_path(self, folderpath):
        self.kml_path = folderpath


    def run(self):
        if os.path.isfile(self.kml_path):
            f_d, d, thr, d_travelled = process_using_diff_method(self.kml_path)
            self.updateUi_signal.emit(f_d, d, thr, d_travelled, "Differentiation")
            f_d, d,thr,d_travelled = process_using_average_method(self.kml_path)
            self.updateUi_signal.emit(f_d,d,thr,d_travelled,"Average")
        elif os.path.isdir(self.kml_path):
            pass





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    try:
        sys.exit(app.exec_())
    except Exception as exp:
        print(exp)
        print("Exiting")