"""
Main Tkinter GUI application for PDF OCR Renamer.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
import os
import threading

from utils.config import Config
from utils.logger import setup_logger
from utils.validators import validate_pdf_files
from ocr.pdf_processor import PDFProcessor
from ocr.text_extractor import TextExtractor
from extraction.rule_engine import ExtractionEngine
from renaming.file_renamer import FileRenamer


logger = setup_logger(__name__)


class PDFRenamerApp:
    """Main application window."""
    
    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.root.title("PDF OCR Renamer")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        try:
            self.config = Config()
            logger.info("Configuration loaded successfully")
        except Exception as e:
            messagebox.showerror("Configuration Error", f"Failed to load configuration: {e}")
            self.root.quit()
            return
        
        self.processor = None
        self.extractor = None
        self.engine = None
        self.renamer = None
        
        self.current_folder = None
        self.pdf_files = []
        self.is_processing = False
        
        self.setup_ui()
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize OCR and processing components."""
        try:
            self.processor = PDFProcessor(
                dpi=self.config.get_setting("ocr_dpi", 300),
                poppler_path=self.config.get_setting("poppler_path")
            )
            
            tesseract_path = self.config.get_setting("tesseract_path")
            logger.info(f"Using tesseract_path: {tesseract_path}")
            
            self.extractor = TextExtractor(
                tesseract_path=tesseract_path,
                language=self.config.get_setting("language", "eng")
            )
            
            rules = self.config.get_all_rules()
            self.engine = ExtractionEngine(rules)
            
            self.renamer = FileRenamer(
                backup_enabled=self.config.get_setting("backup_renamed_files", True),
                backup_folder=self.config.get_setting("backup_folder", "backups")
            )
            
            logger.info("All components initialized successfully")
            self.status_var.set("Ready")
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize components:\n{e}")
            self.status_var.set("Error: Check logs")
    
    def setup_ui(self):
        """Setup the user interface."""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var = tk.StringVar(value="Initializing...")
        ttk.Label(status_frame, textvariable=self.status_var, 
                 relief=tk.SUNKEN).pack(fill=tk.X, padx=2, pady=2)
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        folder_frame = ttk.LabelFrame(main_frame, text="Select Folder", padding="5")
        folder_frame.pack(fill=tk.X, pady=10)
        
        self.folder_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.folder_var, 
                 state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(folder_frame, text="Browse...", 
                  command=self.select_folder).pack(side=tk.LEFT, padx=5)
        
        files_frame = ttk.LabelFrame(main_frame, text="PDF Files Found", padding="5")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(files_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.files_text = scrolledtext.ScrolledText(
            files_frame, height=8, width=80, yscrollcommand=scrollbar.set
        )
        self.files_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.files_text.yview)
        self.files_text.config(state=tk.DISABLED)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.process_btn = ttk.Button(button_frame, text="Process PDFs", 
                                      command=self.process_pdfs)
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_display).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Exit", 
                  command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        
        log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=8, width=80, yscrollcommand=scrollbar.set
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        self.log_text.config(state=tk.DISABLED)
    
    def select_folder(self):
        """Open folder selection dialog."""
        folder = filedialog.askdirectory(title="Select Folder with PDFs")
        if folder:
            self.current_folder = folder
            self.folder_var.set(folder)
            self.display_pdf_files()
            self.status_var.set(f"Folder selected: {folder}")
    
    def display_pdf_files(self):
        """Display list of PDF files in selected folder."""
        self.files_text.config(state=tk.NORMAL)
        self.files_text.delete(1.0, tk.END)
        
        try:
            self.pdf_files = validate_pdf_files(self.current_folder)
            
            if self.pdf_files:
                self.files_text.insert(tk.END, f"Found {len(self.pdf_files)} PDF files:\n\n")
                for pdf in self.pdf_files:
                    filename = os.path.basename(pdf)
                    self.files_text.insert(tk.END, f"• {filename}\n")
            else:
                self.files_text.insert(tk.END, "No PDF files found in selected folder.")
        except Exception as e:
            self.files_text.insert(tk.END, f"Error: {e}")
        
        self.files_text.config(state=tk.DISABLED)
    
    def process_pdfs(self):
        """Process PDF files in background thread."""
        if not self.pdf_files:
            messagebox.showwarning("No Files", "No PDF files to process.")
            return
        
        if self.is_processing:
            messagebox.showwarning("Processing", "Already processing. Please wait.")
            return
        
        self.process_btn.config(state=tk.DISABLED)
        self.is_processing = True
        self.status_var.set("Processing...")
        
        thread = threading.Thread(target=self._process_pdfs_thread)
        thread.daemon = True
        thread.start()
    
    def _process_pdfs_thread(self):
        """Background thread for PDF processing."""
        try:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            
            self.log("Starting PDF processing...\n")
            
            successful = 0
            failed = 0
            
            for i, pdf_path in enumerate(self.pdf_files, 1):
                if not self.is_processing:
                    self.log("Processing cancelled by user.")
                    break
                
                filename = os.path.basename(pdf_path)
                self.log(f"\n[{i}/{len(self.pdf_files)}] Processing: {filename}")
                self.root.update()
                
                try:
                    self.log("  - Converting PDF to image...")
                    images = self.processor.convert_pdf_to_images(pdf_path)
                    
                    if not images:
                        self.log(f"  X Failed: No pages found")
                        failed += 1
                        continue
                    
                    self.log("  - Preprocessing image...")
                    preprocessing_config = self.config.get_setting("preprocessing", {})
                    preprocessed = self.processor.preprocess_image(
                        images[0],
                        grayscale=preprocessing_config.get("convert_to_grayscale", True),
                        autocontrast=preprocessing_config.get("apply_autocontrast", True),
                        binarize=preprocessing_config.get("apply_binarization", True),
                        threshold=preprocessing_config.get("threshold", 140)
                    )
                    
                    self.log("  - Extracting text with OCR...")
                    text = self.extractor.extract_text(preprocessed)
                    
                    if not text or len(text.strip()) < 10:
                        self.log(f"  X Failed: Insufficient text extracted")
                        failed += 1
                        continue
                    
                    self.log("  - Extracting title and year...")
                    title, year = self.engine.extract_title_and_year(text)
                    
                    if not title or not year:
                        self.log(f"  ! Warning: Could not extract title or year")
                        failed += 1
                        continue
                    
                    self.log(f"  - Extracted: Title='{title}', Year='{year}'")
                    new_filename = self.renamer.format_filename(
                        self.config.get_output_format(),
                        title=title,
                        year=year,
                        original_name=os.path.splitext(filename)[0]
                    )
                    
                    self.log(f"  - New filename: {new_filename}")
                    success, new_path, message = self.renamer.rename_file(pdf_path, new_filename)
                    
                    if success:
                        self.log(f"  + {message}")
                        successful += 1
                    else:
                        self.log(f"  X {message}")
                        failed += 1
                except Exception as e:
                    self.log(f"  X Error: {str(e)}")
                    failed += 1
            
            self.log(f"\n{'='*50}")
            self.log(f"Processing Complete!")
            self.log(f"Successful: {successful}")
            self.log(f"Failed: {failed}")
            self.log(f"Total: {len(self.pdf_files)}")
            self.log(f"{'='*50}")
            
            self.status_var.set(f"Completed: {successful} successful, {failed} failed")
            messagebox.showinfo("Processing Complete", 
                              f"Successful: {successful}\nFailed: {failed}")
        except Exception as e:
            self.log(f"Fatal error: {str(e)}")
            self.status_var.set("Error during processing")
            messagebox.showerror("Processing Error", f"An error occurred:\n{e}")
        finally:
            self.log_text.config(state=tk.DISABLED)
            self.process_btn.config(state=tk.NORMAL)
            self.is_processing = False
    
    def log(self, message):
        """Add message to log display."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear_display(self):
        """Clear all displays."""
        self.files_text.config(state=tk.NORMAL)
        self.files_text.delete(1.0, tk.END)
        self.files_text.config(state=tk.DISABLED)
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.folder_var.set("")
        self.pdf_files = []
        self.current_folder = None
        self.status_var.set("Ready")


def main():
    """Start the application."""
    root = tk.Tk()
    app = PDFRenamerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
