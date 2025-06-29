"""
Web Scraper Module
Contiene la lógica principal de scraping usando BeautifulSoup
"""

import json
import time
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urljoin


class WebScraper:
    """Clase principal para realizar web scraping"""

    def __init__(self, config: Dict[str, Any], delay: float = 1.0):
        """
        Inicializar el web scraper

        Args:
            config (Dict[str, Any]): Diccionario con la configuración del scraper.
            delay (float): Delay entre requests en segundos.
        """
        self.config = self._validate_config(config)
        self.delay = delay
        self.session = self._setup_session()

    def _load_config(self) -> Dict[str, Any]:
        """
        Cargar configuración desde archivo JSON

        Returns:
            Dict[str, Any]: Configuración cargada
        """
        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                config = json.load(file)

            # Validar configuración básica
            required_keys = ["container_class", "fields"]
            for key in required_keys:
                if key not in config:
                    raise ValueError(
                        f"Clave requerida '{key}' no encontrada en configuración"
                    )

            return config

        except Exception as e:
            raise Exception(f"Error cargando configuración: {str(e)}")

    def _setup_session(self) -> requests.Session:
        """
        Configurar sesión de requests con reintentos y headers

        Returns:
            requests.Session: Sesión configurada
        """
        session = requests.Session()

        # Configurar reintentos
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Headers por defecto
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

        return session

    def scrape_products(self, url: str) -> List[Dict[str, Any]]:
        """
        Realizar scraping de productos desde una URL
        """
        try:
            if hasattr(self, "_last_request_time"):
                elapsed = time.time() - self._last_request_time
                if elapsed < self.delay:
                    time.sleep(self.delay - elapsed)

            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            self._last_request_time = time.time()

            soup = BeautifulSoup(response.content, "html.parser")

            # Pasamos la URL base al método de extracción
            products = self._extract_products(soup, base_url=url)

            # Agregar metadata
            for product in products:
                product["_source_url"] = url
                product["_scraped_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                product["_config_used"] = (
                    self.config["name"] if "name" in self.config else "default_config"
                )

            return products

        except requests.RequestException as e:
            raise Exception(f"Error en request HTTP: {str(e)}")
        except Exception as e:
            raise Exception(f"Error general en scraping: {str(e)}")

    def _extract_products(
        self, soup: BeautifulSoup, base_url: str
    ) -> List[Dict[str, Any]]:
        """
        Extraer productos del HTML usando la configuración
        """
        products = []
        container_class = self.config.get("container_class")
        containers = soup.find_all("div", class_=container_class)

        if not containers:
            return products

        for container in containers:
            product = {}
            for field_name, field_config in self.config["fields"].items():
                try:
                    # Pasamos la URL base al método que extrae el valor final
                    value = self._extract_field_value(container, field_config, base_url)
                    product[field_name] = value
                except Exception as e:
                    product[field_name] = "N/A"
                    print(
                        f"Advertencia: Error extrayendo campo '{field_name}': {str(e)}"
                    )

            if any(value != "N/A" for value in product.values()):
                products.append(product)

        return products

    def _extract_field_value(
        self, container: BeautifulSoup, field_config: Dict[str, Any], base_url: str
    ) -> str:
        """
        Extraer valor de un campo específico y convertir enlaces relativos.
        """
        element = container

        for step in field_config.get("path", []):
            if not element:
                break
            step_type = step.get("type")
            tag = step.get("tag")
            class_name = step.get("class")
            if step_type == "find":
                element = (
                    element.find(tag, class_=class_name)
                    if class_name
                    else element.find(tag)
                )
            elif step_type == "find_all":
                elements = (
                    element.find_all(tag, class_=class_name)
                    if class_name
                    else element.find_all(tag)
                )
                index = step.get("index", 0)
                element = (
                    elements[index] if elements and len(elements) > index else None
                )

        if not element:
            return "N/A"

        extract_type = field_config.get("extract", "text")

        if extract_type == "text":
            return element.get_text(strip=True)

        elif extract_type == "href":
            relative_link = element.get("href")
            if relative_link:
                # Usamos urljoin para combinar la URL base con el enlace relativo
                # urljoin es inteligente: si relative_link ya es absoluto, no hace nada.
                return urljoin(base_url, relative_link)
            else:
                return "N/A"
        else:
            attr_value = element.get(extract_type)
            return attr_value if attr_value else "N/A"

    def test_config_on_url(self, url: str, max_products: int = 3) -> Dict[str, Any]:
        """
        Probar la configuración en una URL y mostrar resultados limitados

        Args:
            url (str): URL para probar
            max_products (int): Máximo número de productos a mostrar

        Returns:
            Dict[str, Any]: Resultados de la prueba
        """
        try:
            products = self.scrape_products(url)

            return {
                "success": True,
                "total_products": len(products),
                "sample_products": products[:max_products],
                "url": url,
                "config_used": self.config_path.name,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "config_used": self.config_path.name,
            }

    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar el diccionario de configuración del scraper.
        """
        required_keys = ["container_class", "fields"]
        for key in required_keys:
            if key not in config:
                raise ValueError(
                    f"Clave requerida '{key}' no encontrada en la configuración del scraper"
                )
        return config
