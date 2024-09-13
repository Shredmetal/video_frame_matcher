from tkinter import filedialog, messagebox, Text, END, WORD, ttk, Toplevel, Scrollbar
import os
import queue

class DisplayManager:
    def __init__(self, window):
        self.window = window
        self.queue = queue.Queue()

    def create_output_text(self):
        self.output_text = Text(self.window, wrap=WORD, width=60, height=20)
        self.output_text.grid(row=10, column=0, columnspan=2, pady=10)

        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.output_text.yview)
        scrollbar.grid(row=10, column=2, sticky="ns")
        self.output_text.configure(yscrollcommand=scrollbar.set)

        self.window.after(100, self.check_queue)

    def select_file(self, title, filetypes):
        return filedialog.askopenfilename(initialdir=os.path.expanduser('~'), title=title, filetypes=filetypes)

    def select_directory(self, title):
        return filedialog.askdirectory(title=title)

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

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def check_queue(self):
        try:
            while True:
                message = self.queue.get_nowait()
                self.output_text.insert(END, message + "\n")
                self.output_text.see(END)
        except queue.Empty:
            pass
        self.window.after(100, self.check_queue)

    def show_results_popup(self, matches):
        result_window = Toplevel(self.window)
        result_window.title("Search Results")
        result_window.geometry("600x400")

        result_text = Text(result_window, wrap=WORD)
        result_text.pack(expand=True, fill='both', padx=10, pady=10)

        scrollbar = Scrollbar(result_window, command=result_text.yview)
        scrollbar.pack(side='right', fill='y')
        result_text.configure(yscrollcommand=scrollbar.set)

        if matches:
            for video_file, video_matches in matches:
                result_text.insert(END, f"Matches found in video: {video_file}\n")
                for frame_count, timestamp in video_matches:
                    result_text.insert(END, f"  Frame: {frame_count}, Timestamp: {timestamp:.2f} seconds\n")
                result_text.insert(END, "\n")
        else:
            result_text.insert(END, "No matches found")

        result_text.config(state='disabled')
