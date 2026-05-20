# Guía del módulo cs_piai
## Plan Individualizado de Atención Integral — Centro AEQUILIBRIUM

---

## Índice
1. [Qué es el PIAI](#1-qué-es-el-piai)
2. [Acceso y perfiles](#2-acceso-y-perfiles)
3. [Crear un PIAI](#3-crear-un-piai)
4. [Estados y transiciones](#4-estados-y-transiciones)
5. [Secciones del formulario](#5-secciones-del-formulario)
6. [Imprimir documentos](#6-imprimir-documentos)
7. [Vista de monitoras](#7-vista-de-monitoras)
8. [Alertas automáticas](#8-alertas-automáticas)
9. [Integraciones](#9-integraciones)
10. [Preguntas frecuentes](#10-preguntas-frecuentes)

---

## 1. Qué es el PIAI

El **Plan Individualizado de Atención Integral (PIAI)** es el documento clínico central de cada residente. Recoge:

- Su diagnóstico y formulación del caso
- Los objetivos terapéuticos y las intervenciones asociadas
- El seguimiento de riesgos clínicos
- Las notas de evolución de todos los profesionales
- Las revisiones periódicas del equipo
- El plan de prevención de recaídas y el plan de alta

El módulo implementa el PIAI como estructura **relacional** (no un formulario largo): cada sección es un modelo propio vinculado al PIAI principal.

---

## 2. Acceso y perfiles

| Perfil | Menú de acceso | Permisos clave |
|---|---|---|
| **Dirección** | PIAI → Todos los PIAI | Acceso total + validar + cerrar + reabrir |
| **Psicología** | PIAI → Mis PIAI | Crear, editar área psicológica, enviar a validación |
| **Trabajo Social** | PIAI → Mis PIAI | Editar áreas social, familiar, educativa |
| **Médico / Enfermería** | PIAI → Mis PIAI | Editar área sanitaria y psiquiátrica, riesgos |
| **Monitoras** | PIAI → Vista Monitoras | Solo lectura + registrar incidencias/observaciones |
| **Administración** | — | Datos administrativos y adjuntos |

> **Monitoras:** todos comparten un único usuario. Acceden por el menú *PIAI → Residentes — Vista Monitoras*, que muestra solo los datos operativos sin contenido clínico sensible.

---

## 3. Crear un PIAI

### Creación automática
Al cerrar una **admisión** (`cs_admission`), el sistema crea automáticamente un PIAI en estado **Borrador** asociado al residente. No es necesario crearlo a mano.

### Creación manual
1. Ir a **PIAI → Todos los PIAI → Nuevo**
2. Seleccionar el residente
3. Elegir la fase terapéutica inicial
4. Asignar un profesional referente
5. Rellenar las secciones necesarias

### Requisitos para activar
El PIAI no puede activarse hasta que tenga:
- [ ] Profesional referente
- [ ] Fase terapéutica
- [ ] Fecha de elaboración
- [ ] Al menos una valoración inicial
- [ ] Al menos un objetivo (no suspendido)
- [ ] Al menos una intervención
- [ ] Fecha de próxima revisión

---

## 4. Estados y transiciones

```
Borrador ──► Pendiente de Validación ──► Activo ──► En Revisión
   │                   │                   │              │
   │                   ▼                   ▼              ▼
   │            Volver a Borrador    Cerrado (4 tipos)  Cerrado (4 tipos)
   │                                      │
   └──────────────────────────────────────┘
                    Reabrir (solo Dirección)
```

| Transición | Botón | Perfil |
|---|---|---|
| Borrador → Pendiente | Enviar a Validación | Psicología, Dirección |
| Pendiente → Activo | Activar PIAI | Dirección |
| Activo → En Revisión | Iniciar Revisión | Dirección, Psicología |
| En Revisión → Activo | Reactivar | Dirección |
| Activo/En Revisión → Cerrado | Cerrar (4 opciones) | Dirección |
| Cerrado → Activo | Reabrir | Dirección (con confirmación) |

**Tipos de cierre:** Alta Terapéutica · Alta Voluntaria · Derivación · Expulsión

---

## 5. Secciones del formulario

### 5.1 Datos generales
Referencia (auto-generada), residente, referente, fase terapéutica, versión, fechas de elaboración y próxima revisión, observaciones generales.

### 5.2 Valoraciones Iniciales
Registro por áreas. Cada área incluye: fecha, profesional, prioridad, riesgos detectados, necesidades detectadas, texto libre.

Áreas disponibles: Psicológica · Sanitaria · Psiquiátrica · Social · Educativa · Familiar · Adicciones · Laboral · Convivencial · Judicial · Otra

**Campos específicos por área:**
- **Psicológica:** sustancias, motivación al cambio (Prochaska), estado emocional, craving, riesgo autolítico, riesgo heteroagresivo
- **Sanitaria:** antecedentes, patologías, alergias, medicación actual (vinculada a CIMA), signos de abstinencia
- **Psiquiátrica:** diagnóstico previo, patología dual, nivel de estabilidad
- **Social:** situación familiar, económica, habitacional, laboral
- **Educativa:** nivel educativo, habilidades sociales, autonomía
- **Familiar:** personas implicadas, consentimiento, dinámica familiar

### 5.3 Diagnóstico / Formulación
- Diagnóstico principal
- Código CIE-10 / DSM-5
- Diagnóstico diferencial
- Formulación del caso
- Hipótesis de trabajo
- Pronóstico (Favorable / Reservado / Desfavorable)
- Patología dual

### 5.4 Objetivos Terapéuticos
Cada objetivo tiene: área, nombre, estado, responsable, indicador de seguimiento, fechas inicio/prevista/real.

**Estados:** No iniciado · En progreso · Conseguido · Parcialmente conseguido · No conseguido · Suspendido · Reformulado

**Áreas de objetivo:** Adicciones · Psicológica · Médica · Psiquiátrica · Familiar · Social · Educativa · Laboral · Convivencial · Judicial · Actividad física · Prevención de recaídas · Alta/Reinserción · Espiritual/Cultural · Otro

### 5.5 Intervenciones
Vinculadas a área y uno o varios objetivos. Campos: tipo, descripción, frecuencia, responsable, fechas, estado.

**17 tipos disponibles:** Psicoterapia individual/grupal · Entrevista motivacional · Prevención de recaídas · Terapia familiar · Seguimiento médico/psiquiátrico · Psicoeducación · Entrevista social · Coordinación externa · Control toxicológico · Actividad deportiva · Taller educativo/ocupacional · Asamblea convivencial · Gestión documental · Derivación externa · Mindfulness · Recursos comunitarios · Otro

### 5.6 Riesgos y Alertas
**11 tipos:** Autolítico · Heteroagresivo · Fuga/abandono · Recaída · Intoxicación · Abstinencia · Médico · Psiquiátrico · Judicial · Familiar · Convivencial

Cada riesgo tiene: nivel (Bajo/Moderado/Alto/Crítico), estado (Activo/Resuelto/En seguimiento), medidas preventivas, plan de actuación, responsable y fechas.

> Los riesgos **Críticos** generan una alerta visible en la ficha del residente y en la vista de monitoras.

### 5.7 Notas de Evolución
Cada entrada tiene: fecha/hora, profesional, área, objetivo relacionado, tipo (Evolución/Incidencia/Intervención/Coordinación/Familia/Crisis), contenido y adjuntos.

Usar el botón **"Nueva Nota"** para añadir. Las monitoras usan el botón equivalente en su vista simplificada.

### 5.8 Revisiones
- **Ordinarias:** mensuales
- **Extraordinarias:** ante recaída, crisis, incidente grave, cambio clínico, modificación de fase, etc.

Cada revisión registra: tipo, participantes, evolución global, cambios realizados, acuerdos, participación del residente, validación.

### 5.9 Prevención de Recaídas
Situaciones de alto riesgo, señales de aviso, estrategias de afrontamiento, plan de apoyo social, contactos de emergencia, plan de actuación ante recaída.

### 5.10 Plan Familiar y Social
**Plan familiar:** nivel de implicación, objetivos, psicoeducación, frecuencia de sesiones, plan de comunicación.

**Restricciones operativas** (visibles a monitoras): llamadas · visitas · salidas · objetos personales · medicación autoadministrada.

**Plan social:** integración social, recursos comunitarios, red de apoyo, formación/empleo.

### 5.11 Plan de Alta
*(Visible solo en estado En Revisión o Cerrado)*

**9 tipos de alta:** Terapéutica · Voluntaria · Disciplinaria · Derivación · Traslado sanitario · Finalización administrativa · Abandono · Expulsión · Exitus

Incluye: objetivos conseguidos/pendientes, recurso de derivación, plan de continuidad, seguimiento post-alta, recomendaciones, medicación al alta, firma del residente.

### 5.12 Firmas y Validaciones
Registro de firmas con tipo (validación inicial, revisión, alta, consentimiento residente, consentimiento familiar), profesional firmante y fecha.

---

## 6. Imprimir documentos

Pulse el botón **🖨 Imprimir** en el header del formulario (disponible desde estado Pendiente en adelante).

Se abrirá un selector con 5 opciones:

| Documento | Descripción | Usar para |
|---|---|---|
| **PIAI Completo** | Todas las secciones | Historia clínica, expediente del residente |
| **Resumen Equipo** | Vista operativa sin datos sensibles | Reuniones interdisciplinares |
| **Inspección / Auditoría** | Criterios de cumplimiento + trazabilidad de cambios | Inspecciones externas, auditorías |
| **Evolución Mensual** | Notas del mes en curso + estado de objetivos | Informes mensuales |
| **Plan de Alta** | Continuidad asistencial, derivación, medicación | Alta del residente |

---

## 7. Vista de monitoras

Acceder desde **PIAI → Residentes — Vista Monitoras**.

Muestra solo PIAIs activos. Secciones visibles:
- **Alertas y Restricciones:** riesgos activos de nivel medio/alto/crítico con indicaciones, y restricciones operativas del plan familiar.
- **Objetivos Convivenciales:** objetivos del área convivencial en curso.
- **Notas de Evolución:** historial de incidencias y observaciones. Botón para registrar nuevas.

> El área clínica (diagnóstico, medicación, psicología) **no es visible** para monitoras.

---

## 8. Alertas automáticas

El cron se ejecuta **diariamente**. Genera actividades (tareas) sobre el PIAI afectado cuando:

| Condición | Prioridad |
|---|---|
| PIAI en Borrador con más de 7 días | Media |
| Fecha de próxima revisión vencida | Alta |
| Riesgo **Crítico** sin revisión en 48h | Crítica |
| Riesgo **Alto** sin revisión en 7 días | Alta |
| Objetivo en progreso con fecha superada | Media |
| Revisión próxima (≤30 días) sin plan de alta | Media |

Las actividades aparecen en el chatter del PIAI y en la bandeja de actividades del usuario.

---

## 9. Integraciones

| Módulo | Comportamiento |
|---|---|
| `cs_admission` | Cierre de admisión → crea PIAI Borrador automáticamente |
| `cs_resident` | Smart button PIAI en ficha. Alerta de riesgos críticos visible |
| `cs_cima` | Medicación al ingreso/alta vinculada al catálogo AEMPS |
| `cs_medical_care` | Prescripciones y evolución clínica |
| `cs_psychology` | Sesiones psicológicas vinculables al PIAI |

---

## 10. Preguntas frecuentes

**¿Por qué no puedo activar el PIAI?**
El sistema muestra un mensaje con los requisitos que faltan. Comprueba la lista de validaciones del punto 3.

**¿Puedo tener dos PIAI activos para el mismo residente?**
No. El sistema lo impide con una restricción de unicidad. Debes cerrar el PIAI actual antes de activar uno nuevo.

**¿Cómo corrijo un cierre accidental?**
Solo Dirección puede usar el botón *"Reabrir — Volver a Activo"* que aparece en los estados Cerrado. El sistema pide confirmación.

**¿Las revisiones modifican el PIAI original?**
No. Cada revisión se guarda como un registro independiente e inmutable. El PIAI principal conserva todos sus datos históricos.

**¿Dónde veo el historial de cambios?**
En el **chatter** (panel derecho del formulario) aparecen todos los cambios de estado, con usuario, fecha y valores anterior/nuevo.

**¿Cómo exporto el PDF de auditoría?**
Botón *Imprimir* → seleccionar *"Para Inspección / Auditoría"*. Incluye tabla de cumplimiento de criterios obligatorios y el historial completo de cambios de estado.

---

*cs_piai v19.0.1.0.0 · Centro AEQUILIBRIUM · Desarrollado por Equilibrium*
