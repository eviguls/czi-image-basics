# czi-image-basics

Three small Python functions that turn a Zeiss `.czi` microscopy file into ordinary
grayscale images, with a sample image and a Jupyter notebook that tests them.

The code is adapted from the image-loading part of a larger project that counts
DNA damage repair foci in nuclei (immunofluorescence, DAPI + foci marker).

## What is in the repo

```
czi-image-basics/
├── czi_basics/              <- the package (the folder you import)
│   ├── __init__.py          <- marks the folder as a package; exposes the 3 functions
│   └── image_io.py          <- the code: load_czi, to_8bit, save_image
├── setup.py                 <- install script: name, version, dependencies
├── tests/test_czi_basics.py <- quick automatic checks (run with pytest)
├── czi_basics_demo.ipynb    <- notebook demo with asserts on the sample image
├── environment.yml          <- conda environment
└── data/sample_nuclei_foci.czi  <- test image (0.6 MB, DAPI + GFP, 512 x 512 px)
```

## The functions

1. **`load_czi(path)`** reads the file into a NumPy array shaped `(C, Y, X)`
   (one 2D image per channel) and returns metadata (channel names, pixel size
   in µm, dtype).
2. **`to_8bit(image, low_pct=1, high_pct=99.8)`** converts 16-bit data to 8-bit
   grayscale (0-255) with a percentile contrast stretch.
3. **`save_image(image, path)`** writes a 2D array as `.png` or `.tif`.

```python
from czi_basics import load_czi, to_8bit, save_image

data, meta = load_czi("data/sample_nuclei_foci.czi")
for name, channel in zip(meta["channel_names"], data):
    save_image(to_8bit(channel), f"outputs/{name}.png")
```

## How to install it

```bash
git clone https://github.com/eviguls/czi-image-basics.git
cd czi-image-basics
conda env create -f environment.yml
conda activate czi-basics
pip install .
```

`pip install .` reads `setup.py`, installs the dependencies (numpy, pillow,
bioio, bioio-czi) and copies the `czi_basics` package into the environment, so
`import czi_basics` now works from any folder. After you change the code, run
`pip install .` again (or install once with `pip install -e .`, "editable" mode,
so code changes are picked up without reinstalling).

Check that it worked:

```bash
python -c "import czi_basics; print(czi_basics.__version__)"   # prints 0.1.0
pytest                                                          # 3 passed
```

## How to run the demo

```bash
jupyter lab czi_basics_demo.ipynb
```

Then choose **Run > Run All Cells**. Each section ends with a line like
`load_czi OK`, and the last cell prints `All checks passed.` The PNG and TIFF
files it writes go into `outputs/` (ignored by git).

To run the notebook without opening a browser:

```bash
jupyter nbconvert --to notebook --execute czi_basics_demo.ipynb --output executed_demo.ipynb
```

## About the sample image

`data/sample_nuclei_foci.czi` is a 1024 x 1024 px crop of one focal plane of a
larger image, binned 2 x 2 to 512 x 512 px (pixel size 0.11 µm) and saved with
lossless compression so it is small enough to keep in git. Channel 0 (DAPI) shows the
nuclei; channel 1 (GFP) shows the foci.
