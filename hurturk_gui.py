# created by Hurturk UAV Team (2021)
import datetime
import json
from collections import OrderedDict

import geopy.distance
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import *
from PyQt5 import QtTest, QtCore
from PyQt5.QtCore import *
from pyqtlet import *

from attitude_indicator import AttitudeIndicator
from autopilot import Autopilot
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
        self.ui.tw_menu.currentChanged.connect(self.changed_tab)
        self.oldPosition = self.window().pos()

        self.ui.bt_close.clicked.connect(self.close_window)
        # self.ui.bt_maximize.clicked.connect(self.maximize_window)
        self.ui.bt_minimize.clicked.connect(self.minimize_window)
        self.ui.le_wpRadius.textChanged.connect(self.changed_wp_rad)
        self.ui.bt_saveToFile.clicked.connect(self.save_missions)
        self.ui.bt_loadFromFile.clicked.connect(self.load_missions)
        self.ui.cb_simulation.stateChanged.connect(self.isSimulation)
        self.ui.bt_connect.clicked.connect(self.connect_uav)

        # Parametre sekmesi widget olarak eklenir.
        self.parameters_widget = ParameterWidget()
        self.ui.vl_parameters.addWidget(self.parameters_widget)

        self.attitude_indicator_widget = AttitudeIndicator(self.ui)
        self.ui.vbl_hud.addWidget(self.attitude_indicator_widget)

        # Ekranda zaman göstermek üzere timer oluşturulur.
        show_time_timer = QTimer(self)
        show_time_timer.timeout.connect(self.show_time)
        show_time_timer.start(1000)
        self.show_time()

        self.create_table()
        self.create_planning_map()

        self.waypoints_id_no = 0
        self.geofence_id_no = 0
        self.polygon = None
        self.geofence_markers = []
        self.markers = OrderedDict()
        self.markers_lg = L.layerGroup()
        self.circles_lg = L.layerGroup()
        self.lines_lg = L.layerGroup()
        self.geofence_markers_lg = L.layerGroup()

        self.planning_map.addLayer(self.geofence_markers_lg)
        self.planning_map.addLayer(self.markers_lg)
        self.planning_map.addLayer(self.circles_lg)
        self.planning_map.addLayer(self.lines_lg)

        self.ui.cb_geofenceOnOff.stateChanged.connect(self.is_geofence_on_off)
        self.ui.bt_clearMap.clicked.connect(lambda: self.clear_map(is_markers_clear=True))
        self.ui.bt_clearGeofence.clicked.connect(self.clear_geofence)
        self.ui.bt_completeGeofence.clicked.connect(self.complete_geofence)

        self.dronekit_widget = None

        self.ui.le_roll.textChanged.connect(self.changed_roll)
        self.ui.le_pitch.textChanged.connect(self.changed_pitch)

    ###############################################
    ##             GUI FONKSİYONLARI             ##
    ###############################################

    def isSimulation(self, index):
        if index == 0:
            self.ui.sw_connectionCB.setCurrentIndex(1)
        else:
            self.ui.sw_connectionCB.setCurrentIndex(0)

    def connect_uav(self):
        if self.ui.bt_connect.text() == "Bağlan":

            if self.ui.cb_simulation.isChecked():
                self.dronekit_widget = Autopilot(self.ui, self.markers, self.attitude_indicator_widget,
                                                 "tcp:"+self.ui.cb_connectionAdress.currentText()+":"+ self.ui.cb_port.currentText(),
                                                 self.planning_map)

                self.ui.bt_connect.setText("Bağlantıyı Kes")
                self.ui.bt_connect.setStyleSheet(
                    """
                    QPushButton {
                        box-shadow:inset 0px 1px 0px 0px #f29c93;
                        background:linear-gradient(to bottom, #fe1a00 5%, #ce0100 100%);
                        background-color: rgb(212, 0, 3);
                        border-radius:6px;
                        border:1px solid rgb(212, 0, 3);
                        display:inline-block;
                        cursor:pointer;
                        color:#ffffff;
                        font-family:Arial;
                        font-size:12px;
                        font-weight:bold;
                        text-decoration:none;
                        text-shadow:0px 1px 0px #b23e35;
                    }
                    QPushButton:hover {
                        background:linear-gradient(to bottom, #ce0100 5%, #fe1a00 100%);
                        background-color: rgb(191, 0, 3);
                    }
                    QPushButton:active {
                        position:relative;
                        top:1px;
                    }
                    """
                )
        else:
            self.dronekit_widget.vehicle.close()

            self.ui.bt_connect.setText("Bağlan")
            self.ui.bt_connect.setStyleSheet(
                """
                QPushButton {
                    box-shadow:inset 0px 1px 0px 0px #f29c93;
                    background:linear-gradient(to bottom, #fe1a00 5%, #ce0100 100%);
                    background-color: rgb(54, 161, 30);
                    border-radius:6px;
                    border:1px solid rgb(54, 161, 30);
                    display:inline-block;
                    cursor:pointer;
                    color:#ffffff;
                    font-family:Arial;
                    font-size:12px;
                    font-weight:bold;
                    text-decoration:none;
                    text-shadow:0px 1px 0px #b23e35;
                }
                QPushButton:hover {
                    background:linear-gradient(to bottom, #ce0100 5%, #fe1a00 100%);
                    background-color: rgb(54, 140, 30);
                }
                QPushButton:active {
                    position:relative;
                    top:1px;
                }
                """
            )

    def save_missions(self):
        if len(self.markers.keys()) == 0:
            QMessageBox.warning(self, "Hata", "Önce görev atasana kardeşim.")
        else:
            dialog = QFileDialog()
            dialog.setDefaultSuffix(".json")
            file = dialog.getSaveFileName(None, "Görevi kaydetmek için yol seçin", "", "JSON (*.json)")

            if file:
                wp_list = []

                for tmp_dict in self.markers.values():
                    temp_markers = {}
                    for key in tmp_dict:
                        if key not in ["marker", "circle", "row_no", "wp_rad"]:
                            temp_markers[key] = tmp_dict[key]
                    wp_list.append(temp_markers)

                if file[0].rfind('.') == -1:
                    with open(f'{file[0]}.json', 'w') as json_file:
                        json.dump(wp_list, json_file, indent=2)
                else:
                    with open(file[0], 'w') as json_file:
                        json.dump(wp_list, json_file, indent=2)

    def load_missions(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix(".json")
        file = dialog.getOpenFileName(None, "Görev yüklemek için JSON dosyası seçin", "", "JSON (*.json)")

        if file:
            with open(file[0]) as f:
                data = json.load(f)

            self.clear_map()
            self.draw_all_markers(values=data)

    def changed_tab(self, index):
        if index == 0:
            self.ui.vbl_miniMap.addWidget(self.planning_map_widget)
            self.planning_map.disconnect()
        elif index == 1:
            self.ui.vbl_planningMap.addWidget(self.planning_map_widget)
            self.planning_map.clicked.connect(self.add_marker)

    def is_geofence_on_off(self, index):
        if index == 2:
            self.planning_map.clicked.disconnect()
            self.planning_map.clicked.connect(self.add_geofence_marker)
        elif index == 0:
            self.planning_map.clicked.disconnect()
            self.planning_map.clicked.connect(self.add_marker)

    def changed_wp_rad(self, new_wp_radius):
        for marker in self.markers.values():
            marker["wp_rad"] = new_wp_radius
            self.circles_lg.removeLayer(marker["circle"])
            marker["circle"] = L.circle([marker["enlem"], marker["boylam"]],
                                        {'radius': self.ui.le_wpRadius.text(), 'color': 'white', 'fillOpacity': 0.1,
                                         'weight': 2})
            self.circles_lg.addLayer(marker["circle"])

    def selected_mission(self, new_mission):
        mission_select = self.sender().objectName()
        list(self.markers.values())[int(mission_select[mission_select.rfind('_') + 1:])]["komut"] = new_mission

        if new_mission in ["TAKEOFF", "LAND"]:
            self.planning_map.runJavaScript(
                f'''markerIcon = L.divIcon({{
                                            className: 'icon',
                                            html: '<div style="width: 30px; height: 50px; display: flex; align-items: center; justify-content: center; \
                                                    position: absolute; top: -310%; left: -78%;"> \
                                                    <div style="width: 30px; height: 50px; position: absolute;"> \
                                                        <img src="https://lh3.googleusercontent.com/MReUGcoXc4E7XpgQF58MKGwdMCVz19m3Jpwt1IHortJT-nB4-RzPLr3nsXmcfYXyl-A1QvxD3zcU_kUNM8g2OjcE5Rge3AZWG8c9r4ISSFz76qBwHkZ5pCSMvM8JNBqiymUpwluT7Q=w2400" style="width:30px;"> \
                                                    </div> \
                                                    <span style="color: black; font-size: 13px; z-index: 2; position: absolute; top: 4px;">{new_mission[0]}</span> \
                                                  </div>'
                                        }});
                                        {list(self.markers.values())[int(mission_select[mission_select.rfind('_') + 1:])]["marker"].jsName}.setIcon(markerIcon);
                                        '''
            )
        else:
            self.planning_map.runJavaScript(
                f'''markerIcon = L.divIcon({{
                                                        className: 'icon',
                                                        html: '<div style="width: 30px; height: 50px; display: flex; align-items: center; justify-content: center; \
                                                                position: absolute; top: -310%; left: -78%;"> \
                                                                <div style="width: 30px; height: 50px; position: absolute;"> \
                                                                    <img src="https://lh3.googleusercontent.com/MReUGcoXc4E7XpgQF58MKGwdMCVz19m3Jpwt1IHortJT-nB4-RzPLr3nsXmcfYXyl-A1QvxD3zcU_kUNM8g2OjcE5Rge3AZWG8c9r4ISSFz76qBwHkZ5pCSMvM8JNBqiymUpwluT7Q=w2400" style="width:30px;"> \
                                                                </div> \
                                                                <span style="color: black; font-size: 13px; z-index: 2; position: absolute; top: 4px;">{list(self.markers.values())[int(mission_select[mission_select.rfind('_') + 1:])]["row_no"]}</span> \
                                                              </div>'
                                                    }});
                                                    {list(self.markers.values())[int(mission_select[mission_select.rfind('_') + 1:])]["marker"].jsName}.setIcon(markerIcon);
                                                    '''
            )

        """
        mission_select = self.sender().objectName()
        list(self.markers.values())[int(mission_select[mission_select.rfind('_') + 1:])]["komut"] = new_mission
         self.clear_map(is_markers_clear=False)
        self.draw_all_markers()
        
        """

    def create_table(self):
        horizontal_header = self.ui.tw_waypoints.horizontalHeader()
        horizontal_header.setHighlightSections(False)
        self.ui.tw_waypoints.setColumnWidth(0, 50)
        self.ui.tw_waypoints.setColumnWidth(1, 110)
        self.ui.tw_waypoints.setColumnWidth(2, 60)
        self.ui.tw_waypoints.setColumnWidth(3, 60)
        self.ui.tw_waypoints.setColumnWidth(4, 60)
        self.ui.tw_waypoints.setColumnWidth(5, 60)
        self.ui.tw_waypoints.setColumnWidth(6, 70)
        self.ui.tw_waypoints.setColumnWidth(7, 70)
        self.ui.tw_waypoints.setColumnWidth(8, 60)
        self.ui.tw_waypoints.setColumnWidth(9, 63)

        vertical_header = self.ui.tw_waypoints.verticalHeader()
        vertical_header.hide()

        self.ui.tw_waypoints.setRowCount(1)

    def show_time(self):
        now_time = datetime.datetime.now()
        self.ui.lb_date.setText(now_time.strftime("%d %b %Y %H:%M:%S"))

        comp_date = datetime.datetime(2021, 9, 13)
        delta1 = comp_date - now_time

        report_result_date = datetime.datetime(2021, 4, 5)
        delta2 = report_result_date - now_time

        self.ui.lb_status.setText(
            f"Yarışmaya <b>{delta1.days} gün</b>, kavramsal tasarım rapor sonucunun açıklanmasına ise <b>{delta2.days} gün</b> kaldı.")

    ###############################################
    ##           HARİTA FONKSİYONLARI            ##
    ###############################################

    def change_attitude(self):
        self.changed_pitch()
        self.changed_roll()

    def changed_pitch(self):
        pitch_deg = float(self.ui.le_pitch.text())

        self.attitude_indicator_widget.angles["pitch"] = pitch_deg

        self.attitude_indicator_widget.rotate_pitch()
        self.attitude_indicator_widget.rotate_background()

    def changed_roll(self):
        roll_deg = float(self.ui.le_roll.text())
        self.attitude_indicator_widget.angles["roll"] = roll_deg
        self.attitude_indicator_widget.rotate_roll()
        self.attitude_indicator_widget.rotate_background()

    ###############################################
    ##           HARİTA FONKSİYONLARI            ##
    ###############################################

    def create_planning_map(self):
        self.planning_map_widget = MapWidget()
        self.ui.vbl_miniMap.addWidget(self.planning_map_widget)

        self.planning_map = L.map(self.planning_map_widget)
        self.planning_map.setView([40.215725, 29.080278], 18)

        self.tile_layer = L.tileLayer(
            'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}')
        self.tile_layer.addTo(self.planning_map)

    def add_marker(self, point, mission="WAYPOINT", param1="", param2="", param3="", param4="", irtifa=0):
        marker_ok = True

        for marker_id, dict in self.markers.items():
            if geopy.distance.distance([point['latlng']['lat'], point['latlng']['lng']],
                                       [float(dict["enlem"]), float(dict["boylam"])]).m < float(
                self.ui.le_wpRadius.text()):
                marker_ok = False

        if marker_ok:
            self.marker = L.marker(point['latlng'])
            circle = L.circle(point['latlng'],
                              {'radius': self.ui.le_wpRadius.text(), 'color': 'white', 'fillOpacity': 0.1,
                               'weight': 2})  # kesikli yapmak için 'dashArray': '3, 20' ekle

            # TODO: BU KISIMDA RESMİN ABSOLUTE PATH OLMASINA BİR ÇÖZÜM BUL
            self.planning_map.runJavaScript(
                f'''markerIcon = L.divIcon({{
                                    className: 'icon',
                                    html: '<div style="width: 30px; height: 50px; display: flex; align-items: center; justify-content: center; \
                                            position: absolute; top: -310%; left: -78%;"> \
                                            <div style="width: 30px; height: 50px; position: absolute;"> \
                                                <img src="https://lh3.googleusercontent.com/MReUGcoXc4E7XpgQF58MKGwdMCVz19m3Jpwt1IHortJT-nB4-RzPLr3nsXmcfYXyl-A1QvxD3zcU_kUNM8g2OjcE5Rge3AZWG8c9r4ISSFz76qBwHkZ5pCSMvM8JNBqiymUpwluT7Q=w2400" style="width:30px;"> \
                                            </div> \
                                            <span style="color: black; font-size: 13px; z-index: 2; position: absolute; top: 4px;">{self.waypoints_id_no if mission == "WAYPOINT" else mission[0]}</span> \
                                          </div>'
                                }});
                                {self.marker.jsName}.setIcon(markerIcon);
                                ''')

            self.marker.layerId = f"m_{self.waypoints_id_no}"
            self.markers_lg.addLayer(self.marker)
            self.circles_lg.addLayer(circle)

            self.markers[self.marker.layerId] = {"marker": self.marker,
                                                 "circle": circle,
                                                 "row_no": len(self.markers.keys()),
                                                 "komut": mission,
                                                 "param1": param1,
                                                 "param2": param2,
                                                 "param3": param3,
                                                 "param4": param4,
                                                 "wp_rad": int(self.ui.le_wpRadius.text()),
                                                 "irtifa": irtifa if irtifa != 0 else int(self.ui.le_defaultAlt.text()),
                                                 "enlem": point['latlng']['lat'],
                                                 "boylam": point['latlng']['lng'],
                                                 }

            mission_selection = QComboBox()
            mission_selection.setObjectName(f"ms_{self.waypoints_id_no}")
            missions = ['TAKEOFF', 'WAYPOINT', 'LAND']
            mission_selection.addItems(missions)
            mission_selection.setCurrentText(mission)
            mission_selection.currentTextChanged.connect(self.selected_mission)

            delete_button = QPushButton()
            delete_button.setStyleSheet("""QPushButton {border: none;} QPushButton::hover {background-color: red;}""")
            delete_button.setText('X')
            delete_button.setObjectName(f'bt_{self.waypoints_id_no}')
            delete_button.clicked.connect(self.delete_marker)

            self.ui.tw_waypoints.setRowCount(len(self.markers.keys()))
            self.ui.tw_waypoints.setItem(len(self.markers.keys()) - 1, 0,
                                         QTableWidgetItem(str(self.markers[self.marker.layerId]["row_no"])))
            self.ui.tw_waypoints.setCellWidget(len(self.markers.keys()) - 1, 1, mission_selection)
            self.ui.tw_waypoints.setItem(len(self.markers.keys()) - 1, 2,
                                         QTableWidgetItem(self.markers[self.marker.layerId]["param1"]))
            self.ui.tw_waypoints.setItem(len(self.markers.keys()) - 1, 3,
                                         QTableWidgetItem(self.markers[self.marker.layerId]["param2"]))
            self.ui.tw_waypoints.setItem(len(self.markers.keys()) - 1, 4,
                                         QTableWidgetItem(self.markers[self.marker.layerId]["param3"]))
            self.ui.tw_waypoints.setItem(len(self.markers.keys()) - 1, 5,
                                         QTableWidgetItem(self.markers[self.marker.layerId]["param4"]))
            self.ui.tw_waypoints.setItem(len(self.markers.keys()) - 1, 6,
                                         QTableWidgetItem(f'{self.markers[self.marker.layerId]["enlem"]:.4f}'))
            self.ui.tw_waypoints.setItem(len(self.markers.keys()) - 1, 7,
                                         QTableWidgetItem(f'{self.markers[self.marker.layerId]["boylam"]:.4f}'))
            self.ui.tw_waypoints.setItem(len(self.markers.keys()) - 1, 8,
                                         QTableWidgetItem(str(self.markers[self.marker.layerId]["irtifa"])))
            self.ui.tw_waypoints.setCellWidget(len(self.markers.keys()) - 1, 9, delete_button)

            self.ui.tw_waypoints.item(len(self.markers.keys()) - 1, 0).setTextAlignment(Qt.AlignCenter)
            self.ui.tw_waypoints.item(len(self.markers.keys()) - 1, 2).setTextAlignment(Qt.AlignCenter)
            self.ui.tw_waypoints.item(len(self.markers.keys()) - 1, 3).setTextAlignment(Qt.AlignCenter)
            self.ui.tw_waypoints.item(len(self.markers.keys()) - 1, 4).setTextAlignment(Qt.AlignCenter)
            self.ui.tw_waypoints.item(len(self.markers.keys()) - 1, 5).setTextAlignment(Qt.AlignCenter)
            self.ui.tw_waypoints.item(len(self.markers.keys()) - 1, 6).setTextAlignment(Qt.AlignCenter)
            self.ui.tw_waypoints.item(len(self.markers.keys()) - 1, 6).setFlags(Qt.ItemIsEditable)
            self.ui.tw_waypoints.item(len(self.markers.keys()) - 1, 7).setTextAlignment(Qt.AlignCenter)
            self.ui.tw_waypoints.item(len(self.markers.keys()) - 1, 7).setFlags(Qt.ItemIsEditable)
            self.ui.tw_waypoints.item(len(self.markers.keys()) - 1, 8).setTextAlignment(Qt.AlignCenter)

            if len(self.markers.items()) > 1:
                self.draw_polyline()

            self.waypoints_id_no += 1

    def delete_marker(self):
        # TODO: ROW NO İLE BİRLİKTE SÖZLÜKTEN AYNI SIRADAKİNİ SİL.
        button = self.sender()
        marker_id = f"m_{int(button.objectName()[button.objectName().rfind('_') + 1:])}"

        for i in range(self.markers[marker_id]["row_no"] + 1, self.ui.tw_waypoints.rowCount()):
            for id, dict in self.markers.items():
                if dict["row_no"] == i:
                    dict["row_no"] -= 1

        self.ui.tw_waypoints.removeRow(self.markers[marker_id]["row_no"])
        del self.markers[marker_id]

        self.clear_map(is_markers_clear=False)
        self.draw_all_markers()

        if self.ui.tw_waypoints.rowCount() == 0:
            self.ui.tw_waypoints.setRowCount(1)

        self.draw_polyline()

    def draw_all_markers(self, values=None):

        if values:
            tmp_dict = values
        else:
            tmp_dict = self.markers.copy().values()
            self.markers.clear()

        for tmp_marker in tmp_dict:
            coord = {'latlng': {'lat': tmp_marker["enlem"], 'lng': tmp_marker["boylam"]}}
            self.add_marker(coord, tmp_marker["komut"])

    def draw_polyline(self):
        self.lines_lg.clearLayers()

        tmp_marker_list = list(self.markers.items())
        for i in range(len(tmp_marker_list) - 1):
            polyline = L.polyline([tmp_marker_list[i][1]["marker"].latLng, tmp_marker_list[i + 1][1]["marker"].latLng],
                                  {'color': 'yellow'})
            polyline.bindTooltip(
                f"{geopy.distance.distance(polyline.latLngs[0].values(), polyline.latLngs[1].values()).m:.3f} metre")
            self.lines_lg.addLayer(polyline)

    def clear_map(self, is_markers_clear=True):
        self.markers_lg.clearLayers()
        self.circles_lg.clearLayers()
        self.lines_lg.clearLayers()
        if is_markers_clear:
            self.markers.clear()
            self.ui.tw_waypoints.clearContents()
            self.ui.tw_waypoints.setRowCount(1)
        self.waypoints_id_no = 0

    def add_geofence_marker(self, point):
        marker = L.marker(point['latlng'])

        # TODO: BU KISIMDA RESMİN ABSOLUTE PATH OLMASINA BİR ÇÖZÜM BUL
        self.planning_map.runJavaScript(
            f'''markerIcon = L.divIcon({{
                                            className: 'icon',
                                            html: '<div style="width: 30px; height: 50px; display: flex; align-items: center; justify-content: center; \
                                                    position: absolute; top: -310%; left: -78%;"> \
                                                    <div style="width: 30px; height: 50px; position: absolute;"> \
                                                        <img src="https://lh3.googleusercontent.com/EhOwwR58k5xYmkolDznNYglOqd-UBjBBi6qaj5BHJTTg_5r7aTuaIL2xUzIXVDkMrraGa4osRIMrPlFy9tnqOa4hpdptLV_GfaiBFWrhsPGPtLHeqaHeZPMoplV7VAHb6-kSLgD20g=w2400" style="width:30px;"> \
                                                    </div> \
                                                    <span style="color: black; font-size: 13px; z-index: 2; position: absolute; top: 4px;">{self.geofence_id_no}</span> \
                                                  </div>'
                                        }});
                                        {marker.jsName}.setIcon(markerIcon);
                                        '''
        )

        marker.layerId = f"g_{self.waypoints_id_no}"

        self.geofence_markers_lg.addLayer(marker)
        self.geofence_markers.append(list(marker.latLng.values()))
        self.geofence_id_no += 1

    def clear_geofence(self):
        self.geofence_markers_lg.clearLayers()
        self.geofence_markers.clear()
        if self.polygon:
            self.planning_map.removeLayer(self.temp)

        self.geofence_id_no = 0
        self.ui.cb_geofenceOnOff.setDisabled(False)
        self.polygon = None

    def complete_geofence(self):
        if len(self.geofence_markers) == 0:
            QMessageBox.warning(self, "Hata", "Önce çizsene kardeşim.")
        else:
            if self.polygon is None:
                self.geofence_markers_lg.clearLayers()
                self.polygon = L.polygon(self.geofence_markers)
                self.planning_map.addLayer(self.polygon)
                self.ui.cb_geofenceOnOff.setChecked(False)
                self.ui.cb_geofenceOnOff.setDisabled(True)
                self.temp = self.polygon

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

