from tkinter import Tk, Button, Label, W, N, E, Entry, StringVar
from src.framematcher.frame_matcher import VideoFrameMatcher
from src.gui.display_manager import DisplayManager
import threading

class Interface:
    def __init__(self):
        self.window = Tk()
        self.window.title("Video Frame Matcher")
        self.window.config(padx=10, pady=10)
        self.window.configure(bg='white')

        self.display_manager = DisplayManager(self.window)

        self._create_image_selection()
        self._create_video_directory_selection()
        self._create_threshold_config()
        self._create_search_button()

        self.display_manager.create_output_text()

        self.window.mainloop()

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
        threshold_label.grid(row=7, column=0, sticky=W, pady=5)

        self.threshold_var = StringVar(value="5")
        self.threshold_entry = Entry(self.window, textvariable=self.threshold_var, width=10)
        self.threshold_entry.grid(row=7, column=1, sticky=E, pady=5)

        save_threshold_button = Button(self.window, text="Save Threshold", command=self._save_threshold, bg="white")
        save_threshold_button.grid(row=8, column=0, sticky=W, pady=5)

        self.threshold_saved_label = Label(self.window, text="", bg="white", fg="green")
        self.threshold_saved_label.grid(row=8, column=1, sticky=W, pady=5)

    def _create_search_button(self):
        self.search_button = Button(self.window, text="Search!", width=20, bg="white", command=self._search_videos)
        self.search_button.grid(row=9, column=0, columnspan=2, sticky=N, pady=10)

    def _select_image(self):
        self.img_path = self.display_manager.select_file("Select an image file", [("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*")])
        self.img_path_label.config(text=f"Selected file: {self.img_path}")

    def _select_video_directory(self):
        self.video_directory = self.display_manager.select_directory("Select Directory Containing Videos")
        self.output_path_label.config(text=f"Selected directory: {self.video_directory}")

    def _save_threshold(self):
        self.threshold = self.display_manager.save_threshold(self.threshold_var.get(), self.threshold_saved_label)

    def _search_videos(self):
        if hasattr(self, 'img_path') and hasattr(self, 'video_directory'):
            self.threshold = int(self.threshold_var.get())
            self.display_manager.clear_output()
            matcher = VideoFrameMatcher(self.display_manager.queue)
            matcher.set_target_frame(self.img_path)

            def search_thread():
                matches = matcher.find_matches(self.video_directory, self.threshold)
                self.window.after(0, lambda: self.display_manager.show_results_popup(matches))

            threading.Thread(target=search_thread, daemon=True).start()
        else:
            self.display_manager.show_error("Please select both an image and a video directory before searching.")
