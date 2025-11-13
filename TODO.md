# TODO: Add Progress Indicators and Error Handling to PDF Analyzer GUI

## Steps to Complete

- [x] Step 1: Add status label and progress bar widgets to the GUI layout in setup_layout().
- [x] Step 2: Update upload_pdf() to include progress updates (e.g., "Extracting PDF...", "Chunking...") and error handling (corrupt PDF, empty text).
- [x] Step 3: Update ask_question() to include progress updates ("Talking to LLaMA...") and error handling for LLaMA failures.
- [x] Step 4: Update summarize_pdf() to include progress updates ("Talking to LLaMA...") and error handling for LLaMA failures.
- [x] Step 5: Ensure all UI updates in threads are thread-safe using self.after() for status and progress bar updates.
- [x] Step 6: Test the GUI by uploading a PDF, asking questions, and summarizing to verify functionality.

## Notes
- All changes are in src/gui/main_gui.py.
- Progress indicators: Status label for messages, progress bar for visual feedback.
- Error handling: Catch exceptions and display friendly messages in chat_output.
