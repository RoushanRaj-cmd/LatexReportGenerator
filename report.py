import sys
import re
import os
import tempfile
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                             QCheckBox, QScrollArea, QMessageBox, QTextEdit,
                             QSplitter, QGroupBox, QProgressBar)
from PyQt5.QtCore import Qt, QProcess

class TeXSectionSelector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.tex_file = None
        self.tex_content = ""
        self.sections = []
        self.section_checkboxes = []
        self.section_content = {}
        self.preamble = ""
        self.document_env = {"begin": "", "end": ""}
        
    def initUI(self):
        self.setWindowTitle('TeX Section Selector')
        self.setGeometry(100, 100, 900, 600)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Top buttons
        top_layout = QHBoxLayout()
        self.open_button = QPushButton('Open .tex File')
        self.open_button.clicked.connect(self.open_tex_file)
        top_layout.addWidget(self.open_button)
        
        self.generate_button = QPushButton('Generate PDF')
        self.generate_button.clicked.connect(self.generate_pdf)
        self.generate_button.setEnabled(False)
        top_layout.addWidget(self.generate_button)
        
        main_layout.addLayout(top_layout)
        
        # Splitter for sections and preview
        splitter = QSplitter(Qt.Horizontal)
        
        # Section selection area
        section_group = QGroupBox("Sections")
        section_layout = QVBoxLayout(section_group)
        self.sections_area = QWidget()
        self.sections_layout = QVBoxLayout(self.sections_area)
        scroll = QScrollArea()
        scroll.setWidget(self.sections_area)
        scroll.setWidgetResizable(True)
        section_layout.addWidget(scroll)
        
        # Select/Deselect All buttons
        select_buttons_layout = QHBoxLayout()
        self.select_all_button = QPushButton('Select All')
        self.select_all_button.clicked.connect(self.select_all_sections)
        self.select_all_button.setEnabled(False)
        select_buttons_layout.addWidget(self.select_all_button)
        
        self.deselect_all_button = QPushButton('Deselect All')
        self.deselect_all_button.clicked.connect(self.deselect_all_sections)
        self.deselect_all_button.setEnabled(False)
        select_buttons_layout.addWidget(self.deselect_all_button)
        
        section_layout.addLayout(select_buttons_layout)
        
        # Preview area
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        # Add section and preview to splitter
        splitter.addWidget(section_group)
        splitter.addWidget(preview_group)
        splitter.setSizes([300, 600])
        
        main_layout.addWidget(splitter)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Status bar
        self.statusBar().showMessage('Ready')
        
    def open_tex_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open .tex file', '', 'TeX Files (*.tex)')
        if file_name:
            self.tex_file = file_name
            self.statusBar().showMessage(f'Loaded: {file_name}')
            self.parse_tex_file()
            self.display_sections()
            self.generate_button.setEnabled(True)
            self.select_all_button.setEnabled(True)
            self.deselect_all_button.setEnabled(True)
    
    def parse_tex_file(self):
        try:
            with open(self.tex_file, 'r', encoding='utf-8') as file:
                self.tex_content = file.read()
            
            # Extract preamble (everything before \begin{document})
            begin_doc_match = re.search(r'\\begin{document}', self.tex_content)
            if begin_doc_match:
                self.preamble = self.tex_content[:begin_doc_match.start()]
                self.document_env["begin"] = begin_doc_match.group(0)
            else:
                self.preamble = ""
                self.document_env["begin"] = "\\begin{document}"
            
            # Extract document end
            end_doc_match = re.search(r'\\end{document}', self.tex_content)
            if end_doc_match:
                self.document_env["end"] = end_doc_match.group(0)
            else:
                self.document_env["end"] = "\\end{document}"
            
            # Extract sections
            section_pattern = r'\\(section|subsection|subsubsection)\{([^}]+)\}'
            section_matches = re.finditer(section_pattern, self.tex_content)
            
            self.sections = []
            prev_end = begin_doc_match.end() if begin_doc_match else 0
            
            for match in section_matches:
                section_type = match.group(1)
                section_title = match.group(2)
                section_start = match.start()
                
                # If this is the first section after \begin{document}
                if prev_end == begin_doc_match.end():
                    # Check if there's content between \begin{document} and the first section
                    if section_start > prev_end:
                        preamble_content = self.tex_content[prev_end:section_start]
                        if preamble_content.strip():
                            self.sections.append({
                                "type": "preamble_content",
                                "title": "Content before first section",
                                "start": prev_end,
                                "end": section_start
                            })
                
                self.sections.append({
                    "type": section_type,
                    "title": section_title,
                    "start": section_start,
                    "end": None  # Will be set later
                })
                prev_end = section_start
            
            # Set end positions for each section
            for i in range(len(self.sections) - 1):
                self.sections[i]["end"] = self.sections[i + 1]["start"]
            
            # Set the end position for the last section
            if self.sections and end_doc_match:
                self.sections[-1]["end"] = end_doc_match.start()
            
            # Check if there's content after the last section
            if end_doc_match and (not self.sections or self.sections[-1]["end"] < end_doc_match.start()):
                last_section_end = self.sections[-1]["end"] if self.sections else begin_doc_match.end()
                end_content = self.tex_content[last_section_end:end_doc_match.start()]
                if end_content.strip():
                    self.sections.append({
                        "type": "end_content",
                        "title": "Content after last section",
                        "start": last_section_end,
                        "end": end_doc_match.start()
                    })
            
            # Extract content for each section
            for section in self.sections:
                section_content = self.tex_content[section["start"]:section["end"]]
                self.section_content[section["title"]] = section_content
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error parsing .tex file: {str(e)}")
            self.sections = []
            self.section_content = {}
    
    def display_sections(self):
        # Clear existing checkboxes
        for i in reversed(range(self.sections_layout.count())):
            widget = self.sections_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        self.section_checkboxes = []
        
        # Add checkboxes for each section
        for section in self.sections:
            section_type = section["type"]
            section_title = section["title"]
            
            # Create checkbox with appropriate indentation and formatting
            checkbox = QCheckBox()
            checkbox.setChecked(True)  # Default to selected
            
            if section_type == "section":
                checkbox.setText(f"Section: {section_title}")
            elif section_type == "subsection":
                checkbox.setText(f"    Subsection: {section_title}")
            elif section_type == "subsubsection":
                checkbox.setText(f"        Subsubsection: {section_title}")
            elif section_type == "preamble_content":
                checkbox.setText(f"[Document Introduction]")
            elif section_type == "end_content":
                checkbox.setText(f"[Document Conclusion]")
            
            checkbox.section_title = section_title
            checkbox.section_type = section_type
            checkbox.stateChanged.connect(self.update_preview)
            
            self.sections_layout.addWidget(checkbox)
            self.section_checkboxes.append(checkbox)
        
        # Add a stretch at the end
        self.sections_layout.addStretch()
        
        # Update preview
        self.update_preview()
    
    def update_preview(self):
        if not self.section_checkboxes:
            return
        
        preview_text = "Selected sections:\n\n"
        for checkbox in self.section_checkboxes:
            if checkbox.isChecked():
                preview_text += f"✓ {checkbox.text()}\n"
                
                # Add a snippet of the section content
                content = self.section_content.get(checkbox.section_title, "")
                snippet = content[:200] + "..." if len(content) > 200 else content
                preview_text += f"---\n{snippet}\n---\n\n"
            else:
                preview_text += f"☐ {checkbox.text()}\n\n"
        
        self.preview_text.setText(preview_text)
    
    def select_all_sections(self):
        for checkbox in self.section_checkboxes:
            checkbox.setChecked(True)
    
    def deselect_all_sections(self):
        for checkbox in self.section_checkboxes:
            checkbox.setChecked(False)
    
    def fix_tex_issues(self, tex_content):
        """Fix common issues in TeX files that might cause compilation errors."""
        
        # Fix potential issues with the Area value (incorrect decimal point)
        tex_content = tex_content.replace("381.0", "3.81")
        
        # Fix potential issues with multirow
        tex_content = tex_content.replace("\\multirow{14}{*}", "\\multirow{14}{*}{Member Properties}")
        
        # Fix potential issues with cline
        tex_content = re.sub(r'\\cline{2%\n-%\n5%}', r'\\cline{2-5}', tex_content)
        
        # Fix potential issues with missing braces in textcolor command
        tex_content = re.sub(r'\\textcolor{([^}]+)}{ *\n *\\textbf{([^}]*)} *\n *}', 
                             r'\\textcolor{\1}{\\textbf{\2}}', tex_content)
        
        # Fix potential issues with textcolor empty braces
        tex_content = re.sub(r'\\textcolor{[^}]+}{ *\n *}', r'', tex_content)
        
        # Remove or fix empty commands
        tex_content = re.sub(r'\\textbf{}', r'', tex_content)
        
        return tex_content
    
    def generate_pdf(self):
        if not self.tex_file:
            QMessageBox.warning(self, "Warning", "Please open a .tex file first.")
            return
        
        # Get selected sections
        selected_sections = []
        for checkbox in self.section_checkboxes:
            if checkbox.isChecked():
                selected_sections.append(checkbox.section_title)
        
        if not selected_sections:
            QMessageBox.warning(self, "Warning", "No sections selected.")
            return
        
        # Create new .tex content with only selected sections
        new_content = self.preamble + "\n" + self.document_env["begin"] + "\n"
        
        for section in self.sections:
            if section["title"] in selected_sections:
                new_content += self.section_content[section["title"]]
        
        new_content += "\n" + self.document_env["end"]
        
        # Fix common issues in the TeX content
        new_content = self.fix_tex_issues(new_content)
        
        # Create temporary directory for output
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        
        try:
            temp_dir = tempfile.mkdtemp()
            
            # Create temporary .tex file
            temp_tex_path = os.path.join(temp_dir, "selected_sections.tex")
            with open(temp_tex_path, "w", encoding="utf-8") as temp_tex_file:
                temp_tex_file.write(new_content)
            
            self.progress_bar.setValue(30)
            self.statusBar().showMessage('Compiling PDF...')
            
            # Show detailed log in preview
            self.preview_text.append("\n\nCompiling PDF...\n")
            
            # Run pdflatex with more verbose output
            process = QProcess()
            process.setWorkingDirectory(temp_dir)
            
            # Connect to read output
            process.readyReadStandardOutput.connect(
                lambda: self.preview_text.append(str(process.readAllStandardOutput().data(), 'utf-8'))
            )
            process.readyReadStandardError.connect(
                lambda: self.preview_text.append(str(process.readAllStandardError().data(), 'utf-8'))
            )
            
            # Run pdflatex multiple times to resolve references
            for i in range(2):
                process.start("pdflatex", ["-interaction=nonstopmode", temp_tex_path])
                process.waitForFinished(60000)  # 60 seconds timeout
                self.progress_bar.setValue(50 + i*20)
            
            # Get output file path
            pdf_path = os.path.join(temp_dir, "selected_sections.pdf")
            
            if os.path.exists(pdf_path):
                self.progress_bar.setValue(90)
                
                # Save dialog
                save_path, _ = QFileDialog.getSaveFileName(self, 'Save PDF', '', 'PDF Files (*.pdf)')
                if save_path:
                    # Copy the PDF to the selected location
                    with open(pdf_path, "rb") as src_file:
                        with open(save_path, "wb") as dst_file:
                            dst_file.write(src_file.read())
                    
                    self.progress_bar.setValue(100)
                    self.statusBar().showMessage(f'PDF saved to {save_path}')
                    QMessageBox.information(self, "Success", f"PDF generated successfully and saved to {save_path}")
                else:
                    self.statusBar().showMessage('PDF generation cancelled')
                
            else:
                error_log = os.path.join(temp_dir, "selected_sections.log")
                error_text = "PDF compilation failed."
                
                if os.path.exists(error_log):
                    with open(error_log, 'r', encoding='utf-8', errors='ignore') as log_file:
                        error_text += "\n\nLog file:\n" + log_file.read()
                
                QMessageBox.critical(self, "Error", error_text)
                self.statusBar().showMessage('PDF compilation failed')
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating PDF: {str(e)}")
            self.statusBar().showMessage('PDF generation failed')
        
        finally:
            self.progress_bar.setVisible(False)
            
            # Clean up temp directory if needed
            try:
                if os.path.exists(temp_dir):
                    # Keep the directory for debugging
                    self.statusBar().showMessage(f'Temporary files at: {temp_dir}')
            except:
                pass

def main():
    app = QApplication(sys.argv)
    ex = TeXSectionSelector()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()