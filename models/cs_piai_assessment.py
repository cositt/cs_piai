from odoo import models, fields
from .cs_piai_objective import AREA_SELECTION

SUBSTANCE_SELECTION = [
    ('alcohol', 'Alcohol'),
    ('cannabis', 'Cannabis'),
    ('cocaine', 'Cocaína'),
    ('heroin', 'Heroína'),
    ('opioids', 'Opioides (otros)'),
    ('stimulants', 'Estimulantes (speed, MDMA...)'),
    ('benzos', 'Benzodiacepinas'),
    ('other_drugs', 'Otras drogas'),
    ('gambling', 'Juego patológico'),
    ('sex_addiction', 'Adicción sexual'),
    ('gaming', 'Videojuegos/Internet'),
    ('eating', 'Conducta alimentaria'),
    ('other', 'Otra conducta'),
]


class PiaiAssessment(models.Model):
    _name = 'cs.piai.assessment'
    _description = 'Valoración Inicial PIAI por Área'
    _order = 'area_type'

    piai_id = fields.Many2one('cs.piai', string='PIAI', required=True, ondelete='cascade', index=True)
    area_type = fields.Selection(AREA_SELECTION, string='Área', required=True)
    date_assessment = fields.Date(string='Fecha de Valoración', default=fields.Date.context_today)
    professional_id = fields.Many2one('cs.worker', string='Profesional Valorador')
    priority_level = fields.Selection([
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ], string='Prioridad', default='medium')
    detected_risks = fields.Text(string='Riesgos Detectados')
    detected_needs = fields.Text(string='Necesidades Detectadas')

    # ─── Área Psicológica ──────────────────────────────────────────────────
    main_substance_ids = fields.Many2many(
        'cs.piai.substance.tag',
        'piai_assessment_substance_rel',
        'assessment_id', 'substance_id',
        string='Sustancia/Conducta Principal',
    )
    secondary_substances = fields.Text(string='Sustancias Secundarias')
    onset_age = fields.Integer(string='Edad de Inicio del Consumo')
    awareness_level = fields.Selection([
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    ], string='Nivel de Conciencia de Problema')
    change_motivation = fields.Selection([
        ('precontemplacion', 'Precontemplación'),
        ('contemplacion', 'Contemplación'),
        ('preparacion', 'Preparación'),
        ('accion', 'Acción'),
        ('mantenimiento', 'Mantenimiento'),
    ], string='Motivación al Cambio')
    initial_emotional_state = fields.Text(string='Estado Emocional Inicial')
    suicide_risk = fields.Selection([
        ('none', 'Sin riesgo'),
        ('low', 'Bajo'),
        ('medium', 'Moderado'),
        ('high', 'Alto'),
    ], string='Riesgo Autolítico', default='none')
    heteroaggressive_risk = fields.Selection([
        ('none', 'Sin riesgo'),
        ('low', 'Bajo'),
        ('medium', 'Moderado'),
        ('high', 'Alto'),
    ], string='Riesgo Heteroagresivo', default='none')
    impulsivity = fields.Selection([
        ('none', 'Sin impulsividad'),
        ('low', 'Baja'),
        ('medium', 'Moderada'),
        ('high', 'Alta'),
    ], string='Impulsividad', default='none')
    initial_craving = fields.Selection([
        ('none', 'Sin craving'),
        ('low', 'Bajo'),
        ('medium', 'Moderado'),
        ('high', 'Alto'),
    ], string='Craving Inicial', default='none')
    clinical_observations = fields.Text(string='Observaciones Clínicas Psicológicas')

    # ─── Área Sanitaria ────────────────────────────────────────────────────
    medical_history = fields.Text(string='Antecedentes Médicos')
    active_pathologies = fields.Text(string='Patologías Activas')
    allergies_text = fields.Text(string='Alergias')
    current_medication_ids = fields.Many2many(
        'cs.drug.catalog',
        'piai_assessment_drug_rel',
        'assessment_id', 'drug_id',
        string='Medicación Actual al Ingreso',
    )
    withdrawal_signs = fields.Selection([
        ('none', 'Sin signos'),
        ('mild', 'Leves'),
        ('moderate', 'Moderados'),
        ('severe', 'Severos'),
    ], string='Signos de Abstinencia', default='none')
    sanitary_risk = fields.Selection([
        ('low', 'Bajo'),
        ('medium', 'Moderado'),
        ('high', 'Alto'),
    ], string='Riesgo Sanitario')

    # ─── Área Psiquiátrica ─────────────────────────────────────────────────
    psychiatric_diagnosis = fields.Text(string='Diagnóstico Psiquiátrico Previo')
    dual_pathology = fields.Boolean(string='Patología Dual')
    stability_level = fields.Selection([
        ('unstable', 'Inestable'),
        ('partially_stable', 'Parcialmente estable'),
        ('stable', 'Estable'),
    ], string='Nivel de Estabilidad Psiquiátrica')

    # ─── Área Social ───────────────────────────────────────────────────────
    family_situation = fields.Text(string='Situación Familiar')
    support_network = fields.Text(string='Red de Apoyo')
    economic_situation = fields.Selection([
        ('no_income', 'Sin ingresos'),
        ('welfare', 'Prestación social'),
        ('employed', 'Empleado'),
        ('pension', 'Pensión'),
        ('family_support', 'Apoyo familiar'),
    ], string='Situación Económica')
    housing_situation = fields.Selection([
        ('homeless', 'Sin hogar'),
        ('unstable', 'Inestable'),
        ('family', 'Con familia'),
        ('rented', 'Alquiler propio'),
        ('owned', 'Vivienda propia'),
    ], string='Situación Habitacional')
    employment_situation = fields.Selection([
        ('unemployed', 'Desempleado'),
        ('active_search', 'En búsqueda activa'),
        ('employed', 'Empleado'),
        ('disabled', 'Incapacidad laboral'),
        ('retired', 'Jubilado'),
    ], string='Situación Laboral')

    # ─── Área Educativa ────────────────────────────────────────────────────
    education_level = fields.Selection([
        ('none', 'Sin estudios'),
        ('primary', 'Primaria'),
        ('secondary', 'Secundaria'),
        ('vocational', 'FP'),
        ('university', 'Universidad'),
    ], string='Nivel Educativo')
    social_skills = fields.Selection([
        ('low', 'Bajas'),
        ('medium', 'Medias'),
        ('high', 'Altas'),
    ], string='Habilidades Sociales')
    personal_autonomy = fields.Selection([
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    ], string='Autonomía Personal')

    # ─── Área Familiar ─────────────────────────────────────────────────────
    family_involved_persons = fields.Text(string='Personas Familiares Implicadas')
    consent_inform_family = fields.Boolean(string='Autoriza Informar a Familia')
    family_dynamics = fields.Text(string='Dinámica Familiar')


class SubstanceTag(models.Model):
    _name = 'cs.piai.substance.tag'
    _description = 'Sustancia / Conducta Adictiva'
    _order = 'name'

    name = fields.Char(string='Sustancia/Conducta', required=True)
    code = fields.Char(string='Código')
