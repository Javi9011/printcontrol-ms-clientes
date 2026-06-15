from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Contrato, Arrendamiento


class ArrendamientoInline(admin.TabularInline):
    model = Arrendamiento
    extra = 0
    fields = ['equipo_id', 'equipo_nombre', 'equipo_serial', 'estado', 'cuota_mensual_ciclos', 'ubicacion']


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_contrato', 'cliente', 'fecha_inicio', 'fecha_fin',
        'estado', 'vigencia_display', 'precio_base', 'total_equipos'
    ]
    list_filter = ['estado', 'periodo_facturacion', 'incluye_mantenimiento', 'incluye_toner']
    search_fields = ['numero_contrato', 'cliente__nombre', 'cliente__rfc']
    inlines = [ArrendamientoInline]
    readonly_fields = ['creado_en', 'actualizado_en']

    def vigencia_display(self, obj):
        hoy = timezone.now().date()
        if obj.estado != 'ACTIVO':
            return format_html('<span style="color:gray">—</span>')
        dias = (obj.fecha_fin - hoy).days
        if dias < 0:
            return format_html('<span style="color:red">Vencido</span>')
        if dias <= 30:
            return format_html('<span style="color:orange">Vence en {} días</span>', dias)
        return format_html('<span style="color:green">Vigente ({} días)</span>', dias)
    vigencia_display.short_description = 'Vigencia'

    def total_equipos(self, obj):
        return obj.total_equipos
    total_equipos.short_description = 'Equipos'


@admin.register(Arrendamiento)
class ArrendamientoAdmin(admin.ModelAdmin):
    list_display = [
        'equipo_nombre', 'equipo_serial', 'contrato',
        'estado', 'cuota_mensual_ciclos', 'fecha_entrega'
    ]
    list_filter = ['estado']
    search_fields = ['equipo_nombre', 'equipo_serial', 'contrato__numero_contrato']
