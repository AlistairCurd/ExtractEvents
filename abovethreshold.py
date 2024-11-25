"""abovethreshold.py

Extract sequences of frames around above threshold-events.

Alistair Curd
University of Leeds
2024-11-25
"""


import argparse
import re
from pathlib import Path

import numpy as np
from skimage.io import imread, imsave


def get_inputs():
    """ Get CLI inputs."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--input-dir',
                        type=str,
                        default='.',
                        help='Path to input directory.')
    parser.add_argument('-o', '--output-dir',
                        type=str,
                        default='.//output',
                        help='Path to output directory.')
    parser.add_argument('-t', '--threshold',
                        type=float,
                        default=40,
                        help='Pixel level threshold to trigger'
                        ' event extraction.')
    parser.add_argument('-b', '--before',
                        type=int,
                        default=5,
                        help='The number of frames before a trigger event'
                        ' to include in an extracted sequence.')
    parser.add_argument('-a', '--after',
                        type=int,
                        default=5,
                        help='The number of frames after a trigger event'
                        ' to include in an extracted sequence.')
    return parser.parse_args()


def sortimagenames(filename_list):
    """Sort image filenames by number so that earlier frames come
    before later ones, including 2 before 12, etc.
    
    
    Args:
        filename_list:
            List of filenames.
    
    Returns:
        filename_list:
            Sorted list of filenames.
    """
    filename_num_dict = {}

    # Get integers at end of filename stems
    for filename in filename_list:
        imagenumber = re.search(r'(\d+)\.', filename).group()
        imagenumber = re.search(r'(\d+)', imagenumber).group()
        # imagenumbers.append(int(imagenumber))
        filename_num_dict[filename] = int(imagenumber)

    # Sorted filename list by image number
    filename_list = sorted(filename_num_dict, key=filename_num_dict.get)
    return filename_list



def main():
    user_inputs = get_inputs()
    input_dir = Path(user_inputs.input_dir)
    # output_dir = Path(user_inputs.output_dir)
    threshold = user_inputs.threshold
    before = user_inputs.before
    after = user_inputs.after

    # Get sorted filenames, no extension
    input_filenames = []
    for child in input_dir.iterdir():
        input_filenames.append(child.stem)
    # SORT...
    # probably with extra function
    # framenum = re.search(r'(\d+)\.', filename).group()

    # Create 3D numpy array height * width * length of input sequence
    input_seq = np.zeros(10, 50, 6000)
    for i, image in enumerate(input_seq):
        image = imread(input_dir / input_filenames[i] + 'tiff')

    # Load sorted images into image stack

    # Find and save desired sequences
    for i, image in input_seq:
        if image.max() >= threshold:
            start_frame = max(i - before, 0)
            last_frame = i + after, len(input_seq)
            # short_seq = input_seq[start_frame: last_frame + 1]
            # last_frame_id =
            # outname = start_frame name - last_frame_id
            # imsave(output_dir / outname, short_seq)


if __name__ == '__main__':
    main()
