import os
from typing import Optional
import click
import cv2
import numpy as np

from acquisition.video_input import get_video_input
from postprocessing.local_map_hud import LocalMapHUD
from postprocessing.videofile_write import MP4VideoWriter
from postprocessing.image_hud import ImageHUD
from processing import stitch_processor


usage_text = '''
Hit following to switch to:
1 - Dense optical flow by HSV color image (default);
2 - Dense optical flow by lines;
3 - Dense optical flow by warped image;
4 - Lucas-Kanade method.

Hit 's' to save image.

Hit 'f' to flip image horizontally.

Hit ESC to exit.
'''


@click.command()
@click.option('--path', required=False, type=str, help='Path to the input video file or photo folder')
@click.option('--crop', required=False, type=float, help='Percent of HFOV to retain, 100 percent by default')
@click.option('--maxwidth', required=False, type=int, help='Downsample to maximum width in pixels, no resize by default')
def main(path: Optional[str], crop: Optional[float], maxwidth: Optional[int]):

    original_cwd = os.getcwd()

    if path is None:
        path = 'inputs'

    base_name = os.path.basename(path)
    file_name_without_extension = os.path.splitext(base_name)[0]
    video_writer = MP4VideoWriter(file_name_without_extension)

    image_input = get_video_input(path, crop=crop, maxwidth=maxwidth)

    processor = stitch_processor.StitchProcessor()
    map_visuzalizer = LocalMapHUD()
    visuzalizer = ImageHUD()

    frame_count = 0

    while image_input.is_finished is False:
        frame = image_input.capture()

        visuzalizer.setImage(np.copy(frame))
        processor_trails = processor.apply(frame)
        map_visuzalizer.render(processor_trails)
        visuzalizer.render()
        video_writer.write_frame(visuzalizer.frame)

        frame_count += 1

        ### key operation
        key = cv2.waitKey(1)
        if key == 32:
            print('Paused...')
            while True:
                key = cv2.waitKey()
                if key == 32:
                    print('Resumed...')
                    break
        if key == 27:         # exit on ESC
            print('Closing...')
            break
        elif key == ord('s'):   # save
            video_writer.capture_screen_frame(visuzalizer.frame)
            print('Saved displayed frame')
        elif key == ord('f'):   # save
            flipImage = not flipImage
            print("Flip image: " + {True: "ON", False: "OFF"}.get(flipImage))

    ## finish
    video_writer.cleanup()
    image_input.destroy()
    visuzalizer.destroy()
    os.chdir(original_cwd)


if __name__ == '__main__':
    print(usage_text)
    main()
