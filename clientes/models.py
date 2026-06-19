from django.db import models
from django.core.validators import RegexValidator


class TipoPersona(models.TextChoices):
    FISICA = 'FISICA', 'Persona Física'
    MORAL = 'MORAL', 'Persona Moral / Empresa'


class EstadoCliente(models.TextChoices):
    ACTIVO = 'ACTIVO', 'Activo'
    INACTIVO = 'INACTIVO', 'Inactivo'
    SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'


class Cliente(models.Model):
    """
    Cliente del sistema PrintControl
    """

    tipo_persona = models.CharField(
        max_length=10,
        choices=TipoPersona.choices,
        default=TipoPersona.MORAL
    )

    nombre = models.CharField(max_length=200)

    rfc = models.CharField(
        max_length=13,
        unique=True,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$',
                message='RFC inválido. Formato esperado: XAXX010101000'
            )
        ]
    )

    razon_social = models.CharField(max_length=200, blank=True)

    contacto_nombre = models.CharField(max_length=150)
    contacto_email = models.EmailField()
    contacto_telefono = models.CharField(max_length=20, blank=True)

    calle = models.CharField(max_length=200, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    pais = models.CharField(max_length=100, default='México')

    estado_cuenta = models.CharField(
        max_length=15,
        choices=EstadoCliente.choices,
        default=EstadoCliente.ACTIVO
    )

    notas = models.TextField(blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.nombre

    # 🔥 FIX IMPORTANTE: evita crash si aún no hay contratos
    @property
    def contratos_activos(self):
        try:
            return self.contratos.filter(estado='ACTIVO').count()
        except Exception:
            return 0

    # 🔥 FIX IMPORTANTE: evita import circular + fallback seguro
    @property
    def total_equipos(self):
        try:
            from contratos.models import Arrendamiento
            return Arrendamiento.objects.filter(
                contrato__cliente_id=self.id,
                contrato__estado='ACTIVO',
                estado='ACTIVO'
            ).count()
        except Exception:
            return 0


class ContactoAdicional(models.Model):
    """
    Contactos secundarios del cliente
    """

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='contactos'
    )

    nombre = models.CharField(max_length=150)
    cargo = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = 'Contacto adicional'
        verbose_name_plural = 'Contactos adicionales'

    def __str__(self):
        return f'{self.nombre} — {self.cliente.nombre}'