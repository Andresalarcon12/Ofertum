# Documentación de la API REST de Ofertum

## Descripción General

Ofertum provee una API REST en formato JSON que permite a otros equipos consumir información de productos en stock. La API incluye filtros avanzados, paginación y enlaces directos a cada producto.

## Base URL

```
http://tu-dominio.com/api/
```

## Endpoints Disponibles

### 1. Lista de Productos

**Endpoint:** `GET /api/products/`

**Descripción:** Retorna la lista completa de productos disponibles con toda su información, incluyendo precios actuales (con ofertas aplicadas) y enlaces directos.

**Parámetros de consulta (Query Parameters):**

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `q` | string | Búsqueda de texto en nombre y descripción | `?q=laptop` |
| `category` | string | Filtrar por categoría específica | `?category=Electrónica` |
| `store` | string | Filtrar por tienda | `?store=Amazon` |
| `min` | decimal | Precio mínimo (sobre precio actual con ofertas) | `?min=50.00` |
| `max` | decimal | Precio máximo (sobre precio actual con ofertas) | `?max=500.00` |
| `disponibles` | boolean | Filtrar solo disponibles (por defecto true) | `?disponibles=false` |

**Ejemplo de solicitud:**

```http
GET /api/products/?category=Electrónica&min=100&max=1000
```

**Respuesta exitosa (200 OK):**

```json
{
  "total": 2,
  "productos": [
    {
      "id": 1,
      "nombre": "Laptop HP 15",
      "descripcion": "Laptop con procesador Intel Core i5",
      "categoria": "Electrónica",
      "tienda": "Amazon",
      "link": "https://amazon.com/product/123",
      "precio_base": 850.00,
      "precio_actual": 680.00,
      "oferta": {
        "descuento_porcentaje": 20.0,
        "precio_fijo": null,
        "activo": true
      },
      "imagen_url": "http://tu-dominio.com/media/productos/laptop.jpg",
      "disponible": true,
      "creado": "2025-01-15T10:30:00Z",
      "detail_url": "http://tu-dominio.com/products/1/"
    },
    {
      "id": 2,
      "nombre": "Mouse Logitech MX Master 3",
      "descripcion": "Mouse inalámbrico ergonómico",
      "categoria": "Electrónica",
      "tienda": "BestBuy",
      "link": "",
      "precio_base": 99.99,
      "precio_actual": 99.99,
      "oferta": null,
      "imagen_url": "http://tu-dominio.com/media/productos/mouse.jpg",
      "disponible": true,
      "creado": "2025-01-20T14:15:00Z",
      "detail_url": "http://tu-dominio.com/products/2/"
    }
  ]
}
```

### 2. Detalle de Producto

**Endpoint:** `GET /api/products/<id>/`

**Descripción:** Retorna la información detallada de un producto específico.

**Parámetros de ruta:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `id` | integer | ID del producto |

**Ejemplo de solicitud:**

```http
GET /api/products/1/
```

**Respuesta exitosa (200 OK):**

```json
{
  "id": 1,
  "nombre": "Laptop HP 15",
  "descripcion": "Laptop con procesador Intel Core i5, 8GB RAM, 256GB SSD",
  "categoria": "Electrónica",
  "tienda": "Amazon",
  "link": "https://amazon.com/product/123",
  "precio_base": 850.00,
  "precio_actual": 680.00,
  "oferta": {
    "descuento_porcentaje": 20.0,
    "precio_fijo": null,
    "activo": true
  },
  "imagen_url": "http://tu-dominio.com/media/productos/laptop.jpg",
  "disponible": true,
  "creado": "2025-01-15T10:30:00Z",
  "detail_url": "http://tu-dominio.com/products/1/"
}
```

**Respuesta de error (404 Not Found):**

```json
{
  "error": "Producto no encontrado",
  "detail": "No existe un producto disponible con id 999"
}
```

## Estructura de Datos

