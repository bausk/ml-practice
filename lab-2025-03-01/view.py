# Better samples/python2/opt_flow.py
# for Raspberry Pi

## reference
# - http://www.pyimagesearch.com/2015/03/30/accessing-the-raspberry-pi-camera-with-opencv-and-python/
# - http://stackoverflow.com/questions/2601194/displaying-a-webcam-feed-using-opencv-and-python
# - http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html

from typing import Optional
import click
import cv2

from acquisition.video_input import get_video_input
from processing import optical_flow

usage_text = '''
Hit followings to switch to:
1 - Dense optical flow by HSV color image (default);
2 - Dense optical flow by lines;
3 - Dense optical flow by warped image;
4 - Lucas-Kanade method.

Hit 's' to save image.

Hit 'f' to flip image horizontally.

Hit ESC to exit.
'''

def reset_processor(key, previous_frame):
    message, type = {
        ord('1'): ('==> Dense_by_hsv', 'dense_hsv'),
        ord('2'): ('==> Dense_by_lines', 'dense_lines'),
        ord('3'): ('==> Dense_by_warp', 'dense_warp'),
        ord('4'): ('==> Lucas-Kanade', 'lucas_kanade')
    }.get(key, ('==> Dense_by_hsv', 'dense_hsv'))
    print(message)
    of_processor = optical_flow.CreateOpticalFlow(type)
    of_processor.set1stFrame(previous_frame)
    return of_processor

@click.command()
@click.option('--image_path', required=False, type=str, help='Path to the input video file')
@click.option('--step', required=False, type=float, help='Interval between captured frames in seconds, each frame if not specified')
@click.option('--crop', required=False, type=float, help='Percent of HFOV to retain, 100 percent by default')
@click.option('--maxwidth', required=False, type=int, help='Downsample to maximum width in pixels, no resize by default')
def main(image_path: Optional[str], crop: Optional[float], maxwidth: Optional[int], step: Optional[float]):
    flipImage = True
    camera = get_video_input(image_path, crop=crop, maxwidth=maxwidth)
    cv2.namedWindow('preview')
    processor = None

    while True:  # Adjust the range according to your needs
        # capture frame
        frame = camera.capture()
        # frame = np.array(array.get_data(), dtype=np.uint8).reshape((array.height, array.width, 3))

        if processor is None:
            processor = reset_processor(ord('1'), frame)

        ### flip
        if flipImage:
            frame = cv2.flip(frame, 1)

        ### do it
        img, _ = processor.apply(frame)
        cv2.imshow("preview", img)

        ### key operation
        key = cv2.waitKey(1)
        if key == 27:         # exit on ESC
            print('Closing...')
            break
        elif key == ord('s'):   # save
            cv2.imwrite('img_raw.png', frame)
            cv2.imwrite('img_w_flow.png', img)
            print("Saved raw frame as 'img_raw.png' and displayed as 'img_w_flow.png'")
        elif key == ord('f'):   # save
            flipImage = not flipImage
            print("Flip image: " + {True: "ON", False: "OFF"}.get(flipImage))
        elif ord('1') <= key <= ord('4'):
            processor = reset_processor(key, frame)

    ## finish
    camera.destroy()
    cv2.destroyWindow('preview')


if __name__ == '__main__':
    print(usage_text)
    main()
