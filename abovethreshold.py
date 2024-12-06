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

from tqdm import tqdm
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

    parser.add_argument('-i', '--input-images-path',
                        type=str,
                        default='.',
                        help='Path to input directory of single images'
                        ' (directory) or to cached sequence in an image'
                        ' stack (file).')
    parser.add_argument('--cache-save',
                        type=bool,
                        default=False,
                        help='Option to save whole sequence as cache,'
                        'for faster testing of event extraction parameters.')
    parser.add_argument('--cache-use',
                        type=bool,
                        default=True,
                        help='Option to use cached sequence file,'
                        ' rather than load input images separately.'
                        '\n Needs to be ??????? and contain ???????. ')
    parser.add_argument('-l', '--list-filenames-path',
                        type=str,
                        help='Path to list of filenames in text file'
                        ' to use (optional) if loading cached image stack,'
                        ' to identify frames within the stack.'
                        'If a cached stack is used and no filename list is'
                        ' provided, image numbers will start from 0'
                        ' in the output.')
    parser.add_argument('-o', '--output-path',
                        type=str,
                        default=default_out_dir_arg,
                        help='Path to output directory for extracted events,'
                        ' created if necessary.')
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
    default_out_dir_arg = \
        '<input-path.parent>/<input-path.name>_<length of sequence>frames_events_<params>'
    user_inputs = get_inputs(default_out_dir_arg)
    input_path = Path(user_inputs.input_path)
    output_path = user_inputs.output_path
    threshold = user_inputs.threshold
    before = user_inputs.before
    after = user_inputs.after

    if output_path == default_out_dir_arg:
        output_path = input_path.parent / (
            input_path.name + f'_events_th{threshold}_b{before}_a{after}')
    else:
        output_path = Path(output_path)

    try:
        output_path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print('\nThe output directory already exists'
              ' and you may be overwriting or confusing data:'
              f'\n({output_path})')
        continue_decision = None
        while continue_decision != 'y' and continue_decision != 'n':
            continue_decision = input('\nDo you want to continue? y/n: ')
            if continue_decision == 'y':
                pass
            if continue_decision == 'n':
                print('\nOk, exiting...')
                sys.exit()

    print('')
    print(f'Using files from {input_path}.')
    print(f'Saving extracted sequences in {output_path}.')
    print('')

    # Get sorted filenames, no extension
    filename_list = []
    for child in input_path.iterdir():
        filename_list.append(child.stem)
        # print(child.stem)
    filename_num_dict, filename_list = sortimagenames_by_num(filename_list)

    if len(filename_list) == 0:
        print('No valid image files.')
        print('Exiting...')
        sys.exit()

    ## Load sorted images into image stack
    # First get image dimensions
    image0 = imread(input_path / (filename_list[0] + '.tiff'))
    print(f'Single-image dimensions are: {image0.shape}')
    input_seq = np.zeros((len(filename_list), image0.shape[0], image0.shape[1]))
    print('Loading images to find events...')
    for i in tqdm(range(input_seq.shape[0]), mininterval=1):
        input_seq[i, :, :] = imread(input_path / (filename_list[i] + '.tiff'))

    # Find and save desired sequences
    print('\nExtracting events...')
    progress_bar = tqdm(total=len(filename_list), mininterval=1)
    i = 0
    while i < len(input_seq):
        if input_seq[i, :, :].max() >= threshold:
            start_frame = max(i - before, 0)
            last_frame = min(i + after, len(input_seq))
            short_seq = input_seq[start_frame : last_frame + 1, :, :]
            start_frame_name = filename_list[start_frame]
            last_frame_num = filename_num_dict[filename_list[last_frame]]
            outname = f'{start_frame_name}-{last_frame_num}.tiff'
            imsave(output_path / outname, short_seq)
            i = i + after
            progress_bar.update(after)
        else:
            i = i + 1
            progress_bar.update(1)
    progress_bar.close()

    print('\nDone.\n')


if __name__ == '__main__':
    main()
