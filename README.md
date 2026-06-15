# ms-clientes — PrintControl

Microservicio Django REST para gestión de clientes, contratos y arrendamientos.

## Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET/POST | `/api/v1/clientes/` | Listar / crear clientes |
| GET/PUT/DELETE | `/api/v1/clientes/{id}/` | Detalle, editar, eliminar |
| GET/POST | `/api/v1/contratos/` | Listar / crear contratos |
| GET/PUT/DELETE | `/api/v1/contratos/{id}/` | Detalle, editar, eliminar |
| GET | `/api/v1/contratos/resumen/` | Métricas para dashboard |
| GET | `/api/v1/contratos/por-vencer/` | Contratos que vencen en 30 días |
| GET | `/api/v1/contratos/cliente/{id}/` | Contratos de un cliente |
| GET/POST | `/api/v1/arrendamientos/` | Listar / crear arrendamientos |
| GET | `/api/v1/arrendamientos/por-equipo/{id}/` | Contrato activo de un equipo |
| GET | `/api/docs/` | Swagger UI |

## Levantar con Docker

```bash
# 1. Entrar a la carpeta
cd ms-clientes

# 2. Crear .env  (Windows PowerShell)
Copy-Item .env.example .env

# 3. Levantar
docker-compose up --build

# 4. Crear superusuario (en otra terminal)
docker-compose exec ms-clientes python manage.py createsuperuser
```

Accede a:
- API: http://localhost:8002/api/v1/
- Swagger: http://localhost:8002/api/docs/
- Admin: http://localhost:8002/admin/

## Ejemplo — Crear cliente con contrato

```bash
# 1. Crear cliente
curl -X POST http://localhost:8002/api/v1/clientes/ \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_persona": "MORAL",
    "nombre": "Constructora Alfa S.A.",
    "rfc": "CAL900101ABC",
    "contacto_nombre": "Juan Pérez",
    "contacto_email": "juan@constructoraalfa.com",
    "contacto_telefono": "555-1234",
    "ciudad": "Monterrey",
    "estado": "Nuevo León",
    "estado_cuenta": "ACTIVO"
  }'

# 2. Crear contrato (usar el id del cliente creado)
curl -X POST http://localhost:8002/api/v1/contratos/ \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": 1,
    "numero_contrato": "CNT-2025-001",
    "fecha_inicio": "2025-01-01",
    "fecha_fin": "2025-12-31",
    "precio_base": 2500.00,
    "precio_copia_excedente": 0.0035,
    "incluye_mantenimiento": true,
    "incluye_toner": true,
    "arrendamientos": [
      {
        "equipo_id": 1,
        "equipo_nombre": "Kyocera ECOSYS M2040dn",
        "equipo_serial": "KYO-001-2025",
        "cuota_mensual_ciclos": 8000,
        "ubicacion": "Oficina Principal"
      }
    ]
  }'
```

## Subir a GitHub

```bash
git init
git add .
git commit -m "feat: ms-clientes inicial"
git remote add origin https://github.com/TU_USUARIO/printcontrol-ms-clientes.git
git push -u origin main
```
