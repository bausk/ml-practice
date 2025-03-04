from typing import Optional
import click
import cv2
import numpy as np

from preprocessing.image_operations import resize_cv_image_to_maxwidth


usage_text = '''
Stitch two images together.

Hit ESC to exit.
'''


@click.command()
@click.option('--src', required=True, type=str, help='Path to the from image')
@click.option('--dst', required=True, type=str, help='Path to the to image')
@click.option('--maxwidth', required=False, type=int, help='Downsample to maximum width in pixels, no resize by default')
def main(src: str, dst: str, maxwidth: Optional[int]):

    img1 = cv2.imread(src)
    img2 = cv2.imread(dst)

    if maxwidth is not None:
        img1 = resize_cv_image_to_maxwidth(img1, max_width=maxwidth)
        img2 = resize_cv_image_to_maxwidth(img2, max_width=maxwidth)

    img1_gs = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gs = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    padding = 200
    img2 = cv2.copyMakeBorder( img2, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    img2_gs = cv2.copyMakeBorder( img2_gs, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=(0, 0, 0))

    preview_height = 1000
    preview_width = 1000

    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(img1_gs, None)
    kp2, des2 = sift.detectAndCompute(img2_gs, None)

    kp_show = cv2.drawKeypoints(img1, kp1, None)
    kp_show_resize = cv2.resize(kp_show, (preview_width, preview_height))
    cv2.imshow('Image 1 keypoints', kp_show_resize)
    # Generate matching keypoints in images
    match = cv2.BFMatcher()
    matches = match.knnMatch(des1, des2, k=2)

    good = [] 
    for m, n in matches: # Filter for good matches
        if m.distance < 0.7 * n.distance:
            good.append(m)
    draw_params = dict(matchColor = (0, 255, 0), # draw matches in green color
                    singlePointColor = None,
                    flags = 2)
    img3 = cv2.drawMatches(img1, kp1, img2, kp2, good, None, **draw_params)

    matches_resize = cv2.resize(img3, (preview_width * 2, preview_height))
    cv2.imshow('DrawMatches.jpg', matches_resize)

    MIN_MATCH_COUNT = 10
    if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        h, w, _ = img1.shape
        pts = np.float32([ [0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        img2 = cv2.polylines(img2, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
        img2_preview = cv2.resize(img2, (preview_width, preview_height))
        cv2.imshow("Overlapping.jpg", img2_preview)
    else:
        print(f'Not enough matches are found - {len(good)}/{MIN_MATCH_COUNT}')
    dst = cv2.warpPerspective(img1, M, (img2.shape[1] + img1.shape[1], img2.shape[0]))
    dst[0 : img2.shape[0], 0 : img2.shape[1]] = img2

    dst_resize = cv2.resize(dst, (preview_width, preview_height))
    cv2.imshow("Stitched.jpg", dst_resize)

    while True:
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

    ## finish
    # cv2.destroyWindow('preview')


if __name__ == '__main__':
    print(usage_text)
    main()
