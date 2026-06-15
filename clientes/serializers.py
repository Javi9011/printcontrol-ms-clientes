from rest_framework import serializers
from .models import Cliente, ContactoAdicional


class ContactoAdicionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactoAdicional
        fields = ['id', 'nombre', 'cargo', 'email', 'telefono']


class ClienteListSerializer(serializers.ModelSerializer):
    contratos_activos = serializers.ReadOnlyField()
    total_equipos = serializers.ReadOnlyField()
    estado_cuenta_display = serializers.CharField(source='get_estado_cuenta_display', read_only=True)
    tipo_persona_display = serializers.CharField(source='get_tipo_persona_display', read_only=True)
    contactos = ContactoAdicionalSerializer(many=True, read_only=True)

    class Meta:
        model = Cliente
        fields = [
            'id', 'tipo_persona', 'tipo_persona_display',
            'nombre', 'rfc', 'razon_social',
            'contacto_nombre', 'contacto_email', 'contacto_telefono',
            'calle', 'ciudad', 'estado', 'codigo_postal', 'pais',
            'estado_cuenta', 'estado_cuenta_display',
            'contratos_activos', 'total_equipos',
            'contactos', 'notas',
            'creado_en', 'actualizado_en',
        ]


class ClienteWriteSerializer(serializers.ModelSerializer):
    contactos = ContactoAdicionalSerializer(many=True, required=False)

    class Meta:
        model = Cliente
        fields = [
            'tipo_persona', 'nombre', 'rfc', 'razon_social',
            'contacto_nombre', 'contacto_email', 'contacto_telefono',
            'calle', 'ciudad', 'estado', 'codigo_postal', 'pais',
            'estado_cuenta', 'notas', 'contactos',
        ]

    def create(self, validated_data):
        contactos_data = validated_data.pop('contactos', [])
        cliente = Cliente.objects.create(**validated_data)
        for c in contactos_data:
            ContactoAdicional.objects.create(cliente=cliente, **c)
        return cliente

    def update(self, instance, validated_data):
        contactos_data = validated_data.pop('contactos', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if contactos_data is not None:
            instance.contactos.all().delete()
            for c in contactos_data:
                ContactoAdicional.objects.create(cliente=instance, **c)
        return instance
