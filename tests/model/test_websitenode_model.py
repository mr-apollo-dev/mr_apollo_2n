from datetime import datetime

import pytest

from mr_apollo_2n.model.website_node_model import WebsiteNodeModel


@pytest.fixture
def sample_data():
    """
    Fixture for sample data used in tests.
    """
    return {
        "loc": "https://www.example.com/page1",
        "parent": "https://www.example.com/sitemap.xml",
        "element_type": "url",
        "properties": {
            "lastmod": "2022-01-01T12:00:00",
            "priority": "0.8",
            "changefreq": "daily",
            "custom_property": "custom_value",
        },
        "meta": {"key1": "value1", "key2": "value2"},
    }


def test_website_node_model_initialization(sample_data):
    """
    Test WebsiteNodeModel initialization.
    """
    node = WebsiteNodeModel(
        sample_data["loc"],
        sample_data["parent"],
        sample_data["element_type"],  # noqa
        sample_data["properties"],
        sample_data["meta"],
    )

    assert node.loc == sample_data["loc"]
    assert node.parent == sample_data["parent"]
    assert node.element_type == sample_data["element_type"]
    assert node.domain == "www.example.com"
    assert node.lastmod == datetime(2022, 1, 1, 12, 0)
    assert node.priority == 0.8
    assert node.changefreq == "daily"
    assert node.properties == {"custom_property": "custom_value"}
    assert node.meta == sample_data["meta"]


def test_website_node_model_to_dict(sample_data):
    """
    Test the to_dict method of WebsiteNodeModel.
    """
    node = WebsiteNodeModel(
        sample_data["loc"],
        sample_data["parent"],
        sample_data["element_type"],  # noqa
        sample_data["properties"],
        sample_data["meta"],
    )

    expected_dict = {
        "loc": sample_data["loc"],
        "domain": "www.example.com",
        "parent": sample_data["parent"],
        "element_type": sample_data["element_type"],
        "lastmod": datetime(2022, 1, 1, 12, 0),
        "priority": 0.8,
        "changefreq": "daily",
        "properties": {"custom_property": "custom_value"},
        "meta": sample_data["meta"],
    }

    assert node.to_dict() == expected_dict
