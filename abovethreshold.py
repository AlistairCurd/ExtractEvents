"""abovethreshold.py

Extract and save sequences of frames around above-threshold events.

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
                        default='./events',
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


def sortimagenames_by_num(filename_list):
    """Sort image filenames by number so that earlier frames come
    before later ones, including 2 before 12, etc.
    
    
    Args:
        filename_list:
            List of filenames.
    
    Returns:
        filename_num_dict (dict):
            Keys: filenames, Values: image numbers
        filename_list:
            Sorted list of filenames.
    """
    filename_num_dict = {}

    # Get integers at end of filename stems
    for filename in filename_list:
        imagenumber = re.search(r'(\d+)\.', filename).group()
        imagenumber = re.search(r'(\d+)', imagenumber).group()
        filename_num_dict[filename] = int(imagenumber)

    # Sorted filename list by image number
    filename_list = sorted(filename_num_dict, key=filename_num_dict.get)

    return filename_num_dict, filename_list


def main():
    """Extract chosen sequences and save."""
    user_inputs = get_inputs()
    input_dir = Path(user_inputs.input_dir)
    output_dir = user_inputs.output_dir
    if output_dir == './events':
        output_dir = input_dir / 'events'
    else:
        output_dir = Path(output_dir)
    threshold = user_inputs.threshold
    before = user_inputs.before
    after = user_inputs.after

    # Get sorted filenames, no extension
    filename_list = []
    for child in input_dir.iterdir():
        filename_list.append(child.stem)
    filename_num_dict, filename_list = sortimagenames_by_num(filename_list)

    # Load sorted images into image stack
    input_seq = np.zeros(10, 50, 6000)
    for i, in enumerate(input_seq):
        input_seq[i] = imread(input_dir / filename_list[i] + 'tiff')

    # Load sorted images into image stack

    # Find and save desired sequences
    i = 0
    while i < len(input_seq):
        if input_seq[i].max() >= threshold:
            start_frame = max(i - before, 0)
            last_frame = i + after, len(input_seq)
            short_seq = input_seq[start_frame: last_frame + 1]
            start_frame_name = filename_list[start_frame]
            last_frame_num = filename_num_dict[filename_list[last_frame]]
            outname = f'{start_frame_name}-{last_frame_num}.tiff'
            imsave(output_dir / outname, short_seq)
            i = i + after
        else:
            i = i + 1


if __name__ == '__main__':
    main()
