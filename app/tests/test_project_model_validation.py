import pytest
from app.models.core_models import Project


def test_validate_coordinates_valid():
    Project.validate_coordinates(45.0, -73.0)


def test_validate_coordinates_invalid_latitude():
    with pytest.raises(ValueError):
        Project.validate_coordinates(-95.0, 0)