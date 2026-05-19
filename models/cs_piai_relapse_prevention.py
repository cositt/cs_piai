from odoo import models, fields


class PiaiRelapsePrevention(models.Model):
    _name = 'cs.piai.relapse.prevention'
    _description = 'Plan de Prevención de Recaídas PIAI'

    piai_id = fields.Many2one('cs.piai', string='PIAI', required=True, ondelete='cascade', index=True)
    high_risk_situations = fields.Text(string='Situaciones de Alto Riesgo')
    warning_signs = fields.Text(string='Señales de Aviso')
    coping_strategies = fields.Text(string='Estrategias de Afrontamiento')
    social_support_plan = fields.Text(string='Plan de Apoyo Social')
    emergency_contacts = fields.Text(string='Contactos de Emergencia')
    action_plan_relapse = fields.Text(string='Plan de Actuación ante Recaída')
    psychoeducation_completed = fields.Boolean(string='Psicoeducación sobre recaídas completada')
    emergency_resources = fields.Text(string='Recursos de Emergencia Conocidos')
    notes = fields.Text(string='Observaciones Adicionales')
