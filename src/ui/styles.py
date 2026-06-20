def get_global_style():
    return """
    QMainWindow {
        background-color: #0f111a;
        color: #a6accd;
    }
    QWidget {
        font-family: 'Segoe UI Variable', 'Inter', 'Segoe UI', sans-serif;
        color: #a6accd;
        font-size: 14px;
    }
    QLabel {
        color: #a6accd;
    }
    QLabel#Header {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 16px;
        letter-spacing: 0.5px;
    }
    QLabel#Footer {
        font-size: 12px;
        color: #636b8a;
    }
    QPushButton {
        background-color: #1e2130;
        border: 1px solid #2a2e42;
        border-radius: 6px;
        padding: 10px 18px;
        font-weight: 600;
        color: #e0e0e0;
    }
    QPushButton:hover {
        background-color: #2a2e42;
        border: 1px solid #3c425c;
        color: #ffffff;
    }
    QPushButton:pressed {
        background-color: #151823;
        border: 1px solid #89b4fa;
    }
    QPushButton#PrimaryButton {
        background-color: #89b4fa;
        color: #11111b;
        border: none;
    }
    QPushButton#PrimaryButton:hover {
        background-color: #b4befe;
    }
    QPushButton#PrimaryButton:pressed {
        background-color: #74c7ec;
    }
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
        background-color: #181a26;
        border: 1px solid #2a2e42;
        border-radius: 6px;
        padding: 10px;
        color: #cdd6f4;
        selection-background-color: #89b4fa;
        selection-color: #11111b;
    }
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
        border: 1px solid #89b4fa;
        background-color: #1e2130;
    }
    QListWidget {
        background-color: #0f111a;
        border: none;
        border-right: 1px solid #1e2130;
        outline: 0;
        padding: 10px 0px;
    }
    QListWidget::item {
        padding: 12px 20px;
        margin: 4px 12px;
        border-radius: 8px;
        color: #a6accd;
    }
    QListWidget::item:hover {
        background-color: #1e2130;
        color: #cdd6f4;
    }
    QListWidget::item:selected {
        background-color: #89b4fa;
        color: #11111b;
        font-weight: bold;
    }
    QRadioButton {
        spacing: 8px;
        color: #a6accd;
    }
    QRadioButton::indicator {
        width: 18px;
        height: 18px;
        border-radius: 9px;
        border: 2px solid #3c425c;
        background-color: #181a26;
    }
    QRadioButton::indicator:checked {
        background-color: #89b4fa;
        border: 5px solid #181a26;
    }
    QRadioButton::indicator:hover {
        border: 2px solid #89b4fa;
    }
    QProgressDialog {
        background-color: #1e2130;
        color: #a6accd;
    }
    QProgressBar {
        border: 1px solid #3c425c;
        border-radius: 4px;
        text-align: center;
        background-color: #0f111a;
    }
    QProgressBar::chunk {
        background-color: #89b4fa;
        width: 10px;
    }
    QMessageBox {
        background-color: #0f111a;
    }
    QMessageBox QLabel {
        color: #cdd6f4;
    }
    """
