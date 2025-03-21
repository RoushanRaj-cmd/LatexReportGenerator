# LaTeX Report Generator for FOSSEE Summer Fellowship

## Overview
This project contains a LaTeX report generator and a Python GUI application for generating technical reports with a specific focus on FOSSEE Summer Fellowship projects. The application allows users to select sections of a LaTeX document and generate customized PDF reports.

## Features
- Interactive GUI for LaTeX document manipulation
- Section-wise selection and preview
- Custom header with project details
- Automatic PDF generation
- Support for mathematical equations and technical content
- Professional formatting with tables and figures

## Project Structure
```
.
├── report.py              # Main Python GUI application
├── FOSSEE_SUMMER_FELLOWSHIP_SAMPLE_TEX.tex  # LaTeX template file
└── README.md             # Project documentation
```

## Requirements
### Python Dependencies
- PyQt5
- sys
- re
- os
- tempfile
- subprocess

### System Requirements
- LaTeX distribution (TeX Live recommended)
- Python 3.6 or higher
- PDF viewer

## Installation
1. Install the required LaTeX distribution:
   ```bash
   sudo apt-get install texlive-full
   ```

2. Install Python dependencies:
   ```bash
   pip install PyQt5
   ```

## Usage
1. Run the GUI application:
   ```bash
   python report.py
   ```

2. Using the application:
   - Click "Open .tex File" to load a LaTeX document
   - Select/deselect sections using checkboxes
   - Preview selected content in the right panel
   - Click "Generate PDF" to create the final report

## Features of the GUI Application
- **Section Selection**: Easily select or deselect sections to include in the final report
- **Live Preview**: Preview selected sections before generating the PDF
- **Progress Tracking**: Progress bar for PDF generation
- **Error Handling**: Comprehensive error messages and logging
- **Custom Header**: Professional header with project details
- **Flexible Layout**: Resizable split view for better usability

## LaTeX Template Features
- Professional document structure
- Support for tables and figures
- Mathematical equation support
- Custom color definitions
- Header and footer customization
- Multi-page table support
- Cross-referencing

## Troubleshooting
Common issues and solutions:
1. **PDF Generation Fails**: 
   - Ensure all LaTeX packages are installed
   - Check LaTeX syntax in the template
   - Verify file permissions

2. **GUI Not Launching**:
   - Verify PyQt5 installation
   - Check Python version compatibility
   - Ensure all dependencies are met

3. **Missing Fonts**:
   - Install the Latin Modern fonts package
   - Verify the LaTeX distribution installation

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is open source and available under the MIT License.

## Acknowledgments
- FOSSEE Project (Funded by MHRD, Government of India)
- IIT Bombay for project support
- Osdag FOSSEE team for technical guidance 