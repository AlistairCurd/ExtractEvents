# ExtractEvents

ExtractEvents is a Python library for extracting set of useful frames from longer timelapse sequences.

## Installation

* Download or clone this repository
* Install Miniconda (anaconda.org/downloads)
* Create environment
  * In a Miniconda prompt, Navigate to your local copy of this repository
  * `conda env create -f environment.yml`
    * You can ignore a message containing ```FutureWarning: `remote_definition` is deprecated``` if one appears.

## Usage

* Activate environment
  * `conda activate extractevents`

### From a directory containing one tiff file per image, extract sequences around a frame containing a pixel brighter than a threshold value
* In a Minicaonda prompt, navigate to this local repository
* `python abovethreshold.py -h` to see command options.
* e.g. `python abovethreshold.py -i <input_path>` to extract sequences from files in input_path to default output path.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## Authors and acknowledgement

Created by Alistair Curd, University of Leeds, 25 November 2024.

## License

[Apache-2.0](https://opensource.org/license/apache-2-0)
