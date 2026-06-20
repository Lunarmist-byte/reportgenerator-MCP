# AI Report Generator

A clean, minimalistic standalone desktop software built with **Python and PyQt6** to automatically generate comprehensive PDF reports using LLMs (OpenAI, Gemini, OpenRouter).

*Made by lunarmist-byte from tinkerhub ce-alappuzha*

## Features

- **Multi-LLM Support:** Seamlessly connect to OpenAI, Google Gemini, and OpenRouter APIs. Your API keys are securely saved locally.
- **Advanced Layout Calibrator:** Features an interactive `QGraphicsView` page simulator. Drag and drop your logo, and use your mouse wheel to zoom/resize it precisely where you want it.
- **Customizable Typography & Formats:** Choose your font family (Helvetica, Times, Courier), font size, text color, and target page format (A4, Letter, Legal) for the output PDF.
- **Multi-Page & Multi-Picture Flow:** Upload multiple pictures which seamlessly flow into the multi-page auto-generated document.
- **Financial & Tabular Reports:** Upload raw CSV data and let the AI generate a clean, structured financial table within your report.
- **Rich PDF Generation:** Powered by `reportlab` to produce pixel-perfect, professionally styled, multi-page PDFs.
- **Minimalistic UI:** A dark-themed, premium desktop GUI built from the ground up for a fast, clutter-free user experience.

## Prerequisites

- Python 3.9+
- An API Key from [OpenAI](https://platform.openai.com/), [Google Gemini](https://aistudio.google.com/), or [OpenRouter](https://openrouter.ai/).

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Lunarmist-byte/attendancematcherscraper.git
   cd attendancematcherscraper
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - **Windows:** `.\venv\Scripts\activate`
   - **macOS/Linux:** `source venv/bin/activate`

4. **Install the dependencies:**
   ```bash
   pip install PyQt6 reportlab openai google-generativeai python-dotenv pandas pillow
   ```

## Usage

You can launch the application easily using the provided batch file (on Windows):

```bash
.\run_app.bat
```

Or you can run the Python script directly:

```bash
python main.py
```

### Quick Start Guide

1. **Configure API:** Go to the **API Settings** tab on the left sidebar, enter your preferred API key (e.g., Gemini API Key), and select your default provider. Click **Save Settings**.
2. **Input Notes:** Switch to the **Report Generator** tab. Enter rough notes or a summary of what you want the report to cover.
3. **Upload Assets:** Click "Select Logo" to add a company logo, and "Add Picture" to select multiple inline images. If you have tabular data, click "Select CSV".
4. **Customize Typography:** Pick your font family, size, text color, and target page format (A4, Letter, Legal) directly in the UI.
5. **Calibrate:** Drag your logo around the visual page calibrator on the right to position it precisely. Use your mouse scroll wheel to resize the logo.
6. **Generate:** Click **Generate Report (PDF)**. The AI will process your notes and assets, and prompt you to save the resulting multi-page PDF file.

## Architecture

- `main.py`: Application entry point.
- `src/ui/`: Contains the PyQt6 graphical interface modules (`main_window.py`, `settings_page.py`, `generator_page.py`, `calibrator.py`, `styles.py`).
- `src/core/llm_engine.py`: Handles connections and strict JSON prompting for OpenAI/Gemini/OpenRouter.
- `src/core/pdf_engine.py`: Handles `reportlab` logic for drawing text, tables, and absolutely-positioned images on the PDF canvas.
- `src/core/storage.py`: Manages local `config.json` state for saving API keys securely.

## License

This project is licensed under the MIT License.
