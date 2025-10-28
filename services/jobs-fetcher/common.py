# SCRAPING IMPORTATIONS
from urllib.parse import urljoin, urlparse

def get_domain_from_link(link: str):
    parsed = urlparse(link)
    domain = parsed.netloc
    return domain

def fix_link_with_domain(link: str, domain: str) -> str:
    """
    Ensures the link is a full URL with the given domain.
    
    - If the link already has the domain, return it as-is.
    - If the link is relative (starts with /), prepend the domain.
    - If the link is fully qualified but with a different domain, leave it unchanged.

    Args:
        link (str): The URL or relative path to fix.
        domain (str): The base domain, e.g., "https://www.example.com"

    Returns:
        str: Full URL with the domain.
    """
    # Make sure domain has scheme
    if not domain.startswith("http"):
        domain = "http://" + domain

    # If link is already absolute
    parsed_link = urlparse(link)
    if parsed_link.netloc:
        # Already has a domain, return as-is
        return link
    else:
        # Relative path → join with domain
        return urljoin(domain, link)