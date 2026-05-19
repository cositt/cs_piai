import logging
from datetime import timedelta
from odoo import models, fields, _

_logger = logging.getLogger(__name__)


class AdmissionProcessPiai(models.Model):
    _inherit = 'cs.admission.process'

    def _close_admission(self):
        super()._close_admission()
        for rec in self:
            if not rec.resident_id:
                continue
            existing = self.env['cs.piai'].search([
                ('resident_id', '=', rec.resident_id.id),
                ('state', 'not in', [
                    'closed_discharge', 'closed_voluntary',
                    'closed_referral', 'closed_expulsion',
                ]),
            ], limit=1)
            if existing:
                continue
            today = fields.Date.context_today(self)
            piai = self.env['cs.piai'].create({
                'resident_id': rec.resident_id.id,
                'therapeutic_phase': 'acogida',
                'date_elaboration': today,
                'date_next_review': today + timedelta(days=30),
            })
            rec.message_post(
                body=_('PIAI borrador creado automáticamente: %s') % piai.name
            )
            _logger.info('PIAI draft %s created for resident %s', piai.name, rec.resident_id.name)
