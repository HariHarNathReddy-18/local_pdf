import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

import customtkinter as ctk
from tkinter import filedialog
import pathlib
import threading
from llama_client import call_llama
from pdf_extractor import extract_text_from_pdf
from text_preprocessor import clean_text, chunk_text

from summarizer import save_summaries
import os

# ============ MAIN GUI APP CLASS ============

class PDFAnalyzerGUI(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("PDF Analyzer (LLaMA RAG)")
        self.geometry("1000x700")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.page_image = None


        # State
        self.loaded_pdf_path = None
        self.extracted_text = ""
        self.chunks = []

        # Progress indicators
        self.status_label = None
        self.progress_bar = None

        # Layout
        self.setup_layout()

    # ============ GUI Layout ============

    def setup_layout(self):

        # Left sidebar frame
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        # Upload button
        self.upload_btn = ctk.CTkButton(
            self.sidebar,
            text="Upload PDF",
            command=self.upload_pdf
        )
        self.upload_btn.pack(pady=20)

        # View PDF button
        self.view_pdf_btn = ctk.CTkButton(
            self.sidebar,
            text="View PDF",
            command=self.open_pdf
        )
        self.view_pdf_btn.pack(pady=10)


        # Summarize button
        self.summary_btn = ctk.CTkButton(
            self.sidebar,
            text="Summarize PDF",
            command=self.run_summarization_thread
        )
        self.summary_btn.pack(pady=20)

        # Chat entry
        self.chat_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Ask about the PDF...")
        self.chat_entry.pack(pady=20)

        # Ask button
        self.ask_btn = ctk.CTkButton(
            self.sidebar,
            text="Ask",
            command=self.ask_question_thread
        )
        self.ask_btn.pack(pady=10)

        # Status label for progress messages
        self.status_label = ctk.CTkLabel(self.sidebar, text="")
        self.status_label.pack(pady=10)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.sidebar, width=180)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)  # Start at 0

        # Scrollable text preview area
        self.text_preview = ctk.CTkTextbox(self, font=("Consolas", 14))
        self.text_preview.pack(fill="both", expand=True, padx=10, pady=10)

        # Chat output box
        self.chat_output = ctk.CTkTextbox(self, height=150, font=("Consolas", 14))
        self.chat_output.pack(fill="x", padx=10, pady=5)

        


    # ============ Upload PDF ============

    def upload_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])

        if not file_path:
            return

        self.loaded_pdf_path = file_path
        self.text_preview.delete("1.0", "end")
        self.text_preview.insert("end", f"📄 Loaded PDF: {file_path}\n\n")

        try:
            # Update progress: Extracting PDF...
            self.status_label.configure(text="Extracting PDF...")
            self.progress_bar.set(0.2)
            self.update_idletasks()

            # Extract text
            text = extract_text_from_pdf(file_path)

            # Update progress: Cleaning text...
            self.status_label.configure(text="Cleaning text...")
            self.progress_bar.set(0.4)
            self.update_idletasks()

            self.extracted_text = clean_text(text)

            if not self.extracted_text.strip():
                raise ValueError("Extracted text is empty. The PDF might be image-based or corrupted.")

            self.text_preview.insert("end", "✔ Text extracted successfully!\n\n")
            self.text_preview.insert("end", self.extracted_text)

            # Update progress: Chunking...
            self.status_label.configure(text="Chunking...")
            self.progress_bar.set(0.6)
            self.update_idletasks()

            # Chunk the text
            self.chunks = chunk_text(self.extracted_text)

            self.chat_output.insert("end", f"📦 Created {len(self.chunks)} chunks.\n\n")

            # Complete
            self.status_label.configure(text="Ready")
            self.progress_bar.set(1.0)
            self.update_idletasks()

        except Exception as e:
            error_msg = f"❌ Error loading PDF: {str(e)}\n"
            self.chat_output.insert("end", error_msg)
            self.status_label.configure(text="Error")
            self.progress_bar.set(0)
            self.update_idletasks()
            
    # ============ Open PDF in external viewer ============
    def open_pdf(self):
        if not self.loaded_pdf_path:
            self.chat_output.insert("end", "⚠️ Load a PDF first.\n")
            return

        try:
            os.startfile(self.loaded_pdf_path)  # open with default PDF viewer
        except Exception as e:
            self.chat_output.insert("end", f"❌ Could not open PDF: {e}\n")

    # ============ RAG Question Asking ============

    def ask_question_thread(self):
        threading.Thread(target=self.ask_question).start()

    def ask_question(self):
        question = self.chat_entry.get()

        if not question or not self.chunks:
            self.chat_output.insert("end", "⚠️ Load a PDF first.\n")
            return

        try:
            # Update progress: Talking to LLaMA...
            self.after(0, lambda: self.status_label.configure(text="Talking to LLaMA..."))
            self.after(0, lambda: self.progress_bar.set(0.5))
            self.after(0, lambda: self.update_idletasks())

            # Combine some chunks for now
            context = self.chunks[0] if self.chunks else ""

            prompt = f"""
Use ONLY this context to answer the question.

### CONTEXT:
{context}

### QUESTION:
{question}

### ANSWER:
"""

            answer = call_llama(prompt)

            self.chat_output.insert("end", f"🧠 Q: {question}\n")
            self.chat_output.insert("end", f"💬 A: {answer}\n\n")

            # Complete
            self.after(0, lambda: self.status_label.configure(text="Ready"))
            self.after(0, lambda: self.progress_bar.set(1.0))
            self.after(0, lambda: self.update_idletasks())

        except Exception as e:
            error_msg = f"❌ Error asking question: {str(e)}\n"
            self.chat_output.insert("end", error_msg)
            self.after(0, lambda: self.status_label.configure(text="Error"))
            self.after(0, lambda: self.progress_bar.set(0))
            self.after(0, lambda: self.update_idletasks())

    # ============ Summarization ============

    def run_summarization_thread(self):
        threading.Thread(target=self.summarize_pdf).start()

    def summarize_pdf(self):

        if not self.chunks:
            self.chat_output.insert("end", "⚠️ Load a PDF first.\n")
            return

        try:
            # Update progress: Talking to LLaMA...
            self.after(0, lambda: self.status_label.configure(text="Talking to LLaMA..."))
            self.after(0, lambda: self.progress_bar.set(0.5))
            self.after(0, lambda: self.update_idletasks())

            self.chat_output.insert("end", "🧠 Summarizing PDF using LLaMA...\n")

            complete_text = " ".join(self.chunks)

            prompt = f"""
Summarize this document clearly:

{complete_text}

### SUMMARY:
"""

            summary = call_llama(prompt)

            self.chat_output.insert("end", "📋 Summary:\n")
            self.chat_output.insert("end", summary + "\n\n")

            # Complete
            self.after(0, lambda: self.status_label.configure(text="Ready"))
            self.after(0, lambda: self.progress_bar.set(1.0))
            self.after(0, lambda: self.update_idletasks())

        except Exception as e:
            error_msg = f"❌ Error summarizing PDF: {str(e)}\n"
            self.chat_output.insert("end", error_msg)
            self.after(0, lambda: self.status_label.configure(text="Error"))
            self.after(0, lambda: self.progress_bar.set(0))
            self.after(0, lambda: self.update_idletasks())


# ============ RUN APP ============

if __name__ == "__main__":
    app = PDFAnalyzerGUI()
    app.mainloop()
