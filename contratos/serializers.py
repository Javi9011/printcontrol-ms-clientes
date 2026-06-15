from rest_framework import serializers
from django.utils import timezone
from .models import Contrato, Arrendamiento
from clientes.serializers import ClienteListSerializer


class ArrendamientoSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Arrendamiento
        fields = [
            'id', 'contrato', 'equipo_id', 'equipo_nombre', 'equipo_serial',
            'estado', 'estado_display',
            'fecha_entrega', 'fecha_devolucion',
            'cuota_mensual_ciclos', 'ubicacion', 'notas',
            'creado_en', 'actualizado_en',
        ]
        read_only_fields = ['creado_en', 'actualizado_en']


class ContratoListSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_rfc = serializers.CharField(source='cliente.rfc', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    periodo_facturacion_display = serializers.CharField(source='get_periodo_facturacion_display', read_only=True)
    esta_vigente = serializers.ReadOnlyField()
    total_equipos = serializers.ReadOnlyField()
    arrendamientos = ArrendamientoSerializer(many=True, read_only=True)

    class Meta:
        model = Contrato
        fields = [
            'id', 'numero_contrato',
            'cliente', 'cliente_nombre', 'cliente_rfc',
            'fecha_inicio', 'fecha_fin',
            'estado', 'estado_display', 'esta_vigente',
            'periodo_facturacion', 'periodo_facturacion_display',
            'precio_base', 'precio_copia_excedente',
            'incluye_mantenimiento', 'incluye_toner',
            'total_equipos', 'arrendamientos',
            'referencia_documento', 'notas',
            'creado_en', 'actualizado_en',
        ]


class ContratoWriteSerializer(serializers.ModelSerializer):
    arrendamientos = ArrendamientoSerializer(many=True, required=False)

    class Meta:
        model = Contrato
        fields = [
            'cliente', 'numero_contrato',
            'fecha_inicio', 'fecha_fin', 'estado',
            'periodo_facturacion', 'precio_base', 'precio_copia_excedente',
            'incluye_mantenimiento', 'incluye_toner',
            'referencia_documento', 'notas',
            'arrendamientos',
        ]

    def validate(self, data):
        inicio = data.get('fecha_inicio')
        fin = data.get('fecha_fin')
        if inicio and fin and fin <= inicio:
            raise serializers.ValidationError(
                {'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'}
            )
        return data

    def create(self, validated_data):
        arrendamientos_data = validated_data.pop('arrendamientos', [])
        contrato = Contrato.objects.create(**validated_data)
        for a in arrendamientos_data:
            Arrendamiento.objects.create(contrato=contrato, **a)
        return contrato

    def update(self, instance, validated_data):
        arrendamientos_data = validated_data.pop('arrendamientos', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if arrendamientos_data is not None:
            # Solo actualiza los existentes, no elimina
            for a_data in arrendamientos_data:
                equipo_id = a_data.get('equipo_id')
                Arrendamiento.objects.update_or_create(
                    contrato=instance,
                    equipo_id=equipo_id,
                    defaults=a_data
                )
        return instance


class ResumenClientesSerializer(serializers.Serializer):
    total_clientes = serializers.IntegerField()
    clientes_activos = serializers.IntegerField()
    total_contratos = serializers.IntegerField()
    contratos_activos = serializers.IntegerField()
    contratos_por_vencer = serializers.IntegerField()
    total_equipos_arrendados = serializers.IntegerField()
