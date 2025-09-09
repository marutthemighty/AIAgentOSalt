from core.base_agent import BaseAgent
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
import statistics
import numpy as np

class AnalyticsEstimator(BaseAgent):
    """
    Agent that predicts project effort, timelines, and costs based on 
    historical data and briefs using data-driven insights
    """
    
    def __init__(self, ai_client):
        super().__init__(ai_client, "analytics_estimator")
        
        # Historical data patterns (would be loaded from database in real implementation)
        self.historical_patterns = {
            'website': {
                'avg_duration_days': 45,
                'avg_cost_range': (5000, 15000),
                'complexity_factors': ['pages', 'features', 'integrations'],
                'common_overruns': 1.2
            },
            'branding': {
                'avg_duration_days': 30,
                'avg_cost_range': (3000, 10000),
                'complexity_factors': ['logo_variations', 'brand_guidelines', 'applications'],
                'common_overruns': 1.1
            },
            'marketing': {
                'avg_duration_days': 21,
                'avg_cost_range': (2500, 8000),
                'complexity_factors': ['campaigns', 'channels', 'content_volume'],
                'common_overruns': 1.15
            }
        }
        
        # Cost factors and multipliers
        self.cost_factors = {
            'complexity': {'simple': 0.8, 'medium': 1.0, 'complex': 1.5, 'very_complex': 2.0},
            'timeline': {'rushed': 1.3, 'normal': 1.0, 'flexible': 0.9},
            'team_size': {'solo': 0.7, 'small': 1.0, 'medium': 1.4, 'large': 2.0},
            'client_tier': {'startup': 0.8, 'sme': 1.0, 'enterprise': 1.5}
        }
        
        # Risk factors
        self.risk_factors = [
            'unclear_requirements',
            'tight_deadline',
            'complex_integrations',
            'new_technology',
            'multiple_stakeholders',
            'scope_creep_history'
        ]
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze project and provide effort, timeline, and cost predictions
        
        Args:
            input_data: Dictionary containing 'brief', 'historical_data', 'team_info'
            
        Returns:
            Dictionary with predictions, confidence levels, and recommendations
        """
        required_fields = ['brief']
        if not self._validate_input(input_data, required_fields):
            raise ValueError("Missing required fields for analytics estimation")
        
        return await self._safe_execute(self._analyze_project_metrics, input_data)
    
    async def _analyze_project_metrics(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to analyze project and generate predictions"""
        
        brief = input_data['brief']
        historical_data = input_data.get('historical_data', [])
        team_info = input_data.get('team_info', {})
        
        # Extract project characteristics
        project_type = brief.get('project_type', 'general').lower()
        deliverables = brief.get('deliverables', [])
        constraints = brief.get('constraints', {})
        timeline = brief.get('timeline', {})
        
        # Analyze complexity
        complexity_analysis = self._analyze_complexity(brief, deliverables)
        
        # Analyze historical patterns
        historical_insights = self._analyze_historical_data(historical_data, project_type)
        
        # Use AI to generate comprehensive analysis
        ai_prompt = f"""
        Analyze the following project brief and provide data-driven predictions for effort, timeline, and costs:

        Project Brief: {json.dumps(brief, indent=2)}
        Project Type: {project_type}
        Deliverables: {json.dumps(deliverables, indent=2)}
        Constraints: {json.dumps(constraints, indent=2)}
        Timeline Requirements: {json.dumps(timeline, indent=2)}
        Complexity Analysis: {json.dumps(complexity_analysis, indent=2)}
        Historical Insights: {json.dumps(historical_insights, indent=2)}
        Team Information: {json.dumps(team_info, indent=2)}

        Please provide a JSON response with the following analytics structure:
        {{
            "effort_estimation": {{
                "total_hours": "Estimated total project hours",
                "phase_breakdown": [
                    {{
                        "phase": "Phase name",
                        "estimated_hours": "Hours for this phase",
                        "percentage_of_total": "Percentage of total effort",
                        "confidence_level": "high/medium/low",
                        "key_activities": ["Main activities in this phase"]
                    }}
                ],
                "team_allocation": {{
                    "project_manager": "Hours needed",
                    "designer": "Hours needed",
                    "developer": "Hours needed",
                    "content_creator": "Hours needed",
                    "other_roles": "Additional roles and hours"
                }},
                "effort_confidence": "Overall confidence in effort estimates"
            }},
            "timeline_prediction": {{
                "estimated_duration": "Total project duration in days/weeks",
                "critical_path": ["Key milestones that drive timeline"],
                "milestone_dates": [
                    {{
                        "milestone": "Milestone name",
                        "estimated_date": "YYYY-MM-DD",
                        "dependency": "What this depends on",
                        "risk_level": "high/medium/low"
                    }}
                ],
                "buffer_recommendations": {{
                    "design_phase": "Recommended buffer time",
                    "development_phase": "Recommended buffer time",
                    "review_cycles": "Time for client reviews",
                    "contingency": "Overall contingency buffer"
                }},
                "timeline_confidence": "Confidence in timeline predictions"
            }},
            "cost_estimation": {{
                "base_cost": "Base project cost estimate",
                "cost_range": {{
                    "minimum": "Conservative estimate",
                    "most_likely": "Most probable cost",
                    "maximum": "Worst-case scenario cost"
                }},
                "cost_breakdown": [
                    {{
                        "category": "Cost category",
                        "amount": "Cost for this category",
                        "percentage": "Percentage of total cost",
                        "justification": "Why this cost is necessary"
                    }}
                ],
                "additional_costs": [
                    {{
                        "item": "Additional cost item",
                        "cost": "Estimated cost",
                        "likelihood": "Probability this will be needed",
                        "description": "What this covers"
                    }}
                ],
                "cost_confidence": "Confidence in cost estimates"
            }},
            "risk_analysis": {{
                "overall_risk_level": "high/medium/low",
                "identified_risks": [
                    {{
                        "risk": "Risk description",
                        "probability": "high/medium/low",
                        "impact": "high/medium/low",
                        "mitigation": "How to mitigate this risk",
                        "cost_impact": "Potential cost increase"
                    }}
                ],
                "risk_mitigation_cost": "Additional budget for risk mitigation",
                "confidence_factors": ["Factors affecting prediction confidence"]
            }},
            "resource_requirements": {{
                "team_composition": {{
                    "required_roles": ["List of roles needed"],
                    "skill_levels": ["Required skill levels"],
                    "team_size": "Optimal team size",
                    "collaboration_requirements": "Team coordination needs"
                }},
                "technology_requirements": {{
                    "software_licenses": ["Required software"],
                    "hardware_needs": ["Hardware requirements"],
                    "third_party_services": ["External services needed"],
                    "infrastructure_costs": "Infrastructure-related costs"
                }},
                "external_dependencies": [
                    {{
                        "dependency": "External dependency",
                        "provider": "Who provides this",
                        "timeline_impact": "How this affects timeline",
                        "cost_impact": "Associated costs"
                    }}
                ]
            }},
            "success_metrics": {{
                "project_success_indicators": ["How to measure project success"],
                "quality_metrics": ["Quality measurement criteria"],
                "performance_benchmarks": ["Performance targets"],
                "client_satisfaction_factors": ["Factors affecting client satisfaction"]
            }},
            "recommendations": {{
                "project_approach": "Recommended approach for this project",
                "pricing_strategy": "Suggested pricing approach",
                "timeline_optimization": ["Ways to optimize timeline"],
                "cost_optimization": ["Ways to optimize costs"],
                "risk_management": ["Key risk management strategies"]
            }},
            "comparative_analysis": {{
                "similar_projects": "How this compares to similar projects",
                "industry_benchmarks": "Industry standard comparisons",
                "competitive_positioning": "Market positioning insights",
                "value_proposition": "Unique value this project offers"
            }}
        }}
        """
        
        ai_response = await self._generate_ai_response(ai_prompt)
        
        try:
            analytics_report = json.loads(ai_response)
            
            # Enhance with statistical analysis
            analytics_report['statistical_analysis'] = self._perform_statistical_analysis(
                historical_data, project_type, complexity_analysis
            )
            
            # Add predictive models
            analytics_report['predictive_models'] = self._generate_predictive_models(
                brief, historical_insights, complexity_analysis
            )
            
            # Add scenario analysis
            analytics_report['scenario_analysis'] = self._perform_scenario_analysis(
                analytics_report['cost_estimation'], analytics_report['timeline_prediction']
            )
            
            # Add metadata
            analytics_report['analysis_timestamp'] = datetime.now().isoformat()
            analytics_report['analyzer_version'] = '1.0.0'
            analytics_report['data_sources'] = {
                'historical_projects': len(historical_data),
                'industry_benchmarks': 'included',
                'complexity_factors': len(complexity_analysis.get('factors', []))
            }
            
            # Learn from analysis
            self._learn_from_analysis(brief, analytics_report)
            
            return analytics_report
            
        except json.JSONDecodeError:
            self.logger.warning("AI response wasn't valid JSON, using fallback analysis")
            return self._fallback_analysis(brief, complexity_analysis, historical_insights)
    
    def _analyze_complexity(self, brief: Dict[str, Any], deliverables: List[Dict]) -> Dict[str, Any]:
        """Analyze project complexity based on brief and deliverables"""
        
        complexity_factors = {
            'deliverable_count': len(deliverables),
            'scope_clarity': 'high',  # Would be determined by brief analysis
            'technical_complexity': 'medium',
            'integration_requirements': [],
            'stakeholder_count': 1
        }
        
        # Analyze deliverables for complexity indicators
        complex_deliverables = 0
        integration_needs = []
        
        for deliverable in deliverables:
            item = deliverable.get('item', '').lower()
            
            # Check for complex deliverables
            if any(keyword in item for keyword in ['integration', 'api', 'database', 'custom']):
                complex_deliverables += 1
            
            # Check for integrations
            if 'integration' in item or 'api' in item:
                integration_needs.append(item)
        
        complexity_factors['complex_deliverables'] = complex_deliverables
        complexity_factors['integration_requirements'] = integration_needs
        
        # Calculate overall complexity score
        score = 0
        if len(deliverables) > 10:
            score += 2
        elif len(deliverables) > 5:
            score += 1
        
        if complex_deliverables > 3:
            score += 2
        elif complex_deliverables > 0:
            score += 1
        
        if len(integration_needs) > 0:
            score += 1
        
        # Determine complexity level
        if score >= 4:
            complexity_level = 'very_complex'
        elif score >= 3:
            complexity_level = 'complex'
        elif score >= 2:
            complexity_level = 'medium'
        else:
            complexity_level = 'simple'
        
        complexity_factors['overall_complexity'] = complexity_level
        complexity_factors['complexity_score'] = score
        
        return complexity_factors
    
    def _analyze_historical_data(self, historical_data: List[Dict], project_type: str) -> Dict[str, Any]:
        """Analyze historical project data for patterns"""
        
        if not historical_data:
            # Use default patterns if no historical data
            return self.historical_patterns.get(project_type, self.historical_patterns['website'])
        
        # Analyze historical projects
        similar_projects = [p for p in historical_data if p.get('type', '').lower() == project_type]
        
        if not similar_projects:
            similar_projects = historical_data  # Use all data if no exact matches
        
        insights = {
            'project_count': len(similar_projects),
            'avg_duration': 0,
            'avg_cost': 0,
            'success_rate': 0,
            'common_overruns': 1.0
        }
        
        if similar_projects:
            durations = [p.get('duration_days', 30) for p in similar_projects if p.get('duration_days')]
            costs = [p.get('final_cost', 5000) for p in similar_projects if p.get('final_cost')]
            successes = [p.get('successful', True) for p in similar_projects]
            
            if durations:
                insights['avg_duration'] = statistics.mean(durations)
                insights['duration_std'] = statistics.stdev(durations) if len(durations) > 1 else 0
            
            if costs:
                insights['avg_cost'] = statistics.mean(costs)
                insights['cost_std'] = statistics.stdev(costs) if len(costs) > 1 else 0
            
            insights['success_rate'] = sum(successes) / len(successes) * 100
            
            # Calculate overrun patterns
            estimated_costs = [p.get('estimated_cost', p.get('final_cost', 5000)) for p in similar_projects]
            final_costs = [p.get('final_cost', 5000) for p in similar_projects]
            
            if estimated_costs and final_costs:
                overruns = [final / estimated for estimated, final in zip(estimated_costs, final_costs) if estimated > 0]
                if overruns:
                    insights['common_overruns'] = statistics.mean(overruns)
        
        return insights
    
    def _perform_statistical_analysis(self, historical_data: List[Dict], project_type: str, complexity: Dict[str, Any]) -> Dict[str, Any]:
        """Perform statistical analysis on historical data"""
        
        if not historical_data:
            return {'error': 'Insufficient historical data for statistical analysis'}
        
        # Filter relevant projects
        relevant_projects = [
            p for p in historical_data 
            if p.get('type', '').lower() == project_type or not project_type
        ]
        
        if len(relevant_projects) < 3:
            relevant_projects = historical_data  # Use all data if too few similar projects
        
        analysis = {
            'sample_size': len(relevant_projects),
            'confidence_level': '95%' if len(relevant_projects) >= 10 else '80%'
        }
        
        # Duration analysis
        durations = [p.get('duration_days', 30) for p in relevant_projects if p.get('duration_days')]
        if durations:
            analysis['duration_stats'] = {
                'mean': statistics.mean(durations),
                'median': statistics.median(durations),
                'std_dev': statistics.stdev(durations) if len(durations) > 1 else 0,
                'min': min(durations),
                'max': max(durations),
                'percentile_25': np.percentile(durations, 25),
                'percentile_75': np.percentile(durations, 75)
            }
        
        # Cost analysis
        costs = [p.get('final_cost', 5000) for p in relevant_projects if p.get('final_cost')]
        if costs:
            analysis['cost_stats'] = {
                'mean': statistics.mean(costs),
                'median': statistics.median(costs),
                'std_dev': statistics.stdev(costs) if len(costs) > 1 else 0,
                'min': min(costs),
                'max': max(costs),
                'percentile_25': np.percentile(costs, 25),
                'percentile_75': np.percentile(costs, 75)
            }
        
        # Success rate analysis
        successes = [p.get('successful', True) for p in relevant_projects]
        analysis['success_rate'] = sum(successes) / len(successes) * 100 if successes else 100
        
        return analysis
    
    def _generate_predictive_models(self, brief: Dict[str, Any], historical_insights: Dict[str, Any], complexity: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictive models for the project"""
        
        project_type = brief.get('project_type', 'general').lower()
        
        # Base predictions from historical data
        base_duration = historical_insights.get('avg_duration', 30)
        base_cost = historical_insights.get('avg_cost', 5000)
        
        # Apply complexity multipliers
        complexity_level = complexity.get('overall_complexity', 'medium')
        complexity_multiplier = self.cost_factors['complexity'].get(complexity_level, 1.0)
        
        # Timeline prediction model
        timeline_model = {
            'base_duration': base_duration,
            'complexity_adjusted': base_duration * complexity_multiplier,
            'confidence_interval': {
                'lower': base_duration * 0.8,
                'upper': base_duration * 1.3
            },
            'factors': {
                'complexity': complexity_multiplier,
                'team_experience': 1.0,  # Would be calculated from team_info
                'client_responsiveness': 1.1  # Default assumption
            }
        }
        
        # Cost prediction model
        cost_model = {
            'base_cost': base_cost,
            'complexity_adjusted': base_cost * complexity_multiplier,
            'confidence_interval': {
                'lower': base_cost * 0.85,
                'upper': base_cost * 1.4
            },
            'risk_adjusted': base_cost * complexity_multiplier * historical_insights.get('common_overruns', 1.2)
        }
        
        # Success probability model
        success_model = {
            'base_success_rate': historical_insights.get('success_rate', 90),
            'complexity_penalty': max(0, (5 - complexity.get('complexity_score', 3)) * 5),
            'predicted_success_rate': min(95, historical_insights.get('success_rate', 90) - 
                                        max(0, (complexity.get('complexity_score', 3) - 3) * 10))
        }
        
        return {
            'timeline_model': timeline_model,
            'cost_model': cost_model,
            'success_model': success_model,
            'model_confidence': 'medium'  # Would be calculated based on data quality
        }
    
    def _perform_scenario_analysis(self, cost_estimation: Dict[str, Any], timeline_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Perform scenario analysis for different project outcomes"""
        
        base_cost = float(str(cost_estimation.get('base_cost', 5000)).replace('$', '').replace(',', ''))
        base_duration = 30  # Default
        
        # Extract duration from timeline prediction
        duration_str = timeline_prediction.get('estimated_duration', '30 days')
        if 'day' in duration_str:
            try:
                base_duration = int(duration_str.split()[0])
            except:
                base_duration = 30
        elif 'week' in duration_str:
            try:
                base_duration = int(duration_str.split()[0]) * 7
            except:
                base_duration = 30
        
        scenarios = {
            'best_case': {
                'probability': '20%',
                'description': 'Everything goes perfectly',
                'cost_multiplier': 0.9,
                'duration_multiplier': 0.85,
                'estimated_cost': base_cost * 0.9,
                'estimated_duration': base_duration * 0.85,
                'key_factors': ['No scope changes', 'Quick client approvals', 'No technical issues']
            },
            'most_likely': {
                'probability': '60%',
                'description': 'Normal project progression',
                'cost_multiplier': 1.0,
                'duration_multiplier': 1.0,
                'estimated_cost': base_cost,
                'estimated_duration': base_duration,
                'key_factors': ['Some minor scope changes', 'Normal review cycles', 'Minor issues resolved quickly']
            },
            'worst_case': {
                'probability': '20%',
                'description': 'Multiple challenges arise',
                'cost_multiplier': 1.4,
                'duration_multiplier': 1.3,
                'estimated_cost': base_cost * 1.4,
                'estimated_duration': base_duration * 1.3,
                'key_factors': ['Significant scope changes', 'Technical challenges', 'Extended review cycles']
            }
        }
        
        # Add impact analysis
        impact_analysis = {
            'cost_variance': {
                'range': f"${base_cost * 0.9:,.0f} - ${base_cost * 1.4:,.0f}",
                'standard_deviation': base_cost * 0.15
            },
            'timeline_variance': {
                'range': f"{base_duration * 0.85:.0f} - {base_duration * 1.3:.0f} days",
                'standard_deviation': base_duration * 0.1
            },
            'risk_mitigation_impact': {
                'cost_reduction': 'Up to 10% with proper planning',
                'timeline_improvement': 'Up to 15% with clear requirements'
            }
        }
        
        return {
            'scenarios': scenarios,
            'impact_analysis': impact_analysis,
            'recommendation': 'Plan for most likely scenario with contingency for worst case'
        }
    
    def _learn_from_analysis(self, brief: Dict[str, Any], analytics_report: Dict[str, Any]):
        """Learn from analysis to improve future predictions"""
        
        memory_key = f"analytics_patterns_{datetime.now().strftime('%Y%m')}"
        current_patterns = self.get_memory(memory_key, {
            'prediction_accuracy': [],
            'common_complexity_factors': {},
            'cost_estimation_trends': {}
        })
        
        # Track complexity factors
        project_type = brief.get('project_type', 'general')
        complexity_level = analytics_report.get('statistical_analysis', {}).get('complexity_level', 'medium')
        
        current_patterns['common_complexity_factors'][project_type] = (
            current_patterns['common_complexity_factors'].get(project_type, {})
        )
        current_patterns['common_complexity_factors'][project_type][complexity_level] = (
            current_patterns['common_complexity_factors'][project_type].get(complexity_level, 0) + 1
        )
        
        # Track cost estimation patterns
        estimated_cost = analytics_report.get('cost_estimation', {}).get('base_cost', 0)
        try:
            cost_numeric = float(str(estimated_cost).replace('$', '').replace(',', ''))
            current_patterns['cost_estimation_trends'][project_type] = (
                current_patterns['cost_estimation_trends'].get(project_type, [])
            )
            current_patterns['cost_estimation_trends'][project_type].append(cost_numeric)
            
            # Keep only last 20 entries
            if len(current_patterns['cost_estimation_trends'][project_type]) > 20:
                current_patterns['cost_estimation_trends'][project_type] = (
                    current_patterns['cost_estimation_trends'][project_type][-20:]
                )
        except:
            pass
        
        self.update_memory(memory_key, current_patterns)
    
    def _fallback_analysis(self, brief: Dict[str, Any], complexity: Dict[str, Any], historical_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when AI response fails"""
        
        project_type = brief.get('project_type', 'general').lower()
        project_name = brief.get('project_title', 'New Project')
        
        # Use historical patterns as fallback
        patterns = self.historical_patterns.get(project_type, self.historical_patterns['website'])
        
        # Apply complexity multiplier
        complexity_level = complexity.get('overall_complexity', 'medium')
        multiplier = self.cost_factors['complexity'].get(complexity_level, 1.0)
        
        base_duration = patterns['avg_duration_days']
        base_cost = patterns['avg_cost_range'][0]  # Use lower end of range
        
        return {
            'effort_estimation': {
                'total_hours': base_duration * 6 * multiplier,  # Assume 6 hours per day
                'phase_breakdown': [
                    {
                        'phase': 'Planning & Discovery',
                        'estimated_hours': base_duration * 6 * 0.2 * multiplier,
                        'percentage_of_total': '20%',
                        'confidence_level': 'medium'
                    },
                    {
                        'phase': 'Design & Development',
                        'estimated_hours': base_duration * 6 * 0.6 * multiplier,
                        'percentage_of_total': '60%',
                        'confidence_level': 'medium'
                    },
                    {
                        'phase': 'Testing & Launch',
                        'estimated_hours': base_duration * 6 * 0.2 * multiplier,
                        'percentage_of_total': '20%',
                        'confidence_level': 'medium'
                    }
                ],
                'effort_confidence': 'medium'
            },
            'timeline_prediction': {
                'estimated_duration': f"{int(base_duration * multiplier)} days",
                'critical_path': ['Requirements gathering', 'Design approval', 'Development', 'Testing'],
                'timeline_confidence': 'medium'
            },
            'cost_estimation': {
                'base_cost': f"${base_cost * multiplier:,.0f}",
                'cost_range': {
                    'minimum': f"${base_cost * multiplier * 0.8:,.0f}",
                    'most_likely': f"${base_cost * multiplier:,.0f}",
                    'maximum': f"${base_cost * multiplier * 1.3:,.0f}"
                },
                'cost_confidence': 'medium'
            },
            'risk_analysis': {
                'overall_risk_level': complexity_level if complexity_level in ['low', 'medium', 'high'] else 'medium',
                'identified_risks': [
                    {
                        'risk': 'Scope creep',
                        'probability': 'medium',
                        'impact': 'medium',
                        'mitigation': 'Clear scope documentation and change request process'
                    },
                    {
                        'risk': 'Timeline delays',
                        'probability': 'medium',
                        'impact': 'high',
                        'mitigation': 'Regular progress reviews and buffer time'
                    }
                ]
            },
            'recommendations': {
                'project_approach': f'Standard {project_type} development approach with {complexity_level} complexity considerations',
                'pricing_strategy': 'Fixed price with clearly defined scope',
                'timeline_optimization': ['Clear requirements upfront', 'Regular client check-ins'],
                'cost_optimization': ['Phased approach', 'Reusable components']
            },
            'analysis_timestamp': datetime.now().isoformat(),
            'fallback_analysis': True,
            'data_sources': {
                'historical_projects': 0,
                'industry_benchmarks': 'standard patterns',
                'complexity_factors': len(complexity.get('factors', []))
            }
        }
    
    async def perform_cost_benefit_analysis(self, project_data: Dict[str, Any], business_goals: Dict[str, Any]) -> Dict[str, Any]:
        """Perform cost-benefit analysis for project investment"""
        
        try:
            estimated_cost = project_data.get('estimated_cost', 10000)
            project_duration = project_data.get('duration_months', 3)
            
            # Calculate potential benefits
            benefits = {
                'increased_revenue': estimated_cost * 2.5,  # Typical ROI for creative projects
                'cost_savings': estimated_cost * 0.3,
                'brand_value_increase': estimated_cost * 1.5,
                'efficiency_gains': estimated_cost * 0.8
            }
            
            # Calculate ROI
            total_benefits = sum(benefits.values())
            roi_percentage = ((total_benefits - estimated_cost) / estimated_cost) * 100
            payback_period = estimated_cost / (total_benefits / 12)  # Months
            
            return {
                'success': True,
                'cost_benefit_analysis': {
                    'total_investment': estimated_cost,
                    'projected_benefits': benefits,
                    'total_benefits': total_benefits,
                    'net_benefit': total_benefits - estimated_cost,
                    'roi_percentage': roi_percentage,
                    'payback_period_months': payback_period,
                    'break_even_point': f"{payback_period:.1f} months"
                },
                'recommendation': 'Proceed' if roi_percentage > 100 else 'Review business case'
            }
            
        except Exception as e:
            self.logger.error(f"Error performing cost-benefit analysis: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            'name': 'Analytics & Cost Estimator',
            'description': 'Predicts project effort, timelines, and costs using data-driven insights',
            'inputs': ['brief', 'historical_data', 'team_info'],
            'outputs': ['effort_estimation', 'timeline_prediction', 'cost_analysis', 'risk_assessment'],
            'analysis_types': ['complexity_analysis', 'statistical_analysis', 'scenario_analysis'],
            'features': ['predictive_modeling', 'risk_assessment', 'cost_benefit_analysis'],
            'supported_project_types': list(self.historical_patterns.keys()),
            'version': '1.0.0'
        }
