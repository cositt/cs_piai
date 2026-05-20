![icon](static/description/icon.png)

# cs_piai — Centro Sanitario: PIAI/PTI

**Versión:** 19.0.1.0.0 | **Licencia:** LGPL-3 | **Autor:** Equilibrium

Plan Individualizado de Atención Integral para centros de salud mental.

## Descripción

Módulo Odoo 19 para la gestión completa del Plan Individualizado de Atención Integral (PIAI) / Plan de Tratamiento Individualizado (PTI) en centros de salud mental y residencias terapéuticas. Cubre desde la evaluación inicial hasta el alta, pasando por objetivos, intervenciones, revisiones periódicas y prevención de recaídas.

## Funcionalidades

- Formulario PIAI completo con objetivos e intervenciones
- Evaluaciones y seguimiento de evolución
- Gestión de riesgos y crisis
- Plan de prevención de recaídas
- Informe de alta terapéutica
- Monitor de adherencia al PIAI
- Revisiones periódicas programadas (cron)
- Reportes PDF: completo, resumen, alta y auditoría
- Integración con admisión y seguimiento del residente

## Dependencias

```
base, mail, cs_resident, cs_medical_care, cs_psychology,
cs_patient_followup_forms, cs_cima, cs_admission
```

## Instalación

1. Instalar primero los módulos dependientes
2. Copiar en directorio `addons` de Odoo
3. Actualizar lista de aplicaciones
4. Buscar "PIAI" e instalar

## Proyecto

Parte del ecosistema **Equilibrium** — software de gestión para centros de salud mental.
