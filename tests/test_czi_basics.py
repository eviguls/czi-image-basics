"""Quick checks that the installed package works. Run with: pytest"""

from pathlib import Path

import numpy as np
from PIL import Image

from czi_basics import load_czi, save_image, to_8bit

SAMPLE = Path(__file__).parent.parent / "data" / "sample_nuclei_foci.czi"


def test_load_czi_reads_sample():
    data, meta = load_czi(SAMPLE)
    assert data.shape == (2, 512, 512)
    assert data.dtype == np.uint16
    assert meta["channel_names"] == ["DAPI", "GFP"]


def test_to_8bit_small_example():
    image = np.array([[0, 50], [100, 100]])
    assert to_8bit(image, 0, 100).tolist() == [[0, 128], [255, 255]]


def test_save_image_round_trip(tmp_path):
    image = np.arange(16, dtype=np.uint8).reshape(4, 4)
    path = save_image(image, tmp_path / "test.png")
    assert (np.array(Image.open(path)) == image).all()
