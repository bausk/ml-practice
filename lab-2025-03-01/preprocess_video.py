from typing import Optional
import click

from preprocessing.video_slicing import MP4VideoPreprocessor


@click.command()
@click.option('--image_path', required=True, type=str, help='Path to the input video file')
@click.option('--crop', required=False, type=float, help='Percent of HFOV to retain, 100 percent by default')
@click.option('--maxwidth', required=False, type=int, help='Downsample to maximum width in pixels, no resize by default')
@click.option(
    '--output',
    required=False,
    type=click.Choice(['VIDEO', 'JPG', 'ALL'], case_sensitive=False),
    help='Output either `video`, `jpg`, or `all`. Default is no output to disk'
)
def main(image_path: str, crop: Optional[float], maxwidth: Optional[int], output: Optional[str]):
    """
    Usage:
    $ python preprocess_video.py --image_path=xxx.MP4 --step=50
    Will produce video and images timelapsed with 50 seconds interval
    """
    preprocessor = MP4VideoPreprocessor(image_path, crop_factor=crop, resize_maxwidth=maxwidth)
    preprocessor.process(output)

if __name__ == '__main__':
    main()
