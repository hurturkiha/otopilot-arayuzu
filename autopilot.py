import math

import dronekit as dronekit
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QMessageBox, QMainWindow
from pyqtlet import L

class Autopilot(QMainWindow):
    def __init__(self, ui, markers, attitude_indicator, map, clear_map):
        super().__init__()
        self.clear_map = clear_map
        self.ui = ui
        self.map = map
        self.markers_dict = markers
        self.attitude_indicator = attitude_indicator

        self.uav_marker = None
        self.our_uav = None

        self.location_list = []

        self.ui.bt_connect.clicked.connect(self.connection)
        self.followerline_lg = L.layerGroup()
        self.map.addLayer(self.followerline_lg)

    def connection(self):
        if self.ui.bt_connect.text() == "Bağlan":
            if self.ui.cb_simulation.isChecked():
                try:
                    self.our_uav = dronekit.connect(
                        "tcp:" + self.ui.cb_connectionAdress.currentText() + ":" + self.ui.cb_port.currentText(),
                        baud=115200, wait_ready=True)
                    self.connect_uav()

                    # self.our_uav.add_attribute_listener('location.global_relative_frame',
                    #                                    self.location_callback)
                    self.our_uav.add_attribute_listener('gps_0', self.gpsinfo_callback)
                    self.our_uav.add_attribute_listener('attitude', self.attitude_callback)
                    # self.our_uav.add_attribute_listener('airspeed', self.speed_callback)
                    # self.our_uav.add_attribute_listener('groundspeed', self.speed_callback)
                    # self.our_uav.add_attribute_listener('mode', self.mode_callback)

                except:
                    QMessageBox.warning(self, "Hata", "Bağlantı kurulamadı!")
                    self.disconnect_uav()
            else:
                print(self.ui.cb_connectionType.currentText())
                try:
                    self.our_uav = dronekit.connect(
                        self.ui.cb_connectionType.currentText(),
                        baud=int(self.ui.cb_baudRate.currentText()), wait_ready=True)
                    self.connect_uav()

                    # self.our_uav.add_attribute_listener('location.global_relative_frame',
                    #                                     self.location_callback)
                    self.our_uav.add_attribute_listener('gps_0', self.gpsinfo_callback)
                    self.our_uav.add_attribute_listener('attitude', self.attitude_callback)
                    # self.our_uav.add_attribute_listener('airspeed', self.speed_callback)
                    # self.our_uav.add_attribute_listener('groundspeed', self.speed_callback)
                    # self.our_uav.add_attribute_listener('mode', self.mode_callback)

                except:
                    QMessageBox.warning(self, "Hata", "Bağlantı kurulamadı!")
                    self.disconnect_uav()
        else:
            self.disconnect_uav()

    def connect_uav(self):
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

        self.home_point = [self.our_uav.location.global_relative_frame.lat,
                           self.our_uav.location.global_relative_frame.lon]

        self.uav_marker = L.marker(self.home_point)
        self.map.runJavaScript(
            f'''markerIcon = L.divIcon({{
                                                                    className: 'icon',
                                                                    html: '<div style="width: 30px; height: 50px; display: flex; align-items: center; justify-content: center; \
                                                                            position: absolute; top: -310%; left: -78%;"> \
                                                                            <div style="width: 30px; height: 50px; position: absolute;"> \
                                                                                <img src="https://lh3.googleusercontent.com/KUsDClFxzDHn0UTH45q0-D7K-mYfh5U0q3AhmV63OFrR-9YMQG-wHCgxOfbxGyA33NQfAr51FEsA8nrjW9GCLbDCb-hZxXVQJt8iHKzGa0lvkxqpOBThtWNKIjjl3jCUIpKOCccgVw=w2400" style="width:30px; transform: rotate({round(self.our_uav.attitude.yaw * 180 / math.pi)}deg);"> \
                                                                            </div> \
                                                                            <span style="color: black; font-size: 13px; z-index: 2; position: absolute; top: 4px;"></span> \
                                                                          </div>'
                                                                }});
                                                                {self.uav_marker.jsName}.setIcon(markerIcon);
                                                                ''')

        self.map.addLayer(self.uav_marker)
        self.map.setView(
            [self.our_uav.location.global_relative_frame.lat, self.our_uav.location.global_relative_frame.lon])

        self.ui.le_flightMode.setText(str(self.our_uav.mode.name))

    def clear_line_edits(self):
        self.ui.le_lat.setText("")
        self.ui.le_lng.setText("")
        self.ui.le_alt.setText("")
        self.ui.le_groundSpeed.setText("")
        self.ui.le_airSpeed.setText("")
        self.ui.le_roll.setText("")
        self.ui.le_pitch.setText("")
        self.ui.le_yaw.setText("")
        self.ui.le_sat.setText("")

    def disconnect_uav(self):
        if self.our_uav:
            self.map.removeLayer(self.uav_marker)
            self.clear_map()
            self.clear_line_edits()
            self.our_uav.close()

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
                font-family:Ubuntu;
                font-size:15px;
                font-weight:bold;
                text-decoration:none;
                text-shadow:0px 1px 0px #b23e35;
            }
            QPushButton:hover {
                background:linear-gradient(to bottom, #ce0100 5%, #fe1a00 100%);
                background-color: rgb(54, 141, 30);
            }
            QPushButton:active {
                position:relative;
                top:1px;
            }
            """
        )

    def location_callback(self, vehicle, attr_name, value):

        self.ui.le_lat.setText(f"{value.lat:.4f}")
        self.ui.le_lng.setText(f"{value.lon:.4f}")
        self.ui.le_alt.setText(f"{round(value.alt)}")

        self.uav_marker.setLatLng([value.lat, value.lon])
        self.map.runJavaScript(
            f'''markerIcon = L.divIcon({{
                                                        className: 'icon',
                                                        html: '<div style="width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; \
                                                                position: absolute; top: -62%; left: -66%"> \
                                                                <img src="https://lh3.googleusercontent.com/KUsDClFxzDHn0UTH45q0-D7K-mYfh5U0q3AhmV63OFrR-9YMQG-wHCgxOfbxGyA33NQfAr51FEsA8nrjW9GCLbDCb-hZxXVQJt8iHKzGa0lvkxqpOBThtWNKIjjl3jCUIpKOCccgVw=w2400" style="width:30px; transform: rotate({round(self.our_uav.attitude.yaw * 180 / math.pi)}deg);"> \
                                                              </div>'
                                                    }});
                                                    {self.uav_marker.jsName}.setIcon(markerIcon);
                                                    ''')

        if self.ui.cb_followUav.isChecked():
            self.map.setView([value.lat, value.lon])
    #
    #     if self.our_uav.armed:
    #         pass
    #         # self.location = [value.lat, value.lon]
    #         # self.location_list.append(self.location)
    #         #
    #         # polyline = L.polyline([self.location_list[-2], self.location_list[-1]], {'color': 'purple'})
    #         # self.followerline_lg.addLayer(polyline)
    #
    def gpsinfo_callback(self, vehicle, attr_name, value):
        self.ui.le_sat.setText(f"{value.satellites_visible}")

    def attitude_callback(self, vehicle, attr_name, value):
        self.ui.le_roll.setText(f"{value.roll * 180 / math.pi:.4f}")
        self.ui.le_pitch.setText(f"{value.pitch * 180 / math.pi:.4f}")
        self.ui.le_yaw.setText(f"{value.yaw * 180 / math.pi:.4f}")

        if self.our_uav.armed:
            self.attitude_indicator.ui.lb_armStatus.setText("ARMED")
        else:
            self.attitude_indicator.ui.lb_armStatus.setText("DISARMED")

    # def mode_callback(self, vehicle, attr_name, value):
    #     self.ui.le_flightMode.setText(str(vehicle.mode.name))
    #
    # def speed_callback(self, vehicle, attr_name, value):
    #     if attr_name == "airspeed":
    #         self.ui.le_airSpeed.setText(f"{value:.2f}")
    #     else:
    #         self.ui.le_groundSpeed.setText(f"{value:.2f}")
    #
    #     image = QPixmap(":/hud/icons/speed-indicator-tick.png")
    #     canvas = QPixmap(image.size())
    #     canvas2 = QPixmap(image.size())
    #
    #     canvas.fill(QtCore.Qt.transparent)
    #     canvas2.fill(QtCore.Qt.transparent)
    #
    #     p = QPainter(canvas)
    #     p2 = QPainter(canvas2)
    #
    #     p.setRenderHint(QPainter.Antialiasing)
    #     p.setRenderHint(QPainter.SmoothPixmapTransform)
    #     p.setRenderHint(QPainter.HighQualityAntialiasing)
    #     p.translate(canvas.size().width() / 2, canvas.size().height() / 2)
    #     p2.setRenderHint(QPainter.Antialiasing)
    #     p2.setRenderHint(QPainter.SmoothPixmapTransform)
    #     p2.setRenderHint(QPainter.HighQualityAntialiasing)
    #     p2.translate(canvas2.size().width() / 2, canvas2.size().height() / 2)
    #
    #     if self.ui.le_groundSpeed.text() == '' or self.ui.le_airSpeed.text() == '':
    #         p.rotate(0)
    #         p2.rotate(0)
    #     else:
    #         p.rotate(4.5 * float(self.ui.le_groundSpeed.text()))
    #         p2.rotate(4.5 * float(self.ui.le_airSpeed.text()))
    #
    #     p.translate(-canvas.size().width() / 2, -canvas.size().height() / 2)
    #     p.drawPixmap(0, 0, image)
    #     p2.translate(-canvas.size().width() / 2, -canvas.size().height() / 2)
    #     p2.drawPixmap(0, 0, image)
    #
    #     p.end()
    #     p2.end()
    #
    #     self.ui.lb_groundSpeedIndicatorTick.setPixmap(canvas)
    #     self.ui.lb_airSpeedIndicatorTick.setPixmap(canvas2)
    #
    # def set_auto_mode(self):
    #     self.vehicle.mode = dronekit.VehicleMode('AUTO')
    #
    #     self.flight_timer.start(1000)
    #
    # def set_manual_mode(self):
    #     self.vehicle.mode = dronekit.VehicleMode('MANUAL')
    #
    # def set_loiter_mode(self):
    #     self.vehicle.mode = dronekit.VehicleMode('LOITER')
    #
    # def set_rtl_mode(self):
    #     self.vehicle.mode = dronekit.VehicleMode('RTL')
