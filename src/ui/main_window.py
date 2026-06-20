from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QStackedWidget, QLabel)
from PyQt6.QtCore import Qt
from src.ui.settings_page import SettingsPage
from src.ui.generator_page import GeneratorPage
from src.ui.styles import get_global_style

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Report Generator - MCP Client")
        self.resize(1000, 700)
        self.setStyleSheet(get_global_style())
        
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Content Layout
        content_layout = QHBoxLayout()
        
        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.insertItem(0, "Report Generator")
        self.sidebar.insertItem(1, "API Settings")
        self.sidebar.currentRowChanged.connect(self.display_page)
        content_layout.addWidget(self.sidebar)
        
        # Stacked Widget
        self.stacked_widget = QStackedWidget()
        self.generator_page = GeneratorPage()
        self.settings_page = SettingsPage()
        
        self.stacked_widget.addWidget(self.generator_page)
        self.stacked_widget.addWidget(self.settings_page)
        
        content_layout.addWidget(self.stacked_widget)
        
        main_layout.addLayout(content_layout)
        
        # Footer
        footer = QLabel("made by lunarmist-byte from tinkerhub ce-alappuzha")
        footer.setObjectName("Footer")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(footer)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Default Selection
        self.sidebar.setCurrentRow(0)

    def display_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
