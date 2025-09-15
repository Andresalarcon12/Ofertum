from decimal import Decimal, InvalidOperation

from django.db.models import Q, Count, Avg
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify

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
    Lista de productos con filtros por:
    - q: texto (nombre/descripcion)
    - category: categoría exacta (case-insensitive)
    - store: tienda exacta (case-insensitive)
    - min / max: precio vigente (considerando oferta activa) en rango
    """
    q = (request.GET.get("q") or "").strip()
    category = (request.GET.get("category") or "").strip()
    store = (request.GET.get("store") or "").strip()
    price_min = (request.GET.get("min") or "").strip()
    price_max = (request.GET.get("max") or "").strip()
    # rating filter: minimum average rating (1-5)
    min_rating = (request.GET.get("rating") or "").strip()

    # Base queryset, annotate with avg rating and count using DB-safe names
    qs = Producto.objects.filter(disponible=True).annotate(db_avg_rating=Avg('reviews__rating'), db_rating_count=Count('reviews'))

    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))

    if category:
        qs = qs.filter(categoria__iexact=category)

    if store:
        qs = qs.filter(tienda__iexact=store)

    # Apply rating filter at DB level when possible
    try:
        if min_rating:
            min_r = float(min_rating)
            qs = qs.filter(db_avg_rating__isnull=False).filter(db_avg_rating__gte=min_r)
    except ValueError:
        # ignore invalid rating input
        pass

    productos = qs.order_by("nombre")

    # Parseo de límites de precio (trabajamos con Decimal)
    min_dec = max_dec = None
    try:
        if price_min:
            min_dec = Decimal(price_min.replace(",", "."))
        if price_max:
            max_dec = Decimal(price_max.replace(",", "."))
    except InvalidOperation:
        # Si el usuario mete texto no numérico, ignoramos los límites
        min_dec = max_dec = None

    # Construcción de items y filtro por precio vigente en Python
    items = []
    for p in productos:
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
            "producto_obj": p,   # por si tu template lo usa
            # map annotated values into simple keys used by template
            "avg_rating": getattr(p, 'db_avg_rating', None),
            "rating_count": getattr(p, 'db_rating_count', 0),
        })

    ctx = {
        "q": q, "category": category, "store": store,
        "price_min": price_min, "price_max": price_max,
        "items": items,
        "min_rating": min_rating,
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
