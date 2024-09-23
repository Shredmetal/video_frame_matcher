import threading
import time
import os
import queue
from tkinter import filedialog, messagebox, Text, END, WORD, ttk, Toplevel, Scrollbar


class DisplayManager:
    def __init__(self, window):
        self.output_text = None
        self.window = window
        self.queue = queue.Queue()
        self.periodic_logger = None

    def create_output_text(self):
        self.output_text = Text(self.window, wrap=WORD, width=60, height=20)
        self.output_text.grid(row=11, column=0, columnspan=2, pady=10)

        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.output_text.yview)
        scrollbar.grid(row=11, column=2, sticky="ns")
        self.output_text.configure(yscrollcommand=scrollbar.set)

        self.window.after(100, self.check_queue)

    def save_threshold(self, threshold_value, label):
        try:
            threshold = int(threshold_value)
            if 0 <= threshold <= 255:
                label.config(text=f"Threshold: {threshold}")
                return threshold
            else:
                raise ValueError("Threshold must be between 0 and 255")
        except ValueError as e:
            self.show_error("Invalid Threshold", str(e))
            label.config(text="")
            return None

    def clear_output(self):
        self.output_text.delete(1.0, END)

    def check_queue(self):
        try:
            while True:
                message = self.queue.get_nowait()
                self.output_text.insert(END, message + "\n")
                self.output_text.see(END)

                if not self.periodic_logger:
                    self.periodic_logger = threading.Thread(target=self._periodic_log_check)
                    self.periodic_logger.start()

        except queue.Empty:
            pass
        self.window.after(100, self.check_queue)

    def _periodic_log_check(self):
        while True:
            try:
                message = self.queue.get_nowait()
                self.output_text.insert(END, message + "\n")
                self.output_text.see(END)
            except queue.Empty:
                break
            time.sleep(1)

    def show_results_popup(self, matches, logs):
        result_window = Toplevel(self.window)
        result_window.title("Search Results")
        result_window.geometry("800x600")

        notebook = ttk.Notebook(result_window)
        notebook.pack(expand=True, fill='both')

        # Matches tab
        matches_frame = ttk.Frame(notebook)
        notebook.add(matches_frame, text='Matches')
        matches_text = Text(matches_frame, wrap=WORD)
        matches_text.pack(expand=True, fill='both')
        matches_scrollbar = Scrollbar(matches_frame, command=matches_text.yview)
        matches_scrollbar.pack(side='right', fill='y')
        matches_text.configure(yscrollcommand=matches_scrollbar.set)

        if matches:
            for video_file, video_matches in matches:
                matches_text.insert(END, f"Matches found in video: {video_file}\n")
                for frame_count, timestamp in video_matches:
                    matches_text.insert(END, f"  Frame: {frame_count}, Timestamp: {timestamp:.2f} seconds\n")
                matches_text.insert(END, "\n")
        else:
            matches_text.insert(END, "No matches found")

        # Logs tab
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text='Logs')
        logs_text = Text(logs_frame, wrap=WORD)
        logs_text.pack(expand=True, fill='both')
        logs_scrollbar = Scrollbar(logs_frame, command=logs_text.yview)
        logs_scrollbar.pack(side='right', fill='y')
        logs_text.configure(yscrollcommand=logs_scrollbar.set)

        for log in logs:
            logs_text.insert(END, f"{log}\n")

        matches_text.config(state='disabled')
        logs_text.config(state='disabled')

    @staticmethod
    def show_error(title, message):
        messagebox.showerror(title, message)

    @staticmethod
    def select_file(title, filetypes):
        return filedialog.askopenfilename(initialdir=os.path.expanduser('~'), title=title, filetypes=filetypes)

    @staticmethod
    def select_directory(title):
        return filedialog.askdirectory(title=title)