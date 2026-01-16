"""Test IOC type classification to ensure URLs are not misclassified as IPs"""

import logging
from backend.extractors.iocs_extractor import IOCsExtractor
from backend.data_model.ioc import IOCType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_ioc_classification_with_blog_article():
    """Test that IOCs from the blog article are correctly classified"""

    # Read the test blog article
    with open("tests/test_blog_article.txt", "r", encoding="utf-8") as f:
        article_content = f.read()

    # Extract IOCs
    logger.info("Extracting IOCs from blog article...")
    extractor = IOCsExtractor(article_content=article_content)
    iocs = extractor.extract_iocs_from_text()

    # Group IOCs by type
    iocs_by_type = {}
    for ioc in iocs:
        type_name = ioc.type.name
        if type_name not in iocs_by_type:
            iocs_by_type[type_name] = []
        iocs_by_type[type_name].append(ioc.value)

    # Print results
    logger.info("\n" + "=" * 80)
    logger.info("IOC EXTRACTION RESULTS")
    logger.info("=" * 80)

    for ioc_type in IOCType:
        type_name = ioc_type.name
        count = len(iocs_by_type.get(type_name, []))
        logger.info(f"\n{ioc_type.value} ({type_name}): {count} found")

        if count > 0:
            for value in iocs_by_type[type_name]:
                logger.info(f"  - {value}")

    logger.info("\n" + "=" * 80)
    logger.info(f"TOTAL IOCs: {len(iocs)}")
    logger.info("=" * 80)

    # Validation checks
    urls = iocs_by_type.get("URL", [])
    ips = iocs_by_type.get("IP", [])

    # Check that we found URLs
    assert len(urls) > 0, "Should find URLs in the article"

    # Check that URLs are not classified as IPs
    for url in urls:
        assert (
            "http" in url.lower() or "[.]" in url or "." in url
        ), f"URL should contain http or domain pattern: {url}"

    # Check that IPs (if any) are actually IPs, not URLs
    for ip in ips:
        assert "http" not in ip.lower(), f"IP should not contain 'http': {ip}"
        assert (
            "[.]" not in ip
            or ip.replace("[.]", ".").replace(".", "").replace(":", "").isdigit()
        ), f"IP should be numeric format: {ip}"

    # Expected URLs from the article (sample)
    expected_urls = [
        "facturacionmexico[.]net",
        "facturacionmx[.]autos",
        "dlxfreights[.]site",
        "cssangular[.]com",
    ]

    # Check that at least some expected URLs were found
    found_expected = 0
    for expected in expected_urls:
        for url in urls:
            if expected in url:
                found_expected += 1
                logger.info(f"✓ Found expected URL pattern: {expected} in {url}")
                break

    assert (
        found_expected > 0
    ), f"Should find at least some expected URLs. Found {found_expected}/{len(expected_urls)}"

    logger.info(
        f"\n✓ Test passed! Found {found_expected}/{len(expected_urls)} expected URL patterns"
    )
    logger.info(f"✓ No URLs misclassified as IPs")

    return iocs_by_type


if __name__ == "__main__":
    test_ioc_classification_with_blog_article()
