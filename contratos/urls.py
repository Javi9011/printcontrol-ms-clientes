from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContratoViewSet, ArrendamientoViewSet

router = DefaultRouter()
router.register(r'contratos', ContratoViewSet, basename='contrato')
router.register(r'arrendamientos', ArrendamientoViewSet, basename='arrendamiento')

urlpatterns = [
    path('', include(router.urls)),
]
