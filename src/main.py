"""
Web Scraper - Punto de entrada principal
Orquesta el proceso completo de scraping
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Agregar src al path para importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from url_reader import URLReader
from scraper import WebScraper
from utils import FileManager, Logger


def main():
    """Función principal que orquesta todo el proceso"""
    
    # Configurar paths
    base_dir = Path(__file__).parent.parent
    configs_dir = base_dir / "configs"
    output_dir = base_dir / "output"
    
    # Crear directorio de salida principal si no existe
    output_dir.mkdir(exist_ok=True)
    
    # Inicializar logger
    logger = Logger()
    logger.info("Iniciando proceso de scraping...")
    
    try:
        # 1. Leer configuración
        config_file = configs_dir / "config_01.json"
        urls_file = configs_dir / "urls.txt"
        
        if not config_file.exists():
            logger.error(f"Archivo de configuración no encontrado: {config_file}")
            return False
            
        if not urls_file.exists():
            logger.error(f"Archivo de URLs no encontrado: {urls_file}")
            return False
        
        # Cargar el JSON completo
        with open(config_file, 'r', encoding='utf-8') as f:
            full_config = json.load(f)

        # Separar las configuraciones
        scraper_config = full_config.get("scraper_settings")
        export_config = full_config.get("export_settings")
        site_name = full_config.get("site_name", "default_site")

        if not scraper_config or not export_config:
            logger.error("El archivo de configuración no tiene 'scraper_settings' o 'export_settings'.")
            return False
        
        # 2. Cargar URLs
        url_reader = URLReader(urls_file)
        urls = url_reader.load_urls()
        
        if not urls:
            logger.warning("No se encontraron URLs válidas para procesar")
            return False
            
        logger.info(f"Se encontraron {len(urls)} URLs para procesar")
        
        # 3. Inicializar scraper
        scraper = WebScraper(scraper_config)
        
        # 4. Procesar cada URL
        all_products = []
        successful_scrapes = 0
        
        for i, url in enumerate(urls, 1):
            logger.info(f"Procesando URL {i}/{len(urls)}: {url}")
            
            try:
                products = scraper.scrape_products(url)
                if products:
                    all_products.extend(products)
                    successful_scrapes += 1
                    logger.info(f"Extraídos {len(products)} productos de la URL {i}")
                else:
                    logger.warning(f"No se encontraron productos en la URL {i}")
                    
            except Exception as e:
                logger.error(f"Error procesando URL {i}: {str(e)}")
                continue
        
        # 5. Guardar resultados
        if all_products:
            # El directorio de salida se construye a partir de la base y el subdirectorio del config
            # Si "directory" está vacío, final_output_dir será igual a output_dir
            subdir_from_config = export_config.get("directory", "")
            final_output_dir = output_dir / subdir_from_config
            
            # Asegurarse de que el directorio final exista
            final_output_dir.mkdir(parents=True, exist_ok=True)

            # Formatear el nombre del archivo usando la plantilla del config
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = export_config["filename_template"].format(
                site_name=site_name,
                timestamp=timestamp,
                format=export_config["format"]
            )
            
            output_path = final_output_dir / filename
            
            file_manager = FileManager()
            
            # Guardar según el formato especificado
            if export_config.get("format") == "json":
                success = file_manager.save_to_json(all_products, output_path)
            else:
                logger.error(f"Formato de exportación no soportado: {export_config.get('format')}")
                return False

            if success:
                logger.info("Proceso completado exitosamente!")
                logger.info(f"Total de productos extraídos: {len(all_products)}")
                logger.info(f"Archivo guardado en: {output_path}")
                return True
            else:
                logger.error("Error al guardar el archivo de resultados")
                return False
        else:
            logger.warning("No se extrajeron productos de ninguna URL")
            return False
            
    except Exception as e:
        logger.error(f"Error general en el proceso: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)