from odoo import models, fields


class PiaiReview(models.Model):
    _name = 'cs.piai.review'
    _description = 'Revisión del PIAI'
    _order = 'review_date desc'

    piai_id = fields.Many2one('cs.piai', string='PIAI', required=True, ondelete='cascade', index=True)
    review_date = fields.Date(string='Fecha de Revisión', required=True, default=fields.Date.context_today)
    review_type = fields.Selection([
        ('ordinary', 'Ordinaria (mensual)'),
        ('extraordinary', 'Extraordinaria'),
    ], string='Tipo de Revisión', required=True, default='ordinary')
    reason = fields.Text(string='Motivo (si es extraordinaria)')
    participant_ids = fields.Many2many(
        'cs.worker',
        'piai_review_participant_rel',
        'review_id', 'worker_id',
        string='Participantes',
    )
    overall_evolution = fields.Selection([
        ('very_favorable', 'Muy favorable'),
        ('favorable', 'Favorable'),
        ('stable', 'Estable'),
        ('irregular', 'Irregular'),
        ('unfavorable', 'Desfavorable'),
    ], string='Evolución Global')
    changes_made = fields.Text(string='Cambios Realizados')
    agreements = fields.Text(string='Acuerdos')
    user_participates = fields.Boolean(string='Participa el Residente')
    info_transferred_to_user = fields.Boolean(string='Información Trasladada al Residente')
    next_review_date = fields.Date(string='Próxima Revisión Prevista')
    validated_by = fields.Many2one('cs.worker', string='Validado por')
    validated_date = fields.Date(string='Fecha de Validación')
