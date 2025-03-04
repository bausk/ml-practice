## reference
# - http://www.pyimagesearch.com/2015/03/30/accessing-the-raspberry-pi-camera-with-opencv-and-python/
# - http://stackoverflow.com/questions/2601194/displaying-a-webcam-feed-using-opencv-and-python
# - http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html

import os
from typing import Optional
import click
import cv2
import numpy as np

from acquisition.video_input import get_video_input
from postprocessing.generational_sparse_hud import GenerationalSparseHUD
from postprocessing.sparse_hud import IdentityHUD, SparseLinesHUD
from postprocessing.stitch_hud import StitchHUD
from postprocessing.videofile_write import MP4VideoWriter
from postprocessing.image_hud import ImageHUD
from processing import optical_flow
from processing.generational_motion_tracking import GenerationalVectorInference
from processing.generational_sparse_flow import GenerationalLKFlow
from processing.image_stitching import blend_images, crop_lower_half, crop_upper_half, detect_and_match_features, estimate_homography, warp_images
from processing.motion_tracking import CompoundVectorInferenceSparse, StaticVectorInferenceSparse
from processing.pose_tracking import CompoundPoseInference


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
@click.option('--image_path', required=False, type=str, help='Path to the input video file')
@click.option('--step', required=False, type=float, help='Interval between captured frames in seconds, each frame if not specified')
@click.option('--crop', required=False, type=float, help='Percent of HFOV to retain, 100 percent by default')
@click.option('--maxwidth', required=False, type=int, help='Downsample to maximum width in pixels, no resize by default')
def main(image_path: Optional[str], crop: Optional[float], maxwidth: Optional[int], step: Optional[float]):
    if image_path is None:
        base_name = ''
    else:
        base_name = os.path.basename(image_path)

    file_name_without_extension = os.path.splitext(base_name)[0]
    flipImage = False
    camera = get_video_input(image_path, crop=crop, maxwidth=maxwidth)

    visuzalizer = ImageHUD()
    video_writer = MP4VideoWriter(file_name_without_extension)

    # FIX THIS
    create_default_lk_flow = None

    CompoundTrackerInstantiator = lambda x: CompoundVectorInferenceSparse(
        initial_motion_vector=x,
        undistort=False
    )

    inference_pipelines = [
        # [
        #     optical_flow.DenseOpticalFlowByLines(),
        #     [
        #         CompoundVectorInferenceDense(percentile=80)
        #     ],
        #     DenseLinesHUD(step=32),
        # ],
        [
            GenerationalLKFlow(create_default_lk_flow),
            [
                GenerationalVectorInference(CompoundTrackerInstantiator),
            ],
            GenerationalSparseHUD(),
        ],
        # [
        #     create_default_lk_flow(),
        #     [
        #         CompoundVectorInferenceSparse(),
        #         CompoundVectorInferenceSparse(estimator_algo='ICP'),
        #         StaticVectorInferenceSparse(),
        #         StaticVectorInferenceSparse(estimator_algo='ICP'),
        #         # CompoundPoseInference(50),
        #     ],
        #     SparseLinesHUD(),
        # ],
    ]

    frame_count = 0
    unstitched_count = 0

    while True:
        frame = camera.capture()
        if frame is None:
            break

        if flipImage:
            frame = cv2.flip(frame, 1)

        visuzalizer.setImage(np.copy(frame))
        color_position = 1

        for processor, vector_inferences, inference_hud in inference_pipelines:
            inference_hud: SparseLinesHUD
            _, processor_result = processor.apply(frame)

            visuzalizer.frame = inference_hud.draw_mask(visuzalizer, processor_result)

            for vector_inference in vector_inferences:
                vector_results = vector_inference.infer(processor_result)
                match vector_results:
                    case [motion_vector, initial_vector]:
                        visuzalizer.draw_central_vector(motion_vector, color_position)
                    case (x, y): # tuple denotes single vector
                        visuzalizer.draw_central_vector((x, y), color_position)
                    case {
                        'average_motion_vector': result,
                        'subvector_results': subvectors
                    }:
                        visuzalizer.draw_central_vector(result, color_position)
                        # inference_hud.draw_subvectors(subvectors)
                text = vector_inference.get_title_message()
                visuzalizer.write_uppertext(text, color_position)
                text = vector_inference.get_parameter_message()
                visuzalizer.write_lowertext(text, color_position)

                color_position += 1


        visuzalizer.render()
        video_writer.write_frame(visuzalizer.frame)

        frame_count += 1
        unstitched_count += 1

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
    camera.destroy()
    cv2.destroyWindow('preview')


if __name__ == '__main__':
    print(usage_text)
    main()
