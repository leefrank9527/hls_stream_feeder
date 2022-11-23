import os
import sys

import gi

gi.require_version("Gst", "1.0")
gi.require_version("GstApp", "1.0")
gi.require_version("GstVideo", "1.0")
from gi.repository import Gst, GLib, GObject, GstApp, GstVideo

Gst.init(sys.argv if hasattr(sys, "argv") else None)


def main(args):
    video_file_path = os.path.expanduser("~/Videos/27.mp4")

    # Standard GStreamer initialization
    # GObject.threads_init()
    Gst.init(None)

    print("Creating Pipeline \n ")
    pipeline = Gst.Pipeline()
    if not pipeline:
        sys.stderr.write(" Unable to create Pipeline \n")

    source = Gst.ElementFactory.make("filesrc", "file-source")
    source.set_property("location", video_file_path)

    stream_demux = Gst.ElementFactory.make("qtdemux", "mux")
    h264parser = Gst.ElementFactory.make("h264parse", "videoparsersbad")
    h264parser.set_property("config-interval", -1)

    mpeg_ts_mux = Gst.ElementFactory.make("mpegtsmux", "mpegtsmux")

    hls_sink = Gst.ElementFactory.make("hlssink", "hls")
    hls_sink.set_property("location", "%06d.ts")
    hls_sink.set_property("target-duration", 5)

    pipeline.add(source)
    pipeline.add(stream_demux)
    pipeline.add(h264parser)
    pipeline.add(mpeg_ts_mux)
    pipeline.add(hls_sink)

    source.link(stream_demux)
    stream_demux.link(h264parser)

    h264parser.link(mpeg_ts_mux)
    mpeg_ts_mux.link(hls_sink)

    loop = GLib.MainLoop()

    # start play back and listen to events
    print("Starting pipeline \n")
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        pass
    # cleanup
    pipeline.set_state(Gst.State.NULL)


def demo():
    # pipeline_str = 'filesrc location=/home/leefr/Videos/27.mp4 ! qtdemux ! h264parse config-interval=-1 ! mpegtsmux ! hlssink location="%06d.ts" target-duration=5'
    # pipeline_str = 'appsrc emit-signals=True is-live=True caps=video/x-raw,format=RGB,width=640,height=480,framerate=30/1 ! queue ! videoconvert ! autovideosink'
    pipeline_str = 'filesrc location=/home/leefr/Videos/27.mp4 ! queue ! videoconvert ! autovideosink'


    pipeline = Gst.parse_launch(pipeline_str)
    loop = GLib.MainLoop()

    # start play back and listen to events
    print("Starting pipeline \n")
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        pass
    # cleanup
    pipeline.set_state(Gst.State.NULL)


if __name__ == '__main__':
    # sys.exit(main(sys.argv))
    demo()
