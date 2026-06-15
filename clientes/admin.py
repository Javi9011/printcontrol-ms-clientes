from django.contrib import admin
from .models import Cliente, ContactoAdicional


class ContactoInline(admin.TabularInline):
    model = ContactoAdicional
    extra = 0


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'rfc', 'tipo_persona', 'estado_cuenta', 'contacto_email', 'ciudad', 'creado_en']
    list_filter = ['tipo_persona', 'estado_cuenta', 'pais']
    search_fields = ['nombre', 'rfc', 'razon_social', 'contacto_email']
    inlines = [ContactoInline]
    readonly_fields = ['creado_en', 'actualizado_en']


@admin.register(ContactoAdicional)
class ContactoAdicionalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'cargo', 'cliente', 'email', 'telefono']
    search_fields = ['nombre', 'cliente__nombre']
