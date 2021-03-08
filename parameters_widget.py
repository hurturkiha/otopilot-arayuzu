# created by Hurturk UAV Team (2021)

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from parameters_design_ui import Ui_Form
import json


class ParameterWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # Arama kutusunun tetikleyeceği fonksiyonu ekler.
        self.ui.le_search.textChanged.connect(self.search)

        self.parameters_dict = {}
        self.read_json()
        self.create_filter_button()
        self.create_table_widget()
        self.show_parameters(first_show=True)

    def search(self, searching_word):
        index = 0
        self.ui.tw_parameters.setRowCount(0)

        for parameter_family, parameters in self.parameters_dict.items():
            for parameter, attribute in parameters.items():
                if searching_word in parameter:
                    self.ui.tw_parameters.setRowCount(self.ui.tw_parameters.rowCount() + 1)
                    self.ui.tw_parameters.setItem(index, 0, QTableWidgetItem(parameter))
                    self.ui.tw_parameters.setItem(index, 1, QTableWidgetItem(attribute['deger']))
                    self.ui.tw_parameters.setItem(index, 2, QTableWidgetItem(attribute['aciklama']))
                    index += 1

    def create_table_widget(self):
        self.ui.tw_parameters.setColumnCount(3)

        horizontal_header = self.ui.tw_parameters.horizontalHeader()
        horizontal_header.setHighlightSections(False)
        horizontal_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        horizontal_header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        horizontal_header.setSectionResizeMode(2, QHeaderView.Stretch)

        vertical_header = self.ui.tw_parameters.verticalHeader()
        vertical_header.hide()

        # Delegate'ler ile birlikte sütunlar ortalanır.
        delegate = AlignDelegate(self.ui.tw_parameters)
        self.ui.tw_parameters.setItemDelegateForColumn(0, delegate)
        self.ui.tw_parameters.setItemDelegateForColumn(1, delegate)
        self.ui.tw_parameters.setItemDelegateForColumn(2, delegate)

    def show_parameters(self, first_show=False):
        index = 1

        if first_show or self.sender().objectName() == "Tümü":
            for parameter_family, parameters in self.parameters_dict.items():
                for parameter, attribute in parameters.items():
                    self.ui.tw_parameters.setRowCount(index)
                    self.ui.tw_parameters.setItem(index - 1, 0, QTableWidgetItem(parameter))
                    self.ui.tw_parameters.setItem(index - 1, 1, QTableWidgetItem(attribute['deger']))
                    self.ui.tw_parameters.setItem(index - 1, 2, QTableWidgetItem(attribute['aciklama']))

                    self.ui.tw_parameters.item(index - 1, 0).setFlags(Qt.ItemIsEditable)
                    self.ui.tw_parameters.item(index - 1, 2).setFlags(Qt.ItemIsEditable)

                    index += 1
        else:
            for parameter, attribute in self.parameters_dict[self.sender().objectName()].items():
                self.ui.tw_parameters.setRowCount(index)
                self.ui.tw_parameters.setItem(index - 1, 0, QTableWidgetItem(parameter))
                self.ui.tw_parameters.setItem(index - 1, 1, QTableWidgetItem(attribute['deger']))
                self.ui.tw_parameters.setItem(index - 1, 2, QTableWidgetItem(attribute['aciklama']))

                self.ui.tw_parameters.item(index - 1, 0).setFlags(Qt.ItemIsEditable)
                self.ui.tw_parameters.item(index - 1, 2).setFlags(Qt.ItemIsEditable)

                index += 1

    def read_json(self):
        with open("parameters.json", "r") as f:
            self.parameters_dict = json.load(f)

    def create_filter_button(self):
        button = QPushButton()
        button.setStyleSheet("""
                        QPushButton
                        {
                        border-radius: 0px;
                        background-color: #d9d9d9;
                        margin-bottom: 1px;
                        font-size: 23px;
                        height: 48px;
                        width: 120px;
                        height: 35.4px;
                        }
                        QPushButton::hover {
                            background-color: #999999;
                        }
                        QPushButton::focus {
                            background-color: #999999;
                            outline: none;
                            border: none;
                        }
                        QPushButton::focus::hover {
                            background-color: #999999;
                            outline: none;
                            border: none;
                        }
                    """)
        button.setText("Tümü")
        button.setObjectName("Tümü")
        button.clicked.connect(self.show_parameters)

        item = QListWidgetItem(self.ui.lw_parameterFamily)
        item.setSizeHint(button.sizeHint())

        self.ui.lw_parameterFamily.addItem(item)
        self.ui.lw_parameterFamily.setItemWidget(item, button)

        for i in self.parameters_dict.keys():
            button = QPushButton()
            button.setStyleSheet("""
                QPushButton
                {
                border-radius: 0px;
                background-color: #d9d9d9;
                margin-bottom: 1px;
                font-size: 23px;
                height: 48px;
                width: 120px;
                height: 35.4px;
                }
                QPushButton::hover {
                    background-color: #999999;
                }
                QPushButton:focus {
                    background-color: #999999;
                    outline: none;
                    border: none;
                }
            """)
            button.setText(i)
            button.setObjectName(i)
            button.clicked.connect(self.show_parameters)

            family_item = QListWidgetItem(self.ui.lw_parameterFamily)
            family_item.setSizeHint(button.sizeHint())

            self.ui.lw_parameterFamily.addItem(family_item)
            self.ui.lw_parameterFamily.setItemWidget(family_item, button)


class AlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter
