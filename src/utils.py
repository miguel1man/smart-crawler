# src/utils.py
"""
Utilities Module
Funciones de utilidad para el web scraper
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class FileManager:
    """Manejo de archivos y operaciones de E/S"""
    
    @staticmethod
    def save_to_json(data: List[Dict[str, Any]], file_path: Path, indent: int = 2) -> bool:
        """
        Guardar datos en archivo JSON
        
        Args:
            data (List[Dict[str, Any]]): Datos a guardar
            file_path (Path): Ruta del archivo
            indent (int): Indentación para el JSON
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            # Crear directorio padre si no existe
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=indent)
            
            return True
            
        except Exception as e:
            print(f"Error guardando archivo JSON: {str(e)}")
            return False
    
    @staticmethod
    def load_from_json(file_path: Path) -> Optional[List[Dict[str, Any]]]:
        """
        Cargar datos desde archivo JSON
        
        Args:
            file_path (Path): Ruta del archivo
            
        Returns:
            Optional[List[Dict[str, Any]]]: Datos cargados o None si hay error
        """
        try:
            if not file_path.exists():
                return None
                
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
                
        except Exception as e:
            print(f"Error cargando archivo JSON: {str(e)}")
            return None
    
    @staticmethod
    def backup_file(file_path: Path, backup_suffix: str = "_backup") -> bool:
        """
        Crear respaldo de un archivo
        
        Args:
            file_path (Path): Archivo a respaldar
            backup_suffix (str): Sufijo para el archivo de respaldo
            
        Returns:
            bool: True si se creó el respaldo exitosamente
        """
        try:
            if not file_path.exists():
                return False
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}{backup_suffix}_{timestamp}{file_path.suffix}"
            backup_path = file_path.parent / backup_name
            
            # Copiar archivo
            import shutil
            shutil.copy2(file_path, backup_path)
            
            return True
            
        except Exception as e:
            print(f"Error creando respaldo: {str(e)}")
            return False


class Logger:
    """Clase para manejo de logging"""
    
    def __init__(self, name: str = "WebScraper", level: int = logging.INFO):
        """
        Inicializar logger
        
        Args:
            name (str): Nombre del logger
            level (int): Nivel de logging
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Evitar duplicar handlers
        if not self.logger.handlers:
            # Handler para consola
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            
            # Formato
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """Log mensaje de información"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log mensaje de advertencia"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log mensaje de error"""
        self.logger.error(message)
    
    def debug(self, message: str):
        """Log mensaje de debug"""
        self.logger.debug(message)


class DataProcessor:
    """Procesamiento y análisis de datos extraídos"""
    
    @staticmethod
    def clean_price(price_str: str) -> Optional[float]:
        """
        Limpiar y convertir string de precio a float
        
        Args:
            price_str (str): String del precio
            
        Returns:
            Optional[float]: Precio como float o None si no se puede convertir
        """
        if not price_str or price_str == "N/A":
            return None
        
        try:
            # Remover caracteres no numéricos excepto punto y coma
            import re
            cleaned = re.sub(r'[^\d.,]', '', price_str)
            
            # Manejar diferentes formatos de decimales
            if ',' in cleaned and '.' in cleaned:
                # Formato: 1,234.56
                cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                # Formato: 1234,56 (europeo)
                parts = cleaned.split(',')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    cleaned = cleaned.replace(',', '.')
                else:
                    # Formato: 1,234 (separador de miles)
                    cleaned = cleaned.replace(',', '')
            
            return float(cleaned)
            
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    def extract_brand_from_title(title: str, known_brands: List[str] = None) -> Optional[str]:
        """
        Extraer marca desde el título del producto
        
        Args:
            title (str): Título del producto
            known_brands (List[str]): Lista de marcas conocidas
            
        Returns:
            Optional[str]: Marca encontrada o None
        """
        if not title or title == "N/A":
            return None
        
        title_lower = title.lower()
        
        # Si se proporcionan marcas conocidas, buscar coincidencias
        if known_brands:
            for brand in known_brands:
                if brand.lower() in title_lower:
                    return brand
        
        # Intentar extraer primera palabra como marca
        words = title.split()
        if words:
            return words[0]
        
        return None
    
    @staticmethod
    def generate_product_stats(products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generar estadísticas de los productos extraídos
        
        Args:
            products (List[Dict[str, Any]]): Lista de productos
            
        Returns:
            Dict[str, Any]: Estadísticas generadas
        """
        if not products:
            return {"total_products": 0}
        
        stats = {
            "total_products": len(products),
            "fields_found": {},
            "brands": {},
            "sources": {},
            "extraction_time": datetime.now().isoformat()
        }
        
        # Analizar campos
        all_fields = set()
        for product in products:
            all_fields.update(product.keys())
        
        for field in all_fields:
            non_na_count = sum(1 for p in products if p.get(field, "N/A") != "N/A")
            stats["fields_found"][field] = {
                "total": len(products),
                "with_data": non_na_count,
                "completion_rate": round(non_na_count / len(products) * 100, 2)
            }
        
        # Analizar marcas (si existe campo Marca)
        if "Marca" in all_fields:
            brand_count = {}
            for product in products:
                brand = product.get("Marca", "N/A")
                if brand != "N/A":
                    brand_count[brand] = brand_count.get(brand, 0) + 1
            stats["brands"] = dict(sorted(brand_count.items(), key=lambda x: x[1], reverse=True))
        
        # Analizar fuentes (si existe campo _source_url)
        if "_source_url" in all_fields:
            source_count = {}
            for product in products:
                source = product.get("_source_url", "N/A")
                if source != "N/A":
                    source_count[source] = source_count.get(source, 0) + 1
            stats["sources"] = source_count
        
        return stats


class ConfigGenerator:
    """Generador de configuraciones para diferentes sitios web"""
    
    @staticmethod
    def create_base_config() -> Dict[str, Any]:
        """
        Crear configuración base como plantilla
        
        Returns:
            Dict[str, Any]: Configuración base
        """
        return {
            "site_name": "ejemplo.com",
            "container_class": "product-container",
            "fields": {
                "titulo": {
                    "path": [
                        {"type": "find", "tag": "h3", "class": "product-title"}
                    ],
                    "extract": "text"
                },
                "precio": {
                    "path": [
                        {"type": "find", "tag": "span", "class": "price"}
                    ],
                    "extract": "text"
                },
                "enlace": {
                    "path": [
                        {"type": "find", "tag": "a"}
                    ],
                    "extract": "href"
                }
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "description": "Configuración base para scraping",
                "version": "1.0"
            }
        }
    
    @staticmethod
    def save_config_template(output_path: Path) -> bool:
        """
        Guardar plantilla de configuración
        
        Args:
            output_path (Path): Ruta donde guardar la plantilla
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            config = ConfigGenerator.create_base_config()
            
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(config, file, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error guardando plantilla de configuración: {str(e)}")
            return False


class URLManager:
    """Utilidades para manejo de URLs"""
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalizar URL (agregar protocolo si falta, etc.)
        
        Args:
            url (str): URL a normalizar
            
        Returns:
            str: URL normalizada
        """
        url = url.strip()
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """
        Extraer dominio de una URL
        
        Args:
            url (str): URL
            
        Returns:
            Optional[str]: Dominio extraído
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return None
    
    @staticmethod
    def is_same_domain(url1: str, url2: str) -> bool:
        """
        Verificar si dos URLs pertenecen al mismo dominio
        
        Args:
            url1 (str): Primera URL
            url2 (str): Segunda URL
            
        Returns:
            bool: True si son del mismo dominio
        """
        domain1 = URLManager.extract_domain(url1)
        domain2 = URLManager.extract_domain(url2)
        
        return domain1 and domain2 and domain1 == domain2


def generate_timestamp_filename(base_name: str, extension: str = "json") -> str:
    """
    Generar nombre de archivo con timestamp
    
    Args:
        base_name (str): Nombre base del archivo
        extension (str): Extensión del archivo
        
    Returns:
        str: Nombre de archivo con timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"


def validate_file_path(file_path: Path, must_exist: bool = True) -> bool:
    """
    Validar ruta de archivo
    
    Args:
        file_path (Path): Ruta a validar
        must_exist (bool): Si el archivo debe existir
        
    Returns:
        bool: True si la ruta es válida
    """
    try:
        if must_exist:
            return file_path.exists() and file_path.is_file()
        else:
            # Verificar que el directorio padre exista o se pueda crear
            parent_dir = file_path.parent
            return parent_dir.exists() or parent_dir.parent.exists()
    except Exception:
        return False
