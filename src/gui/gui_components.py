from tkinter import Tk, Button, Label, W, N, E, Entry, StringVar
from src.framematcher.frame_matcher import VideoFrameMatcher
from src.gui.display_manager import DisplayManager
import threading
import multiprocessing as mp
import queue


class Interface:
    def __init__(self):
        self.window = Tk()
        self.window.title("Video Frame Matcher")
        self.window.config(padx=10, pady=10)
        self.window.configure(bg='white')

        self.display_manager = DisplayManager(self.window)

        self._create_write_directory_selection()
        self._create_image_selection()
        self._create_video_directory_selection()
        self._create_threshold_config()
        self._create_search_button()
        self._create_max_threads_config()

        self.display_manager.create_output_text()

        self.matcher = None
        self.result_queue = queue.Queue()
        self.window.bind("<<SearchComplete>>", self.on_search_complete)
        self.window.after(100, self.check_result_queue)

        self.window.mainloop()

    def check_result_queue(self):
        try:
            result = self.result_queue.get_nowait()
            if result == "SEARCH_COMPLETE":
                self.search_button.config(state='normal')
            else:
                self.display_manager.show_results_popup(result)
        except queue.Empty:
            pass
        finally:
            self.window.after(100, self.check_result_queue)


    def _create_image_selection(self):
        file_open_button = Button(self.window, text="Select Image For Comparison", width=30, command=self._select_image, bg="white")
        file_open_button.grid(row=1, column=0, sticky=W)

        self.img_path_label = Label(self.window, text="Select an image to search videos for using the button above.", bg="white")
        self.img_path_label.grid(row=2, column=0, columnspan=2, sticky=W, pady=10)

    def _create_video_directory_selection(self):
        select_output_dir_button = Button(self.window, text="Select Directory Containing Videos", width=30, command=self._select_video_directory, bg="white")
        select_output_dir_button.grid(row=4, column=0, sticky=W)

        self.output_path_label = Label(self.window, text="Select a directory containing the videos to search for image.", bg="white")
        self.output_path_label.grid(row=5, column=0, columnspan=2, sticky=W, pady=10)

    def _create_threshold_config(self):
        threshold_label = Label(self.window, text="Set Threshold (Difference Tolerance) (0-255):", bg="white")
        threshold_label.grid(row=8, column=0, sticky=W, pady=5)

        self.threshold_var = StringVar(value="5")
        self.threshold_entry = Entry(self.window, textvariable=self.threshold_var, width=10)
        self.threshold_entry.grid(row=8, column=1, sticky=E, pady=5)

        save_threshold_button = Button(self.window, text="Save Threshold", command=self._save_threshold, bg="white")
        save_threshold_button.grid(row=9, column=0, sticky=W, pady=5)

        self.threshold_saved_label = Label(self.window, text="", bg="white", fg="green")
        self.threshold_saved_label.grid(row=9, column=1, sticky=E, pady=5)

    def _create_max_threads_config(self):
        max_threads_label = Label(self.window, text="Set Max Processes (Defaults to greater of (CPU Threads - 2) or 1):", bg="white")
        max_threads_label.grid(row=10, column=0, sticky=W, pady=5)

        self.max_threads_var = StringVar(value="5")
        self.max_threads_entry = Entry(self.window, textvariable=self.max_threads_var, width=10)
        self.max_threads_entry.grid(row=10, column=1, sticky=E, pady=5)

        max_threads_button = Button(self.window, text="Save Max Processes", command=self._save_max_threads, bg="white")
        max_threads_button.grid(row=11, column=0, sticky=W, pady=5)

        self.max_threads_saved_saved_label = Label(self.window, text="", bg="white", fg="green", width=24)
        self.max_threads_saved_saved_label.grid(row=11, column=1, sticky=E, pady=5, columnspan=2)

    def _create_search_button(self):
        self.search_button = Button(self.window, text="Search!", width=20, bg="white", command=self._search_videos)
        self.search_button.grid(row=12, column=0, columnspan=2, sticky=N, pady=10)

    def _select_image(self):
        self.img_path = self.display_manager.select_file("Select an image file", [("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*")])
        self.img_path_label.config(text=f"Selected file: {self.img_path}")

    def _select_video_directory(self):
        self.video_directory = self.display_manager.select_directory("Select Directory Containing Videos")
        self.output_path_label.config(text=f"Selected directory: {self.video_directory}")

    def _save_threshold(self):
        self.threshold = self.display_manager.save_threshold(self.threshold_var.get(), self.threshold_saved_label)

    def _save_max_threads(self):
        self.max_threads = self.display_manager.save_max_threads(self.max_threads_var.get(), self.max_threads_saved_saved_label)

    def _search_videos(self):
        if hasattr(self, 'img_path') and hasattr(self, 'video_directory') and hasattr(self, 'write_directory'):
            self.threshold = int(self.threshold_var.get())
            self.display_manager.clear_output()
            self.matcher = VideoFrameMatcher(self.display_manager.queue, write_directory=self.write_directory)
            self.matcher.set_target_frame(self.img_path)

            # Disable the search button
            self.search_button.config(state='disabled')

            def search_thread():
                try:
                    num_processes = self.max_threads
                    matches, logs = self.matcher.find_matches(self.video_directory, num_processes, self.threshold)
                    self.result_queue.put((matches, logs))
                except Exception as e:
                    print(f"An error occurred during the search: {str(e)}")
                    self.result_queue.put(([], [str(e)]))
                finally:
                    # Signal that the search is complete using event_generate
                    self.window.event_generate("<<SearchComplete>>", when="tail")

            threading.Thread(target=search_thread, daemon=True).start()

        else:
            self.display_manager.show_error(
                "Please select an image, a video directory, and a write directory before searching.")

    def on_search_complete(self, event):
        self.search_button.config(state='normal')
        matches, logs = self.result_queue.get()
        self.display_manager.show_results_popup(matches, logs)

    def _create_write_directory_selection(self):
        select_write_dir_button = Button(self.window, text="Select Write Directory", width=30,
                                         command=self._select_write_directory, bg="white")
        select_write_dir_button.grid(row=6, column=0, sticky=W)

        self.write_dir_label = Label(self.window, text="Select a directory to save matched frames.", bg="white")
        self.write_dir_label.grid(row=7, column=0, columnspan=2, sticky=W, pady=10)

    def _select_write_directory(self):
        self.write_directory = self.display_manager.select_directory("Select Directory to Save Matched Frames")
        self.write_dir_label.config(text=f"Selected write directory: {self.write_directory}")

    def _handle_log_queue(self, log_queue):
        while True:
            try:
                message = log_queue.get_nowait()
                self.display_manager.queue.put(message)
            except queue.Empty:
                break
