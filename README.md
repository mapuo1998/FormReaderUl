# FormReaderUltra

FormReaderUltra is a Python-based desktop application developed as the final project for CST3990 Undergraduate Individual Project.
The aim was to create a simple, single-page application that utilizes Google Cloud's Document AI to scan PDF documents of handwritten maintenanceforms 
and extract specific information from fields.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction

FormReaderUltra is designed to streamline the process of extracting information from handwritten maintenance forms. By leveraging Google Cloud's Document AI,
the application performs OCR on PDF files to identify and extract specific field data, making it easier to digitize and analyze handwritten records.

### Motivation

The motivation behind this project was to create an efficient tool for digitizing handwritten maintenance forms, which are often difficult to process manually.
The project aims to reduce the time and effort required to extract valuable information from these documents, making it easier for organizations to manage and
analyze their maintenance data.

## Features

- **File Selection**: Select multiple PDF files for processing.
- **Preview**: Preview the pages of the selected PDF files.
- **OCR Processing**: Perform OCR on selected PDF files using Google Document AI.
- **Text Extraction**: Extract and save text from PDF files.
- **JSON Response Handling**: Save JSON responses from the OCR process.
- **File Management**: Delete selected PDF and text files.
- **Text Preview**: Preview the extracted text files.
- **Text Copy**: Copy selected text from the preview to the clipboard.
- **Loading Screen**: Display a loading screen with a progress bar during OCR processing.

## Project Structure

The project structure is as follows:

```
- build
  - FormReaderUltra
    - Analysis-00.toc
    - base_library.zip
    - EXE-00.toc
    - FormReaderUltra.pkg
    - localpycs
      - pyimod01_archive.pyc
      - pyimod02_importers.pyc
      - pyimod03_ctypes.pyc
      - pyimod04_pywin32.pyc
      - struct.pyc
    - PKG-00.toc
    - PYZ-00.pyz
    - PYZ-00.toc
    - Tree-00.toc
    - Tree-01.toc
    - Tree-02.toc
    - warn-FormReaderUltra.txt
    - xref-FormReaderUltra.html
- dist
  - FormReaderUltra.exe
- FormReaderUltra.spec
- img
  - ocr_icon.ico
- src
  - FormReaderUltra.py
  - pdf_window
  - text_window
```

- **build**: Contains files generated during the build process.
- **dist**: Contains the final executable file `FormReaderUltra.exe`.
- **FormReaderUltra.spec**: The PyInstaller spec file used to create the executable.
- **img**: Contains the icon file `ocr_icon.ico` used in the application.
- **src**: Contains the main application script `FormReaderUltra.py` and directories for storing PDF and text files.

## Installation

To install and run FormReaderUltra, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/mapuo1998/FormReaderUltra.git
    cd FormReaderUltra
    ```

2. **Create a virtual environment and activate it**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the application**:
    ```bash
    python src/FormReaderUltra.py
    ```

To create an executable, you can use the provided `FormReaderUltra.spec` file with PyInstaller:

```bash
pyinstaller FormReaderUltra.spec
```

This will generate the executable in the `dist` directory.

## Usage

1. **Select PDF File**: Click on the "Select PDF File" button to choose PDF files for processing.
2. **Preview**: Select a file from the file tree to preview its pages.
3. **Read File(s)**: Click on the "Read File(s)" button to start the OCR process.
4. **Delete Files**: Select files and click "Delete Selected File(s)" to remove them.
5. **Processed Tab**: View and manage extracted text files in the "Processed" tab.
6. **Copy Text**: Select and copy text from the text preview.

## Dependencies

FormReaderUltra uses the following libraries:

- `tkinter`: For the graphical user interface.
- `Pillow`: For handling image operations.
- `shutil`, `os`: For file operations.
- `fitz` (PyMuPDF): For extracting images from PDF files.
- `requests`: For making HTTP requests to the Google Document AI API.
- `base64`, `json`: For encoding and decoding file content and handling JSON data.
- `threading`: For handling concurrent tasks.

Make sure to have these dependencies installed, which can be done using the `requirements.txt` file provided.

## Contributing

Contributions are welcome! Follow these steps to contribute:

1. **Fork the repository**.
2. **Create a new branch** (`git checkout -b feature/YourFeature`).
3. **Commit your changes** (`git commit -m 'Add some feature'`).
4. **Push to the branch** (`git push origin feature/YourFeature`).
5. **Open a pull request**.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
