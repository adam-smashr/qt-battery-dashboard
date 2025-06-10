# Qt Battery Dashboard

A desktop application for monitoring battery voltage using a Qt-based GUI.

## Features

- Read and display battery voltage from serial input
- Simple and clean user interface built with PySide6 (Qt for Python)

## Requirements

- Python 3.8+
- [PySide6](https://pypi.org/project/PySide6/)

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/qt-battery-dashboard.git
   cd qt-battery-dashboard
   ```

2. (Optional) Create and activate a virtual environment:
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

Run the application with:
```sh
python main.py
```

## Testing

Run unit tests with:
```sh
pytest
```

## Project Structure

- `main.py` — Application entry point
- `serial_operations/` — Serial communication and voltage reading logic
- `ui/` — Qt Designer UI files and generated Python code
- `views/` — Application views and window logic
- `tests/` — Unit tests

## License

MIT License

---
