# cs_piai — Plantillas de Informes QWeb

## Ubicación

Todos los XMLs de reports están en `cs_piai/reports/`.

| Archivo | ID del template | Descripción | Binding |
|---------|----------------|-------------|---------|
| `cs_piai_report_full.xml` | `report_piai_full_document` | Informe clínico completo | Sí — menú Imprimir |
| `cs_piai_report_summary.xml` | `report_piai_summary_document` | Resumen para el equipo | Sí |
| `cs_piai_report_discharge.xml` | `report_piai_discharge_document` | Plan de alta | Sí |
| `cs_piai_report_audit.xml` | `report_piai_audit_document` | Inspección / Auditoría con trazabilidad | Sí |
| `cs_piai_report_monthly.xml` | `report_piai_monthly_document` | Informe mensual | Sí |

## Cómo modificar una plantilla

1. Editar el XML en `cs_piai/reports/<archivo>.xml`
2. Actualizar el módulo para recargar las vistas:
   ```bash
   docker compose exec odoo odoo -d cs_followup_install_test --stop-after-init --http-port=8099 -u cs_piai
   ```
3. En producción, basta con `Configuración → Activar modo desarrollador → Actualizar lista de módulos → Actualizar cs_piai`.

## Estructura de un template de report

```xml
<template id="report_piai_XXX_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="piai">
            <t t-call="web.external_layout">
                <div class="page">
                    <!-- contenido -->
                </div>
            </t>
        </t>
    </t>
</template>
```

- `docs` es el recordset de `cs.piai` que se está imprimiendo.
- `web.external_layout` aplica la cabecera/pie de empresa.
- Para acceder al logo de empresa: `env.company.logo`.

## Odoo 19 — Campos de trazabilidad (`mail.tracking.value`)

En Odoo 17+ el modelo `mail.tracking.value` eliminó el atributo `field_desc`.
Tabla de equivalencias:

| Odoo ≤16 | Odoo 17-19 |
|----------|-----------|
| `track.field_desc` | `track.field_id.field_description` |
| `track.field_id.name` | igual |
| `track.old_value_char` | igual |
| `track.new_value_char` | igual |
| `track.old_value_text` | igual |
| `track.new_value_text` | igual |
| `track.old_value_integer` | igual |
| `track.new_value_integer` | igual |
| `track.old_value_float` | igual |
| `track.new_value_float` | igual |
| `track.old_value_datetime` | igual |
| `track.new_value_datetime` | igual |

### Ejemplo de uso correcto en QWeb (Odoo 19)

```xml
<t t-foreach="piai.message_ids.filtered(lambda m: m.tracking_value_ids)" t-as="msg">
    <t t-foreach="msg.tracking_value_ids" t-as="track">
        <tr>
            <td><t t-esc="msg.date"/></td>
            <td><t t-esc="msg.author_id.name"/></td>
            <td><t t-esc="track.field_id.field_description"/></td>  <!-- NO field_desc -->
            <td><t t-esc="track.old_value_char or track.old_value_text or '—'"/></td>
            <td><t t-esc="track.new_value_char or track.new_value_text or '—'"/></td>
        </tr>
    </t>
</t>
```

## Bug conocido (pendiente)

Los dos smart buttons en `cs_piai_form_views.xml` (objetivo_count y active_risk_count)
ambos llaman a `action_view_evolutions`. El de objetivos debería llamar a la lista
de objetivos — es un bug menor de UX, no afecta a la funcionalidad.
