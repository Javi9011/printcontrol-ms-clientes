from datetime import timedelta
from django.utils import timezone
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema

from .models import Contrato, Arrendamiento, EstadoContrato
from .serializers import (
    ContratoListSerializer,
    ContratoWriteSerializer,
    ArrendamientoSerializer,
    ResumenClientesSerializer,
)
from clientes.models import Cliente, EstadoCliente


@extend_schema_view(
    list=extend_schema(summary='Listar contratos'),
    retrieve=extend_schema(summary='Detalle de contrato'),
    create=extend_schema(summary='Crear contrato'),
    update=extend_schema(summary='Actualizar contrato'),
    partial_update=extend_schema(summary='Actualizar parcialmente'),
    destroy=extend_schema(summary='Eliminar contrato'),
)
class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.select_related('cliente').prefetch_related('arrendamientos').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'cliente', 'periodo_facturacion']
    search_fields = ['numero_contrato', 'cliente__nombre', 'cliente__rfc']
    ordering_fields = ['fecha_inicio', 'fecha_fin', 'creado_en']
    ordering = ['-fecha_inicio']
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ContratoWriteSerializer
        return ContratoListSerializer

    @extend_schema(summary='Contratos próximos a vencer (30 días)')
    @action(detail=False, methods=['get'], url_path='por-vencer')
    def por_vencer(self, request):
        hoy = timezone.now().date()
        limite = hoy + timedelta(days=30)
        contratos = self.get_queryset().filter(
            estado=EstadoContrato.ACTIVO,
            fecha_fin__gte=hoy,
            fecha_fin__lte=limite
        ).order_by('fecha_fin')
        serializer = ContratoListSerializer(contratos, many=True)
        return Response(serializer.data)

    @extend_schema(summary='Contratos de un cliente específico')
    @action(detail=False, methods=['get'], url_path='cliente/(?P<cliente_id>[^/.]+)')
    def por_cliente(self, request, cliente_id=None):
        contratos = self.get_queryset().filter(cliente_id=cliente_id)
        serializer = ContratoListSerializer(contratos, many=True)
        return Response(serializer.data)

    @extend_schema(summary='Resumen general para dashboard')
    @action(detail=False, methods=['get'], url_path='resumen')
    def resumen(self, request):
        hoy = timezone.now().date()
        limite = hoy + timedelta(days=30)

        data = {
            'total_clientes': Cliente.objects.count(),
            'clientes_activos': Cliente.objects.filter(estado_cuenta=EstadoCliente.ACTIVO).count(),
            'total_contratos': Contrato.objects.count(),
            'contratos_activos': Contrato.objects.filter(estado=EstadoContrato.ACTIVO).count(),
            'contratos_por_vencer': Contrato.objects.filter(
                estado=EstadoContrato.ACTIVO,
                fecha_fin__gte=hoy,
                fecha_fin__lte=limite
            ).count(),
            'total_equipos_arrendados': Arrendamiento.objects.filter(estado='ACTIVO').count(),
        }
        return Response(ResumenClientesSerializer(data).data)


@extend_schema_view(
    list=extend_schema(summary='Listar arrendamientos'),
    retrieve=extend_schema(summary='Detalle de arrendamiento'),
    create=extend_schema(summary='Crear arrendamiento'),
    update=extend_schema(summary='Actualizar arrendamiento'),
    partial_update=extend_schema(summary='Actualizar parcialmente'),
    destroy=extend_schema(summary='Eliminar arrendamiento'),
)
class ArrendamientoViewSet(viewsets.ModelViewSet):
    queryset = Arrendamiento.objects.select_related('contrato__cliente').all()
    serializer_class = ArrendamientoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['contrato', 'estado', 'equipo_id']
    search_fields = ['equipo_nombre', 'equipo_serial', 'contrato__numero_contrato']
    permission_classes = [AllowAny]

    @extend_schema(summary='Buscar arrendamiento por equipo ID (ms-equipos)')
    @action(detail=False, methods=['get'], url_path='por-equipo/(?P<equipo_id>[^/.]+)')
    def por_equipo(self, request, equipo_id=None):
        """
        Permite que ms-equipos consulte a qué contrato y cliente pertenece un equipo.
        """
        arrendamiento = Arrendamiento.objects.filter(
            equipo_id=equipo_id,
            estado='ACTIVO'
        ).select_related('contrato__cliente').first()

        if not arrendamiento:
            return Response({'detail': 'No se encontró arrendamiento activo para este equipo.'}, status=404)

        return Response(ArrendamientoSerializer(arrendamiento).data)
