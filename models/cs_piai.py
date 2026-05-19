import logging
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

PIAI_STATES = [
    ('draft', 'Borrador'),
    ('pending', 'Pendiente de Validación'),
    ('active', 'Activo'),
    ('in_review', 'En Revisión'),
    ('closed_discharge', 'Cerrado — Alta Terapéutica'),
    ('closed_voluntary', 'Cerrado — Alta Voluntaria'),
    ('closed_referral', 'Cerrado — Derivado'),
    ('closed_expulsion', 'Cerrado — Expulsión'),
]

THERAPEUTIC_PHASES = [
    ('acogida', 'Acogida / Admisión'),
    ('evaluacion', 'Evaluación'),
    ('desintoxicacion', 'Desintoxicación'),
    ('deshabituacion', 'Deshabituación'),
    ('rehabilitacion', 'Rehabilitación'),
    ('reinsercion', 'Reinserción Social'),
    ('preparacion_alta', 'Preparación al Alta'),
    ('seguimiento_post_alta', 'Seguimiento Post-Alta'),
]


class Piai(models.Model):
    _name = 'cs.piai'
    _description = 'Plan Individualizado de Atención Integral'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_elaboration desc, id desc'

    name = fields.Char(string='Referencia', readonly=True, copy=False, default='Nuevo')

    resident_id = fields.Many2one(
        'cs.resident', string='Residente', required=True, ondelete='restrict',
        index=True, tracking=True,
    )
    state = fields.Selection(PIAI_STATES, string='Estado', default='draft', required=True, tracking=True)
    version = fields.Integer(string='Versión', default=1, readonly=True)
    therapeutic_phase = fields.Selection(
        THERAPEUTIC_PHASES, string='Fase Terapéutica', required=True, tracking=True,
    )
    referent_id = fields.Many2one('cs.worker', string='Profesional Referente', tracking=True)
    date_elaboration = fields.Date(string='Fecha de Elaboración', required=True, default=fields.Date.context_today)
    date_next_review = fields.Date(string='Fecha Próxima Revisión', tracking=True)
    general_observations = fields.Text(string='Observaciones Generales')

    # ─── Relaciones One2many ───────────────────────────────────────────────
    assessment_ids = fields.One2many('cs.piai.assessment', 'piai_id', string='Valoraciones Iniciales')
    objective_ids = fields.One2many('cs.piai.objective', 'piai_id', string='Objetivos')
    intervention_ids = fields.One2many('cs.piai.intervention', 'piai_id', string='Intervenciones')
    risk_ids = fields.One2many('cs.piai.risk', 'piai_id', string='Riesgos y Alertas')
    review_ids = fields.One2many('cs.piai.review', 'piai_id', string='Revisiones')
    evolution_ids = fields.One2many('cs.piai.evolution', 'piai_id', string='Notas de Evolución')
    relapse_prevention_id = fields.Many2one(
        'cs.piai.relapse.prevention', string='Plan de Prevención de Recaídas',
        ondelete='set null',
    )
    discharge_plan_id = fields.Many2one(
        'cs.piai.discharge.plan', string='Plan de Alta',
        ondelete='set null',
    )

    # ─── Campos compute / contadores ──────────────────────────────────────
    objective_count = fields.Integer(compute='_compute_counts', string='Objetivos', store=True)
    active_risk_count = fields.Integer(compute='_compute_counts', string='Riesgos Activos', store=True)
    critical_risk_count = fields.Integer(compute='_compute_counts', string='Riesgos Críticos', store=True)
    review_overdue = fields.Boolean(compute='_compute_counts', string='Revisión Vencida', store=True)

    @api.depends('objective_ids', 'objective_ids.state', 'risk_ids', 'risk_ids.state',
                 'risk_ids.level', 'date_next_review')
    def _compute_counts(self):
        today = fields.Date.today()
        for piai in self:
            piai.objective_count = len(piai.objective_ids.filtered(lambda o: o.state != 'suspended'))
            active_risks = piai.risk_ids.filtered(lambda r: r.state == 'active')
            piai.active_risk_count = len(active_risks)
            piai.critical_risk_count = len(active_risks.filtered(lambda r: r.level == 'critical'))
            piai.review_overdue = bool(piai.date_next_review and piai.date_next_review < today)

    # ─── Restricción: solo un PIAI activo por residente ───────────────────
    @api.constrains('state', 'resident_id')
    def _check_unique_active(self):
        for piai in self:
            if piai.state == 'active':
                other = self.search([
                    ('resident_id', '=', piai.resident_id.id),
                    ('state', '=', 'active'),
                    ('id', '!=', piai.id),
                ])
                if other:
                    raise ValidationError(_(
                        'El residente %s ya tiene un PIAI activo. '
                        'Cierre el PIAI actual antes de activar uno nuevo.'
                    ) % piai.resident_id.name)

    # ─── Ciclo de vida ────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('cs.piai') or 'Nuevo'
        return super().create(vals_list)

    def _validate_for_activation(self):
        self.ensure_one()
        errors = []
        if not self.date_elaboration:
            errors.append(_('Falta la fecha de elaboración.'))
        if not self.referent_id:
            errors.append(_('Falta el profesional referente.'))
        if not self.therapeutic_phase:
            errors.append(_('Falta la fase terapéutica.'))
        if not self.assessment_ids:
            errors.append(_('Debe existir al menos una valoración inicial.'))
        active_objectives = self.objective_ids.filtered(lambda o: o.state != 'suspended')
        if not active_objectives:
            errors.append(_('Debe existir al menos un objetivo activo.'))
        if not self.intervention_ids:
            errors.append(_('Debe existir al menos una intervención.'))
        if not self.date_next_review:
            errors.append(_('Falta la fecha de próxima revisión.'))
        return errors

    def action_set_pending(self):
        self.write({'state': 'pending'})

    def action_activate(self):
        for piai in self:
            errors = piai._validate_for_activation()
            if errors:
                raise UserError('\n'.join(errors))
        self.write({'state': 'active'})

    def action_set_review(self):
        self.write({'state': 'in_review'})

    def action_close_discharge(self):
        self.write({'state': 'closed_discharge'})

    def action_close_voluntary(self):
        self.write({'state': 'closed_voluntary'})

    def action_close_referral(self):
        self.write({'state': 'closed_referral'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_reopen(self):
        self.write({'state': 'active'})

    # ─── Cron: verificar alertas diarias ─────────────────────────────────
    @api.model
    def _cron_check_alerts(self):
        today = fields.Date.today()
        now = fields.Datetime.now()
        threshold_48h = now - timedelta(hours=48)

        # PIAI en borrador > 7 días
        draft_7d = self.search([
            ('state', '=', 'draft'),
            ('date_elaboration', '<=', today - timedelta(days=7)),
        ])
        for piai in draft_7d:
            piai.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_('PIAI en borrador desde hace más de 7 días'),
                user_id=self.env.uid,
            )

        # Revisión vencida
        overdue = self.search([
            ('state', 'in', ['active', 'in_review']),
            ('date_next_review', '<', today),
        ])
        for piai in overdue:
            piai.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_('Revisión del PIAI vencida'),
                user_id=self.env.uid,
            )

        # Riesgos críticos sin revisión en 48h
        critical_risks = self.env['cs.piai.risk'].search([
            ('level', '=', 'critical'),
            ('state', '=', 'active'),
            '|',
            ('date_last_reviewed', '=', False),
            ('date_last_reviewed', '<', threshold_48h.date()),
        ])
        for risk in critical_risks:
            risk.piai_id.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_('Riesgo crítico sin revisión en 48h: %s') % risk.risk_type,
                user_id=self.env.uid,
            )

        # Objetivos con fecha vencida en progreso
        overdue_obj = self.env['cs.piai.objective'].search([
            ('state', '=', 'in_progress'),
            ('expected_date', '<', today),
        ])
        for obj in overdue_obj:
            obj.piai_id.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_('Objetivo vencido: %s') % obj.name,
                user_id=self.env.uid,
            )

        _logger.info('PIAI cron alerts processed: draft=%d, overdue=%d, critical=%d, obj=%d',
                     len(draft_7d), len(overdue), len(critical_risks), len(overdue_obj))

    # ─── Acciones de vista ────────────────────────────────────────────────
    def action_view_evolutions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Notas de Evolución — %s') % self.name,
            'res_model': 'cs.piai.evolution',
            'view_mode': 'list,form',
            'domain': [('piai_id', '=', self.id)],
            'context': {'default_piai_id': self.id},
        }

    def action_add_evolution(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Nueva Nota de Evolución'),
            'res_model': 'cs.piai.evolution',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_piai_id': self.id},
        }

    def action_open_print_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Imprimir PIAI'),
            'res_model': 'cs.piai.print.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_piai_id': self.id},
        }
