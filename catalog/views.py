from django.shortcuts import render, redirect
from .models import Producto

def home(request):
    return render(request, "catalog/home.html")

def product_list(request):
    # En esta primera versión solo leemos filtros desde la URL y los mostramos;
    # luego conectamos con los modelos reales.
    q = request.GET.get("q", "")
    category = request.GET.get("category", "")
    store = request.GET.get("store", "")
    price_min = request.GET.get("min", "")
    price_max = request.GET.get("max", "")

    # Consultar productos creados en la base de datos y mapear al formato de la plantilla
    productos = Producto.objects.filter(disponible=True).order_by('nombre')

    items = []
    for p in productos:
        items.append({
            'name': p.nombre,
            'price': p.obtener_precio_actual(),
            'store': p.tienda,
            'category': p.categoria,
            'producto_obj': p,
        })

    ctx = {
        'q': q, 'category': category, 'store': store,
        'price_min': price_min, 'price_max': price_max,
        'items': items,
    }
    return render(request, "catalog/product_list.html", ctx)


def categories(request):
    # placeholder de categorías con color (hue) para bordes
    cats = [
        {"name":"GPU",            "icon":"gpu-card",   "h":280},
        {"name":"Almacenamiento", "icon":"hdd",        "h":190},
        {"name":"Teclados",       "icon":"keyboard",   "h":260},
        {"name":"Mouse",          "icon":"mouse",      "h":200},
        {"name":"Monitores",      "icon":"display",    "h":230},
        {"name":"Laptops",        "icon":"laptop",     "h":210},
        {"name":"Audio",          "icon":"earbuds",    "h":170},
        {"name":"CPU/Procesador", "icon":"cpu",        "h":300},
        {"name":"Motherboards",   "icon":"motherboard","h":250},
    ]
    return render(request, "catalog/categories.html", {"cats": cats})


def detalle_producto(request, pk):
    """Vista de detalle para un producto."""
    try:
        producto = Producto.objects.get(pk=pk)
    except Producto.DoesNotExist:
        return render(request, 'catalog/product_detail.html', {'error': 'Producto no encontrado'})

    oferta = producto.obtener_oferta_activa()

    return render(request, 'catalog/product_detail.html', {
        'producto': producto,
        'oferta': oferta,
    })