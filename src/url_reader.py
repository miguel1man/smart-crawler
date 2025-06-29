# src/url_reader.py
"""
URL Reader Module
Maneja la lectura y validación de URLs desde archivos de texto
"""

from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse


class URLReader:
    """Clase para leer y validar URLs desde archivos de texto"""
    
    def __init__(self, file_path: Path):
        """
        Inicializar el lector de URLs
        
        Args:
            file_path (Path): Ruta al archivo de URLs
        """
        self.file_path = Path(file_path)
        self.urls: List[str] = []
    
    def load_urls(self) -> List[str]:
        """
        Cargar URLs desde el archivo de texto
        
        Returns:
            List[str]: Lista de URLs válidas
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {self.file_path}")
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # Procesar cada línea
            raw_urls = []
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Ignorar líneas vacías y comentarios
                if not line or line.startswith('#'):
                    continue
                    
                raw_urls.append((line_num, line))
            
            # Validar URLs
            valid_urls = []
            for line_num, url in raw_urls:
                if self._is_valid_url(url):
                    valid_urls.append(url)
                else:
                    print(f"Advertencia: URL inválida en línea {line_num}: {url}")
            
            self.urls = valid_urls
            return self.urls
            
        except Exception as e:
            raise Exception(f"Error leyendo archivo de URLs: {str(e)}")
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Validar si una URL es válida
        
        Args:
            url (str): URL a validar
            
        Returns:
            bool: True si la URL es válida
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def add_url(self, url: str) -> bool:
        """
        Agregar una URL a la lista (validándola primero)
        
        Args:
            url (str): URL a agregar
            
        Returns:
            bool: True si se agregó exitosamente
        """
        if self._is_valid_url(url):
            if url not in self.urls:
                self.urls.append(url)
                return True
        return False
    
    def save_urls(self, output_path: Optional[Path] = None) -> bool:
        """
        Guardar las URLs actuales en un archivo
        
        Args:
            output_path (Path, optional): Ruta de salida. Si no se proporciona, 
                                        se usa la ruta original
            
        Returns:
            bool: True si se guardó exitosamente
        """
        save_path = output_path or self.file_path
        
        try:
            with open(save_path, 'w', encoding='utf-8') as file:
                file.write("# URLs para scraping\n")
                file.write("# Una URL por línea\n")
                file.write("# Las líneas que empiecen con # son ignoradas\n\n")
                
                for url in self.urls:
                    file.write(f"{url}\n")
            
            return True
            
        except Exception as e:
            print(f"Error guardando URLs: {str(e)}")
            return False
    
    def get_domain_stats(self) -> dict:
        """
        Obtener estadísticas de dominios en las URLs cargadas
        
        Returns:
            dict: Estadísticas por dominio
        """
        domain_count = {}
        
        for url in self.urls:
            try:
                domain = urlparse(url).netloc
                domain_count[domain] = domain_count.get(domain, 0) + 1
            except Exception:
                continue
        
        return domain_count
    
    def filter_by_domain(self, domain: str) -> List[str]:
        """
        Filtrar URLs por dominio específico
        
        Args:
            domain (str): Dominio a filtrar
            
        Returns:
            List[str]: URLs que pertenecen al dominio especificado
        """
        filtered_urls = []
        
        for url in self.urls:
            try:
                url_domain = urlparse(url).netloc
                if domain.lower() in url_domain.lower():
                    filtered_urls.append(url)
            except Exception:
                continue
        
        return filtered_urls
    
    def __len__(self) -> int:
        """Retornar número de URLs cargadas"""
        return len(self.urls)
    
    def __str__(self) -> str:
        """Representación string del objeto"""
        return f"URLReader: {len(self.urls)} URLs cargadas desde {self.file_path}"
    