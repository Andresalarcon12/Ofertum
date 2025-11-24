# Integración de APIs Externas - Ofertum

## 📋 Resumen

Este documento describe las integraciones de APIs externas implementadas en el proyecto Ofertum, incluyendo la API de socios aliados y recomendaciones de APIs públicas para futuras integraciones.

---

## 🔗 API de Socios Aliados (Implementada)

### Endpoint Integrado
- **URL**: `http://13.218.169.6/api/productos/`
- **Método**: GET
- **Formato**: JSON
- **Estado**: ✅ Implementada y funcional

### Estructura de Respuesta

```json
[
  {
    "idProducto": 5,
    "nombreProducto": "Buzo Crewneck Azul",
    "tipoProducto": "buzo",
    "marcaProducto": "Azul Oscuro",
    "cantidadDeProducto": 40,
    "fechaVencimientoProducto": null,
    "precioDeProducto": 80000.0,
    "imagenProducto": "/media/productos/CrewneckBuzoAzul-HansSachsHNS-02_1000x.webp"
  }
]
```

### Mapeo de Campos

| Campo API Externa | Campo Ofertum | Descripción |
|-------------------|---------------|-------------|
| `idProducto` | `id` | Identificador único del producto |
| `nombreProducto` | `name` | Nombre del producto |
| `tipoProducto` | `category` | Tipo/categoría del producto |
| `marcaProducto` | `store` | Marca/tienda del producto |
| `precioDeProducto` | `price` | Precio del producto |
| `imagenProducto` | `image` | Ruta de la imagen (se convierte a URL completa) |

### Características Implementadas

1. **Vista dedicada**: `/partner-products/`
2. **Botón en navbar**: "Páginas Aliadas" con icono de enlace
3. **Filtros compatibles**: 
   - Búsqueda por texto (nombre/descripción)
   - Categoría
   - Tienda/Marca
   - Rango de precios
   - Ordenamiento (nombre, precio asc/desc)
4. **Paginación**: 9 productos por página
5. **Manejo de errores**: Mensajes descriptivos para timeout, conexión, etc.
6. **Estilo consistente**: Mismos colores y diseño que productos locales

### Acceso

- **URL Frontend**: `http://localhost:8000/partner-products/`
- **Ubicación en navbar**: Menú principal → "Páginas Aliadas"

---

## 🌐 APIs Externas Recomendadas

### 1. **Fake Store API** (Recomendada para Desarrollo/Testing)

**URL Base**: `https://fakestoreapi.com`

#### Ventajas
- ✅ Gratuita y sin autenticación
- ✅ Datos realistas de productos
- ✅ Respuestas rápidas y confiables
- ✅ Ideal para demos y pruebas
- ✅ Documentación excelente

#### Endpoints Útiles

```
GET https://fakestoreapi.com/products
GET https://fakestoreapi.com/products/{id}
GET https://fakestoreapi.com/products/categories
GET https://fakestoreapi.com/products/category/{categoryName}
```

#### Estructura de Respuesta

```json
{
  "id": 1,
  "title": "Fjallraven - Foldsack No. 1 Backpack",
  "price": 109.95,
  "description": "Your perfect pack for everyday use...",
  "category": "men's clothing",
  "image": "https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg",
  "rating": {
    "rate": 3.9,
    "count": 120
  }
}
```

#### Ejemplo de Integración

```python
def fake_store_products(request):
    api_url = "https://fakestoreapi.com/products"
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        productos = response.json()
        
        items = []
        for p in productos:
            items.append({
                "id": p['id'],
                "name": p['title'],
                "description": p['description'],
                "price": Decimal(str(p['price'])),
                "category": p['category'],
                "store": "Fake Store",
                "image": p['image'],
                "link": f"https://fakestoreapi.com/products/{p['id']}",
                "avg_rating": p['rating']['rate'],
                "rating_count": p['rating']['count'],
            })
        
        # ... paginación y renderizado ...
        
    except Exception as e:
        # Manejo de errores
        pass
```

---

### 2. **DummyJSON API** (Alternativa Robusta)

**URL Base**: `https://dummyjson.com`

#### Ventajas
- ✅ Más de 100 productos con datos completos
- ✅ Soporte de filtros, ordenamiento y paginación
- ✅ Imágenes de alta calidad
- ✅ Ratings y reviews incluidos
- ✅ Sin límite de requests

#### Endpoints Útiles

