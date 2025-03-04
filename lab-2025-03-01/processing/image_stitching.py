import cv2
import numpy as np


def detect_and_match_features(img1, img2):
    orb = cv2.ORB_create()
    keypoints1, descriptors1 = orb.detectAndCompute(img1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(img2, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    matches = sorted(matches, key=lambda x: x.distance)

    return keypoints1, keypoints2, matches

# keypoints1, keypoints2, matches = detect_and_match_features(img1, img2)

def estimate_homography(keypoints1, keypoints2, matches, threshold=3):
    src_points = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_points = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    H, mask = cv2.findHomography(src_points, dst_points, cv2.RANSAC, threshold)
    return H, mask

# H, mask = estimate_homography(keypoints1, keypoints2, matches)

def warp_images(img1, img2, H):
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]

    corners1 = np.float32([[0, 0], [0, h1], [w1, h1], [w1, 0]]).reshape(-1, 1, 2)
    corners2 = np.float32([[0, 0], [0, h2], [w2, h2], [w2, 0]]).reshape(-1, 1, 2)
    warped_corners2 = cv2.perspectiveTransform(corners2, H)

    corners = np.concatenate((corners1, warped_corners2), axis=0)
    [xmin, ymin] = np.int32(corners.min(axis=0).ravel() - 0.5)
    [xmax, ymax] = np.int32(corners.max(axis=0).ravel() + 0.5)

    t = [-xmin, -ymin]
    Ht = np.array([[1, 0, t[0]], [0, 1, t[1]], [0, 0, 1]])

    warped_img2 = cv2.warpPerspective(img2, Ht @ H, (xmax - xmin, ymax - ymin))
    warped_img2[t[1]:h1 + t[1], t[0]:w1 + t[0]] = img1

    return warped_img2

# warped_img = warp_images(img1, img2, H)

def blend_images(img1, img2):
    mask = np.where(img1 != 0, 1, 0).astype(np.float32)
    blended_img = img1 * mask + img2 * (1 - mask)
    return blended_img.astype(np.uint8)

# output_img = blend_images(warped_img, img1)

def crop_lower_half(image):
    height, width = image.shape[:2]

    # Define the start and end points of the crop
    start_row, start_col = int(height * .5), int(0)
    end_row, end_col = int(height), int(width)

    # Crop the image
    cropped = image[start_row:end_row, start_col:end_col]
    return cropped

def crop_upper_half(image):
    height, width = image.shape[:2]

    # Define the start and end points of the crop
    start_row, start_col = int(0), int(0)
    end_row, end_col = int(height * .5), int(width)

    # Crop the image
    cropped = image[start_row:end_row, start_col:end_col]
    return cropped
