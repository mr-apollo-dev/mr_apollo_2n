from mr_apollo_2n.utils.utils import build_domain_name


def test_build_domain_name_with_www():
    url = "https://www.example.com"
    result = build_domain_name(url)
    assert result == "www_example_com"


def test_build_domain_name_with_port():
    url = "https://example.com:8080"
    result = build_domain_name(url)
    assert result == "example_com"


def test_build_domain_name_with_special_characters():
    url = "https://www.my-website.com/page"
    result = build_domain_name(url)
    assert result == "www_my_website_com"


def test_build_domain_name_empty_url():
    url = ""
    result = build_domain_name(url)
    assert result == ""


def test_build_domain_name_with_special_characters_in_fragment():
    url = "https://www.example.com/#section"
    result = build_domain_name(url)
    assert result == "www_example_com"


def test_build_domain_name_with_query_parameters():
    url = "https://www.example.com/page?param=value"
    result = build_domain_name(url)
    assert result == "www_example_com"


def test_build_domain_name_without_scheme():
    url = "www.example.com"
    result = build_domain_name(url)
    assert result == "www_example_com"


def test_build_domain_name_with_username_and_password():
    url = "https://user:pass@example.com"  # pragma: allowlist secret
    result = build_domain_name(url)
    assert result == "example_com"
