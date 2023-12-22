import re
from urllib.parse import urlparse


def build_domain_name(url: str) -> str:
    """
    Extracts and customizes the domain name from a URL, replacing non-alphanumeric
    and non-punctuation characters with underscores.

    Parameters
    ----------
    url : str
        The URL from which to extract the domain name.

    Returns
    -------
    str
        The customized domain name with non-alphanumeric and non-punctuation
        characters replaced by underscores.

    Examples
    --------
    >>> build_domain_name("https://www.example.com/#section")
    'www_example_com'
    >>> build_domain_name("www.example.com")
    'www_example_com'

    Notes
    -----
    If the URL does not contain a scheme (like 'http://' or 'https://'), it is
    assumed to be an HTTP URL. The function also handles URLs containing
    username and password, extracting only the domain part.
    """
    if not urlparse(url).scheme:
        url = "http://" + url

    parsed_url = urlparse(url)
    netloc = parsed_url.netloc

    # Extraer solo el dominio (ignorando el nombre de usuario y la contraseña)
    if "@" in netloc:
        netloc = netloc.split("@")[1]
    domain = netloc.split(":")[0]  # Remover puerto si existe

    subdomain = re.sub(r"[^a-zA-Z0-9_]", "_", domain)
    return subdomain
