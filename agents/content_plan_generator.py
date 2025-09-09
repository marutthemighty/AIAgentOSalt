from core.base_agent import BaseAgent
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
import calendar

class ContentPlanGenerator(BaseAgent):
    """
    Agent that creates comprehensive content plans including blogs, 
    landing pages, and social media calendars based on project briefs
    """
    
    def __init__(self, ai_client):
        super().__init__(ai_client, "content_plan_generator")
        
        # Content types and their characteristics
        self.content_types = {
            'blog_post': {
                'frequency': 'weekly',
                'length': '800-1200 words',
                'channels': ['website', 'linkedin'],
                'seo_importance': 'high'
            },
            'social_media': {
                'frequency': 'daily',
                'length': '50-280 characters',
                'channels': ['twitter', 'facebook', 'instagram', 'linkedin'],
                'seo_importance': 'medium'
            },
            'landing_page': {
                'frequency': 'project-based',
                'length': '500-800 words',
                'channels': ['website'],
                'seo_importance': 'very_high'
            },
            'email_campaign': {
                'frequency': 'bi-weekly',
                'length': '200-500 words',
                'channels': ['email'],
                'seo_importance': 'low'
            },
            'video_script': {
                'frequency': 'monthly',
                'length': '150-300 words',
                'channels': ['youtube', 'social_media'],
                'seo_importance': 'high'
            }
        }
        
        # Channel-specific requirements
        self.channel_specs = {
            'instagram': {
                'post_types': ['photo', 'carousel', 'reel', 'story'],
                'optimal_times': ['11:00', '14:00', '17:00'],
                'hashtag_limit': 30,
                'character_limit': 2200
            },
            'twitter': {
                'post_types': ['text', 'image', 'thread'],
                'optimal_times': ['09:00', '12:00', '15:00'],
                'hashtag_limit': 2,
                'character_limit': 280
            },
            'linkedin': {
                'post_types': ['text', 'document', 'video'],
                'optimal_times': ['08:00', '12:00', '17:00'],
                'hashtag_limit': 5,
                'character_limit': 3000
            },
            'facebook': {
                'post_types': ['text', 'image', 'video', 'link'],
                'optimal_times': ['13:00', '15:00', '19:00'],
                'hashtag_limit': 10,
                'character_limit': 63206
            }
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive content plan from brief
        
        Args:
            input_data: Dictionary containing 'brief', 'content_preferences', 'timeline'
            
        Returns:
            Dictionary with detailed content plan including calendar and templates
        """
        required_fields = ['brief']
        if not self._validate_input(input_data, required_fields):
            raise ValueError("Missing required fields for content plan generation")
        
        return await self._safe_execute(self._generate_content_plan, input_data)
    
    async def _generate_content_plan(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to generate content plan"""
        
        brief = input_data['brief']
        content_prefs = input_data.get('content_preferences', {})
        timeline = input_data.get('timeline', {})
        
        # Extract project information
        project_type = brief.get('project_type', 'general').lower()
        target_audience = brief.get('target_audience', {})
        brand_context = brief.get('brand_context', {})
        goals = brief.get('goals', {})
        
        # Determine content strategy based on project type
        content_strategy = self._determine_content_strategy(project_type, goals, target_audience)
        
        # Use AI to generate comprehensive content plan
        ai_prompt = f"""
        Create a comprehensive content plan based on the following information:

        Project Brief: {json.dumps(brief, indent=2)}
        Content Preferences: {json.dumps(content_prefs, indent=2)}
        Timeline: {json.dumps(timeline, indent=2)}
        Content Strategy: {json.dumps(content_strategy, indent=2)}
        Target Audience: {json.dumps(target_audience, indent=2)}
        Brand Context: {json.dumps(brand_context, indent=2)}

        Please provide a JSON response with the following content plan structure:
        {{
            "content_strategy": {{
                "objectives": ["Primary content objectives"],
                "target_audience": {{
                    "primary_persona": "Main target audience description",
                    "content_preferences": ["What type of content they prefer"],
                    "pain_points": ["Audience pain points to address"],
                    "preferred_channels": ["Where they consume content"]
                }},
                "content_pillars": [
                    {{
                        "pillar": "Content theme name",
                        "description": "What this pillar covers",
                        "percentage": "% of total content",
                        "content_types": ["blog", "social", "video"]
                    }}
                ],
                "brand_voice": {{
                    "tone": "Brand tone for content",
                    "style": "Writing style guidelines",
                    "do_use": ["Words/phrases to use"],
                    "dont_use": ["Words/phrases to avoid"]
                }}
            }},
            "content_calendar": {{
                "duration": "Plan duration (e.g., 3 months)",
                "start_date": "YYYY-MM-DD",
                "end_date": "YYYY-MM-DD",
                "monthly_themes": [
                    {{
                        "month": "Month name",
                        "theme": "Monthly theme",
                        "focus_areas": ["Key focus areas"],
                        "content_count": {{
                            "blog_posts": "number",
                            "social_posts": "number",
                            "other_content": "number"
                        }}
                    }}
                ]
            }},
            "content_types": [
                {{
                    "type": "blog_post/social_media/landing_page/email",
                    "frequency": "how often to create",
                    "topics": [
                        {{
                            "title": "Content title",
                            "description": "Content description",
                            "keywords": ["SEO keywords"],
                            "content_pillar": "Which pillar it supports",
                            "target_audience": "Primary audience",
                            "call_to_action": "Desired CTA",
                            "estimated_length": "Word/character count",
                            "channel": "Primary distribution channel"
                        }}
                    ]
                }}
            ],
            "social_media_calendar": {{
                "platforms": ["instagram", "twitter", "linkedin", "facebook"],
                "posting_schedule": {{
                    "monday": ["platform: post_type"],
                    "tuesday": ["platform: post_type"],
                    "wednesday": ["platform: post_type"],
                    "thursday": ["platform: post_type"],
                    "friday": ["platform: post_type"],
                    "saturday": ["platform: post_type"],
                    "sunday": ["platform: post_type"]
                }},
                "content_mix": {{
                    "educational": "percentage",
                    "promotional": "percentage",
                    "behind_scenes": "percentage",
                    "user_generated": "percentage",
                    "curated": "percentage"
                }}
            }},
            "seo_strategy": {{
                "primary_keywords": ["main keywords to target"],
                "secondary_keywords": ["supporting keywords"],
                "content_clusters": [
                    {{
                        "topic": "Main topic",
                        "pillar_content": "Main piece of content",
                        "cluster_content": ["Supporting content pieces"]
                    }}
                ],
                "internal_linking": "Strategy for linking content together"
            }},
            "content_templates": [
                {{
                    "template_name": "Template name",
                    "content_type": "blog/social/email",
                    "structure": ["Section 1", "Section 2", "Section 3"],
                    "example": "Example content using template"
                }}
            ],
            "performance_metrics": {{
                "kpis": ["Key performance indicators"],
                "tracking_methods": ["How to measure success"],
                "reporting_frequency": "How often to report",
                "success_benchmarks": ["What constitutes success"]
            }}
        }}
        """
        
        ai_response = await self._generate_ai_response(ai_prompt)
        
        try:
            content_plan = json.loads(ai_response)
            
            # Enhance with detailed calendar
            content_plan['detailed_calendar'] = self._generate_detailed_calendar(content_plan)
            
            # Add channel-specific guidelines
            content_plan['channel_guidelines'] = self._generate_channel_guidelines(content_plan)
            
            # Add content production workflow
            content_plan['production_workflow'] = self._generate_production_workflow()
            
            # Add metadata
            content_plan['generated_at'] = datetime.now().isoformat()
            content_plan['generator_version'] = '1.0.0'
            content_plan['based_on_brief'] = brief.get('project_title', 'Unknown Project')
            
            # Learn from generation
            self._learn_from_content_planning(brief, content_plan)
            
            return content_plan
            
        except json.JSONDecodeError:
            self.logger.warning("AI response wasn't valid JSON, using fallback generation")
            return self._fallback_content_planning(brief, content_strategy)
    
    def _determine_content_strategy(self, project_type: str, goals: Dict[str, Any], audience: Dict[str, Any]) -> Dict[str, Any]:
        """Determine content strategy based on project context"""
        
        strategy = {
            'focus_areas': [],
            'recommended_channels': [],
            'content_frequency': {},
            'primary_objectives': []
        }
        
        # Project type specific strategies
        if 'website' in project_type or 'web' in project_type:
            strategy['focus_areas'].extend(['SEO content', 'Landing pages', 'Blog posts'])
            strategy['recommended_channels'].extend(['website', 'blog', 'social_media'])
            strategy['content_frequency']['blog_posts'] = 'weekly'
            strategy['primary_objectives'].append('Drive organic traffic')
            
        elif 'branding' in project_type:
            strategy['focus_areas'].extend(['Brand storytelling', 'Visual content', 'Brand awareness'])
            strategy['recommended_channels'].extend(['social_media', 'website', 'email'])
            strategy['content_frequency']['social_posts'] = 'daily'
            strategy['primary_objectives'].append('Build brand recognition')
            
        elif 'marketing' in project_type:
            strategy['focus_areas'].extend(['Lead generation', 'Promotional content', 'Campaign support'])
            strategy['recommended_channels'].extend(['social_media', 'email', 'ads'])
            strategy['content_frequency']['campaign_content'] = 'campaign-based'
            strategy['primary_objectives'].append('Generate qualified leads')
        
        else:
            strategy['focus_areas'].extend(['General content', 'Audience engagement'])
            strategy['recommended_channels'].extend(['social_media', 'website'])
            strategy['content_frequency']['mixed_content'] = 'regular'
            strategy['primary_objectives'].append('Engage target audience')
        
        return strategy
    
    def _generate_detailed_calendar(self, content_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed monthly calendar with specific dates"""
        
        calendar_data = content_plan.get('content_calendar', {})
        start_date = datetime.now()
        
        if calendar_data.get('start_date'):
            try:
                start_date = datetime.fromisoformat(calendar_data['start_date'])
            except:
                pass
        
        detailed_calendar = {}
        
        # Generate 3 months of detailed calendar
        for month_offset in range(3):
            current_month = start_date + timedelta(days=30 * month_offset)
            month_key = current_month.strftime('%Y-%m')
            
            # Get days in month
            _, days_in_month = calendar.monthrange(current_month.year, current_month.month)
            
            month_calendar = {
                'month_name': current_month.strftime('%B %Y'),
                'days': {}
            }
            
            # Generate daily content assignments
            for day in range(1, days_in_month + 1):
                day_date = current_month.replace(day=day)
                weekday = day_date.strftime('%A').lower()
                
                # Get posting schedule for this day
                posting_schedule = content_plan.get('social_media_calendar', {}).get('posting_schedule', {})
                day_posts = posting_schedule.get(weekday, [])
                
                month_calendar['days'][day] = {
                    'date': day_date.strftime('%Y-%m-%d'),
                    'weekday': weekday,
                    'content_scheduled': day_posts,
                    'special_events': [],  # Could be enhanced with holiday/event data
                    'content_deadlines': []
                }
            
            detailed_calendar[month_key] = month_calendar
        
        return detailed_calendar
    
    def _generate_channel_guidelines(self, content_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific guidelines for each channel"""
        
        platforms = content_plan.get('social_media_calendar', {}).get('platforms', [])
        guidelines = {}
        
        for platform in platforms:
            if platform in self.channel_specs:
                spec = self.channel_specs[platform]
                guidelines[platform] = {
                    'posting_specs': spec,
                    'content_guidelines': {
                        'image_sizes': self._get_image_specs(platform),
                        'best_practices': self._get_best_practices(platform),
                        'hashtag_strategy': self._generate_hashtag_strategy(platform, content_plan)
                    }
                }
        
        return guidelines
    
    def _get_image_specs(self, platform: str) -> Dict[str, str]:
        """Get image size specifications for platform"""
        
        specs = {
            'instagram': {
                'square_post': '1080x1080px',
                'story': '1080x1920px',
                'reel': '1080x1920px',
                'carousel': '1080x1080px'
            },
            'twitter': {
                'post_image': '1200x675px',
                'header': '1500x500px'
            },
            'linkedin': {
                'post_image': '1200x627px',
                'company_logo': '300x300px'
            },
            'facebook': {
                'post_image': '1200x630px',
                'cover_photo': '820x312px'
            }
        }
        
        return specs.get(platform, {'standard': '1200x630px'})
    
    def _get_best_practices(self, platform: str) -> List[str]:
        """Get best practices for platform"""
        
        practices = {
            'instagram': [
                'Use high-quality visuals',
                'Post consistently',
                'Engage with comments quickly',
                'Use relevant hashtags',
                'Share behind-the-scenes content'
            ],
            'twitter': [
                'Keep tweets concise',
                'Use threads for longer content',
                'Engage in conversations',
                'Share timely content',
                'Retweet relevant industry content'
            ],
            'linkedin': [
                'Share professional insights',
                'Engage with industry discussions',
                'Use native video when possible',
                'Tag relevant connections',
                'Share company updates'
            ],
            'facebook': [
                'Post when audience is active',
                'Use Facebook Live for engagement',
                'Share diverse content types',
                'Respond to comments promptly',
                'Create shareable content'
            ]
        }
        
        return practices.get(platform, ['Follow platform guidelines', 'Engage with audience'])
    
    def _generate_hashtag_strategy(self, platform: str, content_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate hashtag strategy for platform"""
        
        brand_context = content_plan.get('content_strategy', {}).get('brand_voice', {})
        
        return {
            'branded_hashtags': ['#BrandName', '#BrandTagline'],
            'industry_hashtags': ['#Industry', '#Niche'],
            'community_hashtags': ['#Community', '#Audience'],
            'campaign_hashtags': ['#CampaignName'],
            'usage_guidelines': f'Use {self.channel_specs.get(platform, {}).get("hashtag_limit", 5)} hashtags maximum'
        }
    
    def _generate_production_workflow(self) -> Dict[str, Any]:
        """Generate content production workflow"""
        
        return {
            'workflow_stages': [
                {
                    'stage': 'Planning',
                    'duration': '1 week',
                    'activities': ['Topic research', 'Keyword analysis', 'Content calendar review'],
                    'stakeholders': ['Content strategist', 'SEO specialist']
                },
                {
                    'stage': 'Creation',
                    'duration': '2 weeks',
                    'activities': ['Writing', 'Design', 'Video production'],
                    'stakeholders': ['Content creator', 'Designer', 'Videographer']
                },
                {
                    'stage': 'Review',
                    'duration': '3 days',
                    'activities': ['Content review', 'Brand compliance check', 'SEO optimization'],
                    'stakeholders': ['Content manager', 'Brand manager']
                },
                {
                    'stage': 'Approval',
                    'duration': '2 days',
                    'activities': ['Client review', 'Final approval', 'Scheduling'],
                    'stakeholders': ['Client', 'Account manager']
                },
                {
                    'stage': 'Publishing',
                    'duration': '1 day',
                    'activities': ['Content publishing', 'Cross-platform distribution', 'Performance monitoring'],
                    'stakeholders': ['Social media manager', 'Analytics specialist']
                }
            ],
            'quality_checkpoints': [
                'Brand voice consistency',
                'SEO optimization',
                'Visual brand compliance',
                'Call-to-action effectiveness',
                'Channel-specific formatting'
            ]
        }
    
    def _learn_from_content_planning(self, brief: Dict[str, Any], content_plan: Dict[str, Any]):
        """Learn from content planning to improve future results"""
        
        memory_key = f"content_patterns_{datetime.now().strftime('%Y%m')}"
        current_patterns = self.get_memory(memory_key, {
            'popular_content_types': {},
            'successful_posting_frequencies': {},
            'effective_content_pillars': {}
        })
        
        # Track content type preferences
        content_types = content_plan.get('content_types', [])
        for content_type in content_types:
            type_name = content_type.get('type', 'unknown')
            current_patterns['popular_content_types'][type_name] = (
                current_patterns['popular_content_types'].get(type_name, 0) + 1
            )
        
        # Track content pillars
        pillars = content_plan.get('content_strategy', {}).get('content_pillars', [])
        for pillar in pillars:
            pillar_name = pillar.get('pillar', 'unknown')
            current_patterns['effective_content_pillars'][pillar_name] = (
                current_patterns['effective_content_pillars'].get(pillar_name, 0) + 1
            )
        
        self.update_memory(memory_key, current_patterns)
    
    def _fallback_content_planning(self, brief: Dict[str, Any], content_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback content planning when AI response fails"""
        
        project_name = brief.get('project_title', 'New Project')
        
        return {
            'content_strategy': {
                'objectives': ['Increase brand awareness', 'Engage target audience'],
                'content_pillars': [
                    {
                        'pillar': 'Educational',
                        'description': 'Helpful tips and insights',
                        'percentage': '40%',
                        'content_types': ['blog', 'social']
                    },
                    {
                        'pillar': 'Behind the Scenes',
                        'description': 'Company culture and process',
                        'percentage': '30%',
                        'content_types': ['social', 'video']
                    },
                    {
                        'pillar': 'Promotional',
                        'description': 'Product and service highlights',
                        'percentage': '30%',
                        'content_types': ['social', 'email']
                    }
                ]
            },
            'content_calendar': {
                'duration': '3 months',
                'start_date': datetime.now().strftime('%Y-%m-%d'),
                'end_date': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
            },
            'content_types': [
                {
                    'type': 'blog_post',
                    'frequency': 'weekly',
                    'topics': [
                        {
                            'title': 'Industry Best Practices',
                            'description': 'Share expertise and insights',
                            'keywords': ['industry', 'best practices'],
                            'content_pillar': 'Educational'
                        }
                    ]
                },
                {
                    'type': 'social_media',
                    'frequency': 'daily',
                    'topics': [
                        {
                            'title': 'Daily Tips',
                            'description': 'Quick valuable insights',
                            'content_pillar': 'Educational'
                        }
                    ]
                }
            ],
            'social_media_calendar': {
                'platforms': ['instagram', 'twitter', 'linkedin'],
                'posting_schedule': {
                    'monday': ['linkedin: professional insight'],
                    'tuesday': ['twitter: industry tip'],
                    'wednesday': ['instagram: behind the scenes'],
                    'thursday': ['linkedin: thought leadership'],
                    'friday': ['twitter: weekly recap'],
                    'saturday': ['instagram: lifestyle content'],
                    'sunday': ['instagram: inspirational quote']
                }
            },
            'generated_at': datetime.now().isoformat(),
            'fallback_generation': True
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            'name': 'Content Plan Generator',
            'description': 'Creates comprehensive content plans including blogs, social media, and landing pages',
            'inputs': ['brief', 'content_preferences', 'timeline'],
            'outputs': ['content_strategy', 'content_calendar', 'channel_guidelines'],
            'supported_content_types': list(self.content_types.keys()),
            'supported_channels': list(self.channel_specs.keys()),
            'features': ['seo_optimization', 'multi_channel_planning', 'performance_tracking'],
            'version': '1.0.0'
        }
