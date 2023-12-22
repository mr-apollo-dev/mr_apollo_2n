from xml.etree.ElementTree import Element

import pytest

from mr_apollo_2n.model.website_node_model import WebsiteNodeModel
from mr_apollo_2n.utils.website_node_crawler import WebsiteNodeCrawler


@pytest.fixture
def website_node_crawler():
    return WebsiteNodeCrawler("https://example.com")


def test_fetch_and_parse_success(website_node_crawler, requests_mock):
    requests_mock.get("https://example.com/sitemap.xml", text="<urlset></urlset>")
    result = website_node_crawler.fetch_and_parse("https://example.com/sitemap.xml")
    assert isinstance(result, Element)
    assert result.tag == "urlset"


def test_extract_sitemaps(website_node_crawler, requests_mock):
    robots_content = "Sitemap: https://example.com/sitemap.xml\n"
    requests_mock.get("https://example.com/robots.txt", text=robots_content)
    sitemaps = website_node_crawler.extract_sitemaps()
    assert sitemaps == ["https://example.com/sitemap.xml"]


def test_process_sitemap(website_node_crawler, requests_mock):
    # Mock the response for sitemap and its URLs
    requests_mock.get(
        "https://example.com/sitemap.xml",
        text="<urlset><url><loc>https://example.com/page</loc></url></urlset>",
    )
    # Mock response for each URL in the sitemap
    requests_mock.get("https://example.com/page", text="Page Content")

    result = website_node_crawler.process_sitemap("https://example.com/sitemap.xml")
    assert len(result) > 0
    assert all(isinstance(item, WebsiteNodeModel) for item in result)
