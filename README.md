# ExtractEvents

ExtractEvents is a Python library for extracting sets of useful frames from longer timelapse sequences.

## Platform

May only work on Windows, currently (developed on Windows 10).

## Installation

* Download or clone this repository
* Install Miniconda (anaconda.org/downloads)
* Create environment
  * In a Miniconda prompt, Navigate to your local copy of this repository
  * Enter `conda env create -f environment.yml`
    * You can ignore a message containing ```FutureWarning: `remote_definition` is deprecated``` if one appears.

## Usage

* Activate environment
  * In Miniconda, enter `conda activate extractevents`

### From a directory containing one tiff file per image, extract sequences around a frame containing a pixel brighter than a threshold value
* In a Miniconda prompt, navigate to this local repository
* Enter `python extractevents.py` to run the GUI for extracting events
* In the GUI:
  * Select an input directory
  * In the text fields in the GUI, set threshold grey level to trigger subsequence extraction, and frames to include before and after trigger, or leave as defaults
  * Select an *empty* output directory
  * Run event extraction
* The input sequence remains ready for another run with different parameters, if desired (the output directory must be emptied or changed)

### Timings
* Downloading ImageJ for running useful commands with PyImageJ will take some time on the first run of your installation (this is an automatic and necessary part of setting up the software).
* Within a GUI session, second and subsequent runs of the event extraction step are faster than the first, for the same input image sequence.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## Authors and acknowledgement

Created by Alistair Curd, University of Leeds, 25 November 2024.

## License

[Apache-2.0](https://opensource.org/license/apache-2-0)
