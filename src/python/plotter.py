import logging
import pyqtgraph as pg
from manager import AXC1DEventManager
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QDialog


class AXC1DPlotter(QWidget):
    def __init__(self, logger: logging.Logger, event_manager: AXC1DEventManager, parent = None):
        super().__init__(parent)
        self.logger = logger
        # initialize widget with one plot
        self.plots = QVBoxLayout()
        plot = pg.PlotWidget()
        plot.setBackground("w")
        plot.addLegend()
        plot.showGrid(x = True, y = True)
        self.plots.addWidget(plot)
        self.setLayout(self.plots)

    def delete_plot(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Delete Plot")
        dialog.setGeometry(500, 500, 700, 300)
        result = dialog.exec()
        if result == QDialog.accepted:
            self.logger.info("Dialog Accepted")
        else:
            self.logger.info("Dialog Rejected")

    def add_plot(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Plot")
        dialog.setGeometry(500, 500, 700, 300)
        result = dialog.exec()
        if result == QDialog.accepted:
            self.logger.info("Dialog Accepted")
        else:
            self.logger.info("Dialog Rejected")

        plot = pg.PlotWidget()
        plot.setBackground("w")
        plot.addLegend()
        plot.showGrid(x = True, y = True)
        self.plots.addWidget(plot)
        # self.plots.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.plots)

    def edit_plot(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Plot")
        dialog.setGeometry(500, 500, 700, 300)
        result = dialog.exec()
        if result == QDialog.accepted:
            self.logger.info("Dialog Accepted")
        else:
            self.logger.info("Dialog Rejected")

        plot = pg.PlotWidget()
        plot.setBackground("w")
        plot.addLegend()
        plot.showGrid(x = True, y = True)
        self.plots.addWidget(plot)
        # self.plots.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.plots)