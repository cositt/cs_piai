from odoo import models, fields

RISK_TYPE_SELECTION = [
    ('autolytic', 'Autolítico / Suicida'),
    ('heteroaggressive', 'Heteroagresivo'),
    ('escape', 'Fuga / Abandono voluntario'),
    ('relapse', 'Recaída'),
    ('intoxication', 'Intoxicación aguda'),
    ('withdrawal', 'Abstinencia / Síndrome de retirada'),
    ('medical', 'Médico / Físico'),
    ('psychiatric', 'Psiquiátrico'),
    ('legal', 'Judicial / Legal'),
    ('family', 'Familiar'),
    ('coexistence', 'Convivencial'),
    ('other', 'Otro'),
]


class PiaiRisk(models.Model):
    _name = 'cs.piai.risk'
    _description = 'Riesgo / Alerta Clínica PIAI'
    _order = 'level desc, date_start'

    piai_id = fields.Many2one('cs.piai', string='PIAI', required=True, ondelete='cascade', index=True)
    risk_type = fields.Selection(RISK_TYPE_SELECTION, string='Tipo de Riesgo', required=True)
    level = fields.Selection([
        ('low', 'Bajo'),
        ('medium', 'Moderado'),
        ('high', 'Alto'),
        ('critical', 'Crítico'),
    ], string='Nivel de Riesgo', required=True, default='medium')
    description = fields.Text(string='Descripción del Riesgo')
    preventive_measures = fields.Text(string='Medidas Preventivas')
    action_plan = fields.Text(string='Plan de Actuación')
    responsible_id = fields.Many2one('cs.worker', string='Responsable de Seguimiento')
    date_start = fields.Date(string='Fecha de Identificación', default=fields.Date.context_today)
    date_review = fields.Date(string='Fecha de Revisión')
    date_last_reviewed = fields.Date(string='Última Revisión')
    state = fields.Selection([
        ('active', 'Activo'),
        ('resolved', 'Resuelto'),
        ('monitoring', 'En seguimiento'),
    ], string='Estado', default='active', required=True)
