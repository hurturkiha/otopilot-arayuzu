# created by Hurturk UAV Team (2021)
import datetime

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
from PyQt5 import QtTest
from PyQt5.QtCore import *

from parameters_widget import ParameterWidget

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

        # Başlangıçta ana sayfadan başlamayı sağlar.
        self.ui.tw_menu.setCurrentIndex(0)

        self.oldPosition = self.window().pos()

        # Pencere kontrol düğmelerinin tetikleyeceği fonksiyonları ayarlar.
        self.ui.bt_close.clicked.connect(self.close_window)
        # self.ui.bt_maximize.clicked.connect(self.maximize_window)
        self.ui.bt_minimize.clicked.connect(self.minimize_window)

        # Parametre sekmesi widget olarak eklenir.
        self.parameters_widget = ParameterWidget()
        self.ui.vl_parameters.addWidget(self.parameters_widget)

        # Ekranda zaman göstermek üzere timer oluşturulur.
        show_time_timer = QTimer(self)
        show_time_timer.timeout.connect(self.show_time)
        show_time_timer.start(1000)
        self.show_time()

    ###############################################
    ##          PENCERE ZAMAN GÖSTERGESİ         ##
    ###############################################

    def show_time(self):
        now_time = datetime.datetime.now()
        self.ui.lb_date.setText(now_time.strftime("%d %b %Y %H:%M:%S"))

        comp_date = datetime.datetime(2021, 9, 13)
        delta1 = comp_date - now_time

        report_result_date = datetime.datetime(2021, 3, 15)
        delta2 = report_result_date - now_time

        self.ui.lb_status.setText(
            f"Yarışmaya <b>{delta1.days} gün</b>, kavramsal tasarım rapor sonucunun açıklanmasına ise <b>{delta2.days} gün</b> kaldı.")

    ###############################################
    ##         PENCERE KONTROL DÜĞMELERİ         ##
    ###############################################

    def close_window(self):
        """Kapatma butonu ile pencereyi kapatır."""

        self.window().close()

    def minimize_window(self):
        """Ekran küçültme butonu ile pencereyi küçültür."""

        self.window().showMinimized()

    def maximize_window(self):
        """Tam ekran butonu ile pencereyi genişletir."""

        if self.isFullScreen():
            self.window().showNormal()
        else:
            self.window().showFullScreen()

    ###############################################
    ##   PENCERE HAREKET ETTİRME FONKSİYONLARI   ##
    ###############################################

    def mousePressEvent(self, event):
        """Pencereye tıklanınca taşımadan önce kordinatı alır."""

        self.oldPosition = event.globalPos()

    def mouseMoveEvent(self, event):
        """Pencere hareketini gerçekleştirir."""

        delta = QPoint(event.globalPos() - self.oldPosition)  # x ve y ekseninde kaydırılan mesafe
        self.window().move(self.window().x() + delta.x(), self.window().y() + delta.y())  # başlangıç noktası kaydırılır
        self.oldPosition = event.globalPos()
