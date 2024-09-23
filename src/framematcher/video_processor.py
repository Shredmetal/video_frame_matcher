import gc
import cv2
import imagehash
from PIL import Image

from src.framematcher.frame_writer import FrameWriter


class VideoProcessor:
    @staticmethod
    def process_video(video_path, threshold, write_directory, target_hash, shared_logs):
        matches = []
        try:
            video = cv2.VideoCapture(video_path)
            fps = video.get(cv2.CAP_PROP_FPS)
            frame_count = 0

            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

            shared_logs.append(f"Processing {video_path}")
            shared_logs.append(f"Video FPS: {fps}, Resolution: {width}x{height}")

            while True:
                ret, frame = video.read()
                if not ret:
                    break

                pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                frame_hash = imagehash.phash(pil_image)

                hash_diff = abs(target_hash - frame_hash)

                if hash_diff <= threshold:
                    timestamp = frame_count / fps
                    matches.append((frame_count, timestamp))
                    shared_logs.append(
                        f"Match found at frame {frame_count}, timestamp {timestamp:.2f}s, hash difference: {hash_diff}")

                    if write_directory:
                        log_message = FrameWriter.write_frame(frame, video_path, timestamp, write_directory)
                        shared_logs.append(log_message)

                frame_count += 1

                if frame_count % 1000 == 0:
                    gc.collect()
                    shared_logs.append(f"Processed {frame_count} frames...")

            shared_logs.append(f"Total frames processed for {video_path}: {frame_count}")
            return matches
        except Exception as e:
            shared_logs.append(f"Error processing {video_path}: {str(e)}")
            return []

