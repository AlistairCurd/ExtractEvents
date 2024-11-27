"""abovethreshold.py

Extract and save sequences of frames around above-threshold events.

Alistair Curd
University of Leeds
2024-11-25
"""


import argparse
import re
import sys
from pathlib import Path

import numpy as np
from skimage.io import imread, imsave


def get_inputs(default_out_dir_arg):
    """ Get CLI inputs.
    
    Args:
        default_out_dir_arg (str):
            String to diaply for default output directory path.

    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    ### ADD DESCRIPTION
    ### REQUIRES FILENAMES TO END IN <integer>.tiff

    parser.add_argument('-i', '--input-dir',
                        type=str,
                        default='.',
                        help='Path to input directory.')
    parser.add_argument('-o', '--output-dir',
                        type=str,
                        default=default_out_dir_arg,
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
        # print(filename)
        try:
            imagenumber = re.search(r'\d+$', filename).group()
            filename_num_dict[filename] = int(imagenumber)
            # print(imagenumber)
        except AttributeError:
            print(f'AttributeError. Could not extract number from {filename}')
            # sys.exit()

    # Sorted filename list by image number
    filename_list = sorted(filename_num_dict, key=filename_num_dict.get)
    print(f'{len(filename_list)} image files found.')

    return filename_num_dict, filename_list


def main():
    """Extract chosen sequences and save."""
    # Get and display inputs
    default_out_dir_arg = '<parent of input-dir>/<input-dir>_events_<params>'
    user_inputs = get_inputs(default_out_dir_arg)

    input_dir = Path(user_inputs.input_dir)
    output_dir = user_inputs.output_dir
    threshold = user_inputs.threshold
    before = user_inputs.before
    after = user_inputs.after

    if output_dir == default_out_dir_arg:
        output_dir = input_dir.parent / (
            input_dir.name + f'_events_th{threshold}_b{before}_a{after}')
    else:
        output_dir = Path(output_dir)

    try:
        output_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print('\nThe output directory already exists'
              ' and you may be overwriting or confusing data:'
              f'\n({output_dir})')
        continue_decision = None
        while continue_decision != 'y' and continue_decision != 'n':
            continue_decision = input('\nDo you want to continue? y/n: ')
            if continue_decision == 'y':
                pass
            if continue_decision == 'n':
                print('\nOk, exiting...')
                sys.exit()

    print('')
    print(f'Using files from {input_dir}.')
    print(f'Saving extracted sequences in {output_dir}.')
    print('')

    # Get sorted filenames, no extension
    filename_list = []
    for child in input_dir.iterdir():
        filename_list.append(child.stem)
        # print(child.stem)
    filename_num_dict, filename_list = sortimagenames_by_num(filename_list)

    if len(filename_list) == 0:
        print('No valid image files.')
        print('Exiting...')
        sys.exit()

    ## Load sorted images into image stack
    # First get image dimensions
    image0 = imread(input_dir / (filename_list[0] + '.tiff'))
    print(f'Single-image dimensions are: {image0.shape}')
    input_seq = np.zeros((image0.shape[0], image0.shape[1], len(filename_list)))
    for i in range(input_seq.shape[2]):
        input_seq[:,:,i] = imread(input_dir / (filename_list[i] + '.tiff'))

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
