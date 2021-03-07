from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from hurturk_gui import SplashScreen, HurturkGui
import sys


app = QApplication(sys.argv)
app.setStyle("Fusion")

splash_enabled = True

if splash_enabled:
    widget = SplashScreen()
else:
    widget = HurturkGui()

widget.setWindowTitle("Hürtürk Otopilot Arayüzü")
widget.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # title bar'ı kaldırır
widget.show()
sys.exit(app.exec_())
