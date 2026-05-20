from odoo import models, fields


class PiaiFamilyPlan(models.Model):
    _name = 'cs.piai.family.plan'
    _description = 'Plan Familiar y Social PIAI'

    piai_id = fields.Many2one('cs.piai', required=True, ondelete='cascade', index=True)

    # ─── Plan familiar ─────────────────────────────────────────────────────
    family_involvement_level = fields.Selection([
        ('none', 'Sin implicación'),
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    ], string='Nivel de implicación familiar', default='medium')
    family_goals = fields.Text(string='Objetivos con la familia')
    family_education = fields.Text(string='Psicoeducación familiar')
    family_sessions_frequency = fields.Selection([
        ('weekly', 'Semanal'),
        ('biweekly', 'Quincenal'),
        ('monthly', 'Mensual'),
        ('as_needed', 'Según necesidad'),
        ('none', 'Sin sesiones programadas'),
    ], string='Frecuencia de sesiones familiares')
    communication_plan = fields.Text(string='Plan de comunicación con familia')
    next_family_session = fields.Date(string='Próxima sesión familiar')
    responsible_worker_id = fields.Many2one('cs.worker', string='Trabajador/a Social responsable')

    # ─── Restricciones operativas (visibles a monitoras) ──────────────────
    restrictions_calls = fields.Text(string='Restricciones — Llamadas')
    restrictions_visits = fields.Text(string='Restricciones — Visitas')
    restrictions_outings = fields.Text(string='Restricciones — Salidas')
    restrictions_objects = fields.Text(string='Restricciones — Objetos personales')
    restrictions_medication = fields.Text(string='Restricciones — Medicación autoadministrada')

    # ─── Plan social ───────────────────────────────────────────────────────
    social_integration_goals = fields.Text(string='Objetivos de integración social')
    community_resources = fields.Text(string='Recursos comunitarios identificados')
    social_network_plan = fields.Text(string='Plan de red de apoyo social')
    employment_training_plan = fields.Text(string='Plan de formación / empleo')

    notes = fields.Text(string='Observaciones')
