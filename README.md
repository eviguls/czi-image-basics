# czi-image-basics

Three small Python functions that turn a Zeiss `.czi` microscopy file into ordinary
grayscale images, with a sample image and a Jupyter notebook that tests them.

The code is adapted from the image-loading part of a larger project that counts
DNA damage repair foci in nuclei (immunofluorescence, DAPI + foci marker).

## What is in the repo

| File | What it is |
|---|---|
| `czi_basics.py` | The custom module: `load_czi`, `to_8bit`, `save_image` |
| `czi_basics_demo.ipynb` | Notebook that runs every function on the sample and checks the results with `assert`s |
| `environment.yml` | Conda environment with the required packages |
| `data/sample_nuclei_foci.czi` | Test image (0.6 MB): 2 channels (DAPI, GFP foci), 512 x 512 px |

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

## How to run it

```bash
git clone https://github.com/eviguls/czi-image-basics.git
cd czi-image-basics
conda env create -f environment.yml
conda activate czi-basics
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
