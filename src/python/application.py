import sys
import logging
from PyQt6.QtCore import QTimer, QDateTime
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import  ( 
    QMainWindow, QApplication, QHBoxLayout,
    QWidget, QStatusBar, 
    QLabel
)
from editor import AXC1DTextEditor
from plotter import AXC1DPlotter
from solver import AXC1DSolver
from manager import AXC1DEventManager

class AXC1DMainWindow(QMainWindow):
    """
    Docstring for AXC1DMainWindow
    """
    def __init__(self, application: QApplication, title: str, x: int, y: int, width: int, height: int, parent = None):
        """
        Docstring for __init__
        
        :param self: Description
        :param application: Description
        :type application: QApplication
        :param title: Description
        :type title: str
        :param x: Description
        :type x: int
        :param y: Description
        :type y: int
        :param width: Description
        :type width: int
        :param height: Description
        :type height: int
        :param parent: Description
        """
        super().__init__(parent)
        self.application = application

        # setup logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logging_handler = logging.StreamHandler()
        self.logging_handler.setLevel(logging.DEBUG)
        # self.logging_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        self.logging_formatter = logging.Formatter("%(asctime)s - %(message)s")
        self.logging_handler.setFormatter(self.logging_formatter)
        self.logger.addHandler(self.logging_handler)

        # configure application window settings
        self.setWindowTitle(title)
        self.setGeometry(x, y, width, height)
        self.setFixedSize(width, height)

        # setup the event manager
        self.event_manager = AXC1DEventManager(logger = self.logger)

        # setup custom components
        self.editor = AXC1DTextEditor(logger = self.logger, event_manager = self.event_manager)
        self.plotter = AXC1DPlotter(logger = self.logger, event_manager = self.event_manager)
        self.solver = AXC1DSolver(logger = self.logger, event_manager = self.event_manager)

        # build menu bar
        self.menu_bar = self.menuBar()

        # file menu
        self.file_menu = self.menu_bar.addMenu("&File")
        # menu option to new file
        new_file_action = QAction("&New File", self)
        new_file_action.triggered.connect(self.editor.new_file)
        new_file_action.setShortcut(QKeySequence("Ctrl+N"))
        self.file_menu.addAction(new_file_action)

        # menu option to open file
        open_file_action = QAction("&Open File", self)
        open_file_action.triggered.connect(self.editor.open_file)
        open_file_action.setShortcut(QKeySequence("Ctrl+O"))
        self.file_menu.addAction(open_file_action)

        # menu option to save file
        save_file_action = QAction("&Save File", self)
        save_file_action.triggered.connect(self.editor.save_file)
        save_file_action.setShortcut(QKeySequence("Ctrl+S"))
        self.file_menu.addAction(save_file_action)

        # plots menu
        self.plot_menu = self.menu_bar.addMenu("&Plots")
        # menu option to add plots
        add_new_plot_action = QAction("&Add Plot", self)
        add_new_plot_action.triggered.connect(self.plotter.add_plot)
        add_new_plot_action.setShortcut(QKeySequence("Ctrl+A"))
        self.plot_menu.addAction(add_new_plot_action)

        # menu option to delete plots
        delete_plot_action = QAction("&Delete Plot", self)
        delete_plot_action.triggered.connect(self.plotter.delete_plot)
        delete_plot_action.setShortcut(QKeySequence("Ctrl+D"))
        self.plot_menu.addAction(delete_plot_action)

        # menu option to edit plots
        edit_plot_action = QAction("&Edit Plot", self)
        edit_plot_action.triggered.connect(self.plotter.edit_plot)
        edit_plot_action.setShortcut(QKeySequence("Ctrl+D"))
        self.plot_menu.addAction(edit_plot_action)

        # simulations menu
        self.simulation_menu = self.menu_bar.addMenu("&Simulations")
        # menu option to run the simulation
        run_simulation_action = QAction("&Run Simulation", self)
        run_simulation_action.setEnabled(False) 
        # subscribe to the open file event so that way the run simulation is only enabled once a file is opened
        self.event_manager.subscribe("open_file", lambda: run_simulation_action.setEnabled(True))
        run_simulation_action.triggered.connect(lambda: self.solver.run(self.editor.file_path))
        # create a keyboard shortcut from running the simulation
        run_simulation_action.setShortcut(QKeySequence("Ctrl+R"))
        self.simulation_menu.addAction(run_simulation_action)

        # self.simulation_menu.addAction("&Edit Simulation Path")

        self.settings_menu = self.menu_bar.addMenu("&Settings")
        # menu option to open the settinsg menu
        open_settings_action = QAction("&Open Settings", self)
        open_settings_action.triggered.connect(self.open_settings)
        open_settings_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.settings_menu.addAction(open_settings_action)
        # menu option to close the application
        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.application.quit)
        exit_action.setShortcut(QKeySequence("Ctrl+X"))
        self.settings_menu.addAction(exit_action)

        # create a workspace layout
        self.workspace = QHBoxLayout()

        # add the text editor and the plotter to the workspace layout
        self.workspace.addWidget(self.editor)
        self.workspace.addWidget(self.plotter)

        # treat the workspace layout as the central widget
        self.central = QWidget()
        self.central.setLayout(self.workspace)
        self.setCentralWidget(self.central)

        # create status bar 
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # include the time in the status bar
        self.time_label = QLabel(self)
        self.status_bar.addPermanentWidget(self.time_label)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        # update time every second
        self.timer.start(1000)

    def update_time(self):
        """
        Docstring for update_time
        
        :param self: Description
        """
        # update the time
        current_time = QDateTime.currentDateTime().toString("MM/dd/yyyy hh:mm:ss AP")
        self.time_label.setText(current_time)

    def open_settings(self):
        """
        Docstring for open_settings
        
        :param self: Description
        """
        # open the settings menu
        self.logger.info(f"Test Open Settings")
        

application = QApplication(sys.argv)
window = AXC1DMainWindow(application = application, title = "AXC1D", x = 500, y = 500, width = 1500, height = 800)
window.show()
sys.exit(application.exec())

# python src/python/application.py