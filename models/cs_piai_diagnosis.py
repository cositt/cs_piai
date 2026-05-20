from odoo import models, fields


class PiaiDiagnosis(models.Model):
    _name = 'cs.piai.diagnosis'
    _description = 'Diagnóstico y Formulación del Caso PIAI'

    piai_id = fields.Many2one('cs.piai', required=True, ondelete='cascade', index=True)
    date_diagnosis = fields.Date(string='Fecha del diagnóstico', default=fields.Date.context_today)
    professional_id = fields.Many2one('cs.worker', string='Profesional responsable')

    main_diagnosis = fields.Text(string='Diagnóstico Principal')
    cie10_code = fields.Char(string='Código CIE-10', size=20)
    dsm5_code = fields.Char(string='Código DSM-5', size=20)
    differential_diagnosis = fields.Text(string='Diagnóstico Diferencial')

    dual_pathology = fields.Boolean(string='Patología Dual')
    dual_pathology_notes = fields.Text(string='Notas Patología Dual')

    case_formulation = fields.Text(string='Formulación del Caso')
    working_hypothesis = fields.Text(string='Hipótesis de Trabajo')

    prognosis = fields.Selection([
        ('favorable', 'Favorable'),
        ('reserved', 'Reservado'),
        ('unfavorable', 'Desfavorable'),
    ], string='Pronóstico')
    notes = fields.Text(string='Observaciones adicionales')
