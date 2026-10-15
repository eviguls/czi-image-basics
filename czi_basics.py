"""Small helpers for turning a Zeiss .czi microscopy file into ordinary images.

Adapted from the image I/O code of the FociCounter project (DNA damage foci
counting). The four steps are:

1. ``load_czi``         read a .czi file into a NumPy array (C, Z, Y, X) + metadata
2. ``max_projection``   collapse the Z stack into one 2D image per channel
3. ``to_8bit``          rescale a 16-bit channel to 8-bit grayscale (0-255)
4. ``save_image``       write a 2D array to disk as PNG or TIFF
"""

from __future__ import annotations

from pathlib import Path

import numpy as np


def load_czi(path: str | Path, scene: int = 0) -> tuple[np.ndarray, dict]:
    """Read one scene of a .czi file.

    Returns the pixel data as a ``(C, Z, Y, X)`` array (first time point only)
    and a dict with the channel names, pixel size in micrometres and dtype.
    """
    from bioio import BioImage  # imported here so the other functions work without bioio

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    img = BioImage(str(path))
    img.set_scene(img.scenes[scene])
    data = np.asarray(img.get_image_data("CZYX", T=0))

    pps = img.physical_pixel_sizes
    metadata = {
        "path": str(path),
        "shape_CZYX": tuple(int(n) for n in data.shape),
        "channel_names": [str(c) for c in (img.channel_names or [])],
        "pixel_size_um": {"Z": pps.Z, "Y": pps.Y, "X": pps.X},
        "dtype": str(data.dtype),
    }
    return data, metadata


def max_projection(stack: np.ndarray, z_axis: int = 1) -> np.ndarray:
    """Maximum-intensity projection along Z.

    For a ``(C, Z, Y, X)`` stack this returns ``(C, Y, X)``: each pixel keeps its
    brightest value across the focal planes, so foci from every plane are visible.
    """
    if stack.ndim < 3:
        raise ValueError(f"expected a stack with a Z axis, got shape {stack.shape}")
    return stack.max(axis=z_axis)


def to_8bit(image: np.ndarray, low_pct: float = 1.0, high_pct: float = 99.8) -> np.ndarray:
    """Rescale an image to 8-bit grayscale using percentile contrast stretching.

    Pixels at or below the ``low_pct`` percentile become 0, pixels at or above the
    ``high_pct`` percentile become 255, and everything in between is scaled
    linearly. Using percentiles instead of min/max stops a few hot pixels from
    making the whole image look dark.
    """
    if not 0 <= low_pct < high_pct <= 100:
        raise ValueError("need 0 <= low_pct < high_pct <= 100")

    image = np.asarray(image, dtype=np.float64)
    lo, hi = np.percentile(image, [low_pct, high_pct])
    if hi <= lo:  # flat image: nothing to stretch
        return np.zeros(image.shape, dtype=np.uint8)
    scaled = (image - lo) / (hi - lo)
    return (np.clip(scaled, 0, 1) * 255).round().astype(np.uint8)


def save_image(image: np.ndarray, path: str | Path) -> Path:
    """Save a 2D array as ``.png`` or ``.tif``/``.tiff`` (format taken from the suffix).

    Parent folders are created if needed. Returns the path written.
    """
    from PIL import Image

    path = Path(path)
    if image.ndim != 2:
        raise ValueError(f"expected a 2D image, got shape {image.shape}")
    if path.suffix.lower() not in {".png", ".tif", ".tiff"}:
        raise ValueError(f"unsupported file type {path.suffix!r}; use .png or .tif")

    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image).save(path)
    return path
