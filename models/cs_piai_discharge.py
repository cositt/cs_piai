from odoo import models, fields


class PiaiDischargePlan(models.Model):
    _name = 'cs.piai.discharge.plan'
    _description = 'Plan de Alta y Continuidad PIAI'

    piai_id = fields.Many2one('cs.piai', string='PIAI', required=True, ondelete='cascade', index=True)
    discharge_type = fields.Selection([
        ('therapeutic', 'Alta Terapéutica'),
        ('voluntary', 'Alta Voluntaria'),
        ('referral', 'Derivación a otro recurso'),
        ('expulsion', 'Expulsión'),
        ('death', 'Exitus'),
    ], string='Tipo de Alta', required=True)
    expected_date = fields.Date(string='Fecha Prevista de Alta')
    achieved_objectives = fields.Text(string='Objetivos Conseguidos')
    pending_objectives = fields.Text(string='Objetivos Pendientes')
    referral_resource = fields.Char(string='Recurso de Derivación')
    referral_contact = fields.Char(string='Contacto del Recurso')
    continuity_treatment = fields.Text(string='Plan de Tratamiento de Continuidad')
    follow_up_plan = fields.Text(string='Plan de Seguimiento Post-Alta')
    recommendations = fields.Text(string='Recomendaciones al Alta')
    medication_at_discharge = fields.Many2many(
        'cs.drug.catalog',
        'piai_discharge_drug_rel',
        'discharge_id', 'drug_id',
        string='Medicación al Alta',
    )
    family_informed = fields.Boolean(string='Familia Informada')
    user_signed = fields.Boolean(string='Residente Firma')
    notes = fields.Text(string='Observaciones')
