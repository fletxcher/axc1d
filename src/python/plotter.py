import logging
import pyqtgraph as pg
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

# ==========================================================================

# class AXC1DPlotter(QWidget):
#     def __init__(self, logger: logging.Logger, parent = None):
#         super().__init__(parent)
#         self.logger = logger

#         # inner widget that holds all the plots
#         self.plots_widget = QWidget()
#         self.plots = QVBoxLayout(self.plots_widget)
#         self.plots.setSpacing(10)
#         self.plots.setContentsMargins(10, 10, 10, 10)

#         plot_info = [
#             ("Mass Flow Rate Vs Flow Coefficient",      "Mass Flow Rate", "Flow Coefficient"),
#             ("Mass Flow Rate Vs Adiabatic Efficiency",  "Mass Flow Rate", "Adiabatic Efficiency"),
#             ("Pressure Ratio Vs Adiabatic Efficiency",  "Pressure Ratio", "Adiabatic Efficiency"),
#             ("Pressure Ratio Vs Flow Coefficient",      "Pressure Ratio", "Flow Coefficient"),
#             ("Title",                                   "X Label",        "Y Label"),
#         ]
#         for title, x_label, y_label in plot_info:
#             plot = pg.PlotWidget()
#             plot.setBackground("w")
#             plot.setTitle(title)
#             plot.setLabel("bottom", x_label)
#             plot.setLabel("left", y_label)
#             plot.setMinimumHeight(250)   # each plot gets a fixed minimum height
#             plot.addLegend()
#             plot.showGrid(x=True, y=True)
#             self.plots.addWidget(plot)

#         # scroll area wraps the inner widget
#         self.scroll = QScrollArea()
#         self.scroll.setWidget(self.plots_widget)
#         self.scroll.setWidgetResizable(True)      
#         self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
#         self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

#         # outer layout just holds the scroll area
#         outer = QVBoxLayout(self)
#         outer.setContentsMargins(0, 0, 0, 0)
#         outer.addWidget(self.scroll)

#     def _make_plot(self, title="", x_label="", y_label="") -> pg.PlotWidget:
#         """Helper so add_plot / edit_plot don't repeat themselves."""
#         plot = pg.PlotWidget()
#         plot.setBackground("w")
#         plot.setTitle(title)
#         plot.setLabel("bottom", x_label)
#         plot.setLabel("left", y_label)
#         plot.setMinimumHeight(250)
#         plot.addLegend()
#         plot.showGrid(x=True, y=True)
#         return plot

#     def delete_plot(self):
#         dialog = QDialog(self)
#         dialog.setWindowTitle("Delete Plot")
#         dialog.setGeometry(500, 500, 700, 300)
#         result = dialog.exec()
#         if result == QDialog.DialogCode.Accepted:
#             self.logger.info("Dialog Accepted")
#         else:
#             self.logger.info("Dialog Rejected")

#     def add_plot(self):
#         dialog = QDialog(self)
#         dialog.setWindowTitle("Add Plot")
#         dialog.setGeometry(500, 500, 700, 300)
#         result = dialog.exec()
#         if result == QDialog.DialogCode.Accepted:
#             self.logger.info("Dialog Accepted")
#             plot = self._make_plot()
#             self.plots.addWidget(plot)

#     def edit_plot(self):
#         dialog = QDialog(self)
#         dialog.setWindowTitle("Edit Plot")
#         dialog.setGeometry(500, 500, 700, 300)
#         result = dialog.exec()
#         if result == QDialog.DialogCode.Accepted:
#             self.logger.info("Dialog Accepted")
#             plot = self._make_plot()
#             self.plots.addWidget(plot)

#     def clear_plot(self):
#         dialog = QDialog(self)
#         dialog.setWindowTitle("Clear Plot")
#         dialog.setGeometry(500, 500, 700, 300)
#         result = dialog.exec()
#         if result == QDialog.DialogCode.Accepted:
#             self.logger.info("Dialog Accepted")
#             plot = self._make_plot()
#             self.plots.addWidget(plot)

