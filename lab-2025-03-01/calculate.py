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
from postprocessing.sparse_hud import SparseLinesHUD
from postprocessing.videofile_write import MP4VideoWriter
from postprocessing.image_hud import ImageHUD
from processing import optical_flow
from processing.generational_motion_tracking import GenerationalVectorInference
from processing.generational_sparse_flow import GenerationalLKFlow
from processing.motion_tracking import CompoundVectorInferenceSparse



usage_text = '''
Переключення між режимами:
1 - Dense optical flow by HSV color image;
2 - Dense optical flow by lines;
3 - Generational Lucas-Kanade method for motion vector inference.

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
    
    # Current visualization mode (default: Lucas-Kanade method)
    current_mode = 3

    # FIX THIS
    create_default_lk_flow = None

    CompoundTrackerInstantiator = lambda x: CompoundVectorInferenceSparse(
        initial_motion_vector=x,
        undistort=False
    )

    # Create dense optical flow processors
    dense_flow_hsv = optical_flow.DenseOpticalFlowByHSV()
    dense_flow_lines = optical_flow.DenseOpticalFlowByLines()
    
    # Create Lucas-Kanade pipeline
    lk_pipeline = [
        GenerationalLKFlow(create_default_lk_flow),
        [
            GenerationalVectorInference(CompoundTrackerInstantiator),
        ],
        GenerationalSparseHUD(),
    ]

    frame_count = 0
    unstitched_count = 0
    prev_frame = None

    while True:
        frame = camera.capture()
        if frame is None:
            break

        if flipImage:
            frame = cv2.flip(frame, 1)

        visuzalizer.setImage(np.copy(frame))
        
        # Process based on current mode
        if current_mode == 1:  # Dense optical flow by HSV
            if prev_frame is not None:
                # For HSV visualization, we need to convert the flow to a color image
                _, flow = dense_flow_hsv.apply(frame)
                # Convert flow to RGB visualization
                if flow is not None:
                    # Create HSV image
                    h, w = flow.shape[:2]
                    hsv = np.zeros((h, w, 3), dtype=np.uint8)
                    hsv[..., 1] = 255  # Saturation is always max
                    
                    # Calculate magnitude and angle
                    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                    # Normalize magnitude to 0-255
                    hsv[..., 0] = ang * 180 / np.pi / 2  # Hue is angle
                    hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)  # Value is magnitude
                    
                    # Convert to BGR
                    flow_rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                    visuzalizer.frame = flow_rgb
            
        elif current_mode == 2:  # Dense optical flow by lines
            if prev_frame is not None:
                # For line visualization, we'll draw the flow on a copy of the original frame
                _, flow = dense_flow_lines.apply(frame)
                if flow is not None:
                    # Create a copy of the frame to draw on
                    flow_vis = frame.copy()
                    
                    # Draw flow lines
                    h, w = flow.shape[:2]
                    step = 16  # Draw a line every 16 pixels
                    for y in range(0, h, step):
                        for x in range(0, w, step):
                            fx, fy = flow[y, x].flatten()
                            # Only draw significant movements
                            if abs(fx) > 1 or abs(fy) > 1:
                                cv2.line(flow_vis, (x, y), (int(x + fx), int(y + fy)), (0, 255, 0), 1)
                                cv2.circle(flow_vis, (x, y), 1, (0, 0, 255), -1)
                    
                    visuzalizer.frame = flow_vis
            
        elif current_mode == 3:  # Lucas-Kanade method
            processor, vector_inferences, inference_hud = lk_pipeline
            _, processor_result = processor.apply(frame)
            
            visuzalizer.frame = inference_hud.draw_mask(visuzalizer, processor_result)
            
            color_position = 1
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
                text = vector_inference.get_title_message()
                visuzalizer.write_uppertext(text, color_position)
                text = vector_inference.get_parameter_message()
                visuzalizer.write_lowertext(text, color_position)
                
                color_position += 1

        # Display current mode
        visuzalizer.write_uppertext(f"Mode: {current_mode}", 0)
        
        visuzalizer.render()
        video_writer.write_frame(visuzalizer.frame)
        
        # Store current frame for next iteration
        prev_frame = frame.copy()

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
        elif key == ord('1'):   # Mode 1: Dense optical flow by HSV
            current_mode = 1
            print("Switched to Mode 1: Dense optical flow by HSV color image")
        elif key == ord('2'):   # Mode 2: Dense optical flow by lines
            current_mode = 2
            print("Switched to Mode 2: Dense optical flow by lines")
        elif key == ord('3'):   # Mode 3: Lucas-Kanade method
            current_mode = 3
            print("Switched to Mode 3: Generational Lucas-Kanade method")

    ## finish
    video_writer.cleanup()
    camera.destroy()
    cv2.destroyWindow('preview')


if __name__ == '__main__':
    print(usage_text)
    main()
