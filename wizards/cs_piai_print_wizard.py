from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PiaiPrintWizard(models.TransientModel):
    _name = 'cs.piai.print.wizard'
    _description = 'Asistente de Impresión PIAI'

    piai_id = fields.Many2one('cs.piai', string='PIAI', required=True, ondelete='cascade')
    report_type = fields.Selection([
        ('full', 'PIAI Completo — Historia clínica'),
        ('summary', 'Resumen para Equipo — Versión operativa'),
        ('audit', 'Para Inspección / Auditoría — Con trazabilidad completa'),
        ('monthly', 'Evolución Mensual — Notas del mes en curso'),
        ('discharge', 'Plan de Alta — Continuidad asistencial'),
    ], string='Tipo de documento', required=True, default='full')

    REPORT_MAP = {
        'full': 'cs_piai.report_cs_piai_full',
        'summary': 'cs_piai.report_cs_piai_summary',
        'audit': 'cs_piai.report_cs_piai_audit',
        'monthly': 'cs_piai.report_cs_piai_monthly',
        'discharge': 'cs_piai.report_cs_piai_discharge',
    }

    def action_print(self):
        self.ensure_one()
        report_xml_id = self.REPORT_MAP.get(self.report_type)
        if not report_xml_id:
            raise UserError(_('Tipo de informe no reconocido.'))
        return self.env.ref(report_xml_id).report_action(self.piai_id)
