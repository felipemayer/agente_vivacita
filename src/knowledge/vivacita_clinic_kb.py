#!/usr/bin/env python3
"""
Base de Conhecimento da Clínica Vivacità Saúde Mental
Baseada na análise real do banco de dados e estrutura da clínica
"""

from typing import Dict, List, Any

class VivacitaClinicKnowledgeBase:
    """
    Base de conhecimento completa da Clínica Vivacità com informações 
    atualizadas baseadas na estrutura real do banco de dados.
    """
    
    def __init__(self):
        self.clinic_info = self._load_clinic_info()
        self.specialties = self._load_specialties()
        self.doctors = self._load_doctors()
        self.policies = self._load_policies()
        self.prices = self._load_prices()
    
    def _load_clinic_info(self) -> Dict[str, Any]:
        """Informações básicas da clínica"""
        return {
            "name": "Clínica Vivacità Saúde Mental",
            "focus": "Saúde Mental e Psiquiatria",
            "established": "Clínica especializada em saúde mental",
            "location": "Brasil",
            "working_hours": {
                "monday_to_friday": "08:00 - 18:00",
                "weekend": "Fechado",
                "timezone": "America/Sao_Paulo"
            },
            "contact": {
                "scheduling": "Via WhatsApp com Hígia",
                "emergency": "Encaminhamento para serviços de emergência quando necessário"
            },
            "mission": "Oferecer atendimento humanizado e especializado em saúde mental"
        }
    
    def _load_specialties(self) -> Dict[str, Dict[str, Any]]:
        """Especialidades reais disponíveis na clínica"""
        return {
            "PSIQUIATRA": {
                "name": "Psiquiatria",
                "description": "Consultas médicas psiquiátricas para diagnóstico, tratamento e acompanhamento de transtornos mentais",
                "code": "PSIQUIATRA",
                "category": "medical",
                "available": True,
                "price": "R$ 500,00",
                "modalities": ["presencial", "online (apenas Dr. Ernesto)"],
                "common_conditions": [
                    "Depressão", "Ansiedade", "Transtorno Bipolar", "Esquizofrenia",
                    "TDAH", "Transtornos do Humor", "Transtornos de Personalidade",
                    "Transtornos Alimentares", "Dependência Química"
                ],
                "age_groups": ["Adultos (todos médicos)", "Crianças 7+ anos (apenas Dr. Ernesto)"],
                "duration": "Consulta padrão de 50 minutos",
                "preparation": "Trazer exames anteriores se houver, lista de medicamentos em uso",
                "follow_up": "Retornos conforme orientação médica"
            },
            
            "PSICOLOGIA": {
                "name": "Psicologia",
                "description": "Atendimento psicológico com psicólogos especializados em diversas abordagens terapêuticas",
                "code": "PSICOLOGIA",
                "category": "therapeutic",
                "available": True,
                "price": "R$ 250,00 (Particular) / R$ 150,00 (Bradesco)",
                "modalities": ["presencial"],
                "common_conditions": [
                    "Psicoterapia individual", "Terapia cognitivo-comportamental",
                    "Acompanhamento psicológico", "Suporte emocional",
                    "Tratamento de fobias", "Gestão de estresse e ansiedade"
                ],
                "age_groups": ["Adultos"],
                "duration": "Sessão padrão de 50 minutos",
                "approaches": ["Cognitivo-comportamental", "Psicanálise", "Humanística"],
                "preparation": "Disposição para falar sobre sentimentos e experiências"
            },
            
            "NEUROPSICOLOGIA": {
                "name": "Neuropsicologia",
                "description": "Avaliação neuropsicológica especializada para diagnóstico de funções cognitivas",
                "code": "NEUROPSICOLOGIA",
                "category": "diagnostic",
                "available": True,
                "price": "R$ 1.950,00",
                "modalities": ["presencial"],
                "indications": [
                    "Avaliação de memória", "Déficits de atenção",
                    "Dificuldades de aprendizagem", "Demências",
                    "Sequelas de AVC", "Traumatismo craniano",
                    "Transtornos neurodegenerativos"
                ],
                "age_groups": ["Adultos"],
                "duration": "Processo completo: 4-6 sessões",
                "includes": ["Testagem neuropsicológica", "Relatório detalhado", "Devolutiva"],
                "preparation": "Óculos se usar, bom estado de sono, alimentação adequada"
            },
            
            "EXAMES": {
                "name": "Exames",
                "description": "Diversos exames médicos e procedimentos diagnósticos",
                "code": "EXAMES",
                "category": "diagnostic",
                "available": True,
                "price": "Consultar tabela específica por exame",
                "modalities": ["presencial"],
                "types": [
                    "Exames laboratoriais relacionados à psiquiatria",
                    "Procedimentos diagnósticos específicos",
                    "Avaliações complementares"
                ],
                "scheduling": "Agendamento específico por tipo de exame",
                "preparation": "Varia conforme o tipo de exame - será informado no agendamento"
            },
            
            "POLISSONOGRAFIA": {
                "name": "Polissonografia",
                "description": "Exame do sono para diagnóstico de distúrbios do sono",
                "code": "POLISSONOGRAFIA",
                "category": "diagnostic",
                "available": True,
                "price": "Consultar valor específico",
                "modalities": ["presencial"],
                "indications": [
                    "Apneia do sono", "Ronco excessivo",
                    "Insônia crônica", "Sonolência diurna",
                    "Distúrbios do movimento durante o sono",
                    "Investigação de qualidade do sono"
                ],
                "duration": "Exame noturno completo",
                "preparation": [
                    "Evitar cafeína 6h antes",
                    "Não usar produtos no cabelo",
                    "Trazer pijama confortável",
                    "Seguir rotina normal de sono"
                ],
                "provider": "BIOLOGIC - Centro especializado"
            }
        }
    
    def _load_doctors(self) -> Dict[str, Any]:
        """Informações dos médicos baseadas no banco real"""
        return {
            "total_active": 18,
            "by_specialty": {
                "PSIQUIATRA": 11,
                "PSICOLOGIA": 2,
                "NEUROPSICOLOGIA": 1,
                "EXAMES": 1,
                "POLISSONOGRAFIA": 1
            },
            
            "featured_doctors": {
                "dr_ernesto": {
                    "id": 5,
                    "name": "ERNESTO GIL BUCHILLÓN",
                    "specialty": "PSIQUIATRA",
                    "unique_capabilities": [
                        "ÚNICO médico autorizado para crianças (7+ anos)",
                        "ÚNICO médico que realiza consultas online",
                        "ÚNICO médico que elabora relatórios médicos"
                    ],
                    "online_slots": ["11:45", "17:00", "17:15"],
                    "consultation_types": ["presencial", "online"],
                    "age_specialization": "Crianças (7+) e adultos",
                    "reports": {
                        "available": True,
                        "price": "R$ 500,00",
                        "payment": "Antecipado obrigatório",
                        "delivery": "Conforme prazo acordado"
                    },
                    "booking_priority": "Alta (capacidades únicas)"
                }
            },
            
            "psychiatrists": [
                {"id": 2, "name": "ANA JULIA CORTES"},
                {"id": 3, "name": "ARTHUR SUMAN NOGUEIRA"},
                {"id": 4, "name": "CARLA TAISI DA CRUZ ARAGÃO"},
                {"id": 5, "name": "ERNESTO GIL BUCHILLÓN"},
                {"id": 7, "name": "JESSICA FIGUEREDO NOVATO"},
                {"id": 8, "name": "JOÃO PAULO BARBOSA DE JESUS"},
                {"id": 10, "name": "LARA AUGUSTA EUGENIO PINTO"},
                {"id": 13, "name": "MARIELA LOZI DIAS CHAVES"},
                {"id": 15, "name": "NATANAEL SANTANA CARDOSO DE OLIVEIRA"},
                {"id": 16, "name": "PAULA TOLENTINO ABDALLA"},
                {"id": 18, "name": "WALESKA PALHARES PIRES"}
            ],
            
            "psychologists": [
                {"id": 9, "name": "JULIANA RODRIGUES FARIA DA SILVA"},
                {"id": 12, "name": "MARIANA DE SOUSA E SILVA"}
            ],
            
            "specialists": [
                {"id": 1, "name": "ALINE ELLEN ALVES QUEIROS CRUZ", "specialty": "NEUROPSICOLOGIA"},
                {"id": 6, "name": "EXAMES", "specialty": "EXAMES"},
                {"id": 17, "name": "POLISSONOGRAFIA - BIOLOGIC", "specialty": "POLISSONOGRAFIA"}
            ]
        }
    
    def _load_policies(self) -> Dict[str, Any]:
        """Políticas e regras da clínica"""
        return {
            "age_restrictions": {
                "minimum_age": 7,
                "children_policy": "Menores de 18 anos DEVEM ser atendidos pelo Dr. Ernesto",
                "adult_policy": "Adultos podem ser atendidos por qualquer médico da especialidade"
            },
            
            "online_consultation": {
                "availability": "Apenas com Dr. Ernesto",
                "specialty": "Psiquiatria apenas",
                "fixed_times": ["11:45", "17:00", "17:15"],
                "scheduling": "Horários não negociáveis",
                "price": "Mesmo valor da consulta presencial"
            },
            
            "reports": {
                "provider": "Apenas Dr. Ernesto",
                "types": ["Relatório médico", "Laudo psiquiátrico"],
                "payment": "Antecipado obrigatório",
                "price": "R$ 500,00",
                "delivery": "Conforme prazo acordado"
            },
            
            "payment": {
                "methods": ["Dinheiro", "Cartão", "PIX"],
                "insurance": "Aceita diversos convênios",
                "private_return": "Não há retorno gratuito para particulares",
                "insurance_interval": "16 dias de carência entre consultas para convênios"
            },
            
            "scheduling": {
                "advance_booking": "Recomendado agendar com antecedência",
                "cancellation": "Avisar com 24h de antecedência",
                "rescheduling": "Conforme disponibilidade da agenda",
                "confirmation": "Confirmação necessária 1 dia antes"
            },
            
            "emergency": {
                "clinic_scope": "Não é pronto-socorro",
                "emergency_action": "Orientação para procurar serviços de emergência",
                "crisis_support": "Suporte inicial e encaminhamento adequado"
            }
        }
    
    def _load_prices(self) -> Dict[str, str]:
        """Tabela de preços 2024"""
        return {
            "consulta_psiquiatrica": "R$ 500,00",
            "consulta_psicologia_particular": "R$ 250,00",
            "consulta_psicologia_bradesco": "R$ 150,00",
            "avaliacao_neuropsicologica": "R$ 1.950,00",
            "relatorio_medico": "R$ 500,00",
            "exames": "Consultar tabela específica",
            "polissonografia": "Consultar valor específico"
        }
    
    def get_specialty_info(self, specialty_code: str) -> Dict[str, Any]:
        """Retorna informações completas de uma especialidade"""
        return self.specialties.get(specialty_code.upper(), {})
    
    def get_dr_ernesto_info(self) -> Dict[str, Any]:
        """Retorna informações completas do Dr. Ernesto"""
        return self.doctors["featured_doctors"]["dr_ernesto"]
    
    def validate_age_requirement(self, age: int, specialty: str) -> Dict[str, Any]:
        """Valida requisitos de idade para atendimento"""
        if age < 7:
            return {
                "valid": False,
                "reason": "Clínica atende pacientes a partir de 7 anos",
                "minimum_age": 7
            }
        elif age < 18:
            return {
                "valid": True,
                "required_doctor": "Dr. Ernesto Gil Buchillón",
                "doctor_id": 5,
                "reason": "Menores de 18 anos devem ser atendidos pelo Dr. Ernesto"
            }
        else:
            return {
                "valid": True,
                "options": "Qualquer médico da especialidade escolhida"
            }
    
    def get_online_consultation_info(self) -> Dict[str, Any]:
        """Informações sobre consultas online"""
        return {
            "available": True,
            "exclusive_doctor": self.doctors["featured_doctors"]["dr_ernesto"],
            "specialty": "Psiquiatria",
            "fixed_times": ["11:45", "17:00", "17:15"],
            "price": "R$ 500,00",
            "important_notes": [
                "Apenas Dr. Ernesto realiza consultas online",
                "Horários fixos não negociáveis",
                "Mesmo valor da consulta presencial"
            ]
        }
    
    def get_clinic_summary(self) -> str:
        """Resumo executivo da clínica para agentes"""
        return f"""
        CLÍNICA VIVACITÀ SAÚDE MENTAL - RESUMO EXECUTIVO
        
        ESPECIALIDADES DISPONÍVEIS:
        • PSIQUIATRA ({self.doctors['by_specialty']['PSIQUIATRA']} médicos) - R$ 500,00
        • PSICOLOGIA ({self.doctors['by_specialty']['PSICOLOGIA']} profissionais) - R$ 250,00/R$ 150,00
        • NEUROPSICOLOGIA ({self.doctors['by_specialty']['NEUROPSICOLOGIA']} especialista) - R$ 1.950,00
        • EXAMES (diversos procedimentos)
        • POLISSONOGRAFIA (exame do sono)
        
        DR. ERNESTO GIL BUCHILLÓN - CAPACIDADES ESPECIAIS:
        • ÚNICO médico para crianças (7+ anos)
        • ÚNICO médico para consultas online (11:45, 17:00, 17:15)
        • ÚNICO médico para relatórios médicos (R$ 500,00)
        
        HORÁRIO: Segunda a Sexta, 08:00-18:00
        POLÍTICAS: Sem retorno gratuito particular | 16 dias carência convênio
        PAGAMENTO: Dinheiro, Cartão, PIX
        """

# Instance global para uso em toda aplicação
vivacita_kb = VivacitaClinicKnowledgeBase()

if __name__ == "__main__":
    # Teste da base de conhecimento
    kb = VivacitaClinicKnowledgeBase()
    
    print("=== Base de Conhecimento Vivacità ===")
    print(kb.get_clinic_summary())
    
    print("\n=== Dr. Ernesto ===")
    dr_info = kb.get_dr_ernesto_info()
    print(f"Nome: {dr_info['name']}")
    print(f"Capacidades: {dr_info['unique_capabilities']}")
    
    print("\n=== Validação de Idade ===")
    child_validation = kb.validate_age_requirement(10, "PSIQUIATRA")
    print(f"Criança 10 anos: {child_validation}")
    
    adult_validation = kb.validate_age_requirement(25, "PSIQUIATRA")
    print(f"Adulto 25 anos: {adult_validation}")