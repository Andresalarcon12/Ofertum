from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Producto, Oferta, Review, Proposal


class ProductoModelTest(TestCase):
    """Pruebas unitarias para el modelo Producto."""

    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.producto = Producto.objects.create(
            nombre='Producto de prueba',
            descripcion='Descripción de prueba',
            categoria='Electrónica',
            tienda='TiendaTest',
            precio=Decimal('100.00'),
            disponible=True
        )

    def test_producto_creation(self):
        """Verifica que se pueda crear un producto correctamente."""
        self.assertEqual(self.producto.nombre, 'Producto de prueba')
        self.assertEqual(self.producto.precio, Decimal('100.00'))
        self.assertTrue(self.producto.disponible)

    def test_producto_str(self):
        """Verifica que el método __str__ retorne el nombre del producto."""
        self.assertEqual(str(self.producto), 'Producto de prueba')

    def test_obtener_precio_actual_sin_oferta(self):
        """Verifica que el precio actual sea el precio base sin ofertas."""
        precio_actual = self.producto.obtener_precio_actual()
        self.assertEqual(precio_actual, Decimal('100.00'))

    def test_obtener_precio_actual_con_descuento(self):
        """Verifica que el precio actual aplique el descuento de la oferta."""
        Oferta.objects.create(
            producto=self.producto,
            descuento_porcentaje=Decimal('20.00'),
            activo=True
        )
        precio_actual = self.producto.obtener_precio_actual()
        self.assertEqual(precio_actual, Decimal('80.00'))

    def test_obtener_precio_actual_con_precio_fijo(self):
        """Verifica que el precio fijo de la oferta reemplace al precio con descuento."""
        Oferta.objects.create(
            producto=self.producto,
            descuento_porcentaje=Decimal('20.00'),
            precio_fijo=Decimal('75.00'),
            activo=True
        )
        precio_actual = self.producto.obtener_precio_actual()
        self.assertEqual(precio_actual, Decimal('75.00'))

    def test_categoria_slug(self):
        """Verifica que se genere correctamente el slug de la categoría."""
        self.assertEqual(self.producto.categoria_slug, 'electronica')

    def test_get_absolute_url(self):
        """Verifica que get_absolute_url genere la URL correcta."""
        url = self.producto.get_absolute_url()
        expected_url = reverse('catalog:product_detail', args=[self.producto.pk])
        self.assertEqual(url, expected_url)


class OfertaModelTest(TestCase):
    """Pruebas unitarias para el modelo Oferta."""

    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.producto = Producto.objects.create(
            nombre='Producto con oferta',
            precio=Decimal('200.00')
        )

    def test_oferta_con_descuento_porcentaje(self):
        """Verifica que la oferta calcule correctamente el precio con descuento."""
        oferta = Oferta.objects.create(
            producto=self.producto,
            descuento_porcentaje=Decimal('25.00'),
            activo=True
        )
        precio_oferta = oferta.precio_oferta()
        self.assertEqual(precio_oferta, Decimal('150.00'))

    def test_oferta_con_precio_fijo(self):
        """Verifica que la oferta use el precio fijo cuando está definido."""
        oferta = Oferta.objects.create(
            producto=self.producto,
            descuento_porcentaje=Decimal('25.00'),
            precio_fijo=Decimal('140.00'),
            activo=True
        )
        precio_oferta = oferta.precio_oferta()
        self.assertEqual(precio_oferta, Decimal('140.00'))

    def test_oferta_esta_activa(self):
        """Verifica que el método esta_activa() funcione correctamente."""
        oferta_activa = Oferta.objects.create(
            producto=self.producto,
            descuento_porcentaje=Decimal('10.00'),
            activo=True
        )
        oferta_inactiva = Oferta.objects.create(
            producto=self.producto,
            descuento_porcentaje=Decimal('10.00'),
            activo=False
        )
        self.assertTrue(oferta_activa.esta_activa())
        self.assertFalse(oferta_inactiva.esta_activa())


class ReviewModelTest(TestCase):
    """Pruebas unitarias para el modelo Review."""

    def setUp(self):
        """Configuración inicial para las pruebas."""
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.producto = Producto.objects.create(
            nombre='Producto para reseñar',
            precio=Decimal('50.00')
        )

    def test_review_creation(self):
        """Verifica que se pueda crear una reseña correctamente."""
        review = Review.objects.create(
            producto=self.producto,
            usuario=self.user,
            rating=5,
            comentario='Excelente producto'
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comentario, 'Excelente producto')

    def test_review_unique_per_user_per_product(self):
        """Verifica que un usuario no pueda crear múltiples reseñas para el mismo producto."""
        Review.objects.create(
            producto=self.producto,
            usuario=self.user,
            rating=4,
            comentario='Primera reseña'
        )
        # Intentar crear una segunda reseña debería lanzar IntegrityError
        with self.assertRaises(Exception):
            Review.objects.create(
                producto=self.producto,
                usuario=self.user,
                rating=5,
                comentario='Segunda reseña'
            )

    def test_producto_avg_rating(self):
        """Verifica que se calcule correctamente el promedio de calificaciones."""
        User = get_user_model()
        user2 = User.objects.create_user(username='testuser2', password='testpass123')
        
        Review.objects.create(producto=self.producto, usuario=self.user, rating=5)
        Review.objects.create(producto=self.producto, usuario=user2, rating=3)
        
        # avg_rating es una property, no un método
        avg_rating = self.producto.avg_rating
        self.assertEqual(avg_rating, 4.0)

    def test_producto_rating_count(self):
        """Verifica que se cuente correctamente el número de reseñas."""
        User = get_user_model()
        user2 = User.objects.create_user(username='testuser2', password='testpass123')
        
        Review.objects.create(producto=self.producto, usuario=self.user, rating=5)
        Review.objects.create(producto=self.producto, usuario=user2, rating=4)
        
        # rating_count es una property, no un método
        count = self.producto.rating_count
        self.assertEqual(count, 2)


