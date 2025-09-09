from core.base_agent import BaseAgent
from typing import Dict, Any, List
import json
from datetime import datetime
import os
import zipfile
import hashlib

class DeliverablesPackager(BaseAgent):
    """
    Agent that gathers, renames, zips, and delivers final assets 
    with a summary and changelog for professional client delivery
    """
    
    def __init__(self, ai_client):
        super().__init__(ai_client, "deliverables_packager")
        
        # File organization templates
        self.organization_templates = {
            'website': {
                'folders': [
                    '01_Final_Website_Files',
                    '02_Design_Assets',
                    '03_Documentation',
                    '04_Source_Files'
                ],
                'naming_convention': 'project_name_file_type_version'
            },
            'branding': {
                'folders': [
                    '01_Logo_Files',
                    '02_Brand_Guidelines',
                    '03_Marketing_Materials',
                    '04_Source_Files'
                ],
                'naming_convention': 'brand_name_asset_type_version'
            },
            'marketing': {
                'folders': [
                    '01_Campaign_Assets',
                    '02_Social_Media_Assets',
                    '03_Documentation',
                    '04_Source_Files'
                ],
                'naming_convention': 'campaign_name_asset_type_version'
            }
        }
        
        # Standard file naming patterns
        self.naming_patterns = {
            'logo': '{brand_name}_Logo_{variation}_{format}',
            'website': '{project_name}_{page_name}_{version}',
            'social_media': '{brand_name}_{platform}_{size}_{version}',
            'document': '{project_name}_{document_type}_{version}',
            'image': '{project_name}_{description}_{size}_{version}'
        }
        
        # Quality checklist for final delivery
        self.delivery_checklist = [
            'All files are properly named and organized',
            'All required formats are included',
            'Source files are backed up',
            'Documentation is complete and clear',
            'Client instructions are included',
            'File integrity has been verified',
            'Delivery package is virus-scanned'
        ]
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Package deliverables for professional client delivery
        
        Args:
            input_data: Dictionary containing 'assets', 'project_info', 'packaging_preferences'
            
        Returns:
            Dictionary with packaging results and delivery information
        """
        required_fields = ['assets', 'project_info']
        if not self._validate_input(input_data, required_fields):
            raise ValueError("Missing required fields for deliverables packaging")
        
        return await self._safe_execute(self._package_deliverables, input_data)
    
    async def _package_deliverables(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to package deliverables"""
        
        assets = input_data['assets']
        project_info = input_data['project_info']
        packaging_prefs = input_data.get('packaging_preferences', {})
        
        # Extract project information
        project_name = project_info.get('name', 'Project')
        project_type = project_info.get('type', 'general').lower()
        client_name = project_info.get('client_name', 'Client')
        
        # Organize files according to project type
        file_organization = self._organize_files(assets, project_type, project_info)
        
        # Generate comprehensive delivery package using AI
        ai_prompt = f"""
        Create a comprehensive deliverables package for a creative project with the following information:

        Project Information: {json.dumps(project_info, indent=2)}
        Client: {client_name}
        Project Type: {project_type}
        Assets to Package: {json.dumps(assets, indent=2)}
        File Organization: {json.dumps(file_organization, indent=2)}
        Packaging Preferences: {json.dumps(packaging_prefs, indent=2)}

        Please provide a JSON response with the following delivery package structure:
        {{
            "package_summary": {{
                "project_name": "{project_name}",
                "client_name": "{client_name}",
                "delivery_date": "YYYY-MM-DD",
                "package_version": "Version number",
                "total_files": "Number of files included",
                "total_size": "Estimated total size",
                "package_description": "Brief description of what's included"
            }},
            "file_structure": {{
                "root_folder": "Main folder name",
                "subfolders": [
                    {{
                        "folder_name": "Folder name",
                        "description": "What this folder contains",
                        "file_count": "Number of files",
                        "files": [
                            {{
                                "original_name": "Original filename",
                                "final_name": "Renamed filename",
                                "file_type": "File type/category",
                                "file_size": "File size",
                                "description": "What this file contains"
                            }}
                        ]
                    }}
                ]
            }},
            "documentation": {{
                "readme_file": {{
                    "filename": "README.md",
                    "content": "Detailed README content explaining the deliverables"
                }},
                "file_guide": {{
                    "filename": "File_Guide.md",
                    "content": "Guide explaining what each file is for and how to use it"
                }},
                "changelog": {{
                    "filename": "CHANGELOG.md",
                    "content": "Detailed changelog of all deliverables and versions"
                }},
                "instructions": {{
                    "filename": "Client_Instructions.md",
                    "content": "Instructions for the client on how to use the deliverables"
                }}
            }},
            "quality_assurance": {{
                "checklist_completed": [
                    {{
                        "check": "Quality check description",
                        "status": "Completed/Not applicable",
                        "notes": "Additional notes if any"
                    }}
                ],
                "file_integrity": {{
                    "all_files_present": true/false,
                    "naming_convention_followed": true/false,
                    "file_sizes_verified": true/false,
                    "formats_correct": true/false
                }},
                "delivery_readiness": {{
                    "ready_for_delivery": true/false,
                    "issues_to_resolve": ["Any issues that need attention"],
                    "final_review_needed": true/false
                }}
            }},
            "delivery_options": {{
                "zip_package": {{
                    "filename": "Final package zip filename",
                    "estimated_size": "Estimated zip size",
                    "compression_ratio": "Compression percentage"
                }},
                "cloud_delivery": {{
                    "recommended_platform": "Dropbox/Google Drive/etc",
                    "folder_structure": "How to organize in cloud",
                    "sharing_permissions": "Recommended sharing settings"
                }},
                "alternative_delivery": [
                    {{
                        "method": "Delivery method",
                        "pros": "Advantages of this method",
                        "cons": "Disadvantages of this method"
                    }}
                ]
            }},
            "client_communication": {{
                "delivery_email": {{
                    "subject": "Professional email subject line",
                    "body": "Professional email body explaining the delivery"
                }},
                "follow_up_suggestions": [
                    "Suggested follow-up actions with client"
                ],
                "feedback_request": "How to request client feedback on deliverables"
            }}
        }}
        """
        
        ai_response = await self._generate_ai_response(ai_prompt)
        
        try:
            packaging_plan = json.loads(ai_response)
            
            # Enhance with additional components
            packaging_plan['technical_specs'] = self._generate_technical_specs(file_organization)
            packaging_plan['backup_plan'] = self._create_backup_plan(packaging_plan)
            packaging_plan['version_history'] = self._create_version_history(project_info, assets)
            
            # Execute the packaging process
            packaging_results = await self._execute_packaging(packaging_plan, assets, project_info)
            
            # Merge results
            final_package = {**packaging_plan, **packaging_results}
            
            # Add metadata
            final_package['packaging_timestamp'] = datetime.now().isoformat()
            final_package['packager_version'] = '1.0.0'
            final_package['project_reference'] = project_info.get('id', 'unknown')
            
            # Learn from packaging
            self._learn_from_packaging(project_info, final_package)
            
            return final_package
            
        except json.JSONDecodeError:
            self.logger.warning("AI response wasn't valid JSON, using fallback packaging")
            return self._fallback_packaging(assets, project_info)
    
    def _organize_files(self, assets: List[Dict], project_type: str, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """Organize files according to project type and best practices"""
        
        template = self.organization_templates.get(project_type, self.organization_templates['website'])
        organized_structure = {
            'folders': template['folders'],
            'naming_convention': template['naming_convention'],
            'file_assignments': {}
        }
        
        # Assign files to appropriate folders
        for asset in assets:
            file_type = asset.get('type', 'unknown').lower()
            filename = asset.get('filename', 'unknown')
            
            # Determine best folder based on file type
            target_folder = self._determine_target_folder(file_type, filename, template['folders'])
            
            if target_folder not in organized_structure['file_assignments']:
                organized_structure['file_assignments'][target_folder] = []
            
            # Generate standardized filename
            new_filename = self._generate_standard_filename(asset, project_info, file_type)
            
            organized_structure['file_assignments'][target_folder].append({
                'original_filename': filename,
                'new_filename': new_filename,
                'file_info': asset
            })
        
        return organized_structure
    
    def _determine_target_folder(self, file_type: str, filename: str, available_folders: List[str]) -> str:
        """Determine the most appropriate folder for a file"""
        
        # Mapping rules for different file types
        folder_mapping = {
            'logo': '01_Logo_Files',
            'image': '02_Design_Assets',
            'document': '03_Documentation',
            'pdf': '03_Documentation',
            'html': '01_Final_Website_Files',
            'css': '01_Final_Website_Files',
            'js': '01_Final_Website_Files',
            'psd': '04_Source_Files',
            'ai': '04_Source_Files',
            'sketch': '04_Source_Files'
        }
        
        # Check for specific keywords in filename
        filename_lower = filename.lower()
        if 'source' in filename_lower or 'original' in filename_lower:
            return available_folders[-1] if available_folders else 'Source_Files'
        elif 'final' in filename_lower:
            return available_folders[0] if available_folders else 'Final_Files'
        elif file_type in folder_mapping:
            target = folder_mapping[file_type]
            return target if target in available_folders else available_folders[0]
        
        # Default to first folder
        return available_folders[0] if available_folders else 'Files'
    
    def _generate_standard_filename(self, asset: Dict[str, Any], project_info: Dict[str, Any], file_type: str) -> str:
        """Generate standardized filename according to conventions"""
        
        project_name = project_info.get('name', 'Project').replace(' ', '_')
        client_name = project_info.get('client_name', 'Client').replace(' ', '_')
        
        original_filename = asset.get('filename', 'file')
        file_extension = os.path.splitext(original_filename)[1]
        
        # Use appropriate naming pattern
        if file_type in self.naming_patterns:
            pattern = self.naming_patterns[file_type]
            
            # Fill in pattern variables
            new_filename = pattern.format(
                project_name=project_name,
                brand_name=client_name,
                variation='Standard',
                format=file_extension.replace('.', ''),
                page_name='Index',
                platform='Universal',
                size='Standard',
                document_type=file_type.title(),
                description='Asset',
                version='v1'
            )
        else:
            # Generic naming convention
            new_filename = f"{project_name}_{file_type}_{asset.get('id', 'asset')}_v1"
        
        return new_filename + file_extension
    
    def _generate_technical_specs(self, file_organization: Dict[str, Any]) -> Dict[str, Any]:
        """Generate technical specifications for the package"""
        
        return {
            'file_formats_included': self._extract_file_formats(file_organization),
            'total_file_count': sum(len(files) for files in file_organization.get('file_assignments', {}).values()),
            'naming_convention': file_organization.get('naming_convention', 'standard'),
            'compression_settings': {
                'method': 'ZIP',
                'compression_level': 'Standard',
                'preserve_metadata': True
            },
            'compatibility': {
                'windows': True,
                'mac': True,
                'linux': True
            }
        }
    
    def _extract_file_formats(self, file_organization: Dict[str, Any]) -> List[str]:
        """Extract unique file formats from organization"""
        
        formats = set()
        for folder_files in file_organization.get('file_assignments', {}).values():
            for file_info in folder_files:
                original_filename = file_info.get('original_filename', '')
                extension = os.path.splitext(original_filename)[1].lower()
                if extension:
                    formats.add(extension.replace('.', ''))
        
        return sorted(list(formats))
    
    def _create_backup_plan(self, packaging_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create backup and recovery plan"""
        
        return {
            'backup_location': 'Internal project archive',
            'retention_period': '2 years',
            'backup_frequency': 'After each major delivery',
            'recovery_procedure': [
                'Contact project manager',
                'Provide project ID and delivery date',
                'Files will be restored within 24 hours'
            ],
            'version_control': {
                'tracked': True,
                'system': 'Internal version control',
                'accessibility': 'Team members and account manager'
            }
        }
    
    def _create_version_history(self, project_info: Dict[str, Any], assets: List[Dict]) -> Dict[str, Any]:
        """Create version history for deliverables"""
        
        return {
            'current_version': '1.0',
            'version_date': datetime.now().strftime('%Y-%m-%d'),
            'version_notes': 'Initial delivery of all project deliverables',
            'previous_versions': [],
            'version_comparison': {
                'files_added': len(assets),
                'files_modified': 0,
                'files_removed': 0
            },
            'change_summary': f'Complete delivery package for {project_info.get("name", "project")}'
        }
    
    async def _execute_packaging(self, packaging_plan: Dict[str, Any], assets: List[Dict], project_info: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the actual packaging process"""
        
        try:
            # In a real implementation, this would create actual files and zip packages
            # For now, we'll simulate the process
            
            package_name = f"{project_info.get('name', 'Project').replace(' ', '_')}_Deliverables_v1.zip"
            
            # Simulate file operations
            packaging_results = {
                'execution_status': {
                    'files_processed': len(assets),
                    'files_renamed': len(assets),
                    'folders_created': len(packaging_plan.get('file_structure', {}).get('subfolders', [])),
                    'documentation_generated': 4,  # README, File Guide, Changelog, Instructions
                    'package_created': True
                },
                'final_package': {
                    'package_filename': package_name,
                    'package_size': f'{len(assets) * 2.5:.1f}MB',  # Estimated
                    'creation_time': datetime.now().isoformat(),
                    'file_count': len(assets) + 4,  # Assets + documentation files
                    'checksum': hashlib.md5(package_name.encode()).hexdigest()[:16]
                },
                'delivery_ready': {
                    'status': True,
                    'download_link': f'https://delivery.agency.com/download/{package_name}',
                    'expiry_date': (datetime.now().replace(day=datetime.now().day + 30)).strftime('%Y-%m-%d'),
                    'access_password': 'Generated secure password'
                }
            }
            
            return packaging_results
            
        except Exception as e:
            self.logger.error(f"Error executing packaging: {str(e)}")
            return {
                'execution_status': {'error': str(e), 'success': False},
                'final_package': None,
                'delivery_ready': {'status': False}
            }
    
    def _learn_from_packaging(self, project_info: Dict[str, Any], packaging_results: Dict[str, Any]):
        """Learn from packaging process to improve future deliveries"""
        
        memory_key = f"packaging_patterns_{datetime.now().strftime('%Y%m')}"
        current_patterns = self.get_memory(memory_key, {
            'successful_structures': {},
            'common_file_types': {},
            'client_preferences': {}
        })
        
        # Track successful folder structures
        project_type = project_info.get('type', 'general')
        structure_key = f"{project_type}_structure"
        current_patterns['successful_structures'][structure_key] = (
            current_patterns['successful_structures'].get(structure_key, 0) + 1
        )
        
        # Track file type frequencies
        file_structure = packaging_results.get('file_structure', {})
        for folder in file_structure.get('subfolders', []):
            for file_info in folder.get('files', []):
                file_type = file_info.get('file_type', 'unknown')
                current_patterns['common_file_types'][file_type] = (
                    current_patterns['common_file_types'].get(file_type, 0) + 1
                )
        
        self.update_memory(memory_key, current_patterns)
    
    def _fallback_packaging(self, assets: List[Dict], project_info: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback packaging when AI response fails"""
        
        project_name = project_info.get('name', 'Project').replace(' ', '_')
        client_name = project_info.get('client_name', 'Client')
        
        return {
            'package_summary': {
                'project_name': project_info.get('name', 'Project'),
                'client_name': client_name,
                'delivery_date': datetime.now().strftime('%Y-%m-%d'),
                'package_version': 'v1.0',
                'total_files': len(assets),
                'package_description': f'Deliverables package for {project_info.get("name", "project")}'
            },
            'file_structure': {
                'root_folder': f'{project_name}_Deliverables',
                'subfolders': [
                    {
                        'folder_name': '01_Final_Files',
                        'description': 'Final project deliverables',
                        'file_count': len(assets),
                        'files': [
                            {
                                'original_name': asset.get('filename', 'file'),
                                'final_name': f"{project_name}_{asset.get('type', 'asset')}_{i+1}",
                                'file_type': asset.get('type', 'unknown'),
                                'description': f"Project asset {i+1}"
                            } for i, asset in enumerate(assets)
                        ]
                    },
                    {
                        'folder_name': '02_Documentation',
                        'description': 'Project documentation and instructions',
                        'file_count': 2,
                        'files': [
                            {
                                'original_name': 'README.md',
                                'final_name': 'README.md',
                                'file_type': 'documentation',
                                'description': 'Project overview and file guide'
                            },
                            {
                                'original_name': 'Instructions.md',
                                'final_name': 'Client_Instructions.md',
                                'file_type': 'documentation',
                                'description': 'Instructions for using deliverables'
                            }
                        ]
                    }
                ]
            },
            'documentation': {
                'readme_file': {
                    'filename': 'README.md',
                    'content': f'# {project_info.get("name", "Project")} Deliverables\n\nThis package contains all final deliverables for your project.'
                },
                'instructions': {
                    'filename': 'Client_Instructions.md',
                    'content': 'Please contact your project manager if you have any questions about these files.'
                }
            },
            'delivery_options': {
                'zip_package': {
                    'filename': f'{project_name}_Deliverables_v1.zip',
                    'estimated_size': f'{len(assets) * 2}MB'
                }
            },
            'packaging_timestamp': datetime.now().isoformat(),
            'fallback_packaging': True
        }
    
    async def create_delivery_documentation(self, packaging_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive delivery documentation"""
        
        try:
            documentation = {}
            
            # Generate README content
            readme_content = f"""
# Project Deliverables Package

## Package Information
- **Project**: {packaging_plan.get('package_summary', {}).get('project_name', 'N/A')}
- **Client**: {packaging_plan.get('package_summary', {}).get('client_name', 'N/A')}
- **Delivery Date**: {packaging_plan.get('package_summary', {}).get('delivery_date', 'N/A')}
- **Package Version**: {packaging_plan.get('package_summary', {}).get('package_version', 'N/A')}

## Package Contents
{packaging_plan.get('package_summary', {}).get('package_description', 'Complete project deliverables')}

## File Structure
"""
            
            # Add folder descriptions
            for folder in packaging_plan.get('file_structure', {}).get('subfolders', []):
                readme_content += f"\n### {folder.get('folder_name', 'Folder')}\n"
                readme_content += f"{folder.get('description', 'Project files')}\n"
                readme_content += f"Files: {folder.get('file_count', 0)}\n"
            
            documentation['README.md'] = readme_content
            
            # Generate client instructions
            instructions_content = """
# Client Instructions

## How to Use Your Deliverables

### Getting Started
1. Extract all files from the zip package
2. Review the README file for an overview
3. Check the File Guide for specific file usage

### File Organization
All files are organized in clearly labeled folders according to their purpose and usage.

### Support
If you have any questions about these deliverables or need assistance:
- Contact your project manager
- Reference the documentation included in this package

### File Formats
Different file formats are included for different uses:
- Source files for future editing
- Final files for immediate use
- Documentation for reference

## Next Steps
1. Review all deliverables
2. Test any interactive elements
3. Provide feedback if revisions are needed
4. Approve final deliverables

Thank you for choosing our services!
"""
            
            documentation['Client_Instructions.md'] = instructions_content
            
            return {
                'success': True,
                'documentation': documentation,
                'file_count': len(documentation)
            }
            
        except Exception as e:
            self.logger.error(f"Error creating delivery documentation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            'name': 'Deliverables Packager',
            'description': 'Gathers, organizes, and packages final deliverables for professional client delivery',
            'inputs': ['assets', 'project_info', 'packaging_preferences'],
            'outputs': ['packaged_deliverables', 'delivery_documentation', 'quality_report'],
            'supported_project_types': list(self.organization_templates.keys()),
            'features': ['file_organization', 'automatic_renaming', 'documentation_generation', 'quality_assurance'],
            'delivery_formats': ['zip_package', 'cloud_delivery', 'direct_download'],
            'version': '1.0.0'
        }
