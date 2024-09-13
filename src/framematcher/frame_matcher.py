import cv2
import imagehash
from PIL import Image
import os
import glob
import gc

class VideoFrameMatcher:
    def __init__(self, queue):
        self.matches = []
        self.target_hash = None
        self.target_image = None
        self.queue = queue

    def log(self, message):
        self.queue.put(message)

    def set_target_frame(self, target_frame_path):
        """Set the target frame and store the image."""
        self.target_image = Image.open(target_frame_path)
        # We'll compute the hash when we know the video resolution

    def find_matches(self, video_directory, threshold=5):
        if self.target_image is None:
            raise ValueError("Target frame not set. Call set_target_frame() first.")

        self.matches = self.__find_matching_frames(video_directory, threshold)
        self.queue.put("Processing complete. Showing results...")
        return self.matches

    def __find_matching_frames(self, video_directory, threshold):
        """Find matching frames in videos within a directory."""
        all_matches = []

        # List of common video file extensions
        video_extensions = (
            '*.mp4', '*.avi', '*.mov', '*.mkv', '*.flv', '*.wmv',
            '*.webm', '*.m4v', '*.mpg', '*.mpeg', '*.3gp', '*.3g2',
            '*.mxf', '*.roq', '*.nsv', '*.f4v', '*.f4p', '*.f4a', '*.f4b'
        )

        # Create a list of all video files in the directory
        video_files = []
        for ext in video_extensions:
            video_files.extend(glob.glob(os.path.join(video_directory, ext)))

        # Process each video file
        for video_file in video_files:
            try:
                video_matches = self.__process_video(video_file, threshold)

                if video_matches:
                    all_matches.append((video_file, video_matches))
            except Exception as e:
                self.log(f"Error processing {video_file}: {str(e)}")

            # Garbage collect after processing each video
            gc.collect()

        return all_matches

    def __process_video(self, video_path, threshold):
        """Process video frames and store matching frames."""
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_count = 0
        matches = []

        # Get video resolution and resize target image
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        resized_target = self.__resize_image(self.target_image, (width, height))
        self.target_hash = imagehash.phash(resized_target)

        self.log(f"Processing {video_path}")
        self.log(f"Video FPS: {fps}, Resolution: {width}x{height}")
        self.log(f"Target hash: {self.target_hash}")


        while True:
            ret, frame = video.read()
            if not ret:
                break

            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            frame_hash = imagehash.phash(pil_image)

            hash_diff = abs(self.target_hash - frame_hash)

            if hash_diff <= threshold:
                timestamp = frame_count / fps  # Convert frame count to seconds
                matches.append((frame_count, timestamp))
                self.log(
                    f"Match found at frame {frame_count}, timestamp {timestamp:.2f}s, hash difference: {hash_diff}")

            frame_count += 1

            # Garbage collect every 1000 frames
            if frame_count % 1000 == 0:
                gc.collect()
                self.log(f"Processed {frame_count} frames...")

        video.release()
        self.log(f"Total frames processed: {frame_count}")
        return matches

    def __resize_image(self, image, size):
        """Resize the image to match the video resolution."""
        return image.resize(size, Image.LANCZOS)

