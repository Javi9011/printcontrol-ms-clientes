from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema

from .models import Cliente
from .serializers import ClienteListSerializer, ClienteWriteSerializer


@extend_schema_view(
    list=extend_schema(summary='Listar clientes'),
    retrieve=extend_schema(summary='Detalle de cliente'),
    create=extend_schema(summary='Crear cliente'),
    update=extend_schema(summary='Actualizar cliente'),
    partial_update=extend_schema(summary='Actualizar parcialmente'),
    destroy=extend_schema(summary='Eliminar cliente'),
)
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.prefetch_related('contactos', 'contratos').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo_persona', 'estado_cuenta']
    search_fields = ['nombre', 'rfc', 'razon_social', 'contacto_email', 'ciudad']
    ordering_fields = ['nombre', 'creado_en']
    ordering = ['nombre']
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ClienteWriteSerializer
        return ClienteListSerializer
