from decimal import Decimal, InvalidOperation
from django.db.models import Q, Count, Avg
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Producto
from .models import Proposal, Review
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django import forms
from django.contrib import messages
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from urllib.parse import urlencode
from .services.reporting import ReportColumn, DefaultReportFactory
from io import BytesIO
from django.http import FileResponse, HttpResponse
from django.utils import timezone
import csv
import requests

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label})


class CustomAuthForm(AuthenticationForm):
    """AuthenticationForm that adds Bootstrap classes to widgets."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            User = get_user_model()
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data.get('email') or ''
            )
            login(request, user)
            messages.success(request, 'Cuenta creada y sesión iniciada.')
            return redirect('catalog:product_list')
        else:
            messages.error(request, 'Corrija los errores del formulario.')
    else:
        form = RegisterForm()
    return render(request, 'catalog/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada.')
    return redirect('catalog:product_list')


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['nombre', 'descripcion', 'categoria', 'tienda', 'link', 'imagen', 'precio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # file input should keep file type; widget attrs ok
            field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label})


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comentario']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label})


@login_required
def submit_proposal(request):
    if request.method == 'POST':
        form = ProposalForm(request.POST, request.FILES)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.usuario = request.user
            prop.save()
            messages.success(request, 'Propuesta enviada y está pendiente de revisión.')
            return redirect('catalog:product_list')
        else:
            messages.error(request, 'Por favor corrija los errores del formulario.')
    else:
        form = ProposalForm()
    return render(request, 'catalog/submit_proposal.html', {'form': form})


def is_admin(user):
    return user.is_active and user.is_staff


@user_passes_test(is_admin)
def admin_proposals(request):
    qs = Proposal.objects.order_by('-creado')
    return render(request, 'catalog/admin_proposals.html', {'proposals': qs})


@user_passes_test(is_admin)
def admin_proposal_action(request, pk, action):
    prop = get_object_or_404(Proposal, pk=pk)
    if action == 'approve' and prop.status == Proposal.STATUS_PENDING:
        # create product
        Producto.objects.create(
            nombre=prop.nombre,
            descripcion=prop.descripcion,
            categoria=prop.categoria,
            tienda=prop.tienda,
            link=prop.link,
            imagen=prop.imagen,
            precio=prop.precio,
            disponible=True,
        )
        prop.status = Proposal.STATUS_APPROVED
        prop.approved_at = timezone.now()
        prop.save()
        messages.success(request, 'Propuesta aprobada y convertida en producto.')
    elif action == 'reject' and prop.status == Proposal.STATUS_PENDING:
        prop.status = Proposal.STATUS_REJECTED
        prop.save()
        messages.success(request, 'Propuesta rechazada.')
    else:
        messages.error(request, 'Acción inválida o propuesta ya moderada.')
    return redirect('catalog:admin_proposals')


@login_required
def add_or_edit_review(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    try:
        review = Review.objects.get(producto=producto, usuario=request.user)
    except Review.DoesNotExist:
        review = None

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.producto = producto
            rev.usuario = request.user
            try:
                rev.save()
                messages.success(request, 'Reseña guardada.')
            except IntegrityError:
                messages.error(request, 'Ya existe una reseña para este producto.')
            return redirect('catalog:product_detail', pk=producto.pk)
        else:
            messages.error(request, 'Por favor corrija los errores del formulario.')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'catalog/review_form.html', {'form': form, 'producto': producto, 'review': review})


def home(request):
    return render(request, "catalog/home.html")


def product_list(request):
    """
    Lista de productos con filtros + ordenamiento + paginación.
    Filtros: q, category, store, min, max, rating
    Orden:   sort = name | price_asc | price_desc | rating
    Página:  page = 1..N
    """
    # --- Leer parámetros ---
    q = (request.GET.get("q") or "").strip()
    category = (request.GET.get("category") or "").strip()
    store = (request.GET.get("store") or "").strip()
    price_min = (request.GET.get("min") or "").strip()
    price_max = (request.GET.get("max") or "").strip()
    min_rating = (request.GET.get("rating") or "").strip()
    sort = (request.GET.get("sort") or "name").strip()   # default: name
    page = request.GET.get("page", 1)

    # --- Base queryset + anotaciones de rating ---
    qs = (
        Producto.objects.filter(disponible=True)
        .annotate(
            db_avg_rating=Avg('reviews__rating'),
            db_rating_count=Count('reviews')
        )
    )

    # --- Filtros de texto/categoría/tienda ---
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if category:
        qs = qs.filter(categoria__iexact=category)
    if store:
        qs = qs.filter(tienda__iexact=store)

    # --- Filtro por rating mínimo (DB) ---
    try:
        if min_rating:
            min_r = float(min_rating)
            qs = qs.filter(db_avg_rating__isnull=False, db_avg_rating__gte=min_r)
    except ValueError:
        pass

    # Orden base estable antes de construir lista
    qs = qs.order_by("nombre")

    # --- Rango de precios (sobre precio vigente) ---
    min_dec = max_dec = None
    try:
        if price_min:
            min_dec = Decimal(price_min.replace(",", "."))
        if price_max:
            max_dec = Decimal(price_max.replace(",", "."))
    except InvalidOperation:
        min_dec = max_dec = None

    # --- Materializar items con precio vigente y aplicar rango ---
    items = []
    for p in qs:
        vigente = p.obtener_precio_actual()  # Decimal
        if min_dec is not None and vigente < min_dec:
            continue
        if max_dec is not None and vigente > max_dec:
            continue
        items.append({
            "name": p.nombre,
            "price": vigente,
            "store": p.tienda,
            "category": p.categoria,
            "producto_obj": p,
            "avg_rating": getattr(p, 'db_avg_rating', None),
            "rating_count": getattr(p, 'db_rating_count', 0),
        })

    # --- Ordenamiento en memoria (ya tenemos 'price' y 'avg_rating') ---
    if sort == "price_asc":
        items.sort(key=lambda x: (x["price"], x["name"]))
    elif sort == "price_desc":
        items.sort(key=lambda x: (x["price"], x["name"]), reverse=True)
    elif sort == "rating":
        # rating None al final; más reseñas primero si empata
        def rate_key(it):
            ar = it["avg_rating"]
            # invertimos para que mayor rating quede antes
            return (-(ar if ar is not None else -1), -it["rating_count"], it["name"])
        items.sort(key=rate_key)
    else:
        # name (default)
        items.sort(key=lambda x: x["name"])

    # --- Paginación ---
    paginator = Paginator(items, 9)  # 9 tarjetas por página
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    # --- Querystring sin 'page' para reutilizar en links de paginación ---
    qs_params = request.GET.copy()
    qs_params.pop('page', None)
    querystring = urlencode([(k, v) for k, v in qs_params.items() if v not in (None, "")])

    # --- Contexto ---
    ctx = {
        "q": q,
        "category": category,
        "store": store,
        "price_min": price_min,
        "price_max": price_max,
        "min_rating": min_rating,
        "sort": sort,
        "page_obj": page_obj,                  # usar en template
        "items": page_obj.object_list,         # tu HTML ya lo usa
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
        "querystring": querystring,            # para conservar filtros en los links
    }
    return render(request, "catalog/product_list.html", ctx)




#  CATEGORÍAS 
def categories(request):
    """
    Lista de categorías existentes (derivadas de Producto.categoria),
    con total de productos por categoría.
    """
    cats_qs = (
        Producto.objects.filter(disponible=True)
        .exclude(categoria__isnull=True)
        .exclude(categoria__exact="")
        .values("categoria")
        .annotate(total=Count("id"))
        .order_by("categoria")
    )
    cats = [
        {
            "name": c["categoria"],
            "slug": slugify(c["categoria"]),
            "count": c["total"],
        }
        for c in cats_qs
    ]
    return render(request, "catalog/categories.html", {"cats": cats})


def category_detail(request, slug):
    """
    Muestra productos de una categoría, resolviendo el nombre por slug.
    """
    all_cats = list(
        Producto.objects.exclude(categoria__isnull=True)
        .exclude(categoria__exact="")
        .values_list("categoria", flat=True)
        .distinct()
    )
    cat_name = next((c for c in all_cats if slugify(c) == slug), None)
    if not cat_name:
        raise Http404("Categoría no encontrada")

    qs = (
        Producto.objects.filter(disponible=True, categoria__iexact=cat_name)
        .order_by("nombre")
    )

    items = [{
        "name": p.nombre,
        "price": p.obtener_precio_actual(),
        "store": p.tienda,
        "category": p.categoria,
        "producto_obj": p,
    } for p in qs]

    ctx = {
        "items": items,
        "q": "", "category": cat_name, "store": "",
        "price_min": "", "price_max": "",
    }
    return render(request, "catalog/product_list.html", ctx)


# TIENDAS 
def stores(request):
    """
    Lista de tiendas existentes (derivadas de Producto.tienda),
    con total de productos por tienda.
    """
    stores_qs = (
        Producto.objects.filter(disponible=True)
        .exclude(tienda__isnull=True)
        .exclude(tienda__exact="")
        .values("tienda")
        .annotate(total=Count("id"))
        .order_by("tienda")
    )
    stores = [
        {
            "name": s["tienda"],
            "slug": slugify(s["tienda"]),
            "count": s["total"],
        }
        for s in stores_qs
    ]
    return render(request, "catalog/stores.html", {"stores": stores})


def store_detail(request, slug):
    """
    Muestra productos de una tienda, resolviendo el nombre por slug.
    """
    all_stores = list(
        Producto.objects.exclude(tienda__isnull=True)
        .exclude(tienda__exact="")
        .values_list("tienda", flat=True)
        .distinct()
    )
    store_name = next((s for s in all_stores if slugify(s) == slug), None)
    if not store_name:
        raise Http404("Tienda no encontrada")

    qs = (
        Producto.objects.filter(disponible=True, tienda__iexact=store_name)
        .order_by("nombre")
    )

    items = [{
        "name": p.nombre,
        "price": p.obtener_precio_actual(),
        "store": p.tienda,
        "category": p.categoria,
        "producto_obj": p,
    } for p in qs]

    ctx = {
        "items": items,
        "q": "", "category": "", "store": store_name,
        "price_min": "", "price_max": "",
    }
    return render(request, "catalog/product_list.html", ctx)



def detalle_producto(request, pk):
    """Vista de detalle para un producto."""
    producto = get_object_or_404(Producto, pk=pk)
    oferta = producto.obtener_oferta_activa()
    return render(request, "catalog/product_detail.html", {
        "producto": producto,
        "oferta": oferta,
    })

# API JSON PROPIA
def _product_to_dict(p: Producto):
    oferta = p.obtener_oferta_activa()
    return {
        "id": p.id,
        "nombre": p.nombre,
        "descripcion": p.descripcion,
        "categoria": p.categoria,
        "tienda": p.tienda,
        "link": p.link,
        "precio_base": float(p.precio),
        "precio_actual": float(p.obtener_precio_actual()),
        "oferta": (
            None if not oferta else {
                "descuento_porcentaje": float(oferta.descuento_porcentaje),
                "precio_fijo": (None if oferta.precio_fijo is None else float(oferta.precio_fijo)),
                "activo": oferta.activo,
            }
        ),
        "imagen_url": (p.imagen.url if p.imagen else None),
        "disponible": p.disponible,
        "creado": p.creado.isoformat(),
        "detail_url": f"/products/{p.id}/",
    }

def api_products(request):
    """
    Lista JSON de productos disponibles con filtros:
    ?q=...&category=...&store=...&min=...&max=...
    El rango min/max se compara contra el PRECIO ACTUAL (incluye oferta).
    """
    qs = Producto.objects.filter(disponible=True)

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))

    category = (request.GET.get("category") or "").strip()
    if category:
        qs = qs.filter(categoria__iexact=category)

    store = (request.GET.get("store") or "").strip()
    if store:
        qs = qs.filter(tienda__iexact=store)

    # min/max como Decimal, y filtramos por obtener_precio_actual() en Python
    pmin_raw = request.GET.get("min")
    pmax_raw = request.GET.get("max")
    try:
        pmin = Decimal(pmin_raw) if pmin_raw not in (None, "") else None
    except (InvalidOperation, TypeError):
        pmin = None
    try:
        pmax = Decimal(pmax_raw) if pmax_raw not in (None, "") else None
    except (InvalidOperation, TypeError):
        pmax = None

    productos = list(qs)
    if pmin is not None:
        productos = [p for p in productos if p.obtener_precio_actual() >= pmin]
    if pmax is not None:
        productos = [p for p in productos if p.obtener_precio_actual() <= pmax]

    data = [_product_to_dict(p) for p in productos]
    return JsonResponse({"count": len(data), "results": data}, json_dumps_params={"ensure_ascii": False})

def api_product_detail(request, pk: int):
    try:
        p = Producto.objects.get(pk=pk, disponible=True)
    except Producto.DoesNotExist:
        raise Http404("Producto no encontrado")
    return JsonResponse(_product_to_dict(p), json_dumps_params={"ensure_ascii": False})



try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORTLAB_OK = True
except Exception:
    REPORTLAB_OK = False
# --- NUEVA VISTA: exportación de productos ---
def _filtered_items_for_export(request):
    """
    Repite la misma lógica de filtros/orden que product_list(),
    pero devolviendo la lista 'items' ya armada para exportar.
    """
    q = (request.GET.get("q") or "").strip()
    category = (request.GET.get("category") or "").strip()
    store = (request.GET.get("store") or "").strip()
    price_min = (request.GET.get("min") or "").strip()
    price_max = (request.GET.get("max") or "").strip()
    min_rating = (request.GET.get("rating") or "").strip()
    sort = (request.GET.get("sort") or "name").strip()

    qs = Producto.objects.filter(disponible=True).annotate(
        db_avg_rating=Avg('reviews__rating'),
        db_rating_count=Count('reviews')
    )

    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if category:
        qs = qs.filter(categoria__iexact=category)
    if store:
        qs = qs.filter(tienda__iexact=store)

    try:
        if min_rating:
            min_r = float(min_rating)
            qs = qs.filter(db_avg_rating__isnull=False, db_avg_rating__gte=min_r)
    except ValueError:
        pass

    productos = qs.order_by("nombre")

    # Rango de precio vigente
    min_dec = max_dec = None
    try:
        if price_min:
            min_dec = Decimal(price_min.replace(",", "."))
        if price_max:
            max_dec = Decimal(price_max.replace(",", "."))
    except InvalidOperation:
        min_dec = max_dec = None

    items = []
    for p in productos:
        vigente = p.obtener_precio_actual()
        if min_dec is not None and vigente < min_dec:
            continue
        if max_dec is not None and vigente > max_dec:
            continue
        items.append({
            "name": p.nombre,
            "price": vigente,
            "store": p.tienda,
            "category": p.categoria,
            "producto_obj": p,
            "avg_rating": getattr(p, 'db_avg_rating', None),
            "rating_count": getattr(p, 'db_rating_count', 0),
        })

    # Orden
    if sort == "price_asc":
        items.sort(key=lambda x: (x["price"], x["name"]))
    elif sort == "price_desc":
        items.sort(key=lambda x: (x["price"], x["name"]), reverse=True)
    elif sort == "rating":
        items.sort(key=lambda x: (-(x["avg_rating"] or -1), -x["rating_count"], x["name"]))
    else:
        items.sort(key=lambda x: x["name"])

    return items


def export_products_report(request):
    """
    /products/export/?format=pdf|xlsx  (xlsx = CSV con mime de Excel)
    Conserva los mismos filtros del listado.
    """
    fmt = (request.GET.get("format") or "xlsx").lower()
    items = _filtered_items_for_export(request)

    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")

    if fmt == "pdf":
        if not REPORTLAB_OK:
            return HttpResponse(
                "Para exportar a PDF instala reportlab: pip install reportlab",
                content_type="text/plain",
                status=500
            )

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        title = f"Reporte de productos ({timestamp})"
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height - 50, title)

        c.setFont("Helvetica", 10)
        y = height - 80
        line_height = 14

        # Encabezados
        c.drawString(40, y, "Nombre")
        c.drawString(280, y, "Categoría")
        c.drawString(380, y, "Tienda")
        c.drawRightString(560, y, "Precio vigente")
        y -= line_height

        for it in items:
            if y < 60:  # salto de página simple
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 50

            nombre = (it["name"] or "")[:45]
            c.drawString(40, y, nombre)
            c.drawString(280, y, (it["category"] or "")[:18])
            c.drawString(380, y, (it["store"] or "")[:18])
            c.drawRightString(560, y, f"${float(it['price']):,.2f}")
            y -= line_height

        c.showPage()
        c.save()
        buffer.seek(0)

        filename = f"productos_{timestamp}.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename)

    # --- XLSX “rápido” vía CSV (abre en Excel sin problema) ---
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    filename = f"productos_{timestamp}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(["Nombre", "Categoría", "Tienda", "Precio vigente", "Rating prom.", "N° reseñas"])
    for it in items:
        writer.writerow([
            it["name"],
            it["category"] or "",
            it["store"] or "",
            f"{float(it['price']):.2f}",
            (f"{float(it['avg_rating']):.1f}" if it["avg_rating"] is not None else ""),
            it["rating_count"] or 0,
        ])
    return response


def partner_products(request):
    """
    Vista que muestra productos de API externa de equipo aliado.
    Endpoint: http://13.218.169.6/api/productos/
    """
    partner_api_url = "http://13.218.169.6/api/productos/"
    
    # Parámetros de filtro
    q = (request.GET.get("q") or "").strip()
    category = (request.GET.get("category") or "").strip()
    store = (request.GET.get("store") or "").strip()
    price_min = (request.GET.get("min") or "").strip()
    price_max = (request.GET.get("max") or "").strip()
    sort = (request.GET.get("sort") or "name").strip()
    page = request.GET.get("page", 1)
    
    items = []
    error_message = None
    
    try:
        # Hacer petición a la API externa con timeout
        response = requests.get(partner_api_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extraer productos de la respuesta (ajustar según estructura de la API)
        if isinstance(data, dict) and 'results' in data:
            productos = data['results']
        elif isinstance(data, list):
            productos = data
        else:
            productos = []
        
        # Procesar y filtrar productos
        for p in productos:
            # Mapeo de campos según la estructura real de la API
            nombre = p.get('nombreProducto', p.get('nombre', p.get('name', 'Sin nombre')))
            descripcion = p.get('descripcion', p.get('description', ''))
            categoria = p.get('tipoProducto', p.get('categoria', p.get('category', '')))
            tienda = p.get('marcaProducto', p.get('tienda', p.get('store', '')))
            precio = float(p.get('precioDeProducto', p.get('precio', p.get('price', p.get('precio_base', p.get('precio_actual', 0))))))
            imagen_path = p.get('imagenProducto', p.get('imagen', p.get('image', p.get('imagen_url', ''))))
            # Construir URL completa de imagen si es ruta relativa
            if imagen_path and not imagen_path.startswith('http'):
                imagen = f"http://13.218.169.6{imagen_path}"
            else:
                imagen = imagen_path
            link = p.get('link', p.get('url', ''))
            product_id = p.get('idProducto', p.get('id', 0))
            
            # Aplicar filtros
            if q and q.lower() not in nombre.lower() and q.lower() not in descripcion.lower():
                continue
            if category and category.lower() != categoria.lower():
                continue
            if store and store.lower() != tienda.lower():
                continue
            
            # Filtro de precio
            try:
                if price_min and precio < float(price_min.replace(",", ".")):
                    continue
                if price_max and precio > float(price_max.replace(",", ".")):
                    continue
            except (ValueError, InvalidOperation):
                pass
            
            items.append({
                "id": product_id,
                "name": nombre,
                "description": descripcion,
                "price": Decimal(str(precio)),
                "store": tienda,
                "category": categoria,
                "image": imagen,
                "link": link,
                "avg_rating": None,
                "rating_count": 0,
            })
    
    except requests.exceptions.Timeout:
        error_message = "La API externa tardó demasiado en responder. Por favor, intenta más tarde."
    except requests.exceptions.ConnectionError:
        error_message = "No se pudo conectar con la API externa. Verifica tu conexión a internet."
    except requests.exceptions.RequestException as e:
        error_message = f"Error al conectar con la API externa: {str(e)}"
    except Exception as e:
        error_message = f"Error al procesar los datos: {str(e)}"
    
    # Ordenamiento
    if sort == "price_asc":
        items.sort(key=lambda x: (x["price"], x["name"]))
    elif sort == "price_desc":
        items.sort(key=lambda x: (x["price"], x["name"]), reverse=True)
    else:
        items.sort(key=lambda x: x["name"])
    
    # Paginación
    paginator = Paginator(items, 9)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)
    
    # Querystring para paginación
    qs_params = request.GET.copy()
    qs_params.pop('page', None)
    querystring = urlencode([(k, v) for k, v in qs_params.items() if v not in (None, "")])
    
    ctx = {
        "q": q,
        "category": category,
        "store": store,
        "price_min": price_min,
        "price_max": price_max,
        "sort": sort,
        "page_obj": page_obj,
        "items": page_obj.object_list,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
        "querystring": querystring,
        "error_message": error_message,
        "is_partner_page": True,
    }
    return render(request, "catalog/partner_products.html", ctx)