### Objeto Producto

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | Identificador único del producto |
| `nombre` | string | Nombre del producto |
| `descripcion` | string | Descripción detallada |
| `categoria` | string | Categoría del producto |
| `tienda` | string | Tienda donde se vende |
| `link` | string | Enlace externo al producto (puede estar vacío) |
| `precio_base` | float | Precio original sin ofertas |
| `precio_actual` | float | Precio vigente (con oferta aplicada si existe) |
| `oferta` | object\|null | Información de la oferta activa o null |
| `imagen_url` | string\|null | URL absoluta de la imagen del producto |
| `disponible` | boolean | Indica si el producto está disponible |
| `creado` | string | Fecha de creación en formato ISO 8601 |
| `detail_url` | string | URL absoluta para ver el detalle del producto |

### Objeto Oferta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `descuento_porcentaje` | float | Porcentaje de descuento aplicado |
| `precio_fijo` | float\|null | Precio fijo de oferta (reemplaza al descuento si está definido) |
| `activo` | boolean | Indica si la oferta está activa |

## Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | Solicitud exitosa |
| 404 | Recurso no encontrado |
| 500 | Error interno del servidor |

## Ejemplos de Consumo

### Python con requests

```python
import requests

# Obtener todos los productos de electrónica con precio entre 100 y 500
response = requests.get(
    'http://tu-dominio.com/api/products/',
    params={
        'category': 'Electrónica',
        'min': 100,
        'max': 500
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"Total de productos: {data['total']}")
    
    for producto in data['productos']:
        print(f"{producto['nombre']} - ${producto['precio_actual']}")
        print(f"Ver más: {producto['detail_url']}")
```

### JavaScript/Fetch

```javascript
// Obtener producto específico
fetch('http://tu-dominio.com/api/products/1/')
  .then(response => response.json())
  .then(data => {
    console.log(`Producto: ${data.nombre}`);
    console.log(`Precio: $${data.precio_actual}`);
    if (data.oferta) {
      console.log(`Descuento: ${data.oferta.descuento_porcentaje}%`);
    }
  })
  .catch(error => console.error('Error:', error));
```

### jQuery

```javascript
$.ajax({
  url: 'http://tu-dominio.com/api/products/',
  data: {
    q: 'laptop',
    min: 500
  },
  success: function(data) {
    console.log(`Encontrados ${data.total} productos`);
    data.productos.forEach(function(producto) {
      $('#productos-lista').append(
        `<div class="producto">
          <h3>${producto.nombre}</h3>
          <p>${producto.descripcion}</p>
          <p class="precio">$${producto.precio_actual}</p>
          <a href="${producto.detail_url}">Ver detalle</a>
        </div>`
      );
    });
  }
});
```

## Notas Importantes

1. **Precios con Ofertas**: El campo `precio_actual` siempre refleja el precio vigente del producto, incluyendo cualquier oferta activa. Si quieres mostrar el precio original, usa `precio_base`.

2. **URLs Absolutas**: Todos los campos `detail_url` e `imagen_url` retornan URLs absolutas que pueden ser usadas directamente en aplicaciones externas.

3. **Filtros Combinables**: Todos los parámetros de consulta pueden combinarse para hacer búsquedas más específicas.

4. **Productos Disponibles**: Por defecto, la API solo retorna productos con `disponible=True`. Usa `?disponibles=false` para obtener todos los productos.

5. **Formato de Respuesta**: Todas las respuestas están en formato JSON con codificación UTF-8, por lo que los caracteres especiales se manejan correctamente.

## Consumo Recomendado para Otros Equipos

Para mostrar productos aliados en tu aplicación:

1. Crea una nueva ruta en tu aplicación (ej: `/productos-aliados`)
2. Consume la API de Ofertum desde tu controlador
3. Transforma los datos según tu modelo de datos
4. Renderiza en una vista con diseño similar al resto de tu aplicación

Ejemplo de vista en Django:

```python
import requests
from django.shortcuts import render

def productos_aliados(request):
    try:
        response = requests.get(
            'http://tu-dominio.com/api/products/',
            params={'disponibles': 'true'},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        productos = data.get('productos', [])
    except Exception as e:
        productos = []
        print(f"Error al consumir API: {e}")
    
    return render(request, 'productos_aliados.html', {
        'productos': productos
    })
```

## Soporte

Para preguntas o problemas con la API, contactar al equipo de desarrollo de Ofertum.
