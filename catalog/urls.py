from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.detalle_producto, name="product_detail"),
     # --- NUEVA RUTA DE REPORTE ---
    path("products/export/", views.export_products_report, name="products_export"),
    path("proposals/submit/", views.submit_proposal, name="submit_proposal"),
    path("proposals/admin/", views.admin_proposals, name="admin_proposals"),
    path("proposals/<int:pk>/<str:action>/", views.admin_proposal_action, name="admin_proposal_action"),
    path("products/<int:pk>/review/", views.add_or_edit_review, name="add_or_edit_review"),
    # Auth
    path("accounts/register/", views.register_view, name="register"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("accounts/login/", auth_views.LoginView.as_view(template_name='catalog/login.html', authentication_form=views.CustomAuthForm), name="login"),

    
    path("categorias/", views.categories, name="categories"),
    path("categorias/<slug:slug>/", views.category_detail, name="category_detail"),

    
    path("tiendas/", views.stores, name="stores"),
    path("tiendas/<slug:slug>/", views.store_detail, name="store_detail"),
        path("api/products/", views.api_products, name="api_products"),
        path("api/products/<int:pk>/", views.api_product_detail, name="api_product_detail"),
        

]
