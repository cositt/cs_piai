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
    relapse_prevention_ids = fields.One2many('cs.piai.relapse.prevention', 'piai_id', string='Plan de Prevención de Recaídas')
    discharge_plan_id = fields.Many2one(
        'cs.piai.discharge.plan', string='Plan de Alta',
        ondelete='set null',
    )
    diagnosis_ids = fields.One2many('cs.piai.diagnosis', 'piai_id', string='Diagnóstico / Formulación')
    family_plan_ids = fields.One2many('cs.piai.family.plan', 'piai_id', string='Plan Familiar y Social')
    signature_ids = fields.One2many('cs.piai.signature', 'piai_id', string='Firmas y Validaciones')

    # ─── Registros cruzados (lectura automática desde otros módulos) ─────────
    medical_consultation_ids = fields.Many2many(
        'cs.medical.consultation', compute='_compute_cross_module_records',
        string='Consultas Médicas')
    prescription_ids = fields.Many2many(
        'cs.prescription', compute='_compute_cross_module_records',
        string='Prescripciones')
    rescue_ids = fields.Many2many(
        'cs.medical.rescue', compute='_compute_cross_module_records',
        string='Rescates e Intervenciones')
    psychology_session_ids = fields.Many2many(
        'cs.psychology.session', compute='_compute_cross_module_records',
        string='Sesiones Psicología')
    family_call_ids = fields.Many2many(
        'cs.family.call', compute='_compute_cross_module_records',
        string='Llamadas Familiares')

    medical_consultation_count = fields.Integer(
        compute='_compute_cross_module_records', string='Consultas Médicas')
    prescription_count = fields.Integer(
        compute='_compute_cross_module_records', string='Prescripciones')
    rescue_count = fields.Integer(
        compute='_compute_cross_module_records', string='Rescates')
    psychology_session_count = fields.Integer(
        compute='_compute_cross_module_records', string='Sesiones Psicología')
    family_call_count = fields.Integer(
        compute='_compute_cross_module_records', string='Llamadas Familiares')

    @api.depends('resident_id')
    def _compute_cross_module_records(self):
        for piai in self:
            rid = piai.resident_id.id
            if not rid:
                piai.medical_consultation_ids = self.env['cs.medical.consultation']
                piai.prescription_ids = self.env['cs.prescription']
                piai.rescue_ids = self.env['cs.medical.rescue']
                piai.psychology_session_ids = self.env['cs.psychology.session']
                piai.family_call_ids = self.env['cs.family.call']
                piai.medical_consultation_count = 0
                piai.prescription_count = 0
                piai.rescue_count = 0
                piai.psychology_session_count = 0
                piai.family_call_count = 0
                continue
            domain = [('resident_id', '=', rid)]
            consultations = self.env['cs.medical.consultation'].search(
                domain, order='consultation_date desc')
            prescriptions = self.env['cs.prescription'].search(
                domain, order='prescription_date desc')
            rescues = self.env['cs.medical.rescue'].search(
                domain, order='intervention_datetime desc')
            sessions = self.env['cs.psychology.session'].search(
                domain, order='session_date desc')
            calls = self.env['cs.family.call'].search(domain)
            piai.medical_consultation_ids = consultations
            piai.prescription_ids = prescriptions
            piai.rescue_ids = rescues
            piai.psychology_session_ids = sessions
            piai.family_call_ids = calls
            piai.medical_consultation_count = len(consultations)
            piai.prescription_count = len(prescriptions)
            piai.rescue_count = len(rescues)
            piai.psychology_session_count = len(sessions)
            piai.family_call_count = len(calls)

    def action_view_consultations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Consultas Médicas — %s') % self.resident_id.name,
            'res_model': 'cs.medical.consultation',
            'view_mode': 'list,form',
            'domain': [('resident_id', '=', self.resident_id.id)],
            'context': {'default_resident_id': self.resident_id.id},
        }

    def action_view_prescriptions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Prescripciones — %s') % self.resident_id.name,
            'res_model': 'cs.prescription',
            'view_mode': 'list,form',
            'domain': [('resident_id', '=', self.resident_id.id)],
            'context': {'default_resident_id': self.resident_id.id},
        }

    def action_view_rescues(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Rescates — %s') % self.resident_id.name,
            'res_model': 'cs.medical.rescue',
            'view_mode': 'list,form',
            'domain': [('resident_id', '=', self.resident_id.id)],
            'context': {'default_resident_id': self.resident_id.id},
        }

    def action_view_psychology_sessions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sesiones Psicología — %s') % self.resident_id.name,
            'res_model': 'cs.psychology.session',
            'view_mode': 'list,form',
            'domain': [('resident_id', '=', self.resident_id.id)],
            'context': {'default_resident_id': self.resident_id.id},
        }

    def action_view_family_calls(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Llamadas Familiares — %s') % self.resident_id.name,
            'res_model': 'cs.family.call',
            'view_mode': 'list,form',
            'domain': [('resident_id', '=', self.resident_id.id)],
            'context': {'default_resident_id': self.resident_id.id},
        }

    # ─── LOPD / Consentimiento informado ──────────────────────────────────
    lopd_consent = fields.Boolean(string='Consentimiento LOPD firmado', tracking=True)
    lopd_consent_date = fields.Date(string='Fecha consentimiento LOPD')
    lopd_notes = fields.Text(string='Observaciones LOPD / protección de datos')

    # ─── Fecha de ingreso (relay desde admisión) ──────────────────────────
    date_admission = fields.Date(
        compute='_compute_date_admission',
        string='Fecha de Ingreso',
        store=True,
    )

    @api.depends('resident_id')
    def _compute_date_admission(self):
        Admission = self.env['cs.admission.process']
        for piai in self:
            if not piai.resident_id:
                piai.date_admission = False
                continue
            admission = Admission.search(
                [('resident_id', '=', piai.resident_id.id)],
                order='admission_date desc',
                limit=1,
            )
            piai.date_admission = admission.admission_date if admission else False

    # ─── Restricciones (relay desde plan familiar para vista monitoras) ───
    restrictions_calls = fields.Text(compute='_compute_restrictions', string='Restricciones Llamadas')
    restrictions_visits = fields.Text(compute='_compute_restrictions', string='Restricciones Visitas')
    restrictions_outings = fields.Text(compute='_compute_restrictions', string='Restricciones Salidas')
    restrictions_objects = fields.Text(compute='_compute_restrictions', string='Restricciones Objetos')
    restrictions_medication = fields.Text(compute='_compute_restrictions', string='Restricciones Medicación')

    @api.depends('family_plan_ids', 'family_plan_ids.restrictions_calls',
                 'family_plan_ids.restrictions_visits', 'family_plan_ids.restrictions_outings',
                 'family_plan_ids.restrictions_objects', 'family_plan_ids.restrictions_medication')
    def _compute_restrictions(self):
        for piai in self:
            fp = piai.family_plan_ids[:1]
            piai.restrictions_calls = fp.restrictions_calls if fp else False
            piai.restrictions_visits = fp.restrictions_visits if fp else False
            piai.restrictions_outings = fp.restrictions_outings if fp else False
            piai.restrictions_objects = fp.restrictions_objects if fp else False
            piai.restrictions_medication = fp.restrictions_medication if fp else False

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

        # Riesgo alto sin revisión en 7 días
        high_risks = self.env['cs.piai.risk'].search([
            ('level', '=', 'high'),
            ('state', '=', 'active'),
            '|',
            ('date_last_reviewed', '=', False),
            ('date_last_reviewed', '<', today - timedelta(days=7)),
        ])
        for risk in high_risks:
            risk.piai_id.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_('Riesgo alto sin revisión en 7 días: %s') % risk.risk_type,
                user_id=self.env.uid,
            )

        # Alta prevista sin plan de alta registrado
        no_discharge_plan = self.search([
            ('state', 'in', ['active', 'in_review']),
            ('discharge_plan_id', '=', False),
            ('date_next_review', '<=', today + timedelta(days=30)),
            ('date_next_review', '!=', False),
        ])
        for piai in no_discharge_plan:
            piai.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_('Revisión próxima sin plan de alta registrado'),
                user_id=self.env.uid,
            )

        # PIAI activo sin firma de validación inicial
        active_piais = self.search([('state', '=', 'active')])
        unsigned = active_piais.filtered(
            lambda p: not p.signature_ids.filtered(
                lambda s: s.signature_type == 'initial_validation' and s.validated
            )
        )
        for piai in unsigned:
            piai.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_('PIAI activo sin firma de validación inicial registrada'),
                user_id=self.env.uid,
            )

        _logger.info(
            'PIAI cron alerts processed: draft=%d, overdue=%d, critical=%d, high=%d, obj=%d, no_discharge=%d, unsigned=%d',
            len(draft_7d), len(overdue), len(critical_risks), len(high_risks),
            len(overdue_obj), len(no_discharge_plan), len(unsigned),
        )

    # ─── Acciones de vista ────────────────────────────────────────────────
    def action_view_objectives(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Objetivos — %s') % self.name,
            'res_model': 'cs.piai.objective',
            'view_mode': 'list,form',
            'domain': [('piai_id', '=', self.id)],
            'context': {'default_piai_id': self.id},
        }

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

    def action_new_review(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Nueva Revisión PIAI'),
            'res_model': 'cs.piai.review',
            'view_mode': 'form',
            'target': 'new',
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

    @api.model
    def _cron_monthly_review_reminder(self):
        today = fields.Date.today()
        cutoff = today - timedelta(days=30)
        active_piais = self.search([('state', '=', 'active')])
        for piai in active_piais:
            last_review = self.env['cs.piai.review'].search(
                [('piai_id', '=', piai.id)],
                order='review_date desc',
                limit=1,
            )
            if not last_review or last_review.review_date < cutoff:
                piai.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=_('Revisión ordinaria mensual pendiente de programar'),
                    user_id=self.env.uid,
                )
        _logger.info('PIAI cron monthly review: %d reminders generated', len(active_piais))

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
