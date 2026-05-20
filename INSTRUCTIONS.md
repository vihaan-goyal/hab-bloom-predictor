# HAB Bloom Predictor — Setup & Usage

## Environment setup
1. Install Anaconda from anaconda.com
2. Open Anaconda Prompt and run:
   conda create -n hab python=3.11
   conda activate hab
   pip install numpy pandas xarray netCDF4 matplotlib cartopy scikit-learn torch torchvision earthaccess

## Running scripts
Always activate the environment first:
   conda activate hab

Then run from the repo root:
   python download_modis.py   # download satellite data
   python visualize.py        # plot chlorophyll map

## Data
- Raw NetCDF files go in data/raw/
- Do not commit data/ to GitHub (it's in .gitignore)
- NASA Earthdata login required -- earthdata.nasa.gov

## Project structure
   hab-bloom-predictor/
   ├── data/
   │   └── raw/          # MODIS NetCDF files (gitignored)
   ├── download_modis.py  # data download script
   ├── visualize.py       # visualization script
   ├── INSTRUCTIONS.md    # this file
   └── README.md