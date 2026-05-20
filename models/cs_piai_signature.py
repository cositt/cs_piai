from odoo import models, fields


class PiaiSignature(models.Model):
    _name = 'cs.piai.signature'
    _description = 'Firma y Validación PIAI'
    _order = 'date_signed desc'

    piai_id = fields.Many2one('cs.piai', required=True, ondelete='cascade', index=True)
    signature_type = fields.Selection([
        ('initial_validation', 'Validación inicial — Activación del PIAI'),
        ('review', 'Validación de revisión periódica'),
        ('modification', 'Conformidad con modificación'),
        ('discharge', 'Conformidad con plan de alta'),
        ('consent_resident', 'Consentimiento informado del residente'),
        ('consent_family', 'Consentimiento familiar / tutor legal'),
    ], string='Tipo de firma', required=True)
    worker_id = fields.Many2one('cs.worker', string='Profesional firmante')
    resident_signs = fields.Boolean(string='Residente da conformidad')
    family_signs = fields.Boolean(string='Familiar / tutor firma')
    date_signed = fields.Date(string='Fecha de firma', default=fields.Date.context_today)
    validated = fields.Boolean(string='Validado', default=False)
    notes = fields.Text(string='Observaciones')
