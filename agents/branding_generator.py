from core.base_agent import BaseAgent
from typing import Dict, Any, List
import json
from datetime import datetime
import random

class BrandingGenerator(BaseAgent):
    """
    Agent that generates brand kits, tone guides, and messaging templates
    based on creative briefs and client requirements
    """
    
    def __init__(self, ai_client):
        super().__init__(ai_client, "branding_generator")
        
        # Brand personality archetypes
        self.brand_archetypes = {
            'innocent': {'traits': ['optimistic', 'honest', 'pure', 'simple'], 'colors': ['white', 'soft blue', 'pink']},
            'explorer': {'traits': ['adventurous', 'free', 'pioneering', 'ambitious'], 'colors': ['earth tones', 'green', 'brown']},
            'sage': {'traits': ['wise', 'knowledgeable', 'thoughtful', 'mentor'], 'colors': ['navy', 'gray', 'deep blue']},
            'hero': {'traits': ['courageous', 'determined', 'honorable', 'inspiring'], 'colors': ['red', 'blue', 'gold']},
            'outlaw': {'traits': ['rebellious', 'revolutionary', 'wild', 'disruptive'], 'colors': ['black', 'red', 'purple']},
            'magician': {'traits': ['visionary', 'inventive', 'charismatic', 'imaginative'], 'colors': ['purple', 'gold', 'silver']},
            'regular_guy': {'traits': ['friendly', 'down-to-earth', 'genuine', 'practical'], 'colors': ['blue', 'green', 'brown']},
            'lover': {'traits': ['passionate', 'committed', 'intimate', 'warm'], 'colors': ['red', 'pink', 'warm tones']},
            'jester': {'traits': ['playful', 'fun-loving', 'lighthearted', 'clever'], 'colors': ['bright colors', 'yellow', 'orange']},
            'caregiver': {'traits': ['caring', 'compassionate', 'nurturing', 'generous'], 'colors': ['soft colors', 'blue', 'green']},
            'creator': {'traits': ['creative', 'artistic', 'imaginative', 'nonconformist'], 'colors': ['vibrant colors', 'rainbow']},
            'ruler': {'traits': ['responsible', 'authoritative', 'leader', 'role model'], 'colors': ['navy', 'gold', 'burgundy']}
        }
        
        # Typography categories
        self.typography_styles = {
            'modern': ['Helvetica', 'Arial', 'Futura', 'Avenir'],
            'classic': ['Times New Roman', 'Garamond', 'Trajan', 'Optima'],
            'playful': ['Comic Sans', 'Marker Felt', 'Chalkduster', 'Papyrus'],
            'elegant': ['Didot', 'Bodoni', 'Caslon', 'Minion'],
            'bold': ['Impact', 'Anton', 'Bebas Neue', 'Oswald'],
            'friendly': ['Open Sans', 'Lato', 'Source Sans', 'Nunito']
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive brand kit based on brief
        
        Args:
            input_data: Dictionary containing 'brief', 'brand_preferences', 'target_audience'
            
        Returns:
            Dictionary with complete brand kit including guidelines, assets, and messaging
        """
        required_fields = ['brief']
        if not self._validate_input(input_data, required_fields):
            raise ValueError("Missing required fields for branding generation")
        
        return await self._safe_execute(self._generate_brand_kit, input_data)
    
    async def _generate_brand_kit(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to generate brand kit"""
        
        brief = input_data['brief']
        brand_preferences = input_data.get('brand_preferences', {})
        target_audience = input_data.get('target_audience', {})
        
        # Analyze brief to determine brand direction
        brand_analysis = self._analyze_brand_direction(brief, target_audience)
        
        # Generate comprehensive brand kit using AI
        ai_prompt = f"""
        Create a comprehensive brand kit based on the following information:

        Project Brief: {json.dumps(brief, indent=2)}
        Target Audience: {json.dumps(target_audience, indent=2)}
        Brand Analysis: {json.dumps(brand_analysis, indent=2)}
        Client Preferences: {json.dumps(brand_preferences, indent=2)}

        Please provide a JSON response with the following comprehensive brand kit structure:
        {{
            "brand_identity": {{
                "brand_name": "Official brand name",
                "tagline": "Memorable tagline",
                "brand_archetype": "One of the 12 brand archetypes",
                "brand_personality": ["list", "of", "personality", "traits"],
                "mission_statement": "Clear mission statement",
                "vision_statement": "Inspiring vision statement",
                "core_values": ["value 1", "value 2", "value 3"]
            }},
            "visual_identity": {{
                "logo_concepts": [
                    {{
                        "concept": "Logo concept name",
                        "description": "Detailed description",
                        "style": "modern/classic/playful/etc",
                        "elements": ["design elements included"]
                    }}
                ],
                "color_palette": {{
                    "primary": {{
                        "color": "Color name",
                        "hex": "#HEX code",
                        "usage": "When to use this color"
                    }},
                    "secondary": [
                        {{
                            "color": "Color name",
                            "hex": "#HEX code", 
                            "usage": "When to use this color"
                        }}
                    ],
                    "accent": [
                        {{
                            "color": "Color name",
                            "hex": "#HEX code",
                            "usage": "When to use this color"
                        }}
                    ]
                }},
                "typography": {{
                    "primary_font": {{
                        "name": "Font name",
                        "category": "serif/sans-serif/display",
                        "usage": "Headlines, logos",
                        "alternatives": ["web-safe alternatives"]
                    }},
                    "secondary_font": {{
                        "name": "Font name", 
                        "category": "serif/sans-serif/display",
                        "usage": "Body text, subtitles",
                        "alternatives": ["web-safe alternatives"]
                    }}
                }},
                "imagery_style": {{
                    "photography_style": "Style description",
                    "illustration_style": "Style description if applicable",
                    "image_treatment": "Color, filters, effects",
                    "composition_guidelines": "Rules for image composition"
                }}
            }},
            "brand_voice": {{
                "tone_of_voice": "Overall tone description",
                "communication_style": "Formal/casual/friendly/etc",
                "vocabulary": {{
                    "use": ["words", "to", "use"],
                    "avoid": ["words", "to", "avoid"]
                }},
                "messaging_pillars": [
                    {{
                        "pillar": "Main message theme",
                        "description": "Detailed explanation",
                        "example_messages": ["Example 1", "Example 2"]
                    }}
                ],
                "brand_story": "Compelling brand narrative"
            }},
            "applications": {{
                "business_materials": [
                    {{
                        "item": "Business card",
                        "specifications": "Size, format requirements",
                        "design_notes": "Key design considerations"
                    }},
                    {{
                        "item": "Letterhead",
                        "specifications": "Size, format requirements", 
                        "design_notes": "Key design considerations"
                    }}
                ],
                "digital_applications": [
                    {{
                        "platform": "Website",
                        "specifications": "Logo sizes, color usage",
                        "design_notes": "Key considerations"
                    }},
                    {{
                        "platform": "Social Media",
                        "specifications": "Profile image sizes, cover images",
                        "design_notes": "Platform-specific guidelines"
                    }}
                ],
                "marketing_materials": [
                    {{
                        "item": "Brochure",
                        "specifications": "Size, layout guidelines",
                        "design_notes": "Brand application notes"
                    }}
                ]
            }},
            "usage_guidelines": {{
                "logo_usage": {{
                    "minimum_size": "Smallest allowable size",
                    "clear_space": "Required spacing around logo",
                    "acceptable_variations": ["List of approved variations"],
                    "prohibited_uses": ["What not to do with logo"]
                }},
                "color_usage": {{
                    "primary_applications": "When to use primary colors",
                    "accessibility": "Color contrast requirements",
                    "print_considerations": "CMYK values and print notes"
                }},
                "typography_usage": {{
                    "hierarchy": "How to use different font weights/sizes",
                    "spacing": "Letter spacing, line height guidelines",
                    "web_implementation": "CSS specifications"
                }}
            }}
        }}
        """
        
        ai_response = await self._generate_ai_response(ai_prompt)
        
        try:
            brand_kit = json.loads(ai_response)
            
            # Enhance with additional components
            brand_kit['templates'] = self._generate_brand_templates(brand_kit)
            brand_kit['social_media_kit'] = self._generate_social_media_kit(brand_kit)
            brand_kit['brand_audit_checklist'] = self._generate_brand_checklist()
            
            # Add metadata
            brand_kit['generated_at'] = datetime.now().isoformat()
            brand_kit['generator_version'] = '1.0.0'
            brand_kit['based_on_brief'] = brief.get('project_title', 'Unknown Project')
            
            # Learn from generation
            self._learn_from_branding(brief, brand_kit)
            
            return brand_kit
            
        except json.JSONDecodeError:
            self.logger.warning("AI response wasn't valid JSON, using fallback generation")
            return self._fallback_brand_generation(brief, brand_analysis)
    
    def _analyze_brand_direction(self, brief: Dict[str, Any], target_audience: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze brief to determine brand direction"""
        
        # Extract industry and project type
        project_type = brief.get('project_type', '').lower()
        goals = brief.get('goals', {})
        constraints = brief.get('constraints', {})
        
        # Determine appropriate brand archetype
        suggested_archetype = self._suggest_brand_archetype(project_type, goals, target_audience)
        
        # Analyze tone requirements
        tone_analysis = self._analyze_tone_requirements(brief, target_audience)
        
        return {
            'suggested_archetype': suggested_archetype,
            'tone_direction': tone_analysis,
            'industry_context': project_type,
            'audience_insights': self._extract_audience_insights(target_audience),
            'brand_positioning': self._suggest_brand_positioning(brief)
        }
    
    def _suggest_brand_archetype(self, project_type: str, goals: Dict[str, Any], audience: Dict[str, Any]) -> str:
        """Suggest appropriate brand archetype based on context"""
        
        # Simple mapping based on project type and goals
        if 'healthcare' in project_type or 'medical' in project_type:
            return 'caregiver'
        elif 'technology' in project_type or 'innovation' in project_type:
            return 'magician'
        elif 'education' in project_type or 'consulting' in project_type:
            return 'sage'
        elif 'luxury' in str(goals) or 'premium' in str(goals):
            return 'ruler'
        elif 'fun' in str(goals) or 'entertainment' in project_type:
            return 'jester'
        elif 'adventure' in str(goals) or 'travel' in project_type:
            return 'explorer'
        else:
            return 'regular_guy'  # Safe default
    
    def _analyze_tone_requirements(self, brief: Dict[str, Any], audience: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze tone requirements from brief and audience"""
        
        # Extract tone indicators from brief
        goals_text = str(brief.get('goals', {})).lower()
        constraints_text = str(brief.get('constraints', {})).lower()
        
        tone_indicators = {
            'formal': 'formal' in goals_text or 'professional' in goals_text,
            'friendly': 'friendly' in goals_text or 'approachable' in goals_text,
            'playful': 'fun' in goals_text or 'playful' in goals_text,
            'authoritative': 'expert' in goals_text or 'authority' in goals_text,
            'caring': 'caring' in goals_text or 'supportive' in goals_text
        }
        
        # Determine primary tone
        primary_tone = max(tone_indicators.keys(), key=lambda k: tone_indicators[k])
        
        return {
            'primary_tone': primary_tone,
            'tone_indicators': tone_indicators,
            'communication_style': 'formal' if tone_indicators['formal'] else 'casual'
        }
    
    def _extract_audience_insights(self, audience: Dict[str, Any]) -> Dict[str, Any]:
        """Extract insights about target audience"""
        
        if not audience:
            return {'needs_research': True}
        
        return {
            'demographics': audience.get('demographics', 'Not specified'),
            'primary_audience': audience.get('primary', 'General audience'),
            'key_characteristics': audience.get('personas', []),
            'needs_research': False
        }
    
    def _suggest_brand_positioning(self, brief: Dict[str, Any]) -> str:
        """Suggest brand positioning based on brief"""
        
        goals = brief.get('goals', {})
        primary_goal = goals.get('primary', '')
        
        if 'leader' in primary_goal.lower() or 'best' in primary_goal.lower():
            return 'market_leader'
        elif 'affordable' in primary_goal.lower() or 'budget' in primary_goal.lower():
            return 'value_provider'
        elif 'premium' in primary_goal.lower() or 'luxury' in primary_goal.lower():
            return 'premium_option'
        elif 'innovative' in primary_goal.lower() or 'new' in primary_goal.lower():
            return 'innovator'
        else:
            return 'differentiated_alternative'
    
    def _generate_brand_templates(self, brand_kit: Dict[str, Any]) -> Dict[str, Any]:
        """Generate brand application templates"""
        
        return {
            'email_signature': {
                'template': self._create_email_signature_template(brand_kit),
                'specifications': 'Use brand colors and typography'
            },
            'presentation_template': {
                'slides': ['title_slide', 'content_slide', 'closing_slide'],
                'color_scheme': brand_kit.get('visual_identity', {}).get('color_palette', {}),
                'font_usage': brand_kit.get('visual_identity', {}).get('typography', {})
            },
            'social_media_templates': {
                'instagram_post': {'size': '1080x1080', 'format': 'square'},
                'facebook_cover': {'size': '820x312', 'format': 'landscape'},
                'linkedin_banner': {'size': '1584x396', 'format': 'banner'}
            }
        }
    
    def _generate_social_media_kit(self, brand_kit: Dict[str, Any]) -> Dict[str, Any]:
        """Generate social media specific brand guidelines"""
        
        return {
            'profile_setup': {
                'bio_template': self._create_bio_template(brand_kit),
                'hashtag_strategy': self._suggest_hashtags(brand_kit),
                'posting_tone': brand_kit.get('brand_voice', {}).get('tone_of_voice', 'friendly')
            },
            'content_pillars': [
                {
                    'pillar': 'Educational',
                    'percentage': 40,
                    'content_types': ['tips', 'how-tos', 'industry insights']
                },
                {
                    'pillar': 'Behind the Scenes',
                    'percentage': 30,
                    'content_types': ['team photos', 'process videos', 'company culture']
                },
                {
                    'pillar': 'Promotional',
                    'percentage': 20,
                    'content_types': ['product features', 'testimonials', 'case studies']
                },
                {
                    'pillar': 'Community',
                    'percentage': 10,
                    'content_types': ['user-generated content', 'community highlights']
                }
            ],
            'visual_guidelines': {
                'filter_style': 'Consistent with brand colors',
                'image_composition': 'Clean, professional, on-brand',
                'logo_placement': 'Bottom right corner, 10% opacity'
            }
        }
    
    def _generate_brand_checklist(self) -> List[Dict[str, Any]]:
        """Generate brand audit checklist"""
        
        return [
            {
                'category': 'Visual Consistency',
                'items': [
                    'Logo used correctly across all materials',
                    'Color palette applied consistently',
                    'Typography follows brand guidelines',
                    'Imagery style is consistent'
                ]
            },
            {
                'category': 'Voice & Messaging',
                'items': [
                    'Tone of voice is consistent',
                    'Key messages are clear',
                    'Brand story is compelling',
                    'Communication style matches target audience'
                ]
            },
            {
                'category': 'Applications',
                'items': [
                    'Business cards follow brand guidelines',
                    'Website reflects brand identity',
                    'Social media profiles are branded',
                    'Marketing materials are consistent'
                ]
            }
        ]
    
    def _create_email_signature_template(self, brand_kit: Dict[str, Any]) -> str:
        """Create email signature template"""
        
        brand_name = brand_kit.get('brand_identity', {}).get('brand_name', '[Brand Name]')
        primary_color = brand_kit.get('visual_identity', {}).get('color_palette', {}).get('primary', {}).get('hex', '#000000')
        
        return f"""
        [Full Name]
        [Title]
        {brand_name}
        
        [Phone] | [Email]
        [Website]
        
        [Logo - use brand colors: {primary_color}]
        """
    
    def _create_bio_template(self, brand_kit: Dict[str, Any]) -> str:
        """Create social media bio template"""
        
        brand_name = brand_kit.get('brand_identity', {}).get('brand_name', '[Brand Name]')
        tagline = brand_kit.get('brand_identity', {}).get('tagline', '[Tagline]')
        
        return f"{brand_name} | {tagline} | [Key Service/Product] | [Location] | [Website/Contact]"
    
    def _suggest_hashtags(self, brand_kit: Dict[str, Any]) -> List[str]:
        """Suggest relevant hashtags based on brand"""
        
        brand_name = brand_kit.get('brand_identity', {}).get('brand_name', 'brand').replace(' ', '').lower()
        archetype = brand_kit.get('brand_identity', {}).get('brand_archetype', 'regular_guy')
        
        base_hashtags = [f"#{brand_name}", "#branding", "#design"]
        
        # Add archetype-specific hashtags
        archetype_hashtags = {
            'creator': ['#creative', '#art', '#design'],
            'sage': ['#knowledge', '#wisdom', '#education'],
            'explorer': ['#adventure', '#discovery', '#innovation'],
            'hero': ['#leadership', '#courage', '#inspiration']
        }
        
        if archetype in archetype_hashtags:
            base_hashtags.extend(archetype_hashtags[archetype])
        
        return base_hashtags[:10]  # Limit to 10 hashtags
    
    def _learn_from_branding(self, brief: Dict[str, Any], brand_kit: Dict[str, Any]):
        """Learn from brand generation to improve future results"""
        
        memory_key = f"branding_patterns_{datetime.now().strftime('%Y%m')}"
        current_patterns = self.get_memory(memory_key, {
            'popular_archetypes': {},
            'color_trends': {},
            'successful_combinations': []
        })
        
        # Track archetype usage
        archetype = brand_kit.get('brand_identity', {}).get('brand_archetype', 'unknown')
        current_patterns['popular_archetypes'][archetype] = (
            current_patterns['popular_archetypes'].get(archetype, 0) + 1
        )
        
        # Track color combinations
        primary_color = brand_kit.get('visual_identity', {}).get('color_palette', {}).get('primary', {}).get('color', 'unknown')
        current_patterns['color_trends'][primary_color] = (
            current_patterns['color_trends'].get(primary_color, 0) + 1
        )
        
        self.update_memory(memory_key, current_patterns)
    
    def _fallback_brand_generation(self, brief: Dict[str, Any], brand_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback brand generation when AI response fails"""
        
        project_name = brief.get('project_title', 'New Brand')
        archetype = brand_analysis.get('suggested_archetype', 'regular_guy')
        archetype_data = self.brand_archetypes.get(archetype, self.brand_archetypes['regular_guy'])
        
        return {
            'brand_identity': {
                'brand_name': project_name,
                'tagline': 'To be developed',
                'brand_archetype': archetype,
                'brand_personality': archetype_data['traits'],
                'mission_statement': 'To be defined with client',
                'vision_statement': 'To be defined with client',
                'core_values': ['Quality', 'Innovation', 'Integrity']
            },
            'visual_identity': {
                'color_palette': {
                    'primary': {'color': 'Blue', 'hex': '#007bff', 'usage': 'Primary brand color'},
                    'secondary': [{'color': 'Gray', 'hex': '#6c757d', 'usage': 'Supporting color'}],
                    'accent': [{'color': 'White', 'hex': '#ffffff', 'usage': 'Background and contrast'}]
                },
                'typography': {
                    'primary_font': {'name': 'Arial', 'category': 'sans-serif', 'usage': 'Headlines'},
                    'secondary_font': {'name': 'Helvetica', 'category': 'sans-serif', 'usage': 'Body text'}
                }
            },
            'brand_voice': {
                'tone_of_voice': brand_analysis.get('tone_direction', {}).get('primary_tone', 'friendly'),
                'communication_style': 'professional yet approachable'
            },
            'generated_at': datetime.now().isoformat(),
            'fallback_generation': True
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            'name': 'Branding Generator',
            'description': 'Generates comprehensive brand kits including identity, voice, and guidelines',
            'inputs': ['brief', 'brand_preferences', 'target_audience'],
            'outputs': ['brand_kit', 'visual_guidelines', 'messaging_templates'],
            'features': ['brand_archetypes', 'color_psychology', 'typography_pairing'],
            'supported_archetypes': list(self.brand_archetypes.keys()),
            'template_types': ['business_cards', 'letterhead', 'social_media', 'presentations'],
            'version': '1.0.0'
        }