# =======================================================================================

# from __future__ import annotations
 
import logging
from dataclasses import dataclass, field
from typing import Any, Optional
 
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
 
STAGE_FIELDS: dict[str, str] = {
    "mass_flow":        "Mass Flow Rate (lbm/s)",
    "phi":              "Flow Coefficient φ",
    "psi":              "Work Coefficient ψ",
    "eta":              "Adiabatic Efficiency",
    "pr":               "Pressure Ratio",
    "tr":               "Temperature Ratio",
    "tt_inlet":         "Total Temperature Inlet (°R)",
    "tt_outlet":        "Total Temperature Outlet (°R)",
    "pt_inlet":         "Total Pressure Inlet (lbf/ft²)",
    "pt_outlet":        "Total Pressure Outlet (lbf/ft²)",
    "vz2m":             "Axial Velocity Inlet (ft/s)",
    "vz3m":             "Axial Velocity Outlet (ft/s)",
    "incidence":        "Incidence Angle (°)",
    "diffusion_factor": "Diffusion Factor",
}
 
OVERALL_FIELDS: dict[str, str] = {
    "pr_overall":   "Overall Pressure Ratio",
    "tr_overall":   "Overall Temperature Ratio",
    "eta_overall":  "Overall Adiabatic Efficiency",
    "flow_point":   "Flow Point Index",
}
 
ALL_FIELDS = {**STAGE_FIELDS, **OVERALL_FIELDS}
 
_PALETTE = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
]
 
@dataclass
class PlotConfig:
    title:   str   = "New Plot"
    x_field: str   = "phi"
    y_field: str   = "eta"
    stage:   int   = 1          # 1-based stage number; 0 = overall
    speeds:  list  = field(default_factory=list)   # empty → show all
 
 
def _extract_xy(
    results: list[dict],
    speed: float,
    cfg: PlotConfig,
) -> tuple[list[float], list[float]]:
    """Return parallel x/y lists for a single speed line."""
    xs, ys = [], []
 
    for fp in results:
        if abs(fp["speed"] - speed) > 1e-9:
            continue
 
        if cfg.stage == 0:
            # overall fields
            x = fp.get(cfg.x_field)
            y = fp.get(cfg.y_field)
            if x is not None and y is not None:
                xs.append(float(x))
                ys.append(float(y))
        else:
            # stage-level fields
            for s in fp.get("stages", []):
                if s["stage"] == cfg.stage:
                    x = s.get(cfg.x_field) or fp.get(cfg.x_field)
                    y = s.get(cfg.y_field) or fp.get(cfg.y_field)
                    if x is not None and y is not None:
                        xs.append(float(x))
                        ys.append(float(y))
                    break
 
    return xs, ys
 
 
class PlotPanel(QWidget):
    """One pyqtgraph panel that can redraw itself from a PlotConfig."""
 
    def __init__(self, cfg: PlotConfig, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.cfg = cfg
 
        self._pw = pg.PlotWidget()
        self._pw.setBackground("w")
        self._pw.showGrid(x=True, y=True)
        self._pw.addLegend(offset=(10, 10))
        self._pw.setSizePolicy(QSizePolicy.Policy.Expanding,
                               QSizePolicy.Policy.Fixed)
        self._pw.setMinimumHeight(260)
 
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._pw)
 
        self._apply_labels()
 
    def _apply_labels(self) -> None:
        self._pw.setTitle(self.cfg.title)
        self._pw.setLabel("bottom", ALL_FIELDS.get(self.cfg.x_field, self.cfg.x_field))
        self._pw.setLabel("left",   ALL_FIELDS.get(self.cfg.y_field, self.cfg.y_field))
 
    def redraw(self, results: list[dict]) -> None:
        """Clear and replot from *results* using the current PlotConfig."""
        self._pw.clear()
        # Re-add legend after clear (pyqtgraph removes it on clear)
        self._pw.addLegend(offset=(10, 10))
        self._apply_labels()
 
        if not results:
            return
 
        all_speeds = sorted({fp["speed"] for fp in results})
        speeds_to_plot = self.cfg.speeds if self.cfg.speeds else all_speeds
 
        for i, spd in enumerate(speeds_to_plot):
            xs, ys = _extract_xy(results, spd, self.cfg)
            if not xs:
                continue
            colour = _PALETTE[i % len(_PALETTE)]
            pen = pg.mkPen(color=colour, width=2)
            sym_brush = pg.mkBrush(colour)
            self._pw.plot(
                xs, ys,
                pen=pen,
                symbol="o",
                symbolSize=7,
                symbolBrush=sym_brush,
                symbolPen=pg.mkPen(colour),
                name=f"N/N₀ = {spd:.2f}",
            )
 
