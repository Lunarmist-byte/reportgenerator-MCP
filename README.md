# Report Generator

A standalone desktop software built with **Python and CustomTkinter** to generate PDF reports using LLMs (OpenAI, Gemini, OpenRouter).

*Made by Lunarmist-byte. [GitHub](https://github.com/Lunarmist-byte) | [LinkedIn](https://www.linkedin.com/in/amal-s-kumar-ba69a1290/)*

## Features

- **Multi-LLM Support:** Connect to OpenAI, Google Gemini, and OpenRouter APIs. API keys are saved locally.
- **Layout Calibrator:** Features an interactive `tkinter.Canvas` page simulator. Drag and drop your logo, use your mouse wheel to resize, and drag corners/sides to adjust layout.
- **Customizable Typography:** Choose your font family, font size, text color, and target page format for the output PDF.
- **Image Support:** Upload images to include in the document.
- **Financial & Tabular Reports:** Upload raw CSV data to generate structured financial tables.
- **PDF Generation:** Powered by `reportlab` to produce multi-page PDFs matching your canvas layout.
- **Minimal UI:** Native interface built with CustomTkinter.

## Prerequisites

- Python 3.9+
- An API Key from [OpenAI](https://platform.openai.com/), [Google Gemini](https://aistudio.google.com/), or [OpenRouter](https://openrouter.ai/).

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Lunarmist-byte/reportgenerator-MCP.git
   cd reportgenerator-MCP
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
   pip install customtkinter pywinstyles reportlab openai google-generativeai python-dotenv pandas pillow
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
- `src/ui/`: Contains the CustomTkinter graphical interface modules (`main_window.py`, `settings_page.py`, `generator_page.py`, `calibrator.py`).
- `src/core/llm_engine.py`: Handles connections and strict JSON prompting for OpenAI/Gemini/OpenRouter.
- `src/core/pdf_engine.py`: Handles `reportlab` logic for drawing text, tables, and absolutely-positioned images on the PDF canvas.
- `src/core/storage.py`: Manages local `config.json` state for saving API keys securely.

## License

This project is licensed under the MIT License.
