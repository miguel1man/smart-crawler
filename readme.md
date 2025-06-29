# Web Scraper

## Instalación

1. **Clonar proyecto**

```bash
cd web_scraper_project/
```

2. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

## Configuración

### 1. URLs (configs/urls.txt)

Agregar las URLs a procesar, una por línea:

```text
https://...
https://...
```

### 2. Configuración de Scraping (configs/compy_config.json)

Definir qué elementos HTML extraer:

```json
{
  "container_class": "card__container",
  "fields": {
    "Marca": {
      "path": [
        { "type": "find", "tag": "header" },
        { "type": "find", "tag": "h6" }
      ],
      "extract": "text"
    }
  }
}
```

## Uso

### Ejecución básica

```bash
python src/main.py
```

## Salida

Los resultados se guardan automáticamente en la carpeta `output/` con el formato:

```
name_YYYYMMDD_HHMMSS.json
```

## Personalización

### Para otros sitios web:

1. **Crear nueva configuración JSON**:

```json
{
  "site_name": "web.com",
  "container_class": "producto-contenedor",
  "fields": {
    "titulo": {
      "path": [{ "type": "find", "tag": "h2", "class": "titulo-producto" }],
      "extract": "text"
    }
  }
}
```

2. **Actualizar URLs**: Modificar `configs/urls.txt`

3. **Ejecutar**: El sistema usará automáticamente la nueva configuración

### Configuración avanzada de campos:

```json
{
  "campo_ejemplo": {
    "path": [
      { "type": "find", "tag": "div", "class": "contenedor" },
      { "type": "find_all", "tag": "span", "index": 0 },
      { "type": "find", "tag": "a" }
    ],
    "extract": "href"
  }
}
```

**Tipos de path**:

- `find`: Buscar primer elemento que coincida
- `find_all`: Buscar todos, usar índice específico

**Tipos de extract**:

- `text`: Texto del elemento
- `href`: Atributo href (para enlaces)
- `src`: Atributo src (para imágenes)
- Cualquier atributo HTML

## Funciones Avanzadas

### Probar configuración

```python
from src.scraper import WebScraper
from pathlib import Path

scraper = WebScraper(Path("configs/config.json"))
result = scraper.test_config_on_url("https://ejemplo.com", max_products=3)
print(result)
```

### Validar configuración

```python
validation = scraper.validate_config()
print(validation)
```

### Estadísticas de extracción

```python
from src.utils import DataProcessor

stats = DataProcessor.generate_product_stats(productos)
print(stats)
```
