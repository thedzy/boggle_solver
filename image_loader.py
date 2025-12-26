from __future__ import annotations

"""
Script:	image_loader.py
Date:	2025-12-25

Platform: macOS/Windows/Linux

Description:
Load and image and extract text

"""
__author__ = "thedzy"
__copyright__ = "Copyright 2020, thedzy"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "thedzy"
__email__ = "thedzy@hotmail.com"
__status__ = "Development"

import re
from pathlib import Path
from typing import Iterable, Any
import string


def get_newest_image_path(images_dir: Path, image_suffixes: Iterable[str] = ('.png',)) -> Path:
    """
    Return the newest image file in a folder (by mtime).
    :param images_dir: folder containing images
    :param image_suffixes: allowed suffixes (eg ('.png', '.jpg'))
    :return: path to newest matching image
    """
    if not images_dir.exists() or not images_dir.is_dir():
        raise RuntimeError(f'Images folder not found or not a directory: {images_dir}')

    image_suffixes_lower: set[str] = {suffix.lower() for suffix in image_suffixes}

    candidate_paths: list[Path] = [
        file_path
        for file_path in images_dir.iterdir()
        if file_path.is_file() and file_path.suffix.lower() in image_suffixes_lower
    ]

    if not candidate_paths:
        raise RuntimeError(f'No matching images found in: {images_dir}')

    newest_path: Path = max(candidate_paths, key=lambda file_path: file_path.stat().st_mtime)
    return newest_path


def ocr_image(image_path: Path = Path(__file__), clipboard: bool = False,
              threshold: int = 128,
              oem: int = 3, psm: int = 6,
              gutter_px: int = 10, debug: bool = False) -> list[str]:
    """
    OCR an image file and return extracted text.
    :param image_path: path to image file
    :param clipboard: use clipboard
    :param threshold: contrast threshold
    :param oem: Engine to use
    :param psm: Page Segmentation Mode to use
    :param gutter_px: gap padding
    :param debug: run in debug
    :return: extracted text
    """
    # prevent unnecessarily modules from loading
    config: str = f'--oem {oem} --psm {psm} -c tessedit_char_whitelist={string.ascii_letters}'
    if debug:
        print(config)

    # Import necessary modules
    try:
        import pytesseract
        from PIL import Image, ImageOps, ImageFilter, ImageGrab
        import numpy as np
    except ImportError as import_error:
        raise RuntimeError(
            'OCR requires Pillow, pytesseract, and numpy to be installed'
        ) from import_error

    if clipboard:
        image = ImageGrab.grabclipboard()
        if image is None:
            raise RuntimeError('Clipboard does not contain an image')
    else:
        if not image_path.exists() or not image_path.is_file():
            raise RuntimeError(f'Image not found: {image_path}')

        image = Image.open(image_path)
    greyscale_image: Any = ImageOps.autocontrast(image.convert('L'))

    thresholded_image: Any = greyscale_image.point(
        lambda pixel_value: pixel_value if pixel_value < threshold else 255
    )

    scaled_image: Any = thresholded_image.resize(
        (thresholded_image.size[0] * 3, thresholded_image.size[1] * 3),
        resample=Image.Resampling.NEAREST,
    )

    thickened_image: Any = scaled_image.filter(ImageFilter.MaxFilter(3))

    inverted: Any = ImageOps.invert(thickened_image)
    data: np.ndarray = np.array(inverted)

    has_content: Any = data.max(axis=0) > 0

    transitions: Any = np.diff(has_content.astype(int))
    starts: Any = np.where(transitions == 1)[0] + 1
    ends: Any = np.where(transitions == -1)[0] + 1

    if has_content[0]:
        starts: Any = np.insert(starts, 0, 0)
    if has_content[-1]:
        ends: Any = np.append(ends, len(has_content))

    new_data: np.ndarray = data[:, starts[0]:ends[0]]

    spacer: np.ndarray = np.zeros((data.shape[0], gutter_px), dtype=data.dtype)

    # Attach subsequent blocks with the spacer in between
    for i in range(1, len(starts)):
        new_data: Any = np.concatenate([new_data, spacer, data[:, starts[i]:ends[i]]], axis=1)

    rows_with_content = np.where(data.max(axis=1) > 0)[0]
    final_data = new_data[rows_with_content[0]:rows_with_content[-1] + 1, :]

    pad: int = 25
    final_data: np.ndarray = np.pad(
        final_data,
        pad_width=((pad, pad), (pad, pad)),
        mode='constant',
        constant_values=0,
    )

    # Invert back to black-on-white
    final_image: Any = ImageOps.invert(Image.fromarray(final_data))

    image.close()

    if debug:
        debug_output_path: Path = Path('/tmp/text.png')
        final_image.save(debug_output_path)

    extracted_text: str = pytesseract.image_to_string(
        final_image,
        config=config
    )

    if debug:
        print(extracted_text)

    # Reduce to all lower case
    row: str = extracted_text.lower()

    # Return characters as array/list
    tokens: list[str] = re.findall(r'qu|[a-p,r-z]', row)

    return tokens


if __name__ == '__main__':
    # Test
    newest_image_path: Path = get_newest_image_path(Path().home().joinpath('Downloads'))
    print(newest_image_path)
    for psm in range(3, 14):
        extracted_text: str = ocr_image(newest_image_path, oem=1, psm=psm, debug=True)
    print(extracted_text)

    # clipboard
    extracted_text: str = ocr_image(newest_image_path, oem=1, psm=6, clipboard=True, debug=True)
    print(extracted_text)
