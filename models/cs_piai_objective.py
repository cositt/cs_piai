from odoo import models, fields

AREA_SELECTION = [
    ('addiction', 'Adicciones'),
    ('psychological', 'Psicológica'),
    ('psychiatric', 'Psiquiátrica'),
    ('medical', 'Médica/Sanitaria'),
    ('social', 'Social'),
    ('educational', 'Educativa'),
    ('family', 'Familiar'),
    ('labor', 'Laboral'),
    ('leisure', 'Ocio y Tiempo Libre'),
    ('coexistence', 'Convivencial'),
    ('legal', 'Judicial/Legal'),
    ('physical_health', 'Actividad física / Hábitos saludables'),
    ('relapse_prevention', 'Prevención de recaídas'),
    ('discharge_reintegration', 'Alta / Reinserción'),
    ('spiritual', 'Espiritual/Cultural'),
    ('other', 'Otro'),
]

OBJECTIVE_STATE = [
    ('not_started', 'No iniciado'),
    ('in_progress', 'En progreso'),
    ('achieved', 'Conseguido'),
    ('partially_achieved', 'Parcialmente conseguido'),
    ('not_achieved', 'No conseguido'),
    ('suspended', 'Suspendido'),
    ('reformulated', 'Reformulado'),
]


class PiaiObjective(models.Model):
    _name = 'cs.piai.objective'
    _description = 'Objetivo Terapéutico PIAI'
    _order = 'area, name'

    piai_id = fields.Many2one('cs.piai', string='PIAI', required=True, ondelete='cascade', index=True)
    name = fields.Char(string='Objetivo', required=True)
    area = fields.Selection(AREA_SELECTION, string='Área', required=True)
    state = fields.Selection(OBJECTIVE_STATE, string='Estado', default='not_started', required=True)
    responsible_id = fields.Many2one('cs.worker', string='Responsable')
    indicator = fields.Text(string='Indicador de Seguimiento')
    start_date = fields.Date(string='Fecha de Inicio')
    expected_date = fields.Date(string='Fecha Prevista')
    actual_date = fields.Date(string='Fecha Real')
    notes = fields.Text(string='Observaciones')
    sequence = fields.Integer(string='Secuencia', default=10)
