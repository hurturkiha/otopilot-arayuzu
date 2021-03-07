# created by Hurturk UAV Team (2021)
import datetime

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
from PyQt5 import QtTest, QtCore
from PyQt5.QtCore import *
from pyqtlet import *

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

        self.create_table()

        self.create_planning_map()
        self.ui.tw_menu.currentChanged.connect(self.changed_tab)

    ###############################################
    ##            HARİTA FONKSİYONLARI           ##
    ###############################################

    def create_planning_map(self):
        print("aaaa")
        self.planning_map_widget = MapWidget()
        self.ui.vbl_miniMap.addWidget(self.planning_map_widget)

        self.planning_map = L.map(self.planning_map_widget)
        self.planning_map.setView([40.215725, 29.080278], 18)

        self.tile_layer = L.tileLayer(
            'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}')
        self.tile_layer.addTo(self.planning_map)

    ###############################################
    ##             GUI FONKSİYONLARI             ##
    ###############################################

    def changed_tab(self, index):
        if index == 0:
            self.ui.vbl_miniMap.addWidget(self.planning_map_widget)
            self.planning_map.disconnect()
        elif index == 1:
            self.ui.vbl_planningMap.addWidget(self.planning_map_widget)
            self.planning_map.clicked.connect(self.add_marker)

    def create_table(self):
        self.ui.tw_waypoints.horizontalHeader().setVisible(True)
        self.ui.tw_waypoints.verticalHeader().setVisible(True)

        self.ui.tw_waypoints.setRowCount(1)
        self.ui.tw_waypoints.setColumnCount(9)

        self.ui.tw_waypoints.setHorizontalHeaderLabels(
            ['Komut', 'Param1', 'Param2', 'Param3', 'Param4',
             'Enlem', 'Boylam', 'İrtifa', 'Sil?'])

        self.ui.tw_waypoints.setColumnWidth(0, 110)
        self.ui.tw_waypoints.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.tw_waypoints.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.ui.tw_waypoints.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.ui.tw_waypoints.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.ui.tw_waypoints.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.ui.tw_waypoints.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.ui.tw_waypoints.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)
        self.ui.tw_waypoints.setColumnWidth(8, 50)
        self.ui.tw_waypoints.setItemDelegate(AlignDelegate())

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
    ##           HARİTA FONKSİYONLARI            ##
    ###############################################

    def add_marker(self):
        pass

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


class AlignDelegate(QItemDelegate):
    def paint(self, painter, option, index):
        option.displayAlignment = QtCore.Qt.AlignCenter
        QItemDelegate.paint(self, painter, option, index)
