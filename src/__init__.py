"""
Web Scraper Package
Herramientas modulares para web scraping con configuración flexible
"""

__version__ = "0.0.1"
__author__ = "miguel1man"
__description__ = "Web Scraper modular con configuración JSON"

from .scraper import WebScraper
from .url_reader import URLReader
from .utils import FileManager, Logger, DataProcessor, ConfigGenerator

__all__ = [
    'WebScraper',
    'URLReader', 
    'FileManager',
    'Logger',
    'DataProcessor',
    'ConfigGenerator'
]