class ProposalModelTest(TestCase):
    """Pruebas unitarias para el modelo Proposal."""

    def setUp(self):
        """Configuración inicial para las pruebas."""
        User = get_user_model()
        self.user = User.objects.create_user(username='proposaluser', password='testpass123')

    def test_proposal_creation(self):
        """Verifica que se pueda crear una propuesta correctamente."""
        proposal = Proposal.objects.create(
            usuario=self.user,
            nombre='Nueva propuesta',
            descripcion='Descripción de propuesta',
            categoria='Tecnología',
            tienda='TiendaNueva',
            precio=Decimal('150.00'),
            status=Proposal.STATUS_PENDING
        )
        self.assertEqual(proposal.nombre, 'Nueva propuesta')
        self.assertEqual(proposal.status, Proposal.STATUS_PENDING)

    def test_proposal_status_choices(self):
        """Verifica que los estados de propuesta sean correctos."""
        self.assertEqual(Proposal.STATUS_PENDING, 'pending')
        self.assertEqual(Proposal.STATUS_APPROVED, 'approved')
        self.assertEqual(Proposal.STATUS_REJECTED, 'rejected')


class ProductAPITest(TestCase):
    """Pruebas para la API JSON de productos."""

    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.client = Client()
        self.producto1 = Producto.objects.create(
            nombre='Producto API 1',
            descripcion='Descripción 1',
            categoria='Categoría1',
            precio=Decimal('100.00'),
            disponible=True
        )
        self.producto2 = Producto.objects.create(
            nombre='Producto API 2',
            descripcion='Descripción 2',
            categoria='Categoría2',
            precio=Decimal('200.00'),
            disponible=False
        )

    def test_api_products_list(self):
        """Verifica que la API devuelva la lista de productos en formato JSON."""
        response = self.client.get(reverse('catalog:api_products'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('productos', data)
        self.assertIn('total', data)
        # Solo el producto1 está disponible por defecto
        self.assertEqual(len(data['productos']), 1)
        self.assertEqual(data['total'], 1)

    def test_api_products_disponibles_only(self):
        """Verifica que la API filtre productos disponibles."""
        response = self.client.get(reverse('catalog:api_products') + '?disponibles=true')
        data = response.json()
        
        # Solo debe retornar productos disponibles
        self.assertEqual(len(data['productos']), 1)
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['productos'][0]['nombre'], 'Producto API 1')

    def test_api_product_detail(self):
        """Verifica que la API devuelva el detalle de un producto específico."""
        response = self.client.get(reverse('catalog:api_product_detail', args=[self.producto1.pk]))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['nombre'], 'Producto API 1')
        self.assertEqual(data['precio_actual'], 100.00)  # Cambio de 'precio' a 'precio_actual'

    def test_api_product_detail_not_found(self):
        """Verifica que la API devuelva 404 para productos inexistentes."""
        response = self.client.get(reverse('catalog:api_product_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)


class ViewsTest(TestCase):
    """Pruebas para las vistas principales."""

    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='viewuser', password='testpass123')
        
        self.producto = Producto.objects.create(
            nombre='Producto Vista',
            precio=Decimal('100.00'),
            categoria='TestCategoria',
            disponible=True
        )

    def test_home_page(self):
        """Verifica que la página de inicio cargue correctamente."""
        response = self.client.get(reverse('catalog:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/home.html')

    def test_product_list_page(self):
        """Verifica que la lista de productos cargue correctamente."""
        response = self.client.get(reverse('catalog:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/product_list.html')
        # El contexto usa 'items' no 'productos'
        self.assertIn('items', response.context)

    def test_product_detail_page(self):
        """Verifica que la página de detalle de producto cargue correctamente."""
        response = self.client.get(reverse('catalog:product_detail', args=[self.producto.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/product_detail.html')
        self.assertEqual(response.context['producto'], self.producto)

    def test_categories_page(self):
        """Verifica que la página de categorías cargue correctamente."""
        response = self.client.get(reverse('catalog:categories'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/categories.html')

    def test_stores_page(self):
        """Verifica que la página de tiendas cargue correctamente."""
        response = self.client.get(reverse('catalog:stores'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/stores.html')

    def test_login_required_for_proposal(self):
        """Verifica que se requiera login para enviar propuestas."""
        response = self.client.get(reverse('catalog:submit_proposal'))
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)

    def test_submit_proposal_authenticated(self):
        """Verifica que usuarios autenticados puedan acceder al formulario de propuestas."""
        self.client.login(username='viewuser', password='testpass123')
        response = self.client.get(reverse('catalog:submit_proposal'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/submit_proposal.html')
