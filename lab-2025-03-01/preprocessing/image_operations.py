import cv2


def resize_cv_image_to_maxwidth(image: cv2.typing.MatLike, max_width: int) -> cv2.typing.MatLike:
    height, width = image.shape[:2]
    if width > max_width:
        scale_factor = max_width / width
        new_height = int(height * scale_factor)
        resized_image = cv2.resize(image, (max_width, new_height))
        return resized_image
    return image

def crop_cv_image_centered(image: cv2.typing.MatLike, crop_percentage: float) -> cv2.typing.MatLike:
    if crop_percentage == 1:
        return image

    # Get the dimensions of the original image
    height, width = image.shape[:2]

    # Calculate the crop dimensions based on the percentage
    crop_width = int(width * crop_percentage)
    crop_height = int(height * crop_percentage)

    # Calculate the top-left corner coordinates of the crop area
    start_x = (width - crop_width) // 2
    start_y = (height - crop_height) // 2

    # Calculate the bottom-right corner coordinates of the crop area
    end_x = start_x + crop_width
    end_y = start_y + crop_height

    # Crop the image
    cropped_image = image[start_y:end_y, start_x:end_x]

    return cropped_image
