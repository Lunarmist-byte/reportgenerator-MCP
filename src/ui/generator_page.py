import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QFileDialog, QRadioButton, 
                             QButtonGroup, QMessageBox, QProgressDialog)
from PyQt6.QtCore import Qt
from src.ui.calibrator import CalibratorView
from src.core.storage import load_settings
from src.core.llm_engine import generate_report
from src.core.pdf_engine import create_pdf

class GeneratorPage(QWidget):
    def __init__(self):
        super().__init__()
        self.logo_path = None
        self.picture_path = None
        self.csv_path = None
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        
        # Left side: Inputs
        left_layout = QVBoxLayout()
        
        header = QLabel("Report Generator")
        header.setObjectName("Header")
        left_layout.addWidget(header)
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Enter your rough notes here...")
        left_layout.addWidget(self.notes_input)
        
        # Report type
        type_layout = QHBoxLayout()
        self.type_group = QButtonGroup(self)
        self.std_radio = QRadioButton("Standard Report")
        self.std_radio.setChecked(True)
        self.fin_radio = QRadioButton("Financial Report (Tabular)")
        self.type_group.addButton(self.std_radio)
        self.type_group.addButton(self.fin_radio)
        type_layout.addWidget(self.std_radio)
        type_layout.addWidget(self.fin_radio)
        left_layout.addLayout(type_layout)
        
        # Assets
        asset_layout = QHBoxLayout()
        
        self.logo_btn = QPushButton("Select Logo")
        self.logo_btn.clicked.connect(self.select_logo)
        asset_layout.addWidget(self.logo_btn)
        
        self.pic_btn = QPushButton("Select Picture")
        self.pic_btn.clicked.connect(self.select_picture)
        asset_layout.addWidget(self.pic_btn)
        
        self.csv_btn = QPushButton("Select CSV (Optional)")
        self.csv_btn.clicked.connect(self.select_csv)
        asset_layout.addWidget(self.csv_btn)
        
        left_layout.addLayout(asset_layout)
        
        self.asset_labels = QLabel("None selected")
        left_layout.addWidget(self.asset_labels)
        
        self.generate_btn = QPushButton("Generate Report (PDF)")
        self.generate_btn.clicked.connect(self.generate_report_action)
        self.generate_btn.setStyleSheet("background-color: #007acc; font-weight: bold;")
        left_layout.addWidget(self.generate_btn)
        
        # Right side: Calibrator
        right_layout = QVBoxLayout()
        cal_header = QLabel("Logo Calibrator (Drag to position)")
        right_layout.addWidget(cal_header)
        self.calibrator = CalibratorView()
        right_layout.addWidget(self.calibrator)
        right_layout.addStretch()
        
        layout.addLayout(left_layout, 2)
        layout.addLayout(right_layout, 1)
        
        self.setLayout(layout)

    def select_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Logo", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.logo_path = path
            self.calibrator.set_logo(path)
            self.update_asset_labels()

    def select_picture(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Picture", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.picture_path = path
            self.update_asset_labels()
            
    def select_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)")
        if path:
            self.csv_path = path
            self.update_asset_labels()
            
    def update_asset_labels(self):
        texts = []
        if self.logo_path: texts.append(f"Logo: {os.path.basename(self.logo_path)}")
        if self.picture_path: texts.append(f"Pic: {os.path.basename(self.picture_path)}")
        if self.csv_path: texts.append(f"CSV: {os.path.basename(self.csv_path)}")
        self.asset_labels.setText(" | ".join(texts) if texts else "None selected")

    def generate_report_action(self):
        notes = self.notes_input.toPlainText().strip()
        if not notes:
            QMessageBox.warning(self, "Error", "Please enter some notes.")
            return
            
        settings = load_settings()
        report_type = "Financial" if self.fin_radio.isChecked() else "Standard"
        
        csv_data = None
        if self.csv_path and os.path.exists(self.csv_path):
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                csv_data = f.read()
                
        # Show progress
        progress = QProgressDialog("Generating AI Report...", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        try:
            # 1. Ask LLM
            report_data = generate_report(settings, notes, report_type, csv_data)
            
            if not report_data:
                raise Exception("Failed to generate report data from LLM.")
                
            # 2. Get save path
            save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "report.pdf", "PDF Files (*.pdf)")
            if not save_path:
                progress.close()
                return
                
            # 3. Create PDF
            logo_coords = self.calibrator.get_pdf_coordinates()
            create_pdf(save_path, report_data, self.logo_path, logo_coords, self.picture_path)
            
            progress.close()
            QMessageBox.information(self, "Success", f"Report saved to:\n{save_path}")
            
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "Error", str(e))
