import math

import dronekit
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox
from pyqtlet import L
from pymavlink import mavutil


class Autopilot():
    def __init__(self, ui, markers, connection_address, map):
        super().__init__()

        self.ui = ui
        self.map = map
        self.markers_dict = markers

        self.location_list = []

        self.followerline_lg = L.layerGroup()
        self.map.addLayer(self.followerline_lg)

        try:
            self.vehicle = dronekit.connect('tcp:127.0.0.1:14550')
        except:
            print("Bağlantı kurulamadı!")

        self.home_point = [self.vehicle.location.global_relative_frame.lat,
                           self.vehicle.location.global_relative_frame.lon]

        self.vehicle_marker = L.marker(self.home_point)
        self.map.runJavaScript(
            f'''markerIcon = L.divIcon({{
                                                    className: 'icon',
                                                    html: '<div style="width: 30px; height: 50px; display: flex; align-items: center; justify-content: center; \
                                                            position: absolute; top: -310%; left: -78%;"> \
                                                            <div style="width: 30px; height: 50px; position: absolute;"> \
                                                                <img src="https://lh3.googleusercontent.com/KUsDClFxzDHn0UTH45q0-D7K-mYfh5U0q3AhmV63OFrR-9YMQG-wHCgxOfbxGyA33NQfAr51FEsA8nrjW9GCLbDCb-hZxXVQJt8iHKzGa0lvkxqpOBThtWNKIjjl3jCUIpKOCccgVw=w2400" style="width:30px; transform: rotate({round(self.vehicle.attitude.yaw * 180 / math.pi)}deg);"> \
                                                            </div> \
                                                            <span style="color: black; font-size: 13px; z-index: 2; position: absolute; top: 4px;"></span> \
                                                          </div>'
                                                }});
                                                {self.vehicle_marker.jsName}.setIcon(markerIcon);
                                                ''')

        self.map.addLayer(self.vehicle_marker)
        self.map.setView(
            [self.vehicle.location.global_relative_frame.lat, self.vehicle.location.global_relative_frame.lon])

        self.ui.bt_arm.clicked.connect(self.set_armdisarm)
        self.ui.bt_autoMode.clicked.connect(self.set_auto_mode)
        self.ui.bt_manualMode.clicked.connect(self.set_manual_mode)
        self.ui.bt_loiterMode.clicked.connect(self.set_loiter_mode)
        self.ui.bt_rtlMode.clicked.connect(self.set_rtl_mode)
        self.ui.bt_loadFlightToUAV.clicked.connect(self.add_command)
        self.ui.bt_clearTrack.clicked.connect(self.clear_track)

        self.vehicle.add_attribute_listener('location.global_relative_frame',
                                            self.location_callback)
        self.vehicle.add_attribute_listener('gps_0', self.gpsinfo_callback)
        self.vehicle.add_attribute_listener('attitude', self.attitude_callback)
        self.vehicle.add_attribute_listener('airspeed', self.speed_callback)
        self.vehicle.add_attribute_listener('groundspeed', self.speed_callback)
        self.vehicle.add_attribute_listener('mode', self.mode_callback)

        self.ui.le_flightMode.setText(str(self.vehicle.mode.name))

    def add_command(self):
        cmds = self.vehicle.commands
        cmds.clear()

        for mission in self.markers_dict.values():
            if mission["komut"] == "TAKEOFF":
                cmds.add(dronekit.Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                 mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0,
                                 0, 0, 0, mission["enlem"],
                                 mission["boylam"],
                                 mission["irtifa"]))
            elif mission["komut"] == "LAND":
                cmds.add(dronekit.Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                 mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0,
                                 0, 0, 0, mission["enlem"],
                                 mission["boylam"],
                                 mission["irtifa"]))
            elif mission["komut"] == "WAYPOINT":
                cmds.add(dronekit.Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                 mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0,
                                 0, 0, 0, mission["enlem"],
                                 mission["boylam"],
                                 mission["irtifa"]))
        cmds.upload()
        self.vehicle.commands.next = 0

    def clear_track(self):
        self.followerline_lg.clearLayers()

    def mode_callback(self, vehicle, attr_name, value):
        self.ui.le_flightMode.setText(str(vehicle.mode.name))

    def speed_callback(self, vehicle, attr_name, value):
        if attr_name == "airspeed":
            self.ui.le_airSpeed.setText(f"{value:.2f}")
        else:
            self.ui.le_groundSpeed.setText(f"{value:.2f}")

    def attitude_callback(self, vehicle, attr_name, value):
        self.ui.le_roll.setText(f"{value.roll * 180 / math.pi:.4f}")
        self.ui.le_pitch.setText(f"{value.pitch * 180 / math.pi:.4f}")
        self.ui.le_yaw.setText(f"{value.yaw * 180 / math.pi:.4f}")
        # if self.vehicle.armed:
        #     self.attitude_indicator.ui.lb_armStatus.setText("ARMED")
        # else:
        #     self.attitude_indicator.ui.lb_armStatus.setText("DISARMED")

    def gpsinfo_callback(self, vehicle, attr_name, value):
        self.ui.le_sat.setText(f"{value.satellites_visible}")

    def set_armdisarm(self):
        if self.ui.bt_arm.text() == "Arm":
            self.vehicle.armed = True
            self.ui.bt_arm.setText("Disarm")
        else:
            self.vehicle.armed = False
            self.ui.bt_arm.setText("Arm")

    def set_auto_mode(self):
        self.vehicle.mode = 'AUTO'

    def set_manual_mode(self):
        self.vehicle.mode = 'MANUAL'

    def set_loiter_mode(self):
        self.vehicle.mode = 'LOITER'

    def set_rtl_mode(self):
        self.vehicle.mode = 'RTL'

    def location_callback(self, vehicle, attr_name, value):
        self.ui.le_lat.setText(f"{value.lat:.4f}")
        self.ui.le_lng.setText(f"{value.lon:.4f}")
        self.ui.le_alt.setText(f"{round(value.alt)}")

        self.vehicle_marker.setLatLng([value.lat, value.lon])
        self.map.runJavaScript(
                f'''markerIcon = L.divIcon({{
                                                        className: 'icon',
                                                        html: '<div style="width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; \
                                                                position: absolute; top: -62%; left: -66%"> \
                                                                <img src="https://lh3.googleusercontent.com/KUsDClFxzDHn0UTH45q0-D7K-mYfh5U0q3AhmV63OFrR-9YMQG-wHCgxOfbxGyA33NQfAr51FEsA8nrjW9GCLbDCb-hZxXVQJt8iHKzGa0lvkxqpOBThtWNKIjjl3jCUIpKOCccgVw=w2400" style="width:30px; transform: rotate({round(self.vehicle.attitude.yaw * 180 / math.pi)}deg);"> \
                                                              </div>'
                                                    }});
                                                    {self.vehicle_marker.jsName}.setIcon(markerIcon);
                                                    ''')

        if self.ui.cb_followUav.isChecked():
            self.map.setView([value.lat, value.lon])

        if self.vehicle.armed:
            self.location = [value.lat, value.lon]
            self.location_list.append(self.location)

            polyline = L.polyline([self.location_list[-2], self.location_list[-1]], {'color': 'purple'})
            self.followerline_lg.addLayer(polyline)