class PlotDialog(QDialog):
    """Dialog for creating or editing a PlotConfig."""
 
    def __init__(
        self,
        available_speeds: list[float],
        cfg: Optional[PlotConfig] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Add Plot" if cfg is None else "Edit Plot")
        self.setMinimumWidth(440)
 
        self._cfg = cfg or PlotConfig()
        self._speeds = available_speeds
 
        form = QFormLayout()
 
        # Title
        self._title_edit = QLineEdit(self._cfg.title)
        form.addRow("Title:", self._title_edit)
 
        # X axis
        self._x_combo = QComboBox()
        self._y_combo = QComboBox()
        for key, label in ALL_FIELDS.items():
            self._x_combo.addItem(label, key)
            self._y_combo.addItem(label, key)
        self._x_combo.setCurrentIndex(
            self._x_combo.findData(self._cfg.x_field))
        self._y_combo.setCurrentIndex(
            self._y_combo.findData(self._cfg.y_field))
        form.addRow("X Axis:", self._x_combo)
        form.addRow("Y Axis:", self._y_combo)
 
        # Stage selector
        self._stage_combo = QComboBox()
        self._stage_combo.addItem("Overall", 0)
        for s in range(1, 9):          # up to 8 stages
            self._stage_combo.addItem(f"Stage {s}", s)
        self._stage_combo.setCurrentIndex(
            self._stage_combo.findData(self._cfg.stage))
        form.addRow("Stage:", self._stage_combo)
 
        # Speed-line checkboxes
        grp = QGroupBox("Speed Lines  (uncheck to hide)")
        grp_layout = QVBoxLayout(grp)
        self._speed_checks: dict[float, QCheckBox] = {}
        for spd in available_speeds:
            cb = QCheckBox(f"N/N₀ = {spd:.2f}")
            cb.setChecked(
                (not self._cfg.speeds) or (spd in self._cfg.speeds)
            )
            grp_layout.addWidget(cb)
            self._speed_checks[spd] = cb
 
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
 
        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(grp)
        root.addWidget(buttons)
 
    def get_config(self) -> PlotConfig:
        checked_speeds = [
            spd for spd, cb in self._speed_checks.items() if cb.isChecked()
        ]
        # If all are checked treat as "show all" (empty list)
        if len(checked_speeds) == len(self._speed_checks):
            checked_speeds = []
 
        return PlotConfig(
            title=   self._title_edit.text().strip() or "Plot",
            x_field= self._x_combo.currentData(),
            y_field= self._y_combo.currentData(),
            stage=   self._stage_combo.currentData(),
            speeds=  checked_speeds,
        )
 
class DeleteDialog(QDialog):
    """Let the user pick one panel to remove."""
 
    def __init__(
        self,
        titles: list[str],
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Delete Plot")
        self.setMinimumWidth(320)
 
        self._list = QListWidget()
        for t in titles:
            self._list.addItem(QListWidgetItem(t))
        if titles:
            self._list.setCurrentRow(0)
 
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
 
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select the plot to delete:"))
        layout.addWidget(self._list)
        layout.addWidget(buttons)
 
    def selected_index(self) -> int:
        return self._list.currentRow()
 
 
class AXC1DPlotter(QWidget):
 
    # Default panels shown on startup
    _DEFAULT_CONFIGS: list[PlotConfig] = [
        PlotConfig("Stage 1 — φ vs η",          "phi",       "eta",        stage=1),
        PlotConfig("Stage 2 — φ vs η",          "phi",       "eta",        stage=2),
        PlotConfig("Stage 1 — φ vs PR",         "phi",       "pr",         stage=1),
        PlotConfig("Overall — φ vs PR",         "phi",       "pr_overall", stage=1),
        PlotConfig("Stage 1 — Mass Flow vs φ",  "mass_flow", "phi",        stage=1),
    ]
 
    def __init__(self, logger: logging.Logger, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = logger
 
        self._results:  list[dict]   = []
        self._panels:   list[PlotPanel] = []
 
        # Inner widget that holds all panels
        self._inner = QWidget()
        self._vbox  = QVBoxLayout(self._inner)
        self._vbox.setSpacing(12)
        self._vbox.setContentsMargins(10, 10, 10, 10)
 
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidget(self._inner)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
 
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
 
        # Build default panels
        for cfg in self._DEFAULT_CONFIGS:
            self._add_panel(cfg)
 
    def update(self, results: Any) -> None:
        """
        Called by the main window after a solver run.
        *results* is the first element of the tuple returned by
        AXC1DSolver.run() — i.e. the list of flow-point dicts.
        """
        # The solver returns a tuple; the first element is the results list.
        if isinstance(results, tuple):
            results = results[0]
 
        self._results = results or []
        self.logger.info(f"Plotter received {len(self._results)} flow points")
 
        for panel in self._panels:
            panel.redraw(self._results)
 
    def add_plot(self) -> None:
        speeds = self._available_speeds()
        dlg = PlotDialog(speeds, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            cfg = dlg.get_config()
            self.logger.info(f"Adding plot: {cfg.title}")
            panel = self._add_panel(cfg)
            if self._results:
                panel.redraw(self._results)
 
    def delete_plot(self) -> None:
        if not self._panels:
            QMessageBox.information(self, "Delete Plot", "No plots to delete.")
            return
 
        titles = [p.cfg.title for p in self._panels]
        dlg = DeleteDialog(titles, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            idx = dlg.selected_index()
            if 0 <= idx < len(self._panels):
                panel = self._panels.pop(idx)
                self._vbox.removeWidget(panel)
                panel.deleteLater()
                self.logger.info(f"Deleted plot at index {idx}")
 
    def edit_plot(self) -> None:
        if not self._panels:
            QMessageBox.information(self, "Edit Plot", "No plots to edit.")
            return
 
        titles = [p.cfg.title for p in self._panels]
        # Re-use the delete dialog as a "pick which plot to edit" picker
        pick_dlg = DeleteDialog(titles, parent=self)
        pick_dlg.setWindowTitle("Edit Plot — Select")
        if pick_dlg.exec() != QDialog.DialogCode.Accepted:
            return
 
        idx = pick_dlg.selected_index()
        if not (0 <= idx < len(self._panels)):
            return
 
        panel = self._panels[idx]
        speeds = self._available_speeds()
        edit_dlg = PlotDialog(speeds, cfg=panel.cfg, parent=self)
        if edit_dlg.exec() == QDialog.DialogCode.Accepted:
            panel.cfg = edit_dlg.get_config()
            self.logger.info(f"Edited plot {idx}: {panel.cfg.title}")
            panel.redraw(self._results)
 
    def clear_plots(self) -> None:
        """Clear all data from every panel without removing the panels."""
        if not self._panels:
            return
        self._results = []
        for panel in self._panels:
            panel.redraw([])
        self.logger.info("All plot data cleared")
 
 
    def _add_panel(self, cfg: PlotConfig) -> PlotPanel:
        panel = PlotPanel(cfg)
        self._panels.append(panel)
        self._vbox.addWidget(panel)
        return panel
 
    def _available_speeds(self) -> list[float]:
        if self._results:
            return sorted({fp["speed"] for fp in self._results})
        # Sensible defaults before first run
        return [1.0, 0.9, 0.8, 0.7, 0.5]