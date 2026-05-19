from datetime import date, timedelta
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError


class TestCsPiai(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env['res.partner'].create({'name': 'Profesional Test PIAI'})
        cls.worker = cls.env['cs.worker'].create({
            'partner_id': partner.id,
            'job_title': 'psicólogo',
        })
        cls.residence = cls.env['cs.residence'].create({
            'name': 'Residencia Test PIAI',
            'code': 'TST',
        })
        cls.resident = cls.env['cs.resident'].create({
            'name': 'Residente Test PIAI',
            'dni': '00000001T',
            'fecha_nacimiento': '1980-01-01',
            'residence_id': cls.residence.id,
        })
        cls.resident2 = cls.env['cs.resident'].create({
            'name': 'Residente Test PIAI 2',
            'dni': '00000002T',
            'fecha_nacimiento': '1985-06-15',
            'residence_id': cls.residence.id,
        })

    def _make_piai(self, resident=None, **kwargs):
        defaults = {
            'resident_id': (resident or self.resident).id,
            'therapeutic_phase': 'evaluacion',
            'referent_id': self.worker.id,
            'date_elaboration': date.today(),
            'date_next_review': date.today() + timedelta(days=30),
        }
        defaults.update(kwargs)
        return self.env['cs.piai'].create(defaults)

    def _make_activatable_piai(self, resident=None):
        piai = self._make_piai(resident=resident)
        self.env['cs.piai.assessment'].create({
            'piai_id': piai.id,
            'area_type': 'psychological',
            'date_assessment': date.today(),
        })
        self.env['cs.piai.objective'].create({
            'piai_id': piai.id,
            'name': 'Objetivo Test',
            'area': 'psychological',
            'state': 'not_started',
        })
        self.env['cs.piai.intervention'].create({
            'piai_id': piai.id,
            'area': 'psychological',
            'intervention_type': 'individual_psychotherapy',
        })
        return piai

    # ─── Secuencia y estado inicial ────────────────────────────────────────

    def test_sequence_assigned_on_create(self):
        piai = self._make_piai()
        self.assertTrue(piai.name.startswith('PIAI-'))

    def test_default_state_is_draft(self):
        piai = self._make_piai()
        self.assertEqual(piai.state, 'draft')

    # ─── Transiciones de estado ─────────────────────────────────────────────

    def test_action_set_pending(self):
        piai = self._make_piai()
        piai.action_set_pending()
        self.assertEqual(piai.state, 'pending')

    def test_action_activate_fails_without_assessments(self):
        piai = self._make_piai()
        with self.assertRaises(UserError):
            piai.action_activate()

    def test_action_activate_fails_without_objectives(self):
        piai = self._make_piai()
        self.env['cs.piai.assessment'].create({
            'piai_id': piai.id,
            'area_type': 'psychological',
        })
        with self.assertRaises(UserError):
            piai.action_activate()

    def test_action_activate_fails_without_interventions(self):
        piai = self._make_piai()
        self.env['cs.piai.assessment'].create({'piai_id': piai.id, 'area_type': 'psychological'})
        self.env['cs.piai.objective'].create({'piai_id': piai.id, 'name': 'Obj', 'area': 'psychological'})
        with self.assertRaises(UserError):
            piai.action_activate()

    def test_action_activate_success(self):
        piai = self._make_activatable_piai()
        piai.action_activate()
        self.assertEqual(piai.state, 'active')

    def test_action_reset_draft(self):
        piai = self._make_piai()
        piai.action_set_pending()
        piai.action_reset_draft()
        self.assertEqual(piai.state, 'draft')

    def test_action_set_review(self):
        piai = self._make_activatable_piai()
        piai.action_activate()
        piai.action_set_review()
        self.assertEqual(piai.state, 'in_review')

    def test_action_close_discharge(self):
        piai = self._make_activatable_piai()
        piai.action_activate()
        piai.action_close_discharge()
        self.assertEqual(piai.state, 'closed_discharge')

    def test_action_close_voluntary(self):
        piai = self._make_activatable_piai()
        piai.action_activate()
        piai.action_close_voluntary()
        self.assertEqual(piai.state, 'closed_voluntary')

    # ─── Constraint único PIAI activo ───────────────────────────────────────

    def test_unique_active_piai_constraint(self):
        piai1 = self._make_activatable_piai()
        piai1.action_activate()

        piai2 = self._make_activatable_piai()
        with self.assertRaises(ValidationError):
            piai2.action_activate()

    def test_second_piai_allowed_after_closing_first(self):
        piai1 = self._make_activatable_piai()
        piai1.action_activate()
        piai1.action_close_discharge()

        piai2 = self._make_activatable_piai()
        piai2.action_activate()
        self.assertEqual(piai2.state, 'active')

    # ─── Campos computed ────────────────────────────────────────────────────

    def test_review_overdue_is_true_when_past_due(self):
        piai = self._make_piai(date_next_review=date.today() - timedelta(days=1))
        self.assertTrue(piai.review_overdue)

    def test_review_overdue_is_false_when_future(self):
        piai = self._make_piai(date_next_review=date.today() + timedelta(days=1))
        self.assertFalse(piai.review_overdue)

    def test_objective_count(self):
        piai = self._make_piai()
        self.env['cs.piai.objective'].create({'piai_id': piai.id, 'name': 'Obj 1', 'area': 'psychological'})
        self.env['cs.piai.objective'].create({'piai_id': piai.id, 'name': 'Obj 2', 'area': 'social'})
        self.env['cs.piai.objective'].create({
            'piai_id': piai.id, 'name': 'Obj Susp', 'area': 'medical', 'state': 'suspended',
        })
        self.assertEqual(piai.objective_count, 2)

    def test_critical_risk_count(self):
        piai = self._make_piai()
        self.env['cs.piai.risk'].create({
            'piai_id': piai.id,
            'risk_type': 'autolytic',
            'level': 'critical',
            'state': 'active',
        })
        self.env['cs.piai.risk'].create({
            'piai_id': piai.id,
            'risk_type': 'relapse',
            'level': 'high',
            'state': 'active',
        })
        self.assertEqual(piai.critical_risk_count, 1)
        self.assertEqual(piai.active_risk_count, 2)

    # ─── Extensión cs.resident ──────────────────────────────────────────────

    def test_resident_piai_count(self):
        self._make_piai()
        self._make_piai()
        self.assertEqual(self.resident.piai_count, 2)

    def test_resident_active_piai_id(self):
        piai = self._make_activatable_piai()
        piai.action_activate()
        self.assertEqual(self.resident.active_piai_id, piai)

    def test_resident_critical_risk_count(self):
        piai = self._make_activatable_piai()
        piai.action_activate()
        self.env['cs.piai.risk'].create({
            'piai_id': piai.id,
            'risk_type': 'autolytic',
            'level': 'critical',
            'state': 'active',
        })
        self.assertEqual(self.resident.critical_risk_count, 1)

    # ─── Modelos relacionados ───────────────────────────────────────────────

    def test_create_review(self):
        piai = self._make_piai()
        review = self.env['cs.piai.review'].create({
            'piai_id': piai.id,
            'review_date': date.today(),
            'review_type': 'ordinary',
        })
        self.assertEqual(review.piai_id, piai)

    def test_create_evolution(self):
        piai = self._make_piai()
        evolution = self.env['cs.piai.evolution'].create({
            'piai_id': piai.id,
            'note_type': 'evolution',
            'content': 'Buena evolución.',
        })
        self.assertEqual(evolution.piai_id, piai)

    def test_create_relapse_prevention(self):
        piai = self._make_piai()
        rp = self.env['cs.piai.relapse.prevention'].create({
            'piai_id': piai.id,
            'high_risk_situations': 'Estrés laboral',
            'coping_strategies': 'Llamar al terapeuta',
        })
        self.assertEqual(rp.piai_id, piai)

    def test_create_discharge_plan(self):
        piai = self._make_piai()
        dp = self.env['cs.piai.discharge.plan'].create({
            'piai_id': piai.id,
            'discharge_type': 'therapeutic',
        })
        self.assertEqual(dp.piai_id, piai)

    # ─── Cron ───────────────────────────────────────────────────────────────

    def test_cron_runs_without_error(self):
        self._make_piai(date_elaboration=date.today() - timedelta(days=10))
        piai_active = self._make_activatable_piai(resident=self.resident2)
        piai_active.action_activate()
        piai_active.write({'date_next_review': date.today() - timedelta(days=1)})
        self.env['cs.piai.risk'].create({
            'piai_id': piai_active.id,
            'risk_type': 'autolytic',
            'level': 'critical',
            'state': 'active',
        })
        self.env['cs.piai']._cron_check_alerts()

    # ─── Integración cs_admission ────────────────────────────────────────────

    def test_admission_close_creates_piai_draft(self):
        resident3 = self.env['cs.resident'].create({
            'name': 'Residente Admisión Test',
            'dni': '00000003T',
            'fecha_nacimiento': '1990-03-10',
            'residence_id': self.residence.id,
        })
        admission = self.env['cs.admission.process'].create({
            'resident_id': resident3.id,
            'state': 'economy',
        })
        admission._close_admission()
        piai = self.env['cs.piai'].search([('resident_id', '=', resident3.id)])
        self.assertEqual(len(piai), 1)
        self.assertEqual(piai.state, 'draft')
        self.assertEqual(piai.therapeutic_phase, 'acogida')

    def test_admission_close_skips_if_piai_exists(self):
        resident4 = self.env['cs.resident'].create({
            'name': 'Residente Admisión Skip',
            'dni': '00000004T',
            'fecha_nacimiento': '1975-11-20',
            'residence_id': self.residence.id,
        })
        self._make_piai(resident=resident4)
        admission = self.env['cs.admission.process'].create({
            'resident_id': resident4.id,
            'state': 'economy',
        })
        admission._close_admission()
        piaiS = self.env['cs.piai'].search([('resident_id', '=', resident4.id)])
        self.assertEqual(len(piaiS), 1)
