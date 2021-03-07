# created by Hurturk UAV Team (2021)

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
from PyQt5 import QtTest
from PyQt5.QtCore import *

import splash_design_ui
import design_ui


class SplashScreen(QMainWindow):
    """
    Bu sınıf yükleme ekranını oluşturur.
    Timer vasıtasıyla da yükleme animasyonu oynatılır.
    """

    def __init__(self):
        super().__init__()

        self.ui = splash_design_ui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.progress_value = 0
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.progress_animation)
        self.progress_timer.start(100)

    def progress_animation(self):
        """Arayüzün yükleme animasyonunu gerçekleştirir ve arayüzü oluşturur."""
        if self.progress_value <= 100:
            self.ui.progressBar.setValue(self.progress_value)
            self.progress_value += 10
        else:
            self.progress_timer.stop()
            QtTest.QTest.qWait(200)
            self.centralWidget().deleteLater()

            widget = HurturkGui()
            self.layout().addWidget(widget)
            self.show()


class HurturkGui(QMainWindow):
    """
    Bu sınıf, yükleme ekranı sonrası arayüzü oluşturur.
    """

    def __init__(self):
        super().__init__()

        self.ui = design_ui.Ui_MainWindow()
        self.ui.setupUi(self)
