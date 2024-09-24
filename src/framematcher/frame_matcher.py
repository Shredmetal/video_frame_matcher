import imagehash
import os
import glob
import multiprocessing as mp
from functools import partial
from PIL import Image
from src.framematcher.log_manager import LogManager
from src.framematcher.video_processor import VideoProcessor


class VideoFrameMatcher:
    def __init__(self, queue, write_directory=None):
        self.matches = []
        self.target_hash = None
        self.target_image = None
        self.write_directory = write_directory
        self.logger = LogManager(queue)

    def set_target_frame(self, target_frame_path):
        self.target_image = Image.open(target_frame_path)
        self.target_hash = imagehash.phash(self.target_image)
        self.logger.log(f"Target hash: {self.target_hash}")

    def find_matches(self, video_directory, num_processes=1, threshold=5):
        if self.target_image is None:
            raise ValueError("Target frame not set. Call set_target_frame() first.")

        self.logger.start_periodic_logging()
        try:
            self.matches = self._find_matching_frames(video_directory, threshold, num_processes)
        finally:
            self.logger.stop_periodic_logging()
            self.logger.process_logs()
        self.logger.log("Processing complete. Showing results...")
        return self.matches, self.logger.get_all_logs()

    def _find_matching_frames(self, video_directory, threshold, num_processes):
        video_files = self._get_video_files(video_directory)

        with mp.Pool(processes=num_processes) as pool:
            process_video_partial = partial(VideoProcessor.process_video,
                                            threshold=threshold,
                                            write_directory=self.write_directory,
                                            target_hash=self.target_hash,
                                            shared_logs=self.logger.shared_logs)
            results = pool.map(process_video_partial, video_files)

        all_matches = []
        for video_file, matches in zip(video_files, results):
            if matches:
                all_matches.append((video_file, matches))

        return all_matches

    def _get_video_files(self, video_directory):
        """Get a list of all video files in the directory."""
        video_extensions = (
            '*.mp4', '*.avi', '*.mov', '*.mkv', '*.flv', '*.wmv',
            '*.webm', '*.m4v', '*.mpg', '*.mpeg', '*.3gp', '*.3g2',
            '*.mxf', '*.roq', '*.nsv', '*.f4v', '*.f4p', '*.f4a', '*.f4b'
        )
        video_files = []
        for ext in video_extensions:
            video_files.extend(glob.glob(os.path.join(video_directory, ext)))
        return video_files

