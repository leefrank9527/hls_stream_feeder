import os
import sys
from time import sleep

import cv2
from ffprobe import FFProbe
import logging as log
import gi

gi.require_version("Gst", "1.0")
gi.require_version("GstApp", "1.0")
gi.require_version("GstVideo", "1.0")
# from gi.repository import Gst, GLib, GObject, GstApp, GstVideo
# Gst.init(sys.argv if hasattr(sys, "argv") else None)


log.getLogger().addHandler(log.StreamHandler(sys.stdout))
log.getLogger().setLevel(log.DEBUG)


class HlsStreamServer:
    def __init__(self, stream_id, stream_name, video_file, target_duration=5, infinite_loop=False):
        self.stream_id = stream_id
        self.stream_name = stream_name
        self.video_file = video_file
        self.target_duration = target_duration
        self.infinite_loop = infinite_loop

    def start_stream(self):
        metadata = FFProbe(self.video_file)
        frames, duration, fps = 0, 0, 0
        frame_size = None
        for stream in metadata.streams:
            if not stream.is_video():
                continue
            frames = stream.frames()
            duration = stream.duration_seconds()
            frame_size = stream.frame_size()

        if frames <= 0 or duration <= 0:
            log.error(f"Could not get the frames and duration: video_file={self.video_file}, frames={frames}, duration={duration}")
            return

        fps = frames / duration
        log.debug(f"{self.video_file}: frames={frames}, duration={duration}, fps={fps}, frame_size={frame_size}")

        # pipeline = f'appsrc ! queue ! videoconvert ! hlssink location="/tmp/%06d.ts" target-duration={self.target_duration}'
        # pipeline = f'appsrc ! videoconvert ! xlnxvideosink sink-type="dp" plane-id=34 sync=false fullscreen-overlay=true'
        pipeline = 'appsrc ! videoconvert' + \
                   ' ! vaapih264enc' + \
                   ' ! rtspclientsink location=rtsp://localhost:8554/appsrc'
        log.debug(f"pipeline={pipeline}")
        cv2_out = cv2.VideoWriter(pipeline, cv2.CAP_GSTREAMER, 0, fps, frame_size, True)
        cv2_cap = cv2.VideoCapture(self.video_file)
        while cv2_cap.isOpened():
            ret, frame = cv2_cap.read()
            if not ret:
                break
            cv2_out.write(frame)
            sleep(1 / fps)

        cv2_cap.release()
        cv2_out.release()


def main():
    video_file_path = os.path.expanduser("~/Videos/27.mp4")
    ss = HlsStreamServer(stream_id=1, stream_name="demo", video_file=video_file_path)
    ss.start_stream()


if __name__ == "__main__":
    main()
