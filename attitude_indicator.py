import math
import random
import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import *
from indicator_design_ui import Ui_Form

class AttitudeIndicator(QWidget):

    def __init__(self, hurturk_ui):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.hurturk_ui = hurturk_ui

        canvas2 = QPixmap(200, 4)
        canvas2.fill(Qt.transparent)
        self.ui.lb_centerLine.setPixmap(canvas2)

        self.set_pointer()

        self.center_point = {"x": 150, "y": 155}
        self.equation = {"slope": 0, "bias": 0}

        self.angles = {"roll": 0, "pitch": 0, "yaw": 0}
        self.get_line_with_deg()

        self.i = 0

    def rotate_pitch(self):
        if self.angles["pitch"] >= 0:
            deg_to_pixel = 190 / 90 * self.angles["pitch"]
            self.center_point['y'] += deg_to_pixel
        elif self.angles["pitch"] < 0:
            deg_to_pixel = 190 / 90 * - self.angles["pitch"]
            self.center_point['y'] -= deg_to_pixel

        self.ui.lb_pitch.move(0, -295)
        self.ui.lb_pitch.move(self.ui.lb_pitch.x(), -295 + 190 / 90 * self.angles["pitch"])

    def rotate_roll(self):
        if self.angles["roll"] >= 0:
            if self.angles["roll"] > 60:
                self.angles["roll"] = 60
            else:
                self.angles["roll"] = self.angles["roll"]

        elif self.angles["roll"] < 0:
            if self.angles["roll"] < -60:
                self.angles["roll"] = 360 - 60
            else:
                self.angles["roll"] = 360 + self.angles["roll"]

        image = QPixmap(":/hud/icons/roll_bar.png")

        canvas = QPixmap(image.size())
        canvas.fill(Qt.transparent)

        p = QPainter(canvas)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.setRenderHint(QPainter.HighQualityAntialiasing)
        p.translate(canvas.size().width() / 2, canvas.size().height() / 2)
        p.rotate(-self.angles["roll"])
        p.translate(-canvas.size().width() / 2, -canvas.size().height() / 2)
        p.drawPixmap(0, 0, image)
        p.end()
        self.ui.lb_indicatorRoll.setPixmap(canvas)

    def rotate_background(self):
        self.center_point['y'] = 155 + self.angles["pitch"] * 2.1

        self.find_equation(self.center_point, - self.angles["roll"])

        self.draw_line(*self.get_points())
        self.fill_background(*self.get_points()[0], *self.get_points()[1])

    def get_line_with_deg(self):
        self.find_equation(self.center_point, self.angles["roll"])
        self.draw_line(*self.get_points())
        self.fill_background(*self.get_points()[0], *self.get_points()[1])

    def set_pointer(self):
        painter = QPainter(self.ui.lb_centerLine.pixmap())
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.red, 16, Qt.SolidLine))
        painter.drawLine(65, 0, 80, 0)
        painter.drawLine(120, 0, 135, 0)

    def find_equation(self, center_point, angle_of_deg):
        angle_of_rad = math.radians(angle_of_deg)
        try:
            self.equation["slope"] = math.tan(angle_of_rad)
            a = center_point["x"] - center_point["y"] / math.tan(angle_of_rad)
            self.equation["bias"] = math.tan(angle_of_rad) * -a
        except ZeroDivisionError:
            self.equation["slope"] = 0
            self.equation["bias"] = center_point["y"]

        # print(self.equation["slope"], "-", self.equation["bias"])

    def get_points(self):
        if self.angles["roll"]== 90:
            point1 = (190, 0)
            point2 = (190, 380)
        elif self.angles["roll"] == 270:
            point1 = (190, 380)
            point2 = (190, 0)
        else:
            point1 = (0, self.equation["slope"] * 0 + self.equation["bias"]) # x=0
            point2 = (400, self.equation["slope"] * 400 + self.equation["bias"]) # x=400

        return point1, point2

    def draw_line(self, point_1, point_2):
        canvas = QPixmap(300, 310)
        canvas.fill(Qt.white)
        self.ui.lb_background.setPixmap(canvas)

        painter = QPainter(self.ui.lb_background.pixmap())
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.black)
        painter.drawLine(*point_1, *point_2)
        painter.end()
        self.update()

    def fill_background(self, p1_x, p1_y, p2_x, p2_y):
        if 0 <= self.angles["roll"] <= 90:
            # blue area
            blue_area_corner = ((0, 0), (400, 0), (400, 400))
            # brown area
            brown_area_corner = ((0, 0), (0, 400), (400, 400))

        elif 90 < self.angles["roll"] < 180:
            # blue area
            blue_area_corner = ((0,400), (400, 400), (400, 0))
            # brown area
            brown_area_corner = ((0, 400), (0, 0), (400, 0))

        elif 180 <= self.angles["roll"] < 270:
            # blue area
            blue_area_corner = ((0, 0), (0, 400), (400, 400))
            # brown area
            brown_area_corner = ((0, 0), (400, 0), (400, 400))

        elif 270 <= self.angles["roll"] <= 360:
            # blue area
            blue_area_corner = ((0, 400), (0, 0), (400, 0))
            # brown area
            brown_area_corner = ((0, 400), (400, 400), (400, 0))

        painter2 = QPainter(self.ui.lb_background.pixmap())
        painter2.setRenderHint(QPainter.Antialiasing)
        painter2.setBrush(QColor.fromRgb(41, 119, 239))
        painter2.setPen(Qt.transparent)

        points = [
            QPoint(p1_x, p1_y),
            QPoint(*blue_area_corner[0]),
            QPoint(*blue_area_corner[1]),
            QPoint(*blue_area_corner[2]),
            QPoint(p2_x, p2_y),
        ]
        poly = QPolygon(points)
        painter2.drawPolygon(poly)

        painter2.setBrush(QColor.fromRgb(137, 71, 0))
        painter2.setPen(Qt.transparent)
        points = [
            QPoint(p1_x, p1_y),
            QPoint(*brown_area_corner[0]),
            QPoint(*brown_area_corner[1]),
            QPoint(*brown_area_corner[2]),
            QPoint(p2_x, p2_y),
        ]
        poly = QPolygon(points)
        painter2.drawPolygon(poly)

