from core.base_agent import BaseAgent
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
import re

class ProposalGenerator(BaseAgent):
    """
    Agent that converts creative briefs into professional proposals
    or contracts with legal scoping and pricing
    """
    
    def __init__(self, ai_client):
        super().__init__(ai_client, "proposal_generator")
        
        # Proposal templates by project type
        self.proposal_templates = {
            'website': self._website_proposal_template,
            'branding': self._branding_proposal_template,
            'marketing': self._marketing_proposal_template,
            'general': self._general_proposal_template
        }
        
        # Standard pricing models
        self.pricing_models = {
            'fixed': 'Fixed project price',
            'hourly': 'Hourly rate billing',
            'retainer': 'Monthly retainer',
            'milestone': 'Milestone-based payments',
            'value': 'Value-based pricing'
        }
        
        # Legal terms templates
        self.legal_clauses = {
            'payment_terms': '30-day payment terms from invoice date',
            'intellectual_property': 'Client owns final deliverables upon full payment',
            'revisions': 'Up to 3 rounds of revisions included',
            'cancellation': '30-day written notice required for cancellation',
            'liability': 'Liability limited to project value',
            'confidentiality': 'Both parties maintain confidentiality'
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate professional proposal from creative brief
        
        Args:
            input_data: Dictionary containing 'brief', 'pricing_preferences', 'company_info'
            
        Returns:
            Dictionary with complete proposal including scope, timeline, and legal terms
        """
        required_fields = ['brief']
        if not self._validate_input(input_data, required_fields):
            raise ValueError("Missing required fields for proposal generation")
        
        return await self._safe_execute(self._generate_proposal, input_data)
    
    async def _generate_proposal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to generate proposal"""
        
        brief = input_data['brief']
        pricing_prefs = input_data.get('pricing_preferences', {})
        company_info = input_data.get('company_info', {})
        
        # Extract project information
        project_type = brief.get('project_type', 'general').lower()
        deliverables = brief.get('deliverables', [])
        timeline = brief.get('timeline', {})
        constraints = brief.get('constraints', {})
        
        # Generate base proposal structure using template
        template_func = self.proposal_templates.get(project_type, self.proposal_templates['general'])
        base_proposal = template_func(brief, pricing_prefs)
        
        # Use AI to enhance and customize proposal
        ai_prompt = f"""
        Create a professional proposal based on the following creative brief:

        Project Brief: {json.dumps(brief, indent=2)}
        Deliverables: {json.dumps(deliverables, indent=2)}
        Timeline: {json.dumps(timeline, indent=2)}
        Budget Constraints: {json.dumps(constraints.get('budget', 'Not specified'), indent=2)}
        Company Info: {json.dumps(company_info, indent=2)}
        Pricing Preferences: {json.dumps(pricing_prefs, indent=2)}

        Base Proposal Structure: {json.dumps(base_proposal, indent=2)}

        Please enhance this proposal and provide a JSON response with the following structure:
        {{
            "proposal_header": {{
                "title": "Professional proposal title",
                "proposal_number": "Unique proposal number",
                "date": "YYYY-MM-DD",
                "valid_until": "YYYY-MM-DD",
                "client_name": "Client name from brief",
                "project_name": "Project name"
            }},
            "executive_summary": {{
                "overview": "Compelling project overview",
                "key_benefits": ["Benefit 1", "Benefit 2", "Benefit 3"],
                "success_metrics": ["How success will be measured"],
                "timeline_summary": "High-level timeline overview"
            }},
            "project_scope": {{
                "objectives": ["Primary objective", "Secondary objectives"],
                "deliverables": [
                    {{
                        "item": "Deliverable name",
                        "description": "Detailed description",
                        "specifications": "Technical specifications",
                        "acceptance_criteria": "How completion will be measured"
                    }}
                ],
                "out_of_scope": ["What is NOT included"],
                "assumptions": ["Project assumptions"],
                "dependencies": ["Client dependencies"]
            }},
            "methodology": {{
                "approach": "Our approach to this project",
                "phases": [
                    {{
                        "name": "Phase name",
                        "duration": "Duration in weeks",
                        "description": "Phase description",
                        "deliverables": ["Phase deliverables"],
                        "milestones": ["Key milestones"]
                    }}
                ],
                "quality_assurance": "Quality assurance process",
                "communication_plan": "How we'll communicate progress"
            }},
            "timeline": {{
                "project_duration": "Total project duration",
                "start_date": "Proposed start date",
                "end_date": "Proposed end date",
                "key_milestones": [
                    {{
                        "milestone": "Milestone name",
                        "date": "YYYY-MM-DD",
                        "description": "Milestone description"
                    }}
                ],
                "critical_path": ["Critical path items"],
                "buffer_time": "Built-in buffer time"
            }},
            "investment": {{
                "pricing_model": "fixed/hourly/milestone/retainer",
                "total_investment": "Total project cost",
                "payment_schedule": [
                    {{
                        "milestone": "Payment milestone",
                        "amount": "Payment amount",
                        "due_date": "When payment is due"
                    }}
                ],
                "included_services": ["What's included in the price"],
                "additional_costs": ["Potential additional costs"],
                "payment_terms": "Payment terms and conditions"
            }},
            "team_and_expertise": {{
                "team_overview": "Team that will work on project",
                "key_team_members": [
                    {{
                        "name": "Team member name",
                        "role": "Their role on project",
                        "experience": "Relevant experience"
                    }}
                ],
                "company_credentials": "Company background and credentials",
                "relevant_experience": "Similar projects completed",
                "case_studies": ["Brief case study references"]
            }},
            "terms_and_conditions": {{
                "project_terms": ["Key project terms"],
                "intellectual_property": "IP ownership terms",
                "revision_policy": "Revision and change request policy",
                "cancellation_policy": "Project cancellation terms",
                "confidentiality": "Confidentiality agreement terms",
                "liability_limitation": "Liability limitation terms"
            }},
            "next_steps": {{
                "proposal_approval": "How to approve this proposal",
                "project_kickoff": "Next steps after approval",
                "contact_information": "Who to contact with questions",
                "proposal_validity": "How long this proposal is valid"
            }}
        }}
        """
        
        ai_response = await self._generate_ai_response(ai_prompt)
        
        try:
            enhanced_proposal = json.loads(ai_response)
            
            # Add additional components
            enhanced_proposal['risk_mitigation'] = self._generate_risk_mitigation(brief)
            enhanced_proposal['appendices'] = self._generate_appendices(brief, enhanced_proposal)
            enhanced_proposal['contract_addendum'] = self._generate_contract_terms(enhanced_proposal)
            
            # Add metadata
            enhanced_proposal['generated_at'] = datetime.now().isoformat()
            enhanced_proposal['generator_version'] = '1.0.0'
            enhanced_proposal['based_on_brief'] = brief.get('project_title', 'Unknown Project')
            
            # Learn from generation
            self._learn_from_proposal(brief, enhanced_proposal)
            
            return enhanced_proposal
            
        except json.JSONDecodeError:
            self.logger.warning("AI response wasn't valid JSON, using fallback generation")
            return self._fallback_proposal_generation(brief, base_proposal)
    
    def _website_proposal_template(self, brief: Dict[str, Any], pricing_prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate website project proposal template"""
        return {
            'project_type': 'website',
            'estimated_duration': '6-8 weeks',
            'phases': [
                'Discovery & Planning',
                'Design & User Experience',
                'Development & Integration',
                'Testing & Launch'
            ],
            'key_deliverables': [
                'Responsive website design',
                'Content management system',
                'SEO optimization',
                'Analytics integration'
            ],
            'pricing_range': pricing_prefs.get('website_range', '$5,000 - $15,000')
        }
    
    def _branding_proposal_template(self, brief: Dict[str, Any], pricing_prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate branding project proposal template"""
        return {
            'project_type': 'branding',
            'estimated_duration': '4-6 weeks',
            'phases': [
                'Brand Strategy Development',
                'Logo Design & Concepts',
                'Brand Guidelines Creation',
                'Brand Asset Development'
            ],
            'key_deliverables': [
                'Logo design and variations',
                'Brand guidelines document',
                'Color palette and typography',
                'Business card and letterhead designs'
            ],
            'pricing_range': pricing_prefs.get('branding_range', '$3,000 - $10,000')
        }
    
    def _marketing_proposal_template(self, brief: Dict[str, Any], pricing_prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate marketing project proposal template"""
        return {
            'project_type': 'marketing',
            'estimated_duration': '3-4 weeks',
            'phases': [
                'Campaign Strategy',
                'Content Creation',
                'Campaign Launch',
                'Optimization & Reporting'
            ],
            'key_deliverables': [
                'Marketing strategy document',
                'Creative assets',
                'Campaign setup and launch',
                'Performance reports'
            ],
            'pricing_range': pricing_prefs.get('marketing_range', '$2,500 - $8,000')
        }
    
    def _general_proposal_template(self, brief: Dict[str, Any], pricing_prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate general project proposal template"""
        return {
            'project_type': 'general',
            'estimated_duration': '4-6 weeks',
            'phases': [
                'Project Discovery',
                'Concept Development',
                'Implementation',
                'Final Delivery'
            ],
            'key_deliverables': [
                'Project deliverables as specified',
                'Documentation',
                'Final presentation'
            ],
            'pricing_range': pricing_prefs.get('general_range', '$3,000 - $12,000')
        }
    
    def _generate_risk_mitigation(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Generate risk mitigation strategies"""
        
        # Identify potential risks from brief
        constraints = brief.get('constraints', {})
        timeline = brief.get('timeline', {})
        
        risks = {
            'timeline_risks': {
                'description': 'Potential delays due to client feedback cycles',
                'mitigation': 'Built-in buffer time and clear milestone approvals'
            },
            'scope_creep': {
                'description': 'Additional requests outside original scope',
                'mitigation': 'Clear scope definition and change request process'
            },
            'technical_risks': {
                'description': 'Unforeseen technical challenges',
                'mitigation': 'Thorough technical discovery and contingency planning'
            }
        }
        
        # Add budget-specific risks if mentioned
        if constraints.get('budget'):
            risks['budget_risks'] = {
                'description': 'Budget constraints affecting deliverable quality',
                'mitigation': 'Phased approach with priority-based deliverables'
            }
        
        return risks
    
    def _generate_appendices(self, brief: Dict[str, Any], proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Generate proposal appendices"""
        
        return {
            'appendix_a': {
                'title': 'Detailed Project Timeline',
                'content': 'Comprehensive Gantt chart and milestone breakdown'
            },
            'appendix_b': {
                'title': 'Technical Specifications',
                'content': 'Detailed technical requirements and standards'
            },
            'appendix_c': {
                'title': 'Portfolio Examples',
                'content': 'Relevant case studies and previous work examples'
            },
            'appendix_d': {
                'title': 'Terms and Conditions',
                'content': 'Complete legal terms and service agreement'
            }
        }
    
    def _generate_contract_terms(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contract-ready legal terms"""
        
        return {
            'service_agreement': {
                'scope_of_work': 'Detailed scope as outlined in proposal',
                'deliverables': 'All deliverables as specified',
                'timeline': proposal.get('timeline', {}),
                'payment_terms': proposal.get('investment', {}).get('payment_terms', self.legal_clauses['payment_terms'])
            },
            'legal_terms': {
                'intellectual_property': self.legal_clauses['intellectual_property'],
                'liability_limitation': self.legal_clauses['liability'],
                'confidentiality': self.legal_clauses['confidentiality'],
                'termination_clause': self.legal_clauses['cancellation']
            },
            'project_terms': {
                'revision_policy': self.legal_clauses['revisions'],
                'change_requests': 'Additional work requires written approval and separate billing',
                'force_majeure': 'Standard force majeure clause applies',
                'governing_law': 'Agreement governed by [State/Country] law'
            }
        }
    
    def _learn_from_proposal(self, brief: Dict[str, Any], proposal: Dict[str, Any]):
        """Learn from proposal generation to improve future results"""
        
        memory_key = f"proposal_patterns_{datetime.now().strftime('%Y%m')}"
        current_patterns = self.get_memory(memory_key, {
            'successful_pricing_models': {},
            'common_project_durations': {},
            'popular_payment_terms': {}
        })
        
        # Track pricing model usage
        pricing_model = proposal.get('investment', {}).get('pricing_model', 'unknown')
        current_patterns['successful_pricing_models'][pricing_model] = (
            current_patterns['successful_pricing_models'].get(pricing_model, 0) + 1
        )
        
        # Track project durations
        duration = proposal.get('timeline', {}).get('project_duration', 'unknown')
        current_patterns['common_project_durations'][duration] = (
            current_patterns['common_project_durations'].get(duration, 0) + 1
        )
        
        self.update_memory(memory_key, current_patterns)
    
    def _fallback_proposal_generation(self, brief: Dict[str, Any], base_proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback proposal generation when AI response fails"""
        
        project_name = brief.get('project_title', 'New Project')
        client_name = brief.get('client_name', 'Valued Client')
        
        return {
            'proposal_header': {
                'title': f'Proposal for {project_name}',
                'proposal_number': f'PROP-{datetime.now().strftime("%Y%m%d")}-001',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'valid_until': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'client_name': client_name,
                'project_name': project_name
            },
            'executive_summary': {
                'overview': f'Professional {base_proposal.get("project_type", "project")} services for {client_name}',
                'key_benefits': ['Professional results', 'Timely delivery', 'Ongoing support'],
                'timeline_summary': base_proposal.get('estimated_duration', '4-6 weeks')
            },
            'project_scope': {
                'objectives': [brief.get('goals', {}).get('primary', 'Achieve project goals')],
                'deliverables': base_proposal.get('key_deliverables', ['Project deliverables']),
                'out_of_scope': ['Items not specified in original brief']
            },
            'investment': {
                'pricing_model': 'fixed',
                'total_investment': base_proposal.get('pricing_range', 'To be determined'),
                'payment_terms': self.legal_clauses['payment_terms']
            },
            'terms_and_conditions': self.legal_clauses,
            'generated_at': datetime.now().isoformat(),
            'fallback_generation': True
        }
    
    async def generate_contract(self, proposal: Dict[str, Any], client_signature_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Convert approved proposal into legal contract"""
        try:
            contract_data = {
                'contract_header': {
                    'title': f"Service Agreement - {proposal.get('proposal_header', {}).get('project_name', 'Project')}",
                    'contract_number': f"CONT-{datetime.now().strftime('%Y%m%d')}-001",
                    'effective_date': datetime.now().strftime('%Y-%m-%d'),
                    'parties': {
                        'service_provider': 'Your Company Name',
                        'client': proposal.get('proposal_header', {}).get('client_name', 'Client')
                    }
                },
                'scope_of_work': proposal.get('project_scope', {}),
                'timeline_and_deliverables': proposal.get('timeline', {}),
                'compensation': proposal.get('investment', {}),
                'legal_terms': proposal.get('contract_addendum', {}),
                'signature_section': {
                    'client_signature_required': True,
                    'provider_signature': 'Digital signature applied',
                    'witness_required': False
                }
            }
            
            return {
                'success': True,
                'contract': contract_data,
                'contract_id': contract_data['contract_header']['contract_number']
            }
        except Exception as e:
            self.logger.error(f"Error generating contract: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            'name': 'Proposal Generator',
            'description': 'Generates professional proposals and contracts from creative briefs',
            'inputs': ['brief', 'pricing_preferences', 'company_info'],
            'outputs': ['proposal', 'contract', 'legal_terms'],
            'supported_project_types': ['website', 'branding', 'marketing', 'general'],
            'pricing_models': list(self.pricing_models.keys()),
            'features': ['risk_assessment', 'legal_compliance', 'contract_generation'],
            'version': '1.0.0'
        }
