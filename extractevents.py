"""extractevents-gui.py

Alistair Curd
University of Leeds
2025-02-17
"""

import time
import tkinter as tk

from pathlib import Path
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar

import imagej
from scyjava import jimport


# Initialise ImageJ and show result
print("Initialising ImageJ commands...")
ij = imagej.init('2.14.0')  # First download of a version takes a while...
print(f"ImageJ version: {ij.getVersion()}")

# Import FolderOpener for use of virtual stack
FolderOpener = jimport('ij.plugin.FolderOpener')

class ExtractEventsGUI:
    """Interactive GUI object"""
    def __init__(self, window):
        self.window = window
        self.window.geometry('400x450')
        self.window.title('Extract Events')

        # For selecting and reporting on image sequence
        self.open_sequence_text = tk.Label(
            text='Select a directory containing an image sequence:'
        )
        self.open_sequence_text.pack()

        self.open_dir_button = tk.Button(
            window, text="Select", command=self.open_image_sequence)
        self.open_dir_button.pack()

        self.open_dir_result_label = tk.Label(window)
        self.open_dir_result_label.pack()

        self.sequence_props_label = tk.Label(window)
        self.sequence_props_label.pack()

        self.image_seq = None
        self.output_dir = None
        self.progbar = None

        # Blank space
        self.blank = tk.Label()
        self.blank.pack()

        # For choosing sequence extraction parameters
        thresh_default = 55
        before_default = 5
        after_default = 5
        self.thresh_label = tk.Label(
            text="Threshold to trigger event extraction:")
        self.thresh_entry = tk.Entry()
        self.thresh_label.pack()
        self.thresh_entry.pack()

        self.frames_before_label = tk.Label(
            text="Frames to include before threshold trigger:")
        self.frames_before_entry = tk.Entry()
        self.frames_before_label.pack()
        self.frames_before_entry.pack()

        self.frames_after_label = tk.Label(
            text="Frames to include after threshold trigger:")
        self.frames_after_entry = tk.Entry()
        self.frames_after_label.pack()
        self.frames_after_entry.pack()

        self.thresh_entry.insert(0, thresh_default)
        self.frames_after_entry.insert(0, after_default)
        self.frames_before_entry.insert(0, before_default)

        # Blank space
        self.blank2 = tk.Label()
        self.blank2.pack()

        # Select output destination
        self.output_dir_text = tk.Label(
            text='Select an empty directory for the output sequences:'
        )
        self.output_dir_text.pack()

        self.output_dir_button = tk.Button(
            window, text="Select", command=self.select_output_dir)
        self.output_dir_button.pack()

        self.output_dir_result_label = tk.Label(window)
        self.output_dir_result_label.pack()

        # Blank space
        self.blank3 = tk.Label()
        self.blank3.pack()

        # Run event extraction
        self.extract_button = tk.Button(
            window, text="Run event extraction", command=self.extract_events)
        self.extract_button.pack()
        self.prog_bar_label = tk.Label()
        self.prog_bar_len = 300

    def warn_no_image_seq(self):
        """Warn and give signal if no image sequence loaded."""
        if self.image_seq is None:
            messagebox.showwarning(
                message='No image sequence has been loaded.'
            )
            return True

    def warn_no_output_dir(self):
        """Warn and give signal if no output directory selected."""
        if self.output_dir is None:
            messagebox.showwarning(
                message='No output directory selected.'
            )
            return True

    def open_image_sequence(self):
        """Selecting a directory and open the image sequence."""
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.open_dir_result_label.configure(text=f'Opening {dir_path}...')
            self.open_dir_result_label.update()  # Change display
            self.sequence_props_label.config(text="")
            self.sequence_props_label.update()

            starttime = time.time()
            # imp = FolderOpener.open("C:/Temp/15kz-1/", "virtual")
            self.image_seq = FolderOpener.open(dir_path, "virtual")
            load_time = time.time() - starttime

            self.open_dir_result_label.config(
                text=f'Loaded sequence at {dir_path} in {load_time:.1f} s')

            self.sequence_props_label.config(
                text=f'{self.image_seq.shape[2]} images'
                     + f' ({self.image_seq.shape[0]}'
                     + f' x {self.image_seq.shape[1]})'
            )

            # Convert ImagePlus array to ImageJ dataset format
            # # for convenient use of max values
            self.image_seq = ij.py.to_dataset(self.image_seq)

    def select_output_dir(self):
        """Select output directory."""
        if self.warn_no_image_seq():
            return
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir_result_label.configure(text=f'{dir_path}')
            self.output_dir = dir_path
            # self.dummy_save()

    # def dummy_save(self):
    #    """Save one frame to try to get the destination folder into cache."""
    #    testfilename = 'a.tiff'
    #    path = Path(self.output_dir) / (testfilename)
    #    ij.io().save(self.image_seq[:, :, 0],
    #                 self.output_dir + '\\' + testfilename)
    #    # time.sleep(2)
    #    path.unlink()

    def extract_events(self):
        """Run event extraction."""
        # Warn and return if inputs not present / awkward
        if self.warn_no_image_seq():
            return
        if self.warn_no_output_dir():
            return
        if any(Path(self.output_dir).iterdir()):
            messagebox.showwarning(
                message='Output directory is not empty.\n'
                        'Choose an empty output directory.'
            )
            return

        # Do extraction
        num_frames = self.image_seq.shape[2]
        thresh = int(self.thresh_entry.get())
        before = int(self.frames_before_entry.get())
        after = int(self.frames_after_entry.get())

        # Set up progress bar
        self.prog_bar_label.config(text=f'0 / {num_frames}')
        self.prog_bar_label.pack()
        self.progbar = Progressbar(self.window,
                               length=self.prog_bar_len,
                               mode='determinate')
        self.progbar.pack()

        count_updates = 1
        frames_between_updates = 500

        assert frames_between_updates > after, 'frames_between_updates must be > after'

        # Extract events
        i = 0
        start_time = time.time()
        while i < num_frames:
            if ij.py.from_java(ij.op().stats().max(self.image_seq[:, :, i])).value >= thresh:
                start_frame = max(i - before, 0)
                last_frame = min(i + after, num_frames)
                short_seq = self.image_seq[:, :, start_frame : last_frame + 1]
                outname = f'{start_frame}-{last_frame}.tiff'
                outpath = self.output_dir + '\\' + outname
                # print(short_seq.shape)
                ij.io().save(short_seq, outpath)
                i = i + after
            else:
                i = i + 1

            # Update progress bar
            if i > count_updates * frames_between_updates:
                time_elapsed = int(time.time() - start_time)
                total_time_estimate = int(time_elapsed / i * num_frames )
                self.progbar['value'] = 100 * i / num_frames
                count_updates += 1
                self.prog_bar_label.config(
                    text=f'{i} / {num_frames} images'
                         f'        {time_elapsed} / {total_time_estimate}  s')
                self.window.update_idletasks()

        self.prog_bar_label.config(
            text=f'{num_frames} / {num_frames} images'
                 f'        {time_elapsed} / {total_time_estimate}  s'
        )
        self.progbar['value'] = 100
        self.window.update_idletasks()
        time.sleep(1)
        self.progbar.pack_forget()


if __name__ == '__main__':
    root = tk.Tk()
    ExtractEventsGUI(root)
    root.mainloop()
