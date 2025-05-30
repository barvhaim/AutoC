import base64
import multiprocessing
from typing import Optional
from itertools import chain
from PIL import Image
import pytesseract
from io import BytesIO
import logging
import re
import docling.exceptions
from docling.document_converter import DocumentConverter
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HtmlParser:
    """
    A class to parse HTML content from a given URL using Docling,
    extract text from images using OCR.
    """

    def __init__(self, url: str, use_ocr: bool = False):
        self.url = url
        self.converter = DocumentConverter()
        self.use_ocr: bool = use_ocr
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    def extract_text_from_image(self, image_src: str) -> str:
        img = None

        # Load image from URL
        if image_src.startswith("http"):
            response = requests.get(image_src, timeout=10)
            if response.status_code == 200 and "image" in response.headers.get(
                "Content-Type", ""
            ):
                img = Image.open(BytesIO(response.content))
            else:
                content_type = response.headers.get("Content-Type")
                logger.info(
                    f"Skipped: {image_src} (status: {response.status_code}, content-type: {content_type})"
                )

        # Load from base64 (optional enhancement)
        elif image_src.startswith("data:image"):
            base64_data = image_src.split(",")[1]
            img = Image.open(BytesIO(base64.b64decode(base64_data)))

        elif len(self._overlap_with_base_url(image_src)) > 0:
            response = requests.get(urljoin(self.url, image_src), timeout=10)
            img = Image.open(BytesIO(response.content))
        else:
            logger.info(f"Unsupported image src format: {image_src}")

        # OCR on the image
        text = pytesseract.image_to_string(img)
        return text

    def _overlap_with_base_url(self, img_url: str) -> str:
        max_len = min(len(self.url), len(img_url))
        for i in range(max_len, 0, -1):
            if self.url[-i:] == img_url[:i]:
                return self.url[-i:]
        return ""

    @staticmethod
    def _extract_image_src(picture_tag, html_type: str) -> str:
        if html_type == "picture_tag":
            source_tag = picture_tag.find("source")
            if source_tag and source_tag.get("srcset"):
                return source_tag.get("srcset").split(" ")[0]
        else:
            return picture_tag.get("src")

    def _extract_text_from_images_in_html(self, soup_obj: BeautifulSoup) -> str:
        res = []
        img_tags = soup_obj.find_all("img")
        picture_tags = soup_obj.find_all("picture")
        combined_tags = chain(
            zip(picture_tags, ["picture_tag"] * len(picture_tags)),
            zip(img_tags, ["image_tag"] * len(img_tags)),
        )
        for i, (tag, html_type) in enumerate(combined_tags):
            src = self._extract_image_src(tag, html_type)

            if not src:
                continue

            try:
                text = self.extract_text_from_image(image_src=src)
                res.append(text)
            except Exception as e:
                logger.info(f"Failed to process image {i} ({src}): {e}")
        return "".join(res)

    @staticmethod
    def _extract_article_content_from_markdown(markdown: str) -> str:
        # Regex to match the title and everything after it, TODO: improve method (?)
        pattern = r"(# .*)"
        match = re.search(pattern, markdown, re.DOTALL)
        if match:
            return match.group(1)
        return markdown

    def _manually_fetch_blog_html_content(self) -> str:
        response = requests.get(self.url, headers=self.headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Remove common irrelevant elements
        for element in soup(["script", "style", "footer", "header", "nav"]):
            element.extract()

        # Remove elements with certain classes or IDs
        for element in soup(
            ["div", "span"],
            {"class": ["sidebar", "widget", "advertisement", "comments"]},
        ):
            element.extract()

        # Extract the remaining text content
        return soup.get_text(strip=True)

    def _extract_textual_content_with_docling(
        self, result_queue: multiprocessing.Queue
    ):
        logger.info("Attempting to extract HTML data using docling")
        try:
            conversion_result = self.converter.convert(source=self.url)
            markdown = conversion_result.document.export_to_markdown(
                image_placeholder=""
            )
            if markdown:
                result_queue.put(self._extract_article_content_from_markdown(markdown))
                return
        except docling.exceptions.ConversionError:
            logger.warning("Failed to extract blog content using docling")
        result_queue.put(None)

    def _fetch_ocr_data_with_beautifulsoup(self) -> Optional[str]:
        logger.info("Attempting to extract text from images using BeautifulSoup")
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            image_text_str = self._extract_text_from_images_in_html(soup)
            return image_text_str.strip()
        except Exception as e:
            logger.warning(
                f"Failed to extract text from images using BeautifulSoup: {e}"
            )
            return None

    def _extract_textual_content_with_beautifulsoup(self) -> Optional[str]:
        logger.info("Attempting to extract HTML data using BeautifulSoup")
        try:
            content = self._manually_fetch_blog_html_content()
            return content if content else None
        except Exception as e:
            logger.warning(f"Failed to extract blog content using BeautifulSoup: {e}")
        return None

    def get_textual_content(self) -> Optional[str]:
        use_multi_proccesing = True
        if use_multi_proccesing:
            result_queue = multiprocessing.Queue(maxsize=1)
            process = multiprocessing.Process(
                target=self._extract_textual_content_with_docling, args=(result_queue,)
            )
            process.start()
            process.join(timeout=60)

            if process.is_alive():
                logger.warning(
                    "Docling extraction is taking too long, falling back to BeautifulSoup"
                )
                process.terminate()
                process.join()

            content = result_queue.get() if not result_queue.empty() else None
        else:
            content = None
        if content is None:
            content = self._extract_textual_content_with_beautifulsoup()
        if self.use_ocr:
            ocr_text = self._fetch_ocr_data_with_beautifulsoup()
            content = content + ocr_text if content else ocr_text
        if content:
            return content

        logger.error("Failed to extract blog content")
