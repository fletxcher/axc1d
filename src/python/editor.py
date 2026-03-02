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
        self.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background: transparent; 
            }
        """)

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
    def __init__(self, logger: logging.Logger,  parent = None):
        super().__init__(parent)
        self.logger = logger
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
            ("RPM", "Revolutions Per Minute"),
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
        
        # Populate with default values
        self.populate_default_values()

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
            num_points = int(float(self.input_params_widgets['POINTS'].text() or 8))
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
                
                # Create table for this speed point with 3 rows (PHIDES, PSIDES, ETADES)
                # and num_points columns for values
                table = QTableWidget()
                table.setRowCount(3)
                table.setColumnCount(num_points + 1)  # +1 for row labels
                
                # Set row labels (first column)
                row_labels = ['PHIDES', 'PSIDES', 'ETADES']
                for row_idx, row_label in enumerate(row_labels):
                    label_item = QTableWidgetItem(row_label)
                    label_item.setFlags(label_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Read-only
                    table.setItem(row_idx, 0, label_item)
                
                # Set column header
                headers = [''] + [f'{i+1}' for i in range(num_points)]
                table.setHorizontalHeaderLabels(headers)
                
                # Make first column narrower for labels
                table.setColumnWidth(0, 80)
                
                # Create editable cells for values
                for row in range(3):
                    for col in range(1, num_points + 1):
                        item = QTableWidgetItem('')
                        table.setItem(row, col, item)
                
                # Stretch columns
                header = table.horizontalHeader()
                for col in range(1, num_points + 1):
                    header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
                
                # Set fixed height
                table.resizeRowsToContents()
                total_height = table.horizontalHeader().height()
                for i in range(table.rowCount()):
                    total_height += table.rowHeight(i)
                table.setFixedHeight(total_height)
                
                # Disable scrollbars
                table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                
                # Store table reference with key
                key = f"STAGE_{stage_num}_SPEED_{speed:.3f}_TABLE"
                self.characteristics_widgets[key] = table
                
                speed_accordion.add_widget(table)

    def rebuild_bleed_table(self):
        """Dynamically create bleed table based on number of stages"""
        try:
            num_stages = int(float(self.input_params_widgets['STAGES'].text() or 0))
        except (ValueError, TypeError):
            num_stages = 0
        
        if num_stages <= 0:
            return
        
        # clear the section
        while self.bleed_table_section.content_layout.count() > 0:
            item = self.bleed_table_section.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.bleed_table = QTableWidget()
        # columns: PCT SPD + one for each stage
        num_cols = num_stages + 1
        self.bleed_table.setColumnCount(num_cols)
        
        # set header labels: PCT SPD, Stage 1, Stage 2, etc.
        headers = ['PCT SPD'] + [f'Stage {i}' for i in range(1, num_stages + 1)]
        self.bleed_table.setHorizontalHeaderLabels(headers)
        
        # bleed table speed points (5 points, not including 0.000)
        bleed_speeds = [1.000, 0.900, 0.800, 0.700, 0.500]
        self.bleed_table.setRowCount(len(bleed_speeds))
        
        # populate with speed points and empty cells for stage values
        for row, speed in enumerate(bleed_speeds):
            # first column: speed point
            self.bleed_table.setItem(row, 0, QTableWidgetItem(f"{speed:.3f}"))
            # other columns: stage bleed values (initially 0.000)
            for col in range(1, num_cols):
                self.bleed_table.setItem(row, col, QTableWidgetItem("0.000"))
        
        # stretch columns to fill table width
        header = self.bleed_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # shrink table height to fit rows exactly
        self.bleed_table.resizeRowsToContents()
        total_height = self.bleed_table.horizontalHeader().height()
        for i in range(self.bleed_table.rowCount()):
            total_height += self.bleed_table.rowHeight(i)
        self.bleed_table.setFixedHeight(total_height)
        
        # disable scrollbars since everything is visible
        self.bleed_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.bleed_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.bleed_table_section.add_widget(self.bleed_table)
    
    def populate_default_values(self):
        """Populate all fields with default values from origin.axc1d"""
        # input parameters defaults
        defaults_si = {
            'STAGES': '2.000',
            'SPEEDS': '5.000',
            'P_0_IN': '10.135',
            'T_0_IN': '288.170',
            'POINTS': '8.000',
            'MOLE_WT': '28.970',
            'RPM': '16042.797',
            'MASS_FLOW': '33.248'
        }
        for key, value in defaults_si.items():
            if key in self.input_params_widgets:
                self.input_params_widgets[key].setText(value)
        
        # deviation factors defaults (all checked/1.0)
        for widget in self.deviation_factors_widgets.values():
            widget.setChecked(True)
        
        # specific heat coefficients defaults 
        defaults_cpco = {
            'CPCO_1': '0.23747E+00',
            'CPCO_2': '0.21962E-04',
            'CPCO_3': '-0.87791E-07',
            'CPCO_4': '0.13991E-09',
            'CPCO_5': '-0.78056E-13',
            'CPCO_6': '0.15043E-16'
        }
        for key, value in defaults_cpco.items():
            if key in self.specific_heat_widgets:
                self.specific_heat_widgets[key].setText(value)
        
        # rebuild dynamic sections now that STAGES is set, which will populate "Stage Geometry" and "Characteristics"
        self.rebuild_stage_sections()
        
        # stage geometry defaults 
        stage_1_defaults = {
            'STAGE_1_RT2': '25.4200',
            'STAGE_1_RH2': '9.8910',
            'STAGE_1_RT3': '24.6280',
            'STAGE_1_RH3': '12.0880',
            'STAGE_1_BET2M': '0.00',
            'STAGE_1_CB2M': '0.00',
            'STAGE_1_CB2MR': '0.00',
            'STAGE_1_CB3MR': '0.00',
            'STAGE_1_RK2M': '56.15',
            'STAGE_1_RSOLM': '1.6800',
            'STAGE_1_SK2M': '36.10'
        }
        stage_2_defaults = {
            'STAGE_2_RT2': '23.9600',
            'STAGE_2_RH2': '13.6040',
            'STAGE_2_RT3': '23.5660',
            'STAGE_2_RH3': '14.6960',
            'STAGE_2_BET2M': '0.00',
            'STAGE_2_CB2M': '0.00',
            'STAGE_2_CB2MR': '0.00',
            'STAGE_2_CB3MR': '0.00',
            'STAGE_2_RK2M': '55.46',
            'STAGE_2_RSOLM': '1.5700',
            'STAGE_2_SK2M': '36.15'
        }
        
        for key, value in {**stage_1_defaults, **stage_2_defaults}.items():
            if key in self.stage_geometry_widgets:
                self.stage_geometry_widgets[key].setText(value)
        
        # input characteristics defaults 
        stage_1_chars = {
            'STAGE_1_SPEED_1.000_TABLE_PHIDES': '0.3100  0.3500  0.3800  0.4200  0.4300  0.4400  0.4500  0.4600',
            'STAGE_1_SPEED_1.000_TABLE_PSIDES': '0.0000  0.0000  0.0000  0.0000  0.0000  0.0000  0.0000  0.0000',
            'STAGE_1_SPEED_1.000_TABLE_ETADES': '0.0000  0.0000  0.0000  0.0000  0.0000  0.0000  0.0000  0.0000',
        }
        stage_2_chars = {
            'STAGE_2_SPEED_1.000_TABLE_PHIDES': '0.4000  0.4200  0.4400  0.4500  0.4600  0.4800  0.5100  0.5300',
            'STAGE_2_SPEED_1.000_TABLE_PSIDES': '0.0000  0.0000  0.0000  0.0000  0.0000  0.0000  0.0000  0.0000',
            'STAGE_2_SPEED_1.000_TABLE_ETADES': '0.0000  0.0000  0.0000  0.0000  0.0000  0.0000  0.0000  0.0000',
        }
        
        # Populate table cells from defaults
        for key, value in {**stage_1_chars, **stage_2_chars}.items():
            # Convert key from STAGE_X_SPEED_Y_TABLE_LABEL to STAGE_X_SPEED_Y_TABLE
            table_key = key.rsplit('_', 1)[0]
            row_label = key.rsplit('_', 1)[1]
            
            if table_key in self.characteristics_widgets:
                table = self.characteristics_widgets[table_key]
                if isinstance(table, QTableWidget):
                    # Find row index based on label
                    row_idx = {'PHIDES': 0, 'PSIDES': 1, 'ETADES': 2}.get(row_label, 0)
                    # Split values and populate columns
                    values = [v.strip() for v in value.split()]
                    for col_idx, val in enumerate(values):
                        if col_idx + 1 < table.columnCount():  # +1 because first column is labels
                            table.setItem(row_idx, col_idx + 1, QTableWidgetItem(val))
    
    def extract_info(self):
        """
        Extract information from UI widgets and create a structured dict
        """
        config = {}
        
        # Extract SI Input Parameters
        config["SI Input Parameters"] = {}
        for key, widget in self.input_params_widgets.items():
            try:
                config["SI Input Parameters"][key] = float(widget.text())
            except (ValueError, AttributeError):
                config["SI Input Parameters"][key] = widget.text()
        
        # Extract Deviation Factors
        config["Deviation Factors"] = {}
        for key, widget in self.deviation_factors_widgets.items():
            config["Deviation Factors"][key] = 1.0 if widget.isChecked() else 0.0
        
        # Extract Specific Heat Coefficients
        config["Specific Heat Coefficients"] = {}
        for key, widget in self.specific_heat_widgets.items():
            try:
                config["Specific Heat Coefficients"][key] = float(widget.text())
            except (ValueError, AttributeError):
                config["Specific Heat Coefficients"][key] = widget.text()
        
        # Extract Stage Geometry
        config["Stage Geometry"] = {}
        for key, widget in self.stage_geometry_widgets.items():
            try:
                config["Stage Geometry"][key] = float(widget.text())
            except (ValueError, AttributeError):
                config["Stage Geometry"][key] = widget.text()
        
        # Extract Characteristics - structured for solver: list of stages with points
        config["Input Design Characteristics"] = []
        
        try:
            num_stages = int(float(self.input_params_widgets['STAGES'].text() or 0))
        except:
            num_stages = 0
        
        for stage_num in range(1, num_stages + 1):
            # For each stage, get the first speed point's data (1.000 PCT SPD)
            table_key = f"STAGE_{stage_num}_SPEED_1.000_TABLE"
            
            if table_key in self.characteristics_widgets:
                table = self.characteristics_widgets[table_key]
                if isinstance(table, QTableWidget):
                    # Extract phi (PHIDES), psi (PSIDES), eta (ETADES) values
                    points = []
                    
                    # Number of columns - 1 (first column is labels)
                    num_points = table.columnCount() - 1
                    
                    # For each characteristic point
                    for col_idx in range(num_points):
                        phi = 0.0
                        psi = 0.0
                        eta = 0.0
                        
                        # Row 0 = PHIDES, Row 1 = PSIDES, Row 2 = ETADES
                        try:
                            phi_item = table.item(0, col_idx + 1)
                            phi = float(phi_item.text()) if phi_item and phi_item.text() else 0.0
                        except:
                            phi = 0.0
                        
                        try:
                            psi_item = table.item(1, col_idx + 1)
                            psi = float(psi_item.text()) if psi_item and psi_item.text() else 0.0
                        except:
                            psi = 0.0
                        
                        try:
                            eta_item = table.item(2, col_idx + 1)
                            eta = float(eta_item.text()) if eta_item and eta_item.text() else 0.0
                        except:
                            eta = 0.0
                        
                        points.append({
                            "phi": phi,
                            "psi": psi,
                            "eta": eta
                        })
                    
                    config["Input Design Characteristics"].append({
                        "points": points
                    })
        
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
        
        # self.logger.info(f"Config: {json.dumps(config, indent=2, default=str)}")
        return config

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

