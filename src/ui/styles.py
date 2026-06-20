def get_global_style():
    return """
    QMainWindow {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    QWidget {
        font-family: 'Segoe UI', Inter, sans-serif;
        color: #e0e0e0;
    }
    QLabel {
        font-size: 14px;
        color: #e0e0e0;
    }
    QLabel#Footer {
        font-size: 12px;
        color: #888888;
    }
    QLabel#Header {
        font-size: 24px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 10px;
    }
    QPushButton {
        background-color: #3a3f44;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 8px 16px;
        font-size: 14px;
        color: #ffffff;
    }
    QPushButton:hover {
        background-color: #50565c;
    }
    QPushButton:pressed {
        background-color: #2b2f33;
    }
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
        background-color: #2a2a2a;
        border: 1px solid #444;
        border-radius: 4px;
        padding: 8px;
        color: #ffffff;
        font-size: 14px;
    }
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
        border: 1px solid #007acc;
    }
    QListWidget {
        background-color: #252526;
        border: 1px solid #333;
        border-radius: 4px;
        outline: 0;
    }
    QListWidget::item {
        padding: 10px;
        border-bottom: 1px solid #333;
    }
    QListWidget::item:selected {
        background-color: #007acc;
        color: white;
    }
    """
