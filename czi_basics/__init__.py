"""czi_basics: turn Zeiss .czi microscopy files into ordinary grayscale images.

The three functions live in ``czi_basics/image_io.py``. Importing them here
means users can write ``from czi_basics import load_czi`` without knowing
which file inside the package they come from.
"""

from .image_io import load_czi, save_image, to_8bit

__version__ = "0.1.0"

# Names exported by "from czi_basics import *".
__all__ = ["load_czi", "to_8bit", "save_image"]
