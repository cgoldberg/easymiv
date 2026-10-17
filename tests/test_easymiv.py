# Copyright (c) 2013-2026 Corey Goldberg
# SPDX-License-Identifier: GPL-3.0-only


import pytest
from PIL import Image

from easymiv import Display, SlideShow


@pytest.fixture
def image_dir(tmp_path):
    """Create a directory containing images and a non-image file."""
    (tmp_path / "nested").mkdir()
    Image.new("RGB", (100, 100), color="red").save(tmp_path / "image1.png")
    Image.new("RGB", (200, 100), color="green").save(tmp_path / "image2.jpg")
    Image.new("RGB", (50, 50), color="blue").save(tmp_path / "nested" / "image3.png")
    (tmp_path / "notes.txt").write_text("Not an image")
    (tmp_path / "broken.png").write_text("Not a valid image")
    return tmp_path


class TestSlideShow:
    def test_discovers_images_recursively(self, image_dir):
        slideshow = SlideShow(image_dir, randomize=False)
        assert len(slideshow.files) == 3
        assert all(path.is_absolute() for path in slideshow.files)
        assert all(path.is_file() for path in slideshow.files)

    def test_discovers_images_in_sorted_order(self, image_dir):
        slideshow = SlideShow(image_dir, randomize=False)
        expected = sorted(
            [
                (image_dir / "image1.png").resolve(),
                (image_dir / "image2.jpg").resolve(),
                (image_dir / "nested" / "image3.png").resolve(),
            ]
        )
        assert slideshow.files == expected

    def test_ignores_non_image_and_corrupt_files(self, image_dir):
        slideshow = SlideShow(image_dir, randomize=False)
        filenames = [path.name for path in slideshow.files]
        assert "notes.txt" not in filenames
        assert "broken.png" not in filenames

    def test_initial_current_image(self, image_dir):
        slideshow = SlideShow(image_dir, randomize=False)
        assert slideshow.get_current() == slideshow.files[0]

    def test_initial_position_text(self, image_dir):
        slideshow = SlideShow(image_dir, randomize=False)
        assert slideshow.get_extra() == "1 / 3"

    def test_move_next(self, image_dir):
        slideshow = SlideShow(image_dir, randomize=False)
        result = slideshow.move_next()
        assert result == slideshow.files[1]
        assert slideshow.get_extra() == "2 / 3"

    def test_move_previous(self, image_dir):
        slideshow = SlideShow(image_dir, randomize=False)
        result = slideshow.move_previous()
        assert result == slideshow.files[-1]
        assert slideshow.get_extra() == "3 / 3"

    def test_navigation_wraps_forward(self, image_dir):
        slideshow = SlideShow(image_dir, randomize=False)
        for _ in range(len(slideshow.files)):
            slideshow.move_next()
        assert slideshow.get_current() == slideshow.files[0]
        assert slideshow.get_extra() == "1 / 3"

    def test_navigation_wraps_backward(self, image_dir):
        slideshow = SlideShow(image_dir, randomize=False)
        slideshow.move_previous()
        assert slideshow.get_current() == slideshow.files[-1]
        slideshow.move_previous()
        slideshow.move_previous()
        assert slideshow.get_current() == slideshow.files[0]

    def test_empty_directory_raises_value_error(self, tmp_path):
        with pytest.raises(ValueError, match="No images found"):
            SlideShow(tmp_path, randomize=False)

    def test_directory_without_images_raises_value_error(self, tmp_path):
        (tmp_path / "notes.txt").write_text("No images here")
        with pytest.raises(ValueError, match="No images found"):
            SlideShow(tmp_path, randomize=False)

    def test_randomize_preserves_image_count(self, image_dir):
        slideshow = SlideShow(image_dir, randomize=True)
        assert len(slideshow.files) == 3
        assert set(slideshow.files) == {
            (image_dir / "image1.png").resolve(),
            (image_dir / "image2.jpg").resolve(),
            (image_dir / "nested" / "image3.png").resolve(),
        }


class TestDisplay:
    @pytest.fixture
    def display(self):
        """Create a Display instance without initializing Tkinter."""
        return Display.__new__(Display)

    def test_zoom_image_scales_to_fit_width(self, display):
        image = Image.new("RGB", (200, 100))
        resized, zoom_text = display._zoom_image(image, 100, 100)
        assert resized.size == (100, 50)
        assert zoom_text == "50%"

    def test_zoom_image_scales_to_fit_height(self, display):
        image = Image.new("RGB", (100, 200))
        resized, zoom_text = display._zoom_image(image, 100, 100)
        assert resized.size == (50, 100)
        assert zoom_text == "50%"

    def test_zoom_image_preserves_aspect_ratio(self, display):
        image = Image.new("RGB", (400, 200))
        resized, _ = display._zoom_image(image, 300, 300)
        assert resized.size == (300, 150)

    def test_zoom_image_does_not_enlarge_image(self, display):
        image = Image.new("RGB", (100, 50))
        resized, zoom_text = display._zoom_image(image, 300, 300)
        assert resized.size == (300, 150)
        assert zoom_text == "300%"

    def test_zoom_image_handles_zero_width(self, display):
        image = Image.new("RGB", (100, 50))
        resized, zoom_text = display._zoom_image(image, 0, 100)
        assert resized.size == image.size
        assert resized is not image
        assert zoom_text == "100%"

    def test_zoom_image_handles_zero_height(self, display):
        image = Image.new("RGB", (100, 50))
        resized, zoom_text = display._zoom_image(image, 100, 0)
        assert resized.size == image.size
        assert resized is not image
        assert zoom_text == "100%"
