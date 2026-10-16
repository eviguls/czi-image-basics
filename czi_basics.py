"""Small helpers for turning a Zeiss .czi microscopy file into ordinary images.

Adapted from the image-loading code of the FociCounter project, which counts
DNA damage repair foci inside nuclei in immunofluorescence images.

A .czi file is the native format of Zeiss microscopes. Unlike a PNG or JPEG, it
stores several channels (one per fluorescent dye, e.g. DAPI for nuclei and GFP
for foci), keeps the raw 16-bit camera values, and carries metadata such as the
channel names and the physical size of a pixel.

The three steps in this module are:

1. ``load_czi``    read the .czi file into a NumPy array, one 2D image per channel
2. ``to_8bit``     rescale one 16-bit channel to 8-bit grayscale (values 0-255)
3. ``save_image``  write a 2D array to disk as a PNG or TIFF file
"""

# Lets us write type hints like "str | Path" on older Python versions too.
from __future__ import annotations

from pathlib import Path

import numpy as np


def load_czi(path: str | Path) -> tuple[np.ndarray, dict]:
    """Read a .czi file and return its pixels plus the most useful metadata.

    Parameters
    ----------
    path : str or Path
        Location of the .czi file.

    Returns
    -------
    data : numpy.ndarray
        Pixel values shaped ``(C, Y, X)``: channel, row, column. So ``data[0]``
        is the first channel (e.g. DAPI) as a plain 2D image.
    metadata : dict
        File path, array shape, channel names, pixel size in micrometres and
        the data type (usually ``uint16``, i.e. 16-bit, values 0-65535).
    """
    # bioio is a general microscopy reader; with the bioio-czi plugin installed
    # it understands Zeiss files. Importing it inside the function means the
    # other two functions still work on a computer where bioio is missing.
    from bioio import BioImage

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    img = BioImage(str(path))

    # Microscopy files can hold up to five dimensions: T (time), C (channel),
    # Z (focal plane), Y and X. Our images are single snapshots, so we ask for
    # just "CYX" and pin time and focal plane to the first one (index 0).
    data = np.asarray(img.get_image_data("CYX", T=0, Z=0))

    # Pixel size tells you how big one pixel is in real life (micrometres),
    # which you need to report areas or distances instead of pixel counts.
    pixel_size = img.physical_pixel_sizes
    metadata = {
        "path": str(path),
        "shape_CYX": tuple(int(n) for n in data.shape),
        "channel_names": [str(name) for name in (img.channel_names or [])],
        "pixel_size_um": {"Y": pixel_size.Y, "X": pixel_size.X},
        "dtype": str(data.dtype),
    }
    return data, metadata


def to_8bit(image: np.ndarray, low_pct: float = 1.0, high_pct: float = 99.8) -> np.ndarray:
    """Convert one channel to 8-bit grayscale using a percentile contrast stretch.

    Microscope cameras record 16-bit values (0-65535), but most image viewers
    and file formats expect 8-bit values (0-255). Simply dividing by 256 makes
    dim fluorescence images look almost black, because the real signal usually
    uses only a small part of the 16-bit range.

    Instead we pick a dark cut-off and a bright cut-off from the image itself:

    * everything at or below the ``low_pct`` percentile becomes 0 (black),
    * everything at or above the ``high_pct`` percentile becomes 255 (white),
    * values in between are spread evenly over 0-255.

    Percentiles are used instead of the plain minimum and maximum so that a few
    extremely bright pixels (dust, hot pixels) do not squash everything else.

    Parameters
    ----------
    image : numpy.ndarray
        A 2D image of any numeric type.
    low_pct, high_pct : float
        Percentiles (0-100) used as the black and white points.

    Returns
    -------
    numpy.ndarray
        Same shape as ``image``, type ``uint8``.
    """
    if not 0 <= low_pct < high_pct <= 100:
        raise ValueError("need 0 <= low_pct < high_pct <= 100")

    # Work in floating point so the subtraction and division below are exact
    # (integer maths would round or wrap around).
    image = np.asarray(image, dtype=np.float64)
    low, high = np.percentile(image, [low_pct, high_pct])

    # A completely flat image has no contrast to stretch; avoid dividing by zero.
    if high <= low:
        return np.zeros(image.shape, dtype=np.uint8)

    # Map low -> 0.0 and high -> 1.0, clip anything outside that range,
    # then scale to 0-255 and round to whole numbers.
    scaled = (image - low) / (high - low)
    scaled = np.clip(scaled, 0, 1)
    return (scaled * 255).round().astype(np.uint8)


def save_image(image: np.ndarray, path: str | Path) -> Path:
    """Save a 2D array as a PNG or TIFF file.

    The file type is chosen from the extension of ``path``:

    * ``.png``  is lossless and opens anywhere; best for 8-bit images.
    * ``.tif`` / ``.tiff`` can also keep the original 16-bit values, which is
      what you want if the image will be measured later (e.g. in Fiji/ImageJ).

    Missing folders in ``path`` are created automatically.

    Returns
    -------
    Path
        The path of the file that was written.
    """
    # Pillow (PIL) is the standard Python library for writing common image files.
    from PIL import Image

    path = Path(path)

    # Only single-channel (grayscale) images are accepted, so a colour or
    # multi-channel array is caught here with a clear message.
    if image.ndim != 2:
        raise ValueError(f"expected a 2D image, got shape {image.shape}")
    if path.suffix.lower() not in {".png", ".tif", ".tiff"}:
        raise ValueError(f"unsupported file type {path.suffix!r}; use .png or .tif")

    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image).save(path)
    return path
