from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.detalle_producto, name="product_detail"),

    
    path("categorias/", views.categories, name="categories"),
    path("categorias/<slug:slug>/", views.category_detail, name="category_detail"),

    
    path("tiendas/", views.stores, name="stores"),
    path("tiendas/<slug:slug>/", views.store_detail, name="store_detail"),
]
