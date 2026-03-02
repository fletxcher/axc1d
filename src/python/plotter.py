import logging
import pyqtgraph as pg
from src.python.manager import AXC1DEventManager
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QDialog, QScrollArea

# class AXC1DPlotter(QWidget):
#     def __init__(self, logger: logging.Logger, event_manager: AXC1DEventManager, parent = None):
#         super().__init__(parent)
#         self.logger = logger
#         self.event_manager = event_manager

#         # initialize widget with a certain amount of plots
#         self.plots = QVBoxLayout()
#         plot_info = [
#             ("Mass Flow Rate Vs Flow Coffiecient", "Mass Flow Rate", "Flow Coefficient"),
#             ("Mass Flow Rate Vs Adiabatic Efficiency", "Mass Flow Rate", "Adiabatic Efficicency"),
#             ("Pressure Ratio Vs Adiabatic Efficiency", "Pressure Ratio", "Adiabatic Efficiency"),
#             ("Pressure Ratio Vs Flow Coefficient", "Pressure Ratio", "Flow Coefficient"),
#             ("Title", "X Label", "Y Label"),
#         ]
#         for title, x_label, y_label in plot_info:
#             plot = pg.PlotWidget()
#             plot.setBackground("w")
#             plot.setTitle(title)
#             plot.setLabel("bottom", x_label)
#             plot.setLabel("left", y_label)
#             plot.addLegend()
#             plot.showGrid(x = True, y = True)
#             self.plots.addWidget(plot)
#         self.setLayout(self.plots)

#     def delete_plot(self):
#         dialog = QDialog(self)
#         dialog.setWindowTitle("Delete Plot")
#         dialog.setGeometry(500, 500, 700, 300)
#         result = dialog.exec()
#         if result == QDialog.accepted: self.logger.info("Dialog Accepted")
#         else: self.logger.info("Dialog Rejected")

#     def add_plot(self):
#         dialog = QDialog(self)
#         dialog.setWindowTitle("Add Plot")
#         dialog.setGeometry(500, 500, 700, 300)
#         result = dialog.exec()
#         if result == QDialog.accepted: self.logger.info("Dialog Accepted")
#         else: self.logger.info("Dialog Rejected")

#         plot = pg.PlotWidget()
#         plot.setBackground("w")
#         plot.addLegend()
#         plot.showGrid(x = True, y = True)
#         self.plots.addWidget(plot)
#         # self.plots.setContentsMargins(20, 20, 20, 20)
#         self.setLayout(self.plots)

#     def edit_plot(self):
#         dialog = QDialog(self)
#         dialog.setWindowTitle("Edit Plot")
#         dialog.setGeometry(500, 500, 700, 300)
#         result = dialog.exec()
#         if result == QDialog.accepted: self.logger.info("Dialog Accepted")
#         else: self.logger.info("Dialog Rejected")

#         plot = pg.PlotWidget()
#         plot.setBackground("w")
#         plot.addLegend()
#         plot.showGrid(x = True, y = True)
#         self.plots.addWidget(plot)
#         self.setLayout(self.plots)

class AXC1DPlotter(QWidget):
    def __init__(self, logger: logging.Logger, event_manager: AXC1DEventManager, parent=None):
        super().__init__(parent)
        self.logger = logger
        self.event_manager = event_manager

        # inner widget that holds all the plots
        self.plots_widget = QWidget()
        self.plots = QVBoxLayout(self.plots_widget)
        self.plots.setSpacing(10)
        self.plots.setContentsMargins(10, 10, 10, 10)

        plot_info = [
            ("Mass Flow Rate Vs Flow Coefficient",      "Mass Flow Rate", "Flow Coefficient"),
            ("Mass Flow Rate Vs Adiabatic Efficiency",  "Mass Flow Rate", "Adiabatic Efficiency"),
            ("Pressure Ratio Vs Adiabatic Efficiency",  "Pressure Ratio", "Adiabatic Efficiency"),
            ("Pressure Ratio Vs Flow Coefficient",      "Pressure Ratio", "Flow Coefficient"),
            ("Title",                                   "X Label",        "Y Label"),
        ]
        for title, x_label, y_label in plot_info:
            plot = pg.PlotWidget()
            plot.setBackground("w")
            plot.setTitle(title)
            plot.setLabel("bottom", x_label)
            plot.setLabel("left", y_label)
            plot.setMinimumHeight(250)   # each plot gets a fixed minimum height
            plot.addLegend()
            plot.showGrid(x=True, y=True)
            self.plots.addWidget(plot)

        # scroll area wraps the inner widget
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.plots_widget)
        self.scroll.setWidgetResizable(True)      
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # outer layout just holds the scroll area
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.scroll)

    def _make_plot(self, title="", x_label="", y_label="") -> pg.PlotWidget:
        """Helper so add_plot / edit_plot don't repeat themselves."""
        plot = pg.PlotWidget()
        plot.setBackground("w")
        plot.setTitle(title)
        plot.setLabel("bottom", x_label)
        plot.setLabel("left", y_label)
        plot.setMinimumHeight(250)
        plot.addLegend()
        plot.showGrid(x=True, y=True)
        return plot

    def delete_plot(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Delete Plot")
        dialog.setGeometry(500, 500, 700, 300)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            self.logger.info("Dialog Accepted")
        else:
            self.logger.info("Dialog Rejected")

    def add_plot(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Plot")
        dialog.setGeometry(500, 500, 700, 300)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            self.logger.info("Dialog Accepted")
            plot = self._make_plot()
            self.plots.addWidget(plot)

    def edit_plot(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Plot")
        dialog.setGeometry(500, 500, 700, 300)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            self.logger.info("Dialog Accepted")
            plot = self._make_plot()
            self.plots.addWidget(plot)