```
GET https://dummyjson.com/products
GET https://dummyjson.com/products/{id}
GET https://dummyjson.com/products/search?q={query}
GET https://dummyjson.com/products/category/{category}
GET https://dummyjson.com/products/categories
```

#### Estructura de Respuesta

```json
{
  "products": [
    {
      "id": 1,
      "title": "iPhone 9",
      "description": "An apple mobile which is nothing like apple",
      "price": 549,
      "discountPercentage": 12.96,
      "rating": 4.69,
      "stock": 94,
      "brand": "Apple",
      "category": "smartphones",
      "thumbnail": "https://dummyjson.com/image/i/products/1/thumbnail.jpg",
      "images": ["https://dummyjson.com/image/i/products/1/1.jpg"]
    }
  ],
  "total": 100,
  "skip": 0,
  "limit": 30
}
```

---

### 3. **Best Buy API** (Para Producción Real)

**URL Base**: `https://api.bestbuy.com/v1`

#### Ventajas
- ✅ Productos reales de tienda importante
- ✅ Precios actualizados en tiempo real
- ✅ Gran cantidad de categorías
- ✅ Datos de disponibilidad en tiendas

#### Consideraciones
- ⚠️ Requiere API Key (registro gratuito)
- ⚠️ Límite de 50,000 requests/día (tier gratuito)
- 📝 Documentación: https://developer.bestbuy.com/

#### Ejemplo de Uso

```python
def bestbuy_products(request):
    api_key = "TU_API_KEY_AQUI"
    api_url = f"https://api.bestbuy.com/v1/products(search={search_term})"
    
    params = {
        'apiKey': api_key,
        'format': 'json',
        'show': 'sku,name,salePrice,regularPrice,image,categoryPath.name',
        'pageSize': 20
    }
    
    response = requests.get(api_url, params=params, timeout=10)
    # ... procesamiento ...
```

---

### 4. **eBay Browse API** (Marketplace Global)

**URL Base**: `https://api.ebay.com/buy/browse/v1`

#### Ventajas
- ✅ Millones de productos disponibles
- ✅ Precios competitivos y ofertas
- ✅ Datos de vendedores y ratings
- ✅ Cobertura internacional

#### Consideraciones
- ⚠️ Requiere OAuth 2.0
- ⚠️ Proceso de registro y aprobación
- ⚠️ Complejidad mayor de implementación
- 📝 Documentación: https://developer.ebay.com/

---

### 5. **Open Food Facts API** (Productos Alimenticios)

**URL Base**: `https://world.openfoodfacts.org/api/v2`

#### Ventajas
- ✅ Base de datos colaborativa de alimentos
- ✅ Gratuita y open source
- ✅ Información nutricional detallada
- ✅ Imágenes de productos

#### Ejemplo de Endpoint

```
GET https://world.openfoodfacts.org/api/v2/search?categories_tags=beverages&page_size=20
```

---

## 🎯 Recomendación Principal

### **Para Desarrollo y Demo**: Fake Store API
- Implementación inmediata sin configuración
- Datos realistas y consistentes
- Perfecto para presentaciones y pruebas

### **Para Producción**: DummyJSON API + Best Buy API
- DummyJSON como fallback/demo
- Best Buy para productos reales (si se obtiene API key)
- Combinación que ofrece flexibilidad y datos reales

---

## 🛠️ Implementación Rápida de Fake Store API

### 1. Crear nueva vista en `views.py`

