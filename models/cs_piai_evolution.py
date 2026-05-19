from odoo import models, fields
from .cs_piai_objective import AREA_SELECTION


class PiaiEvolution(models.Model):
    _name = 'cs.piai.evolution'
    _description = 'Nota de Evolución PIAI'
    _order = 'datetime desc'

    piai_id = fields.Many2one('cs.piai', string='PIAI', required=True, ondelete='cascade', index=True)
    datetime = fields.Datetime(string='Fecha y Hora', default=fields.Datetime.now, required=True)
    professional_id = fields.Many2one('cs.worker', string='Profesional')
    area = fields.Selection(AREA_SELECTION, string='Área')
    objective_id = fields.Many2one('cs.piai.objective', string='Objetivo Relacionado')
    note_type = fields.Selection([
        ('evolution', 'Evolución'),
        ('incident', 'Incidencia'),
        ('intervention', 'Intervención'),
        ('coordination', 'Coordinación'),
        ('family', 'Familia'),
        ('crisis', 'Crisis'),
    ], string='Tipo de Nota', required=True, default='evolution')
    content = fields.Text(string='Contenido', required=True)
    requires_piai_review = fields.Boolean(string='Requiere Revisión del PIAI')
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'piai_evolution_attachment_rel',
        'evolution_id', 'attachment_id',
        string='Adjuntos',
    )
