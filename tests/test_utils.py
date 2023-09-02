import pytest
import tempfile
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
from fotogenea.utils import update_exif_creation_date


@pytest.fixture
def create_temp_image():
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_image:
        # Create a temporary image with EXIF data
        image = Image.new("RGB", (100, 100), color="red")
        image.save(temp_image.name)
        return temp_image.name


def test_update_exif_creation_date_existing_tag(create_temp_image):
    image_path = create_temp_image

    # Add DateTimeOriginal tag to the image
    image = Image.open(image_path)
    exif_data = image.getexif()
    date_time_original_tag = None
    for k, v in TAGS.items():
        if v == "DateTimeOriginal":
            date_time_original_tag = k
    exif_data[date_time_original_tag] = "2023:01:01 12:00:00"
    image.save(image_path, exif=exif_data)

    new_datetime = datetime(2023, 2, 2, 22, 00, 0)

    # Test the function for updating an existing DateTimeOriginal tag
    update_exif_creation_date(image_path, new_datetime)

    # Verify that the DateTimeOriginal tag has been updated
    updated_image = Image.open(image_path)
    updated_exif_data = updated_image.getexif()
    assert updated_exif_data[date_time_original_tag] == new_datetime.strftime(
        "%Y:%m:%d %H:%M:%S"
    )


def test_update_exif_creation_date_no_tag(create_temp_image):
    image_path = create_temp_image

    new_datetime = datetime(2023, 2, 2, 22, 00, 0)

    # Test the function for updating a non-existing DateTimeOriginal tag
    update_exif_creation_date(image_path, new_datetime)

    # Verify that the DateTimeOriginal tag has been added
    updated_image = Image.open(image_path)
    updated_exif_data = updated_image.getexif()
    for tag, value in TAGS.items():
        if value == "DateTimeOriginal":
            date_time_original_tag = tag
            break

    assert updated_exif_data[date_time_original_tag] == new_datetime.strftime(
        "%Y:%m:%d %H:%M:%S"
    )


def test_update_exif_creation_date_other_tags_not_affected(create_temp_image):
    image_path = create_temp_image
    for tag, value in TAGS.items():
        if value == "DateTimeDigitized":
            date_time_digitized = tag
        elif value == "Model":
            model = tag

    # Add some other tags to the image
    image = Image.open(image_path)
    exif_data = image.getexif()
    exif_data[date_time_digitized] = "2023:08:07 12:00:00"
    exif_data[model] = "Test Camera Model"
    image.save(image_path, exif=exif_data)

    # Test the function for updating the DateTimeOriginal tag without affecting other tags
    new_datetime = datetime(2023, 8, 7, 13, 30, 15)
    update_exif_creation_date(image_path, new_datetime)

    # Verify that the other tags remain unchanged
    updated_image = Image.open(image_path)
    updated_exif_data = updated_image.getexif()
    assert updated_exif_data[date_time_digitized] == "2023:08:07 12:00:00"
    assert updated_exif_data[model] == "Test Camera Model"


def test_update_exif_creation_date_image_not_altered(create_temp_image):
    image_path = create_temp_image

    original_image = Image.open(image_path)
    original_image_data = original_image.tobytes()

    new_datetime = datetime(2023, 8, 7, 13, 30, 15)

    # Test the function and ensure the image file is not altered
    update_exif_creation_date(image_path, new_datetime)

    updated_image = Image.open(image_path)
    updated_image_data = updated_image.tobytes()

    assert original_image_data == updated_image_data
