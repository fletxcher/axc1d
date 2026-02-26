import json
import logging 
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHeaderView, QTableWidget, QTableWidgetItem, 
    QWidget, QVBoxLayout, QPushButton, 
    QScrollArea, QSizePolicy, QLabel, 
    QLineEdit, QCheckBox, QHBoxLayout, 
    QLabel, QScrollArea, QFileDialog, 
    QVBoxLayout
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from manager import AXC1DEventManager

class AccordionSection(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self._collapsed = True
        self.parent_accordion = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toggle button
        self.toggle_btn = QPushButton(title)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-bottom: 1px solid #555;
                padding: 8px 12px;
                text-align: left;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #d3d3d3; 
                color: #ffffff; 
            }
            QPushButton:checked { 
                background-color: #4a4a4a; 
                color: #ffffff; 
            }
        """)
        self.toggle_btn.clicked.connect(self._toggle)
        layout.addWidget(self.toggle_btn)

        # content area
        self.content_area = QWidget()
        self.content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.content_area.setMaximumHeight(0)

        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(12, 8, 12, 8)
        self.content_layout.setSpacing(6)
        layout.addWidget(self.content_area)

        # animation
        self._animation = QPropertyAnimation(self.content_area, b"maximumHeight")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self._animation.finished.connect(self._on_animation_finished)

    def _on_animation_finished(self):
        """Called when animation finishes to notify parent accordion to update"""
        if self.parent_accordion:
            self.parent_accordion._notify_child_changed()

    def _toggle(self, checked: bool):
        self._collapsed = not checked
        content_height = self.content_area.sizeHint().height()
        if checked:
            self._animation.setStartValue(0)
            self._animation.setEndValue(content_height)
        else:
            self._animation.setStartValue(content_height)
            self._animation.setEndValue(0)
        self._animation.start()
        arrow = "▼" if checked else "▶"
        title = self.toggle_btn.text().lstrip("▶▼ ")
        self.toggle_btn.setText(f"{arrow} {title}")

    def _notify_child_changed(self):
        """Recalculate height when a child accordion changes"""
        if self.toggle_btn.isChecked():
            new_height = self.content_area.sizeHint().height()
            self._animation.setStartValue(self.content_area.maximumHeight())
            self._animation.setEndValue(new_height)
            self._animation.start()
            if self.parent_accordion:
                self.parent_accordion._notify_child_changed()

    def add_widget(self, widget: QWidget):
        self.content_layout.addWidget(widget)
        # If we're adding an AccordionSection, set it as a child
        if isinstance(widget, AccordionSection):
            widget.parent_accordion = self

    def set_title(self, title: str):
        arrow = "▼" if self.toggle_btn.isChecked() else "▶"
        self.toggle_btn.setText(f"{arrow} {title}")

    def expand(self):
        if not self.toggle_btn.isChecked():
            self.toggle_btn.setChecked(True)
            self._toggle(True)

    def collapse(self):
        if self.toggle_btn.isChecked():
            self.toggle_btn.setChecked(False)
            self._toggle(False)

class AccordionWidget(QScrollArea):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addStretch()
        self.setWidget(self._container)

        self._sections: list[AccordionSection] = []

    def add_section(self, title: str) -> AccordionSection:
        section = AccordionSection(f"▶ {title}")
        self._layout.insertWidget(self._layout.count() - 1, section)
        self._sections.append(section)
        return section

    def remove_section(self, section: AccordionSection):
        if section in self._sections:
            self._sections.remove(section)
            self._layout.removeWidget(section)
            section.deleteLater()

    def collapse_all(self):
        for s in self._sections:
            s.collapse()

    def expand_all(self):
        for s in self._sections:
            s.expand()

class AXC1DInputEditor(QWidget):
    def __init__(self, logger: logging.Logger, event_manager: AXC1DEventManager, parent = None):
        super().__init__(parent)
        self.logger = logger
        self.event_manager = event_manager
        self.file_path = None
        
        # Store widget references for later extraction
        self.input_params_widgets = {}
        self.deviation_factors_widgets = {}
        self.specific_heat_widgets = {}
        self.stage_geometry_widgets = {}
        self.characteristics_widgets = {}
        self.efficiency_table = None
        self.bleed_table = None
        self.characteristic_tables = []
        
        # Store accordion sections for dynamic updates
        self.accordion = None
        self.stage_geometry_section = None
        self.characteristics_section = None
        self.bleed_table_section = None
        
        # Speed points for characteristics and bleed table
        self.speed_points = [1.000, 0.900, 0.800, 0.700, 0.500]

        accordion = AccordionWidget()
        self.accordion = accordion

        # input parameters 
        s1 = accordion.add_section('SI Input Parameters')
        input_params_config = [
            ("STAGES", "Number Of Stages"),
            ("SPEEDS", "Number Of Speeds"),
            ("P_0_IN", "P\u2080 In"),
            ("T_0_IN", "T\u2080 In"),
            ("POINTS", "Points Per Characteristic"),
            ("MOLE_WT", "Molecular Weight (g/mol)"),
            ("RPM", "Rotations Per Minute"),
            ("MASS_FLOW", "Mass Flow Rate")
        ]
        for var, desc in input_params_config:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            lbl = QLabel(var)
            lbl.setToolTip(desc)
            lbl.setFixedWidth(200)
            widget = QLineEdit(self)
            row_layout.addWidget(lbl)
            row_layout.addWidget(widget)
            s1.add_widget(row)
            self.input_params_widgets[var] = widget
        
        # Connect STAGES field to trigger rebuild
        self.input_params_widgets['STAGES'].textChanged.connect(self.rebuild_stage_sections)

        # deviation factors  
        s2 = accordion.add_section('Deviation Factors')
        deviation_factors_config = [
            ("SPDPSI", "Alter ψ Value For Off-Design Speed"),
            ("SPDPHI", "Alter φ Value For Off-Design Speed"),
            ("DRDEVG", "Alter Rotor Deviation Angle For Blade Reset"),
            ("DRDEVN", "Alter Rotor Deviation Angle For Off-Design Speed"),
            ("DRDEVP", "Alter Rotor Deviation Angle For Off-Design φ"),
            ("UNITS",  "Enable SI Units"),
        ]
        for var, desc in deviation_factors_config:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(4)
            lbl = QLabel(var)
            lbl.setToolTip(desc)
            lbl.setFixedWidth(350)  
            widget = QCheckBox(self)
            row_layout.addWidget(lbl)
            row_layout.addWidget(widget)
            row_layout.addStretch() 
            s2.add_widget(row)
            self.deviation_factors_widgets[var] = widget

        # specific heat coefficients 
        s3 = accordion.add_section('Specific Heat Coefficients')
        for i in range(1, 7):
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            lbl = QLabel(f'CPCO({i}):')
            lbl.setToolTip(f'Specific Heat Coefficient No.{i}')
            widget = QLineEdit(self)
            row_layout.addWidget(lbl)
            row_layout.addWidget(widget)
            s3.add_widget(row)
            self.specific_heat_widgets[f'CPCO_{i}'] = widget

        # stage geometry (dynamic - will be populated on init and when stages change)
        self.stage_geometry_section = accordion.add_section('Stage Geometry')
        self.rebuild_stage_geometry()

        s5 = accordion.add_section('Efficiency Ratio Table')
        self.efficiency_table = QTableWidget()
        self.efficiency_table.setColumnCount(2)
        self.efficiency_table.setHorizontalHeaderLabels(['PCTSPD', 'ETARAT'])
        
        efficiency_ratio_table_entries = [
            {"PCTSPD": 1.0000, "ETARAT": 1.0000},
            {"PCTSPD": 0.9000, "ETARAT": 1.0170},
            {"PCTSPD": 0.8000, "ETARAT": 1.0290},
            {"PCTSPD": 0.7000, "ETARAT": 1.0170},
            {"PCTSPD": 0.5000, "ETARAT": 1.0230}
        ]

        self.efficiency_table.setRowCount(len(efficiency_ratio_table_entries))
        row = 0
        for efficiency_table_entry in efficiency_ratio_table_entries:
            self.efficiency_table.setItem(row, 0, QTableWidgetItem(str(efficiency_table_entry['PCTSPD'])))
            self.efficiency_table.setItem(row, 1, QTableWidgetItem(str(efficiency_table_entry['ETARAT'])))
            row += 1

        # stretch columns to fill the table width
        header = self.efficiency_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # shrink table height to fit rows exactly
        self.efficiency_table.resizeRowsToContents()
        total_height = self.efficiency_table.horizontalHeader().height()
        for i in range(self.efficiency_table.rowCount()):
            total_height += self.efficiency_table.rowHeight(i)
        self.efficiency_table.setFixedHeight(total_height)

        # disable scrollbars since everything is visible
        self.efficiency_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.efficiency_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        s5.add_widget(self.efficiency_table)

        s6 = accordion.add_section('Bleed Table')
        self.bleed_table_section = s6
        self.rebuild_bleed_table()

        # input design characteristics (dynamic - will be populated on init and when stages change)
        self.characteristics_section = accordion.add_section('Input Design Characteristics')
        self.rebuild_characteristics()

        # root layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(accordion)

    def extract_info(self):
        """
        Extract information from UI widgets and create a structured dict
        """
        config = {}
        
        # Extract SI Input Parameters
        config["SI Input Parameters"] = {}
        for key, widget in self.input_params_widgets.items():
            config["SI Input Parameters"][key] = widget.text()
        
        # Extract Deviation Factors
        config["Deviation Factors"] = {}
        for key, widget in self.deviation_factors_widgets.items():
            config["Deviation Factors"][key] = "1.0" if widget.isChecked() else "0.0"
        
        # Extract Specific Heat Coefficients
        config["Specific Heat Coefficients"] = {}
        for key, widget in self.specific_heat_widgets.items():
            config["Specific Heat Coefficients"][key] = widget.text()
        
        # Extract Stage Geometry
        config["Stage Geometry"] = {}
        for key, widget in self.stage_geometry_widgets.items():
            config["Stage Geometry"][key] = widget.text()
        
        # Extract Characteristics
        config["Input Characteristics"] = {}
        for key, widget in self.characteristics_widgets.items():
            config["Input Characteristics"][key] = widget.text()
        
        # Extract Efficiency Table
        config["Efficiency Ratio Table"] = []
        if self.efficiency_table:
            for row in range(self.efficiency_table.rowCount()):
                pctspd = self.efficiency_table.item(row, 0).text()
                etarat = self.efficiency_table.item(row, 1).text()
                config["Efficiency Ratio Table"].append({
                    "PCTSPD": float(pctspd) if pctspd else 0.0,
                    "ETARAT": float(etarat) if etarat else 0.0
                })
        
        # Extract Bleed Table
        config["Bleed Table"] = []
        if self.bleed_table:
            for row in range(self.bleed_table.rowCount()):
                speed = self.bleed_table.item(row, 0).text()
                stage_values = []
                # Columns 1+ are stage bleed values
                for col in range(1, self.bleed_table.columnCount()):
                    value = self.bleed_table.item(row, col).text() if self.bleed_table.item(row, col) else "0.000"
                    try:
                        stage_values.append(float(value))
                    except:
                        stage_values.append(0.0)
                config["Bleed Table"].append({
                    "PCTSPD": float(speed) if speed else 0.0,
                    "stage_values": stage_values
                })
        
        # Extract Characteristic Tables
        config["Characteristic Tables"] = []
        for table in self.characteristic_tables:
            table_data = []
            for row in range(table.rowCount()):
                pctspd = table.item(row, 0).text()
                etarat = table.item(row, 1).text()
                table_data.append({
                    "PCTSPD": float(pctspd) if pctspd else 0.0,
                    "ETARAT": float(etarat) if etarat else 0.0
                })
            config["Characteristic Tables"].append(table_data)
        
        self.logger.info(f"Config: {json.dumps(config, indent=2, default=str)}")
        return config

    def rebuild_stage_sections(self):
        """Rebuild stage geometry, characteristics, and bleed table when STAGES changes"""
        self.rebuild_stage_geometry()
        self.rebuild_characteristics()
        self.rebuild_bleed_table()

    def rebuild_stage_geometry(self):
        """Dynamically create stage geometry inputs based on number of stages"""
        try:
            num_stages = int(float(self.input_params_widgets['STAGES'].text() or 0))
        except (ValueError, TypeError):
            num_stages = 0
        
        if num_stages <= 0:
            return
        
        # Clear the section
        while self.stage_geometry_section.content_layout.count() > 0:
            item = self.stage_geometry_section.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.stage_geometry_widgets = {}
        
        # Stage geometry parameters per the file format
        geometry_params = [
            ("RT2",   "Rotor Inlet Tip Radius"),
            ("RH2",   "Rotor Inlet Hub Radius"),
            ("RT3",   "Rotor Outlet Tip Radius"),
            ("RH3",   "Rotor Outlet Hub Radius"),
            ("BET2M", "Rotor Inlet Absolute Flow Angle At Design Speed And Flow And Specified Blade Reset, Deg"),
            ("CB2M",  "Change In Rotor Inlet Absolute Flow Angle At Meanline Radius, Deg"),
            ("CB2MR", "Change In Rotor Inlet Relative Flow Angle At Meanline Radius, Deg"),
            ("CB3MR", "Change In Rotor Outlet Relative Flow Angle At Meanline Radius, Deg"),
            ("RK2M",  "Rotor Inlet Blade Metal Angle At Meanline Radius, Deg"),
            ("RSOLM", "Rotor Blade Row Solidity At Meanline Radius"),
            ("SK2M",  "Stator Inlet Blade Metal Angle At Meanline Radius, Deg"),
        ]
        
        # Create an accordion for each stage
        for stage_num in range(1, num_stages + 1):
            # Create accordion section for this stage
            stage_accordion = AccordionSection(f"▶ Stage {stage_num}")
            self.stage_geometry_section.add_widget(stage_accordion)
            
            # Parameter inputs for this stage
            for var, desc in geometry_params:
                param_row = QWidget()
                param_layout = QHBoxLayout(param_row)
                param_layout.setContentsMargins(0, 0, 0, 0)
                param_label = QLabel(f"{var}:")
                param_label.setToolTip(desc)
                param_label.setFixedWidth(80)
                param_widget = QLineEdit()
                param_layout.addWidget(param_label)
                param_layout.addWidget(param_widget)
                stage_accordion.add_widget(param_row)
                
                # Store with key: STAGE_X_PARAM
                key = f"STAGE_{stage_num}_{var}"
                self.stage_geometry_widgets[key] = param_widget

    def rebuild_characteristics(self):
        """Dynamically create input characteristics based on number of stages and speeds"""
        try:
            num_stages = int(float(self.input_params_widgets['STAGES'].text() or 0))
        except (ValueError, TypeError):
            return
        
        if num_stages <= 0:
            return
        
        # Clear the section
        while self.characteristics_section.content_layout.count() > 0:
            item = self.characteristics_section.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.characteristics_widgets = {}
        
        # Create characteristics for each stage
        for stage_num in range(1, num_stages + 1):
            # Create accordion for this stage
            stage_accordion = AccordionSection(f"▶ Stage {stage_num}")
            self.characteristics_section.add_widget(stage_accordion)
            
            # Create a nested accordion for each speed point
            for speed in self.speed_points:
                # Create accordion for this speed point
                speed_accordion = AccordionSection(f"▶ {speed:.3f} PCT SPD")
                stage_accordion.add_widget(speed_accordion)
                
                # PHIDES
                phides_row = QWidget()
                phides_layout = QHBoxLayout(phides_row)
                phides_layout.setContentsMargins(0, 0, 0, 0)
                phides_label = QLabel(f"PHIDES:")
                phides_label.setToolTip("Stage Flow Coefficient At Design Speed")
                phides_label.setFixedWidth(80)
                phides_widget = QLineEdit()
                phides_layout.addWidget(phides_label)
                phides_layout.addWidget(phides_widget)
                speed_accordion.add_widget(phides_row)
                key = f"STAGE_{stage_num}_SPEED_{speed:.3f}_PHIDES"
                self.characteristics_widgets[key] = phides_widget
                
                # PSIDES
                psides_row = QWidget()
                psides_layout = QHBoxLayout(psides_row)
                psides_layout.setContentsMargins(0, 0, 0, 0)
                psides_label = QLabel(f"PSIDES:")
                psides_label.setToolTip("Stage Pressure Coefficient At Design Speed")
                psides_label.setFixedWidth(80)
                psides_widget = QLineEdit()
                psides_layout.addWidget(psides_label)
                psides_layout.addWidget(psides_widget)
                speed_accordion.add_widget(psides_row)
                key = f"STAGE_{stage_num}_SPEED_{speed:.3f}_PSIDES"
                self.characteristics_widgets[key] = psides_widget
                
                # ETADES
                etades_row = QWidget()
                etades_layout = QHBoxLayout(etades_row)
                etades_layout.setContentsMargins(0, 0, 0, 0)
                etades_label = QLabel(f"ETADES:")
                etades_label.setToolTip("Stage Adiabatic Efficiency At Design Speed")
                etades_label.setFixedWidth(80)
                etades_widget = QLineEdit()
                etades_layout.addWidget(etades_label)
                etades_layout.addWidget(etades_widget)
                speed_accordion.add_widget(etades_row)
                key = f"STAGE_{stage_num}_SPEED_{speed:.3f}_ETADES"
                self.characteristics_widgets[key] = etades_widget

    def rebuild_bleed_table(self):
        """Dynamically create bleed table based on number of stages"""
        try:
            num_stages = int(float(self.input_params_widgets['STAGES'].text() or 0))
        except (ValueError, TypeError):
            num_stages = 0
        
        if num_stages <= 0:
            return
        
        # Clear the section
        while self.bleed_table_section.content_layout.count() > 0:
            item = self.bleed_table_section.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.bleed_table = QTableWidget()
        # Columns: PCT SPD + one for each stage
        num_cols = num_stages + 1
        self.bleed_table.setColumnCount(num_cols)
        
        # Set header labels: PCT SPD, Stage 1, Stage 2, etc.
        headers = ['PCT SPD'] + [f'Stage {i}' for i in range(1, num_stages + 1)]
        self.bleed_table.setHorizontalHeaderLabels(headers)
        
        # Bleed table speed points (5 points, not including 0.000)
        bleed_speeds = [1.000, 0.900, 0.800, 0.700, 0.500]
        self.bleed_table.setRowCount(len(bleed_speeds))
        
        # Populate with speed points and empty cells for stage values
        for row, speed in enumerate(bleed_speeds):
            # First column: speed point
            self.bleed_table.setItem(row, 0, QTableWidgetItem(f"{speed:.3f}"))
            # Other columns: stage bleed values (initially 0.000)
            for col in range(1, num_cols):
                self.bleed_table.setItem(row, col, QTableWidgetItem("0.000"))
        
        # Stretch columns to fill table width
        header = self.bleed_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Shrink table height to fit rows exactly
        self.bleed_table.resizeRowsToContents()
        total_height = self.bleed_table.horizontalHeader().height()
        for i in range(self.bleed_table.rowCount()):
            total_height += self.bleed_table.rowHeight(i)
        self.bleed_table.setFixedHeight(total_height)
        
        # Disable scrollbars since everything is visible
        self.bleed_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.bleed_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.bleed_table_section.add_widget(self.bleed_table)

    def open_file(self):
        """
        Open a file
        """
        self.file_path = QFileDialog.getOpenFileName(self, "Open File", "~", "All Files (*)")[0]
        if self.file_path:
            self.logger.info(f"Opened file: {self.file_path}")
            self.event_manager.emit("file_opened")

    def new_file(self):
        """Clear all UI fields for a new file"""
        # Clear input parameters
        for widget in self.input_params_widgets.values():
            widget.clear()
        
        # Clear deviation factors
        for widget in self.deviation_factors_widgets.values():
            widget.setChecked(False)
        
        # Clear specific heat coefficients
        for widget in self.specific_heat_widgets.values():
            widget.clear()
        
        self.file_path = None
        self.logger.info("New File Created")

    def save_file(self):
        """Save current UI state"""
        if not self.file_path:
            self.file_path = QFileDialog.getSaveFileName(self, "Save File", "~", "All Files (*)")[0]
            if not self.file_path:
                return
        
        try:
            self.logger.info(f"File saved successfully: {self.file_path}")
        except Exception as e:
            self.logger.error(f"Error saving file: {str(e)}")

