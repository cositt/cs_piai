from odoo import models, fields
from .cs_piai_objective import AREA_SELECTION

INTERVENTION_TYPE = [
    ('individual_psychotherapy', 'Psicoterapia Individual'),
    ('group_psychotherapy', 'Psicoterapia Grupal'),
    ('motivational_interview', 'Entrevista Motivacional'),
    ('relapse_prevention', 'Prevención de Recaídas'),
    ('cognitive_behavioral', 'Terapia Cognitivo-Conductual'),
    ('family_therapy', 'Terapia Familiar'),
    ('social_skills', 'Entrenamiento en Habilidades Sociales'),
    ('occupational', 'Terapia Ocupacional'),
    ('educational', 'Intervención Educativa'),
    ('social_work', 'Trabajo Social'),
    ('nursing_care', 'Cuidados de Enfermería'),
    ('psychiatric_follow', 'Seguimiento Psiquiátrico'),
    ('medical_follow', 'Seguimiento Médico'),
    ('psychoeducation', 'Psicoeducación'),
    ('social_interview', 'Entrevista Social'),
    ('external_coordination', 'Coordinación Externa'),
    ('toxicological_control', 'Control Toxicológico'),
    ('sport_therapy', 'Actividad Deportiva Terapéutica'),
    ('educational_workshop', 'Taller Educativo'),
    ('occupational_workshop', 'Taller Ocupacional'),
    ('community_assembly', 'Asamblea / Intervención Convivencial'),
    ('doc_management', 'Gestión Documental'),
    ('external_referral', 'Derivación a Recurso Externo'),
    ('mindfulness', 'Mindfulness / Relajación'),
    ('community_resources', 'Recursos Comunitarios'),
    ('coordination', 'Coordinación con Red Asistencial'),
    ('other', 'Otra'),
]

FREQUENCY_SELECTION = [
    ('daily', 'Diaria'),
    ('weekly', 'Semanal'),
    ('biweekly', 'Quincenal'),
    ('monthly', 'Mensual'),
    ('as_needed', 'Según necesidad'),
]


class PiaiIntervention(models.Model):
    _name = 'cs.piai.intervention'
    _description = 'Intervención Terapéutica PIAI'
    _order = 'area, intervention_type'

    piai_id = fields.Many2one('cs.piai', string='PIAI', required=True, ondelete='cascade', index=True)
    area = fields.Selection(AREA_SELECTION, string='Área', required=True)
    objective_ids = fields.Many2many(
        'cs.piai.objective',
        'piai_intervention_objective_rel',
        'intervention_id', 'objective_id',
        string='Objetivos Asociados',
    )
    intervention_type = fields.Selection(INTERVENTION_TYPE, string='Tipo de Intervención', required=True)
    description = fields.Text(string='Descripción')
    frequency = fields.Selection(FREQUENCY_SELECTION, string='Frecuencia')
    responsible_id = fields.Many2one('cs.worker', string='Responsable')
    start_date = fields.Date(string='Fecha de Inicio')
    end_date = fields.Date(string='Fecha de Fin')
    state = fields.Selection([
        ('active', 'Activa'),
        ('suspended', 'Suspendida'),
        ('finished', 'Finalizada'),
    ], string='Estado', default='active', required=True)
