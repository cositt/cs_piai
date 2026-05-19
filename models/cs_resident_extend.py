from odoo import models, fields, api


class ResidentPiaiExtend(models.Model):
    _inherit = 'cs.resident'

    piai_ids = fields.One2many('cs.piai', 'resident_id', string='PIAIs')
    piai_count = fields.Integer(compute='_compute_piai_count', string='PIAIs')
    active_piai_id = fields.Many2one(
        'cs.piai', string='PIAI Activo',
        compute='_compute_active_piai',
        store=True,
    )
    critical_risk_count = fields.Integer(
        compute='_compute_active_piai', string='Riesgos Críticos', store=True,
    )
    therapeutic_phase = fields.Selection(
        related='active_piai_id.therapeutic_phase',
        string='Fase Terapéutica',
        store=True,
    )

    @api.depends('piai_ids')
    def _compute_piai_count(self):
        for resident in self:
            resident.piai_count = len(resident.piai_ids)

    @api.depends('piai_ids', 'piai_ids.state', 'piai_ids.risk_ids', 'piai_ids.risk_ids.level',
                 'piai_ids.risk_ids.state')
    def _compute_active_piai(self):
        for resident in self:
            active = resident.piai_ids.filtered(lambda p: p.state == 'active')
            resident.active_piai_id = active[:1] if active else False
            if active:
                critical = active[0].risk_ids.filtered(
                    lambda r: r.level == 'critical' and r.state == 'active'
                )
                resident.critical_risk_count = len(critical)
            else:
                resident.critical_risk_count = 0

    def action_view_piai(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'PIAI',
            'res_model': 'cs.piai',
            'view_mode': 'list,form',
            'domain': [('resident_id', '=', self.id)],
            'context': {'default_resident_id': self.id},
        }
