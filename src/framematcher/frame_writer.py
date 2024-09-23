import os
import cv2


class FrameWriter:
    @staticmethod
    def write_frame(frame, video_path, timestamp, write_directory):
        try:
            if not os.path.exists(write_directory):
                os.makedirs(write_directory)

            video_name = os.path.splitext(os.path.basename(video_path))[0]
            time_str = f"{timestamp:.2f}"
            filename = f"{video_name}_timestamp_{time_str}.jpg"
            filepath = os.path.join(write_directory, filename)

            cv2.imwrite(filepath, frame)
            return f"Saved matched frame: {filepath}"
        except Exception as e:
            return f"Error saving matched frame: {str(e)}"