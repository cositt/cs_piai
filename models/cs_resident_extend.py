from odoo import models, fields, api, _
from odoo.exceptions import UserError


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
    next_review_date = fields.Date(
        related='active_piai_id.date_next_review',
        string='Próxima Revisión PIAI',
        store=True,
    )
    active_objectives_count = fields.Integer(
        compute='_compute_objective_counts',
        string='Objetivos Activos',
        store=True,
    )
    overdue_objectives_count = fields.Integer(
        compute='_compute_objective_counts',
        string='Objetivos en Retraso',
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

    @api.depends('active_piai_id', 'active_piai_id.objective_ids',
                 'active_piai_id.objective_ids.state',
                 'active_piai_id.objective_ids.expected_date')
    def _compute_objective_counts(self):
        today = fields.Date.today()
        for resident in self:
            piai = resident.active_piai_id
            if not piai:
                resident.active_objectives_count = 0
                resident.overdue_objectives_count = 0
                continue
            active_objs = piai.objective_ids.filtered(
                lambda o: o.state in ('not_started', 'in_progress')
            )
            resident.active_objectives_count = len(active_objs)
            resident.overdue_objectives_count = len(active_objs.filtered(
                lambda o: o.expected_date and o.expected_date < today
            ))

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

    def action_new_piai_review(self):
        self.ensure_one()
        if not self.active_piai_id:
            raise UserError(_('Este residente no tiene un PIAI activo.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Nueva Revisión PIAI'),
            'res_model': 'cs.piai.review',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_piai_id': self.active_piai_id.id},
        }

    def action_export_piai_pdf(self):
        self.ensure_one()
        if not self.active_piai_id:
            raise UserError(_('Este residente no tiene un PIAI activo.'))
        return self.active_piai_id.action_open_print_wizard()
