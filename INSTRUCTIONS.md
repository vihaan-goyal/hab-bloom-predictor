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

Then run everything from the repo root (scripts use root-relative data/ paths):
   python src/data/download_modis.py       # download satellite data
   python src/viz/visualize.py             # plot chlorophyll map
   python src/models/final_evaluation_threshold_sweep.py   # final evaluation
   python src/deploy/daily_inference.py --date 2022-07-19  # daily inference

## Data
- Raw NetCDF files go in data/raw/
- Do not commit data/ to GitHub (it's in .gitignore)
- NASA Earthdata login required -- earthdata.nasa.gov

## Project structure
   hab-bloom-predictor/
   ├── data/
   │   └── raw/              # MODIS/satellite NetCDF files (gitignored)
   ├── figures/              # committed output figures
   ├── notebooks/            # exploratory EDA notebooks
   ├── notes/                # paper notes and analysis logs
   ├── src/
   │   ├── data/             # data acquisition & aggregation
   │   ├── features/         # feature engineering
   │   ├── models/           # training, evaluation, tuning
   │   │   └── experiments/  # one-off experiments & diagnostics (do not import)
   │   ├── viz/              # figure & plot generation
   │   └── deploy/           # daily inference pipeline & dashboard
   ├── CLAUDE.md             # run instructions & model card
   ├── INSTRUCTIONS.md       # this file
   └── README.md