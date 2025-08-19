#!/usr/bin/env python3
"""
VivacitaMCPTool - Integração com sistema de agendamentos da Clínica Vivacità
Baseado na documentação MCP fornecida, adaptado para integração direta com CrewAI
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, time
from langchain.tools import BaseTool

# Configurar logging
logger = logging.getLogger(__name__)

class VivacitaMCPTool(BaseTool):
    """
    Ferramenta CrewAI para agendamentos médicos na Clínica Vivacità Saúde Mental.
    
    Especialidades disponíveis:
    - PSIQUIATRA: Consultas psiquiátricas (Dr. Ernesto e outros médicos)
    - PSICOLOGIA: Consultas psicológicas
    - EXAMES: Exames médicos diversos
    - NEUROPSICOLOGIA: Avaliações neuropsicológicas
    - POLISSONOGRAFIA: Exames do sono
    
    Regras especiais do Dr. Ernesto Gil Buchillón (ID: 5):
    - ÚNICO médico autorizado para atender crianças (7+ anos)
    - ÚNICO médico que realiza consultas online (horários: 11:45, 17:00, 17:15)
    - ÚNICO médico que elabora relatórios médicos
    """
    
    name: str = "vivacita_scheduler"
    description: str = """
    Sistema de agendamento médico para Clínica Vivacità Saúde Mental.
    
    Uso: vivacita_scheduler(action="ação", **parâmetros)
    
    Ações disponíveis:
    - get_specialties: Listar especialidades disponíveis
    - get_doctors: Buscar médicos por especialidade
    - get_dr_ernesto: Informações específicas do Dr. Ernesto
    - check_availability: Verificar horários disponíveis
    - validate_appointment: Validar dados antes de agendar
    - get_clinic_info: Informações gerais da clínica
    
    Exemplo: vivacita_scheduler(action="get_dr_ernesto")
    """
    
    # Dados base da clínica (baseados na análise do banco)
    CLINIC_SPECIALTIES = {
        "PSIQUIATRA": {
            "name": "Psiquiatria",
            "description": "Consultas com médicos psiquiatras especializados em saúde mental",
            "price": "R$ 500,00",
            "doctors": [
                {"id": 2, "name": "ANA JULIA CORTES"},
                {"id": 3, "name": "ARTHUR SUMAN NOGUEIRA"},
                {"id": 4, "name": "CARLA TAISI DA CRUZ ARAGÃO"},
                {"id": 5, "name": "ERNESTO GIL BUCHILLÓN", "special": True},
                {"id": 7, "name": "JESSICA FIGUEREDO NOVATO"},
                {"id": 8, "name": "JOÃO PAULO BARBOSA DE JESUS"},
                {"id": 10, "name": "LARA AUGUSTA EUGENIO PINTO"},
                {"id": 13, "name": "MARIELA LOZI DIAS CHAVES"},
                {"id": 15, "name": "NATANAEL SANTANA CARDOSO DE OLIVEIRA"},
                {"id": 16, "name": "PAULA TOLENTINO ABDALLA"},
                {"id": 18, "name": "WALESKA PALHARES PIRES"}
            ]
        },
        "PSICOLOGIA": {
            "name": "Psicologia",
            "description": "Consultas com psicólogos especializados",
            "price": "R$ 250,00 (Particular) / R$ 150,00 (Bradesco)",
            "doctors": [
                {"id": 9, "name": "JULIANA RODRIGUES FARIA DA SILVA"},
                {"id": 12, "name": "MARIANA DE SOUSA E SILVA"}
            ]
        },
        "NEUROPSICOLOGIA": {
            "name": "Neuropsicologia",
            "description": "Avaliações neuropsicológicas especializadas",
            "price": "R$ 1.950,00",
            "doctors": [
                {"id": 1, "name": "ALINE ELLEN ALVES QUEIROS CRUZ"}
            ]
        },
        "EXAMES": {
            "name": "Exames",
            "description": "Exames médicos diversos",
            "price": "Consultar tabela específica",
            "doctors": [
                {"id": 6, "name": "EXAMES"}
            ]
        },
        "POLISSONOGRAFIA": {
            "name": "Polissonografia",
            "description": "Exame do sono - polissonografia",
            "price": "Consultar valor específico",
            "doctors": [
                {"id": 17, "name": "POLISSONOGRAFIA - BIOLOGIC"}
            ]
        }
    }
    
    DR_ERNESTO_INFO = {
        "id": 5,
        "name": "ERNESTO GIL BUCHILLÓN",
        "specialty": "PSIQUIATRA",
        "can_treat_children": True,
        "min_child_age": 7,
        "can_online_consultation": True,
        "online_slots": ["11:45", "17:00", "17:15"],
        "can_create_reports": True,
        "special_capabilities": [
            "ÚNICO médico autorizado a atender crianças (7+ anos)",
            "ÚNICO médico que realiza consultas online",
            "ÚNICO médico que elabora relatórios médicos",
            "Consultas presenciais e online",
            "Psiquiatra com vasta experiência"
        ],
        "consultation_types": ["presencial", "online"],
        "report_price": "R$ 500,00"
    }
    
    CLINIC_INFO = {
        "name": "Clínica Vivacità Saúde Mental",
        "specialties": ["Psiquiatria", "Psicologia", "Neuropsicologia", "Exames", "Polissonografia"],
        "working_hours": {
            "monday_to_friday": "08:00 - 18:00",
            "saturday": "Fechado",
            "sunday": "Fechado"
        },
        "timezone": "America/Sao_Paulo",
        "policies": {
            "no_free_return_private": "Não há retorno gratuito para pacientes particulares",
            "insurance_interval": "16 dias de carência entre consultas para convênios",
            "payment_methods": ["Dinheiro", "Cartão", "PIX"],
            "reports_payment": "Pagamento antecipado obrigatório para relatórios"
        },
        "contact": {
            "address": "Endereço da clínica (consultar recepção)",
            "phone": "Telefone da clínica (consultar recepção)"
        }
    }
    
    def _run(self, action: str, **kwargs) -> str:
        """Executa ação no sistema Vivacita"""
        
        logger.info(f"VivacitaMCPTool executando ação: {action} com parâmetros: {kwargs}")
        
        try:
            # Roteamento das ações
            if action == "get_specialties":
                return self._get_specialties()
            elif action == "get_doctors":
                return self._get_doctors(**kwargs)
            elif action == "get_dr_ernesto":
                return self._get_dr_ernesto()
            elif action == "check_availability":
                return self._check_availability(**kwargs)
            elif action == "validate_appointment":
                return self._validate_appointment(**kwargs)
            elif action == "get_clinic_info":
                return self._get_clinic_info()
            elif action == "get_prices":
                return self._get_prices()
            elif action == "check_child_eligibility":
                return self._check_child_eligibility(**kwargs)
            elif action == "get_online_options":
                return self._get_online_options()
            else:
                available_actions = [
                    "get_specialties", "get_doctors", "get_dr_ernesto", 
                    "check_availability", "validate_appointment", "get_clinic_info",
                    "get_prices", "check_child_eligibility", "get_online_options"
                ]
                return f"Ação inválida '{action}'. Ações disponíveis: {', '.join(available_actions)}"
                
        except Exception as e:
            logger.error(f"Erro ao executar ação {action}: {e}")
            return f"Erro ao executar {action}: {str(e)}"
    
    def _get_specialties(self) -> str:
        """Retorna todas as especialidades disponíveis na clínica"""
        specialties_info = []
        
        for code, info in self.CLINIC_SPECIALTIES.items():
            specialties_info.append({
                "code": code,
                "name": info["name"],
                "description": info["description"],
                "price": info["price"],
                "doctors_count": len(info["doctors"])
            })
        
        return json.dumps({
            "success": True,
            "clinic": "Clínica Vivacità Saúde Mental",
            "specialties": specialties_info,
            "total_specialties": len(specialties_info)
        }, indent=2, ensure_ascii=False)
    
    def _get_doctors(self, specialty: str = None, **kwargs) -> str:
        """Busca médicos por especialidade"""
        
        if specialty:
            specialty_upper = specialty.upper()
            if specialty_upper in self.CLINIC_SPECIALTIES:
                doctors = self.CLINIC_SPECIALTIES[specialty_upper]["doctors"]
                specialty_info = self.CLINIC_SPECIALTIES[specialty_upper]
                
                # Adicionar informações especiais do Dr. Ernesto se estiver na lista
                enhanced_doctors = []
                for doctor in doctors:
                    if doctor["id"] == 5:  # Dr. Ernesto
                        enhanced_doctor = doctor.copy()
                        enhanced_doctor.update({
                            "special_capabilities": self.DR_ERNESTO_INFO["special_capabilities"],
                            "can_treat_children": True,
                            "can_online_consultation": True,
                            "can_create_reports": True
                        })
                        enhanced_doctors.append(enhanced_doctor)
                    else:
                        enhanced_doctors.append(doctor)
                
                return json.dumps({
                    "success": True,
                    "specialty": specialty_info["name"],
                    "specialty_code": specialty_upper,
                    "price": specialty_info["price"],
                    "doctors": enhanced_doctors,
                    "total_doctors": len(enhanced_doctors)
                }, indent=2, ensure_ascii=False)
            else:
                available = list(self.CLINIC_SPECIALTIES.keys())
                return json.dumps({
                    "success": False,
                    "error": f"Especialidade '{specialty}' não encontrada",
                    "available_specialties": available
                }, indent=2, ensure_ascii=False)
        else:
            # Listar todos os médicos de todas especialidades
            all_doctors = []
            for specialty_code, info in self.CLINIC_SPECIALTIES.items():
                for doctor in info["doctors"]:
                    doctor_info = doctor.copy()
                    doctor_info["specialty"] = specialty_code
                    doctor_info["specialty_name"] = info["name"]
                    if doctor["id"] == 5:  # Dr. Ernesto
                        doctor_info["special_capabilities"] = self.DR_ERNESTO_INFO["special_capabilities"]
                    all_doctors.append(doctor_info)
            
            return json.dumps({
                "success": True,
                "all_doctors": all_doctors,
                "total_doctors": len(all_doctors)
            }, indent=2, ensure_ascii=False)
    
    def _get_dr_ernesto(self) -> str:
        """Retorna informações completas do Dr. Ernesto"""
        return json.dumps({
            "success": True,
            "doctor": self.DR_ERNESTO_INFO,
            "consultation_info": {
                "presencial": {
                    "available": True,
                    "schedule": "Segunda a Sexta, 08:00-18:00",
                    "price": "R$ 500,00"
                },
                "online": {
                    "available": True,
                    "fixed_slots": self.DR_ERNESTO_INFO["online_slots"],
                    "price": "R$ 500,00",
                    "note": "Apenas nos horários fixos especificados"
                },
                "reports": {
                    "available": True,
                    "price": self.DR_ERNESTO_INFO["report_price"],
                    "payment": "Antecipado obrigatório"
                }
            },
            "special_rules": {
                "children": "ÚNICO médico autorizado para menores de 18 anos (mínimo 7 anos)",
                "online": "ÚNICO médico que realiza consultas online",
                "reports": "ÚNICO médico que elabora relatórios médicos"
            }
        }, indent=2, ensure_ascii=False)
    
    def _check_availability(self, doctor_id: int = None, date: str = None, **kwargs) -> str:
        """Simula verificação de disponibilidade"""
        
        if doctor_id == 5:  # Dr. Ernesto
            online_slots = [
                {"time": "11:45", "available": True, "modality": "online"},
                {"time": "17:00", "available": True, "modality": "online"},
                {"time": "17:15", "available": True, "modality": "online"}
            ]
            presencial_slots = [
                {"time": "09:00", "available": True, "modality": "presencial"},
                {"time": "10:00", "available": False, "modality": "presencial"},
                {"time": "14:00", "available": True, "modality": "presencial"},
                {"time": "15:00", "available": True, "modality": "presencial"},
                {"time": "16:00", "available": True, "modality": "presencial"}
            ]
            
            return json.dumps({
                "success": True,
                "doctor_id": doctor_id,
                "doctor_name": "ERNESTO GIL BUCHILLÓN",
                "date": date or "2024-01-15",
                "online_slots": online_slots,
                "presencial_slots": presencial_slots,
                "special_note": "Dr. Ernesto é o único que faz consultas online nos horários fixos"
            }, indent=2, ensure_ascii=False)
        else:
            # Outros médicos - apenas presencial
            presencial_slots = [
                {"time": "08:00", "available": True, "modality": "presencial"},
                {"time": "09:00", "available": False, "modality": "presencial"},
                {"time": "10:00", "available": True, "modality": "presencial"},
                {"time": "14:00", "available": True, "modality": "presencial"},
                {"time": "15:00", "available": True, "modality": "presencial"},
                {"time": "16:00", "available": False, "modality": "presencial"}
            ]
            
            return json.dumps({
                "success": True,
                "doctor_id": doctor_id or "geral",
                "date": date or "2024-01-15",
                "presencial_slots": presencial_slots,
                "online_slots": [],
                "note": "Consultas online disponíveis apenas com Dr. Ernesto"
            }, indent=2, ensure_ascii=False)
    
    def _validate_appointment(self, patient_age: int = None, specialty: str = None, 
                           modality: str = None, doctor_id: int = None, **kwargs) -> str:
        """Valida dados de agendamento conforme regras da clínica"""
        
        validations = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Validação de idade mínima
        if patient_age is not None:
            if patient_age < 7:
                validations["valid"] = False
                validations["errors"].append("Clínica atende pacientes a partir de 7 anos")
            elif patient_age < 18 and doctor_id != 5:
                validations["valid"] = False
                validations["errors"].append("Menores de 18 anos DEVEM ser atendidos pelo Dr. Ernesto (ID: 5)")
                validations["recommendations"].append("Agendar com Dr. Ernesto Gil Buchillón")
        
        # Validação de consulta online
        if modality and modality.lower() == "online":
            if doctor_id != 5:
                validations["valid"] = False
                validations["errors"].append("Consultas online disponíveis APENAS com Dr. Ernesto")
                validations["recommendations"].append("Alterar para Dr. Ernesto ou modalidade presencial")
        
        # Validação de relatórios médicos
        if specialty and "relatorio" in specialty.lower():
            if doctor_id != 5:
                validations["valid"] = False
                validations["errors"].append("Relatórios médicos elaborados APENAS pelo Dr. Ernesto")
                validations["recommendations"].append("Agendar com Dr. Ernesto para relatório médico")
        
        # Validação de especialidade
        if specialty:
            specialty_upper = specialty.upper()
            if specialty_upper not in self.CLINIC_SPECIALTIES:
                validations["valid"] = False
                validations["errors"].append(f"Especialidade '{specialty}' não disponível")
                validations["recommendations"].append(f"Especialidades disponíveis: {', '.join(self.CLINIC_SPECIALTIES.keys())}")
        
        # Adicionar políticas da clínica se válido
        if validations["valid"]:
            validations["clinic_policies"] = self.CLINIC_INFO["policies"]
            validations["working_hours"] = self.CLINIC_INFO["working_hours"]
        
        return json.dumps({
            "success": True,
            "validation": validations,
            "timestamp": datetime.now().isoformat()
        }, indent=2, ensure_ascii=False)
    
    def _get_clinic_info(self) -> str:
        """Retorna informações gerais da clínica"""
        return json.dumps({
            "success": True,
            "clinic": self.CLINIC_INFO
        }, indent=2, ensure_ascii=False)
    
    def _get_prices(self) -> str:
        """Retorna tabela de preços da clínica"""
        prices = {}
        for code, info in self.CLINIC_SPECIALTIES.items():
            prices[info["name"]] = info["price"]
        
        prices["Relatório Médico"] = self.DR_ERNESTO_INFO["report_price"]
        
        return json.dumps({
            "success": True,
            "year": 2024,
            "prices": prices,
            "payment_methods": self.CLINIC_INFO["policies"]["payment_methods"],
            "policies": {
                "no_free_return": self.CLINIC_INFO["policies"]["no_free_return_private"],
                "insurance_interval": self.CLINIC_INFO["policies"]["insurance_interval"],
                "reports_payment": self.CLINIC_INFO["policies"]["reports_payment"]
            }
        }, indent=2, ensure_ascii=False)
    
    def _check_child_eligibility(self, age: int, **kwargs) -> str:
        """Verifica elegibilidade para atendimento de crianças"""
        
        if age < 7:
            return json.dumps({
                "success": False,
                "eligible": False,
                "reason": "Clínica atende pacientes a partir de 7 anos",
                "minimum_age": 7
            }, indent=2, ensure_ascii=False)
        elif age < 18:
            return json.dumps({
                "success": True,
                "eligible": True,
                "required_doctor": self.DR_ERNESTO_INFO,
                "special_rule": "Menores de 18 anos DEVEM ser atendidos pelo Dr. Ernesto",
                "note": "Dr. Ernesto é o único médico autorizado para crianças e adolescentes"
            }, indent=2, ensure_ascii=False)
        else:
            return json.dumps({
                "success": True,
                "eligible": True,
                "adult_patient": True,
                "available_doctors": "Todos os médicos da especialidade escolhida"
            }, indent=2, ensure_ascii=False)
    
    def _get_online_options(self) -> str:
        """Retorna opções de consulta online"""
        return json.dumps({
            "success": True,
            "online_consultation": {
                "available": True,
                "exclusive_doctor": self.DR_ERNESTO_INFO,
                "fixed_slots": self.DR_ERNESTO_INFO["online_slots"],
                "specialty": "Psiquiatria apenas",
                "price": "R$ 500,00",
                "important_note": "Dr. Ernesto é o ÚNICO médico que realiza consultas online",
                "booking_rule": "Horários fixos não negociáveis: 11:45, 17:00, 17:15"
            },
            "other_doctors": {
                "online_available": False,
                "modality": "Presencial apenas",
                "note": "Demais médicos atendem apenas presencialmente"
            }
        }, indent=2, ensure_ascii=False)

# Função helper para uso direto
def create_vivacita_tool() -> VivacitaMCPTool:
    """Factory function para criar instância da ferramenta"""
    return VivacitaMCPTool()

# Teste básico da ferramenta
if __name__ == "__main__":
    tool = VivacitaMCPTool()
    
    # Teste das principais funcionalidades
    print("=== Teste VivacitaMCPTool ===")
    
    print("\n1. Especialidades disponíveis:")
    result = tool._run("get_specialties")
    print(result)
    
    print("\n2. Informações do Dr. Ernesto:")
    result = tool._run("get_dr_ernesto")
    print(result)
    
    print("\n3. Validação de agendamento para criança:")
    result = tool._run("validate_appointment", patient_age=10, specialty="PSIQUIATRA", modality="presencial")
    print(result)
    
    print("\n4. Opções de consulta online:")
    result = tool._run("get_online_options")
    print(result)