from django.db import models
from django.core.validators import MinValueValidator
from clientes.models import Cliente


class EstadoContrato(models.TextChoices):
    ACTIVO = 'ACTIVO', 'Activo'
    VENCIDO = 'VENCIDO', 'Vencido'
    CANCELADO = 'CANCELADO', 'Cancelado'
    RENOVACION = 'RENOVACION', 'En renovación'


class PeriodoFacturacion(models.TextChoices):
    MENSUAL = 'MENSUAL', 'Mensual'
    TRIMESTRAL = 'TRIMESTRAL', 'Trimestral'
    ANUAL = 'ANUAL', 'Anual'


class Contrato(models.Model):
    """
    Contrato de arrendamiento entre la empresa y un cliente.
    Puede cubrir uno o varios equipos (ver Arrendamiento).
    """
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='contratos')
    numero_contrato = models.CharField(max_length=50, unique=True)

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=15, choices=EstadoContrato.choices, default=EstadoContrato.ACTIVO)

    periodo_facturacion = models.CharField(
        max_length=15,
        choices=PeriodoFacturacion.choices,
        default=PeriodoFacturacion.MENSUAL
    )

    # Precio base del contrato (sin contar excedentes)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    # Precio por copia excedente (cuando se supera la cuota mensual)
    precio_copia_excedente = models.DecimalField(
        max_digits=8, decimal_places=4,
        default=0.0,
        validators=[MinValueValidator(0)],
        help_text='Precio por ciclo excedente de la cuota mensual'
    )

    # Condiciones generales
    incluye_mantenimiento = models.BooleanField(default=True)
    incluye_toner = models.BooleanField(default=True)
    notas = models.TextField(blank=True)

    # Documento físico (ruta o referencia)
    referencia_documento = models.CharField(max_length=300, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'

    def __str__(self):
        return f'{self.numero_contrato} — {self.cliente}'

    @property
    def esta_vigente(self):
        from django.utils import timezone
        hoy = timezone.now().date()
        return self.fecha_inicio <= hoy <= self.fecha_fin and self.estado == EstadoContrato.ACTIVO

    @property
    def total_equipos(self):
        return self.arrendamientos.filter(estado='ACTIVO').count()


class EstadoArrendamiento(models.TextChoices):
    ACTIVO = 'ACTIVO', 'Activo'
    DEVUELTO = 'DEVUELTO', 'Devuelto'
    SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'


class Arrendamiento(models.Model):
    """
    Línea de contrato: asocia un equipo específico (por ID en ms-equipos)
    a un contrato. Un contrato puede tener N arrendamientos.
    """
    contrato = models.ForeignKey(Contrato, on_delete=models.PROTECT, related_name='arrendamientos')

    # Referencia al equipo en ms-equipos (sin FK real entre servicios)
    equipo_id = models.PositiveIntegerField(help_text='ID del equipo en ms-equipos')
    equipo_nombre = models.CharField(max_length=200, help_text='Cache del nombre para no depender de ms-equipos')
    equipo_serial = models.CharField(max_length=100)

    estado = models.CharField(
        max_length=15,
        choices=EstadoArrendamiento.choices,
        default=EstadoArrendamiento.ACTIVO
    )

    fecha_entrega = models.DateField(null=True, blank=True)
    fecha_devolucion = models.DateField(null=True, blank=True)

    # Cuota mensual pactada específica para este equipo en este contrato
    cuota_mensual_ciclos = models.PositiveIntegerField(
        default=5000,
        help_text='Ciclos de motor incluidos por mes para este equipo'
    )

    ubicacion = models.CharField(max_length=200, blank=True)
    notas = models.TextField(blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Arrendamiento'
        verbose_name_plural = 'Arrendamientos'
        constraints = [
            models.UniqueConstraint(
                fields=['contrato', 'equipo_id'],
                name='unique_equipo_por_contrato'
            )
        ]

    def __str__(self):
        return f'{self.equipo_nombre} ({self.equipo_serial}) — {self.contrato.numero_contrato}'
