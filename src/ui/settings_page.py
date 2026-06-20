from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QFormLayout, QMessageBox)
from src.core.storage import load_settings, save_settings

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel("API Settings")
        header.setObjectName("Header")
        layout.addWidget(header)
        
        form_layout = QFormLayout()
        
        self.openai_input = QLineEdit()
        self.openai_input.setText(self.settings.get("openai_api_key", ""))
        self.openai_input.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        form_layout.addRow("OpenAI API Key:", self.openai_input)
        
        self.gemini_input = QLineEdit()
        self.gemini_input.setText(self.settings.get("gemini_api_key", ""))
        self.gemini_input.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        form_layout.addRow("Gemini API Key:", self.gemini_input)
        
        self.openrouter_input = QLineEdit()
        self.openrouter_input.setText(self.settings.get("openrouter_api_key", ""))
        self.openrouter_input.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        form_layout.addRow("OpenRouter API Key:", self.openrouter_input)
        
        self.model_select = QComboBox()
        self.model_select.addItems(["openai", "gemini", "openrouter"])
        self.model_select.setCurrentText(self.settings.get("default_model", "openai"))
        form_layout.addRow("Default Provider:", self.model_select)
        
        layout.addLayout(form_layout)
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def save_settings(self):
        self.settings["openai_api_key"] = self.openai_input.text()
        self.settings["gemini_api_key"] = self.gemini_input.text()
        self.settings["openrouter_api_key"] = self.openrouter_input.text()
        self.settings["default_model"] = self.model_select.currentText()
        
        save_settings(self.settings)
        QMessageBox.information(self, "Success", "Settings saved locally.")