```python
def fakestore_products(request):
    """Vista para productos de Fake Store API"""
    api_url = "https://fakestoreapi.com/products"
    
    q = (request.GET.get("q") or "").strip()
    category = (request.GET.get("category") or "").strip()
    sort = (request.GET.get("sort") or "name").strip()
    page = request.GET.get("page", 1)
    
    items = []
    error_message = None
    
    try:
        # Construir URL con filtros
        if category:
            api_url = f"https://fakestoreapi.com/products/category/{category}"
        
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        productos = response.json()
        
        for p in productos:
            # Aplicar filtro de búsqueda
            if q and q.lower() not in p['title'].lower() and q.lower() not in p['description'].lower():
                continue
            
            items.append({
                "id": p['id'],
                "name": p['title'],
                "description": p['description'],
                "price": Decimal(str(p['price'])),
                "category": p['category'],
                "store": "Fake Store",
                "image": p['image'],
                "link": f"https://fakestoreapi.com/products/{p['id']}",
                "avg_rating": p['rating']['rate'],
                "rating_count": p['rating']['count'],
            })
    
    except Exception as e:
        error_message = f"Error al conectar con Fake Store API: {str(e)}"
    
    # Ordenamiento
    if sort == "price_asc":
        items.sort(key=lambda x: (x["price"], x["name"]))
    elif sort == "price_desc":
        items.sort(key=lambda x: (x["price"], x["name"]), reverse=True)
    elif sort == "rating":
        items.sort(key=lambda x: (-(x["avg_rating"] or 0), -x["rating_count"], x["name"]))
    else:
        items.sort(key=lambda x: x["name"])
    
    # Paginación
    paginator = Paginator(items, 9)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)
    
    qs_params = request.GET.copy()
    qs_params.pop('page', None)
    querystring = urlencode([(k, v) for k, v in qs_params.items() if v not in (None, "")])
    
    ctx = {
        "q": q,
        "category": category,
        "sort": sort,
        "page_obj": page_obj,
        "items": page_obj.object_list,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
        "querystring": querystring,
        "error_message": error_message,
        "is_external_api": True,
        "api_name": "Fake Store",
    }
    return render(request, "catalog/external_products.html", ctx)
```

### 2. Agregar ruta en `urls.py`

```python
path("fakestore-products/", views.fakestore_products, name="fakestore_products"),
```

### 3. Agregar botón en navbar (base.html)

```html
<li class="nav-item">
  <a class="nav-link" href="{% url 'catalog:fakestore_products' %}">
    <i class="bi bi-shop"></i> {% trans "Fake Store" %}
  </a>
</li>
```

---

## 📊 Comparativa de APIs

| API | Gratuita | Autenticación | Calidad Datos | Velocidad | Recomendación |
|-----|----------|---------------|---------------|-----------|---------------|
| Fake Store | ✅ | ❌ | ⭐⭐⭐⭐ | ⚡⚡⚡ | Desarrollo |
| DummyJSON | ✅ | ❌ | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | Desarrollo/Demo |
| Best Buy | ✅* | ✅ | ⭐⭐⭐⭐⭐ | ⚡⚡ | Producción |
| eBay | ✅* | ✅ | ⭐⭐⭐⭐⭐ | ⚡⚡ | Producción |
| Open Food Facts | ✅ | ❌ | ⭐⭐⭐⭐ | ⚡⚡ | Nicho específico |

*Con límites en tier gratuito

---

## 🔐 Buenas Prácticas de Integración

1. **Timeouts**: Siempre usar timeout (10-15 segundos recomendado)
2. **Manejo de errores**: Capturar excepciones específicas de requests
3. **Cache**: Implementar cache para reducir requests (Django cache framework)
4. **Rate limiting**: Respetar límites de la API
5. **Fallbacks**: Tener plan B si la API falla
6. **Logging**: Registrar errores para debugging
7. **Environment variables**: Almacenar API keys en variables de entorno

---

## 📝 Notas de Implementación

### Código Actual
- ✅ Integración con API de socios (`http://13.218.169.6/api/productos/`)
- ✅ Vista adaptable a diferentes estructuras de API
- ✅ Filtros y ordenamiento funcionales
- ✅ Paginación implementada
- ✅ Manejo robusto de errores

### Próximos Pasos Sugeridos
1. Implementar Fake Store API como segunda fuente de productos externos
2. Agregar sistema de cache para mejorar performance
3. Crear configuración centralizada de APIs en settings.py
4. Implementar logging de requests a APIs externas
5. Agregar tests unitarios para las integraciones

---

## 🚀 Testing

Para probar la integración con la API de socios:

```bash
# Iniciar servidor
python manage.py runserver

# Acceder a:
http://localhost:8000/partner-products/
```

Para probar conexión directa con las APIs recomendadas:

```python
# Fake Store API
import requests
response = requests.get("https://fakestoreapi.com/products")
print(response.json())

# DummyJSON API
response = requests.get("https://dummyjson.com/products?limit=10")
print(response.json())
```

---

## 📞 Contacto y Soporte

Para dudas sobre la implementación de APIs externas:
- Revisar documentación oficial de cada API
- Consultar ejemplos en el código fuente de `views.py`
- Verificar logs de Django para debugging

---

**Última actualización**: Noviembre 23, 2025
**Versión del documento**: 1.0
