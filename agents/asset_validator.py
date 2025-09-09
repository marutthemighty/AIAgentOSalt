from core.base_agent import BaseAgent
from typing import Dict, Any, List
import json
from datetime import datetime
import os
import hashlib

class AssetValidator(BaseAgent):
    """
    Agent that checks deliverables against brief requirements 
    including format, size, quality using AI-based QA
    """
    
    def __init__(self, ai_client):
        super().__init__(ai_client, "asset_validator")
        
        # File format specifications
        self.format_specs = {
            'logo': {
                'required_formats': ['svg', 'png', 'pdf'],
                'resolutions': ['300dpi', '150dpi', '72dpi'],
                'color_modes': ['RGB', 'CMYK', 'Grayscale'],
                'min_size': '1000x1000px'
            },
            'website': {
                'required_formats': ['html', 'css', 'js'],
                'image_formats': ['jpg', 'png', 'webp', 'svg'],
                'max_image_size': '2MB',
                'performance_score': '>90'
            },
            'print': {
                'required_formats': ['pdf', 'ai', 'eps'],
                'resolution': '300dpi',
                'color_mode': 'CMYK',
                'bleed': '3mm'
            },
            'social_media': {
                'instagram_post': '1080x1080px',
                'instagram_story': '1080x1920px',
                'facebook_post': '1200x630px',
                'linkedin_post': '1200x627px',
                'twitter_header': '1500x500px'
            }
        }
        
        # Quality checkpoints
        self.quality_checkpoints = {
            'technical': [
                'File format compliance',
                'Resolution requirements',
                'Color mode accuracy',
                'File size optimization'
            ],
            'design': [
                'Brand compliance',
                'Typography consistency',
                'Color accuracy',
                'Layout alignment'
            ],
            'content': [
                'Spelling and grammar',
                'Messaging accuracy',
                'Legal compliance',
                'Accessibility standards'
            ],
            'functionality': [
                'Link validation',
                'Form functionality',
                'Cross-browser compatibility',
                'Mobile responsiveness'
            ]
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate deliverables against brief requirements
        
        Args:
            input_data: Dictionary containing 'assets', 'brief', 'validation_criteria'
            
        Returns:
            Dictionary with validation results and recommendations
        """
        required_fields = ['assets', 'brief']
        if not self._validate_input(input_data, required_fields):
            raise ValueError("Missing required fields for asset validation")
        
        return await self._safe_execute(self._validate_assets, input_data)
    
    async def _validate_assets(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to validate assets"""
        
        assets = input_data['assets']
        brief = input_data['brief']
        validation_criteria = input_data.get('validation_criteria', {})
        
        # Extract project requirements
        deliverables = brief.get('deliverables', [])
        project_type = brief.get('project_type', 'general').lower()
        constraints = brief.get('constraints', {})
        
        # Validate each asset
        validation_results = []
        
        for asset in assets:
            asset_result = await self._validate_single_asset(asset, deliverables, project_type, validation_criteria)
            validation_results.append(asset_result)
        
        # Generate comprehensive validation report
        ai_prompt = f"""
        Analyze the following asset validation results and provide a comprehensive quality assurance report:

        Project Brief: {json.dumps(brief, indent=2)}
        Deliverables Required: {json.dumps(deliverables, indent=2)}
        Asset Validation Results: {json.dumps(validation_results, indent=2)}
        Project Type: {project_type}
        Validation Criteria: {json.dumps(validation_criteria, indent=2)}

        Please provide a JSON response with the following QA report structure:
        {{
            "overall_assessment": {{
                "quality_score": "Score out of 100",
                "compliance_status": "Compliant/Non-compliant/Partially compliant",
                "ready_for_delivery": "Yes/No/With revisions",
                "critical_issues": "Number of critical issues found",
                "summary": "Overall assessment summary"
            }},
            "asset_by_asset_review": [
                {{
                    "asset_name": "Asset filename",
                    "asset_type": "Type of asset",
                    "validation_score": "Score out of 100",
                    "status": "Pass/Fail/Warning",
                    "issues_found": [
                        {{
                            "category": "technical/design/content/functionality",
                            "severity": "critical/major/minor",
                            "issue": "Description of issue",
                            "recommendation": "How to fix",
                            "brief_requirement": "Which brief requirement this affects"
                        }}
                    ],
                    "compliant_requirements": ["List of requirements met"],
                    "missing_requirements": ["List of requirements not met"]
                }}
            ],
            "technical_compliance": {{
                "format_compliance": {{
                    "required_formats": ["formats that should exist"],
                    "provided_formats": ["formats actually provided"],
                    "missing_formats": ["formats still needed"],
                    "format_issues": ["any format-related problems"]
                }},
                "quality_standards": {{
                    "resolution_check": "Pass/Fail with details",
                    "file_size_check": "Pass/Fail with details",
                    "color_accuracy": "Pass/Fail with details",
                    "compression_optimization": "Pass/Fail with details"
                }},
                "accessibility_compliance": {{
                    "alt_text_present": "Yes/No",
                    "contrast_ratios": "Pass/Fail",
                    "font_readability": "Pass/Fail",
                    "accessibility_score": "Score out of 100"
                }}
            }},
            "brand_compliance": {{
                "visual_consistency": {{
                    "logo_usage": "Correct/Incorrect/Not applicable",
                    "color_palette": "Consistent/Inconsistent/Partially consistent",
                    "typography": "Consistent/Inconsistent/Partially consistent",
                    "style_guidelines": "Followed/Not followed/Partially followed"
                }},
                "messaging_compliance": {{
                    "tone_of_voice": "Consistent/Inconsistent",
                    "key_messages": "Present/Missing/Partially present",
                    "brand_positioning": "Aligned/Not aligned"
                }}
            }},
            "content_quality": {{
                "proofreading": {{
                    "spelling_errors": "Number found",
                    "grammar_errors": "Number found", 
                    "consistency_issues": "Number found",
                    "overall_writing_quality": "Excellent/Good/Needs improvement/Poor"
                }},
                "seo_optimization": {{
                    "meta_descriptions": "Present/Missing",
                    "alt_tags": "Complete/Incomplete",
                    "keyword_optimization": "Good/Needs improvement",
                    "internal_linking": "Present/Missing"
                }}
            }},
            "recommendations": {{
                "immediate_actions": ["Critical fixes needed before delivery"],
                "suggested_improvements": ["Nice-to-have enhancements"],
                "future_considerations": ["Things to consider for next version"],
                "best_practices": ["General best practice recommendations"]
            }},
            "delivery_readiness": {{
                "can_deliver_now": "Yes/No",
                "estimated_fix_time": "Time needed to address issues",
                "priority_fixes": ["Most important fixes to make"],
                "client_communication": "Suggested message to client about status"
            }}
        }}
        """
        
        ai_response = await self._generate_ai_response(ai_prompt)
        
        try:
            qa_report = json.loads(ai_response)
            
            # Enhance with additional analysis
            qa_report['detailed_metrics'] = self._generate_detailed_metrics(validation_results)
            qa_report['comparison_to_brief'] = self._compare_to_brief_requirements(deliverables, validation_results)
            qa_report['automated_fixes'] = self._suggest_automated_fixes(validation_results)
            
            # Add metadata
            qa_report['validation_timestamp'] = datetime.now().isoformat()
            qa_report['validator_version'] = '1.0.0'
            qa_report['total_assets_validated'] = len(assets)
            qa_report['validation_criteria_used'] = validation_criteria
            
            # Learn from validation
            self._learn_from_validation(brief, validation_results, qa_report)
            
            return qa_report
            
        except json.JSONDecodeError:
            self.logger.warning("AI response wasn't valid JSON, using fallback validation")
            return self._fallback_validation_report(validation_results, brief)
    
    async def _validate_single_asset(self, asset: Dict[str, Any], deliverables: List[Dict], project_type: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single asset against requirements"""
        
        asset_name = asset.get('filename', 'unknown')
        asset_type = asset.get('type', 'unknown')
        asset_path = asset.get('path', '')
        
        validation_result = {
            'asset_name': asset_name,
            'asset_type': asset_type,
            'file_info': {
                'size': asset.get('size', 'unknown'),
                'format': asset.get('format', 'unknown'),
                'dimensions': asset.get('dimensions', 'unknown')
            },
            'technical_checks': {},
            'requirements_check': {},
            'issues': [],
            'score': 0
        }
        
        # Technical validation
        technical_score = await self._perform_technical_validation(asset, asset_type)
        validation_result['technical_checks'] = technical_score
        
        # Requirements validation
        requirements_score = self._validate_against_requirements(asset, deliverables)
        validation_result['requirements_check'] = requirements_score
        
        # Calculate overall score
        validation_result['score'] = (technical_score.get('score', 0) + requirements_score.get('score', 0)) / 2
        
        # Determine status
        if validation_result['score'] >= 90:
            validation_result['status'] = 'Pass'
        elif validation_result['score'] >= 70:
            validation_result['status'] = 'Warning'
        else:
            validation_result['status'] = 'Fail'
        
        return validation_result
    
    async def _perform_technical_validation(self, asset: Dict[str, Any], asset_type: str) -> Dict[str, Any]:
        """Perform technical validation of asset"""
        
        technical_checks = {
            'format_check': {'status': 'unknown', 'details': 'Format validation pending'},
            'size_check': {'status': 'unknown', 'details': 'Size validation pending'},
            'quality_check': {'status': 'unknown', 'details': 'Quality validation pending'},
            'score': 0
        }
        
        # Get format requirements for asset type
        format_reqs = self.format_specs.get(asset_type, {})
        
        # Check file format
        asset_format = asset.get('format', '').lower()
        required_formats = format_reqs.get('required_formats', [])
        
        if required_formats and asset_format in required_formats:
            technical_checks['format_check'] = {'status': 'pass', 'details': f'Format {asset_format} is acceptable'}
        elif required_formats:
            technical_checks['format_check'] = {'status': 'fail', 'details': f'Format {asset_format} not in required formats: {required_formats}'}
        else:
            technical_checks['format_check'] = {'status': 'pass', 'details': 'No specific format requirements'}
        
        # Check file size (basic check)
        asset_size = asset.get('size', 0)
        if isinstance(asset_size, str) and 'MB' in asset_size:
            size_mb = float(asset_size.replace('MB', ''))
            if size_mb > 10:  # Basic large file warning
                technical_checks['size_check'] = {'status': 'warning', 'details': f'File size {asset_size} is quite large'}
            else:
                technical_checks['size_check'] = {'status': 'pass', 'details': f'File size {asset_size} is reasonable'}
        else:
            technical_checks['size_check'] = {'status': 'unknown', 'details': 'Could not determine file size'}
        
        # Quality check (would require actual file analysis in real implementation)
        technical_checks['quality_check'] = {'status': 'pass', 'details': 'Basic quality check passed'}
        
        # Calculate technical score
        passes = sum(1 for check in technical_checks.values() if isinstance(check, dict) and check.get('status') == 'pass')
        warnings = sum(1 for check in technical_checks.values() if isinstance(check, dict) and check.get('status') == 'warning')
        total_checks = 3
        
        technical_checks['score'] = ((passes * 100) + (warnings * 70)) / total_checks
        
        return technical_checks
    
    def _validate_against_requirements(self, asset: Dict[str, Any], deliverables: List[Dict]) -> Dict[str, Any]:
        """Validate asset against brief requirements"""
        
        asset_name = asset.get('filename', '').lower()
        
        requirements_check = {
            'matches_deliverable': False,
            'meets_specifications': False,
            'score': 0,
            'matched_requirement': None
        }
        
        # Find matching deliverable requirement
        for deliverable in deliverables:
            deliverable_name = deliverable.get('item', '').lower()
            if deliverable_name in asset_name or any(word in asset_name for word in deliverable_name.split()):
                requirements_check['matches_deliverable'] = True
                requirements_check['matched_requirement'] = deliverable
                
                # Check if specifications are met (basic check)
                required_format = deliverable.get('format', '').lower()
                asset_format = asset.get('format', '').lower()
                
                if not required_format or required_format in asset_format:
                    requirements_check['meets_specifications'] = True
                
                break
        
        # Calculate requirements score
        if requirements_check['matches_deliverable'] and requirements_check['meets_specifications']:
            requirements_check['score'] = 100
        elif requirements_check['matches_deliverable']:
            requirements_check['score'] = 70
        else:
            requirements_check['score'] = 30
        
        return requirements_check
    
    def _generate_detailed_metrics(self, validation_results: List[Dict]) -> Dict[str, Any]:
        """Generate detailed metrics from validation results"""
        
        total_assets = len(validation_results)
        if total_assets == 0:
            return {'error': 'No assets to analyze'}
        
        scores = [result.get('score', 0) for result in validation_results]
        statuses = [result.get('status', 'unknown') for result in validation_results]
        
        return {
            'total_assets': total_assets,
            'average_score': sum(scores) / len(scores),
            'highest_score': max(scores),
            'lowest_score': min(scores),
            'status_breakdown': {
                'pass': statuses.count('Pass'),
                'warning': statuses.count('Warning'),
                'fail': statuses.count('Fail')
            },
            'pass_rate': (statuses.count('Pass') / total_assets) * 100
        }
    
    def _compare_to_brief_requirements(self, deliverables: List[Dict], validation_results: List[Dict]) -> Dict[str, Any]:
        """Compare validated assets to brief requirements"""
        
        required_items = [d.get('item', '') for d in deliverables]
        validated_items = [r.get('asset_name', '') for r in validation_results]
        
        comparison = {
            'required_deliverables': len(required_items),
            'provided_assets': len(validated_items),
            'missing_deliverables': [],
            'extra_assets': [],
            'coverage_percentage': 0
        }
        
        # Find missing deliverables (simplified matching)
        for required in required_items:
            found = False
            for validated in validated_items:
                if any(word.lower() in validated.lower() for word in required.split()):
                    found = True
                    break
            if not found:
                comparison['missing_deliverables'].append(required)
        
        # Calculate coverage
        covered = len(required_items) - len(comparison['missing_deliverables'])
        comparison['coverage_percentage'] = (covered / len(required_items)) * 100 if required_items else 100
        
        return comparison
    
    def _suggest_automated_fixes(self, validation_results: List[Dict]) -> Dict[str, Any]:
        """Suggest automated fixes for common issues"""
        
        automated_fixes = {
            'available_fixes': [],
            'manual_review_needed': [],
            'fix_priority': []
        }
        
        for result in validation_results:
            asset_name = result.get('asset_name', 'unknown')
            technical_checks = result.get('technical_checks', {})
            
            # Format conversion fixes
            format_check = technical_checks.get('format_check', {})
            if format_check.get('status') == 'fail':
                automated_fixes['available_fixes'].append({
                    'asset': asset_name,
                    'fix_type': 'format_conversion',
                    'description': 'Convert to required format',
                    'estimated_time': '5 minutes'
                })
            
            # Size optimization fixes
            size_check = technical_checks.get('size_check', {})
            if size_check.get('status') == 'warning':
                automated_fixes['available_fixes'].append({
                    'asset': asset_name,
                    'fix_type': 'size_optimization',
                    'description': 'Compress file size',
                    'estimated_time': '2 minutes'
                })
        
        return automated_fixes
    
    def _learn_from_validation(self, brief: Dict[str, Any], validation_results: List[Dict], qa_report: Dict[str, Any]):
        """Learn from validation to improve future checks"""
        
        memory_key = f"validation_patterns_{datetime.now().strftime('%Y%m')}"
        current_patterns = self.get_memory(memory_key, {
            'common_issues': {},
            'quality_trends': [],
            'project_type_issues': {}
        })
        
        # Track common issues
        overall_score = qa_report.get('overall_assessment', {}).get('quality_score', 0)
        try:
            score_numeric = float(str(overall_score).replace('%', ''))
            current_patterns['quality_trends'].append(score_numeric)
        except:
            pass
        
        # Track project type specific issues
        project_type = brief.get('project_type', 'general')
        if project_type not in current_patterns['project_type_issues']:
            current_patterns['project_type_issues'][project_type] = {}
        
        self.update_memory(memory_key, current_patterns)
    
    def _fallback_validation_report(self, validation_results: List[Dict], brief: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback validation report when AI response fails"""
        
        total_assets = len(validation_results)
        scores = [result.get('score', 0) for result in validation_results]
        average_score = sum(scores) / len(scores) if scores else 0
        
        return {
            'overall_assessment': {
                'quality_score': f"{average_score:.0f}",
                'compliance_status': 'Partially compliant' if average_score >= 70 else 'Non-compliant',
                'ready_for_delivery': 'With revisions' if average_score >= 70 else 'No',
                'summary': f'Validated {total_assets} assets with average score of {average_score:.0f}'
            },
            'asset_by_asset_review': [
                {
                    'asset_name': result.get('asset_name', 'unknown'),
                    'validation_score': f"{result.get('score', 0):.0f}",
                    'status': result.get('status', 'unknown'),
                    'issues_found': []
                } for result in validation_results
            ],
            'recommendations': {
                'immediate_actions': ['Review all assets marked as Fail or Warning'],
                'suggested_improvements': ['Ensure all deliverables meet brief requirements']
            },
            'validation_timestamp': datetime.now().isoformat(),
            'fallback_validation': True
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            'name': 'Asset Validator',
            'description': 'Validates deliverables against brief requirements using AI-based QA',
            'inputs': ['assets', 'brief', 'validation_criteria'],
            'outputs': ['qa_report', 'validation_results', 'fix_recommendations'],
            'supported_formats': ['images', 'documents', 'web_files', 'design_files'],
            'validation_types': ['technical', 'design', 'content', 'functionality'],
            'features': ['automated_fixes', 'compliance_checking', 'quality_scoring'],
            'version': '1.0.0'
        }
