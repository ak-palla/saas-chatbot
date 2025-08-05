import re
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import cssutils
import tinycss2
from urllib.parse import urlparse

from app.core.database import get_supabase_admin
from app.models.widget import (
    WidgetConfiguration, WidgetConfigurationCreate, WidgetConfigurationUpdate,
    WidgetTemplate, WidgetAnalytics
)

# Set up logging
logger = logging.getLogger(__name__)
cssutils.log.setLevel(logging.CRITICAL)  # Suppress cssutils warnings

class WidgetService:
    """Service for widget management, customization, and security"""
    
    def __init__(self):
        self.supabase = get_supabase_admin()
        
        # Allowed CSS properties for security
        self.allowed_css_properties = {
            # Layout
            'display', 'position', 'top', 'right', 'bottom', 'left', 'z-index',
            'width', 'height', 'max-width', 'max-height', 'min-width', 'min-height',
            'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
            'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
            'box-sizing', 'overflow', 'overflow-x', 'overflow-y',
            
            # Typography
            'font-family', 'font-size', 'font-weight', 'font-style', 'line-height',
            'text-align', 'text-decoration', 'text-transform', 'letter-spacing',
            'word-spacing', 'color', 'font-variant',
            
            # Background & Border
            'background', 'background-color', 'background-image', 'background-position',
            'background-repeat', 'background-size', 'background-attachment',
            'border', 'border-top', 'border-right', 'border-bottom', 'border-left',
            'border-color', 'border-style', 'border-width', 'border-radius',
            'box-shadow', 'outline', 'outline-color', 'outline-style', 'outline-width',
            
            # Flexbox & Grid
            'flex', 'flex-direction', 'flex-wrap', 'justify-content', 'align-items',
            'align-content', 'flex-grow', 'flex-shrink', 'flex-basis', 'order',
            'grid', 'grid-template-columns', 'grid-template-rows', 'grid-gap',
            'grid-column', 'grid-row', 'place-items', 'place-content',
            
            # Animation & Transition
            'transition', 'transition-property', 'transition-duration', 'transition-timing-function',
            'transition-delay', 'animation', 'animation-name', 'animation-duration',
            'animation-timing-function', 'animation-delay', 'animation-iteration-count',
            'animation-direction', 'animation-fill-mode', 'animation-play-state',
            'transform', 'transform-origin', 'transform-style',
            
            # Visibility & Opacity
            'opacity', 'visibility', 'cursor', 'pointer-events',
            
            # List & Table
            'list-style', 'list-style-type', 'list-style-position', 'list-style-image',
            'table-layout', 'border-collapse', 'border-spacing', 'caption-side',
            'empty-cells', 'vertical-align',
            
            # Other
            'content', 'quotes', 'counter-reset', 'counter-increment', 'resize',
            'user-select', 'white-space', 'word-wrap', 'word-break', 'hyphens'
        }
        
        # Dangerous CSS values/functions to block
        self.blocked_css_values = [
            'javascript:', 'data:', 'vbscript:', 'expression', 'behavior',
            'url(javascript:', 'url(data:', '@import', 'eval(', 'iframe'
        ]
        
        # Widget class prefixes that are allowed to be styled
        self.allowed_widget_selectors = [
            '.chatbot-widget-container',
            '.chatbot-toggle-button',
            '.chatbot-window',
            '.chatbot-header',
            '.chatbot-messages',
            '.chatbot-message',
            '.chatbot-input-container',
            '.chatbot-input',
            '.chatbot-send-button',
            '.chatbot-voice-button',
            '.chatbot-audio-level'
        ]

    def validate_custom_css(self, css_content: str) -> Dict[str, Any]:
        """
        Validate and sanitize custom CSS for security
        Returns dict with validation results and sanitized CSS
        """
        logger.info("🔍 Validating custom CSS content")
        
        result = {
            "is_valid": True,
            "sanitized_css": "",
            "warnings": [],
            "errors": [],
            "blocked_properties": [],
            "blocked_values": []
        }
        
        if not css_content or not css_content.strip():
            result["sanitized_css"] = ""
            return result
        
        try:
            # Parse CSS using tinycss2
            parsed_css = tinycss2.parse_stylesheet(css_content)
            sanitized_rules = []
            
            for rule in parsed_css:
                if rule.type == 'qualified-rule':
                    # Check selectors
                    selector_text = tinycss2.serialize(rule.prelude).strip()
                    if not self._is_allowed_selector(selector_text):
                        result["warnings"].append(f"Selector '{selector_text}' is not allowed for widget styling")
                        continue
                    
                    # Process declarations
                    sanitized_declarations = []
                    for token in rule.content:
                        if token.type == 'declaration':
                            prop_name = token.name
                            prop_value = tinycss2.serialize(token.value).strip()
                            
                            # Validate property
                            if prop_name not in self.allowed_css_properties:
                                result["blocked_properties"].append(prop_name)
                                result["warnings"].append(f"Property '{prop_name}' is not allowed")
                                continue
                            
                            # Validate value
                            if self._contains_blocked_value(prop_value):
                                result["blocked_values"].append(f"{prop_name}: {prop_value}")
                                result["warnings"].append(f"Value for '{prop_name}' contains blocked content")
                                continue
                            
                            sanitized_declarations.append(f"{prop_name}: {prop_value}")
                    
                    if sanitized_declarations:
                        sanitized_rule = f"{selector_text} {{ {'; '.join(sanitized_declarations)}; }}"
                        sanitized_rules.append(sanitized_rule)
                
                elif rule.type == 'at-rule':
                    # Block most at-rules for security, allow only safe ones
                    if rule.at_keyword in ['media', 'supports', 'keyframes']:
                        # For now, skip at-rules - can be implemented later with more validation
                        result["warnings"].append(f"At-rule '@{rule.at_keyword}' is not currently supported")
                    else:
                        result["warnings"].append(f"At-rule '@{rule.at_keyword}' is blocked for security")
            
            result["sanitized_css"] = '\n'.join(sanitized_rules)
            
            if result["warnings"] or result["errors"]:
                logger.warning(f"⚠️ CSS validation found {len(result['warnings'])} warnings, {len(result['errors'])} errors")
            else:
                logger.info("✅ CSS validation passed")
                
        except Exception as e:
            result["is_valid"] = False
            result["errors"].append(f"CSS parsing error: {str(e)}")
            logger.error(f"💥 CSS validation error: {str(e)}")
        
        return result

    def _is_allowed_selector(self, selector: str) -> bool:
        """Check if CSS selector is allowed for widget styling"""
        selector = selector.strip()
        
        # Allow selectors that start with allowed widget classes
        for allowed_prefix in self.allowed_widget_selectors:
            if selector.startswith(allowed_prefix):
                return True
        
        # Block universal selectors and overly broad selectors
        if selector in ['*', 'body', 'html', 'div', 'span']:
            return False
        
        return False

    def _contains_blocked_value(self, value: str) -> bool:
        """Check if CSS value contains blocked content"""
        value_lower = value.lower()
        
        for blocked in self.blocked_css_values:
            if blocked in value_lower:
                return True
        
        return False

    def apply_template_to_configuration(self, config_id: str, template_id: str) -> Dict[str, Any]:
        """Apply a widget template to a configuration"""
        logger.info(f"🎨 Applying template {template_id} to configuration {config_id}")
        
        try:
            # Get template
            template_response = self.supabase.table("widget_templates").select("*").eq("id", template_id).eq("is_active", True).execute()
            
            if not template_response.data:
                raise ValueError("Template not found or inactive")
            
            template = template_response.data[0]
            
            # Get current configuration
            config_response = self.supabase.table("widget_configurations").select("*").eq("id", config_id).execute()
            
            if not config_response.data:
                raise ValueError("Widget configuration not found")
            
            current_config = config_response.data[0]
            
            # Merge template configuration with current config
            template_config = template.get("config_template", {})
            custom_css = template.get("css_template", "")
            
            # Validate template CSS
            css_validation = self.validate_custom_css(custom_css)
            if not css_validation["is_valid"]:
                raise ValueError(f"Template CSS validation failed: {css_validation['errors']}")
            
            # Update configuration
            update_data = {
                "template_id": template_id,
                "custom_css": css_validation["sanitized_css"],
                **template_config,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = self.supabase.table("widget_configurations").update(update_data).eq("id", config_id).execute()
            
            # Update template download count
            self.supabase.table("widget_templates").update({
                "downloads_count": template["downloads_count"] + 1
            }).eq("id", template_id).execute()
            
            logger.info(f"✅ Template applied successfully")
            
            return {
                "success": True,
                "updated_config": response.data[0],
                "css_warnings": css_validation.get("warnings", [])
            }
            
        except Exception as e:
            logger.error(f"💥 Error applying template: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_widget_performance_suggestions(self, chatbot_id: str) -> List[Dict[str, Any]]:
        """Analyze widget performance and provide optimization suggestions"""
        logger.info(f"⚡ Analyzing widget performance for chatbot {chatbot_id}")
        
        suggestions = []
        
        try:
            # Get recent analytics data
            end_date = datetime.utcnow()
            start_date = end_date.replace(day=end_date.day - 7)  # Last 7 days
            
            analytics_response = self.supabase.table("widget_analytics").select("*").eq("chatbot_id", chatbot_id).gte("created_at", start_date.isoformat()).execute()
            
            analytics_data = analytics_response.data
            
            if not analytics_data:
                return [{"type": "info", "message": "No recent data available for analysis"}]
            
            # Analyze load times
            load_times = [session.get("load_time_ms", 0) for session in analytics_data if session.get("load_time_ms")]
            if load_times:
                avg_load_time = sum(load_times) / len(load_times)
                if avg_load_time > 3000:  # 3 seconds
                    suggestions.append({
                        "type": "performance",
                        "priority": "high",
                        "message": f"Average load time is {avg_load_time:.0f}ms. Consider optimizing widget assets.",
                        "recommendation": "Enable CDN, minimize custom CSS, optimize images"
                    })
                elif avg_load_time > 1500:  # 1.5 seconds
                    suggestions.append({
                        "type": "performance",
                        "priority": "medium",
                        "message": f"Load time could be improved (current: {avg_load_time:.0f}ms).",
                        "recommendation": "Review custom CSS complexity, consider lazy loading"
                    })
            
            # Analyze bounce rate
            total_sessions = len(analytics_data)
            bounced_sessions = sum(1 for session in analytics_data if session.get("bounce_rate", True))
            bounce_rate = (bounced_sessions / total_sessions) * 100 if total_sessions > 0 else 0
            
            if bounce_rate > 80:
                suggestions.append({
                    "type": "engagement",
                    "priority": "high",
                    "message": f"High bounce rate ({bounce_rate:.1f}%). Users aren't engaging with the widget.",
                    "recommendation": "Review greeting message, adjust auto-open settings, improve positioning"
                })
            elif bounce_rate > 60:
                suggestions.append({
                    "type": "engagement",
                    "priority": "medium",
                    "message": f"Bounce rate could be improved ({bounce_rate:.1f}%).",
                    "recommendation": "A/B test different greetings or conversation starters"
                })
            
            # Analyze device performance
            mobile_sessions = [s for s in analytics_data if s.get("device_type") == "mobile"]
            if mobile_sessions:
                mobile_load_times = [s.get("load_time_ms", 0) for s in mobile_sessions if s.get("load_time_ms")]
                if mobile_load_times:
                    mobile_avg = sum(mobile_load_times) / len(mobile_load_times)
                    desktop_sessions = [s for s in analytics_data if s.get("device_type") == "desktop"]
                    if desktop_sessions:
                        desktop_load_times = [s.get("load_time_ms", 0) for s in desktop_sessions if s.get("load_time_ms")]
                        if desktop_load_times:
                            desktop_avg = sum(desktop_load_times) / len(desktop_load_times)
                            if mobile_avg > desktop_avg * 1.5:
                                suggestions.append({
                                    "type": "mobile",
                                    "priority": "medium",
                                    "message": f"Mobile performance is significantly slower than desktop.",
                                    "recommendation": "Optimize for mobile: reduce bundle size, simplify animations"
                                })
            
            # Check error rates
            deployments_response = self.supabase.table("widget_deployments").select("status").eq("chatbot_id", chatbot_id).execute()
            deployments = deployments_response.data
            
            if deployments:
                error_count = sum(1 for d in deployments if d.get("status") == "error")
                error_rate = (error_count / len(deployments)) * 100
                
                if error_rate > 5:
                    suggestions.append({
                        "type": "reliability",
                        "priority": "high",
                        "message": f"High error rate in deployments ({error_rate:.1f}%).",
                        "recommendation": "Check deployment configurations, verify domain settings"
                    })
            
            logger.info(f"✅ Generated {len(suggestions)} performance suggestions")
            
        except Exception as e:
            logger.error(f"💥 Error analyzing widget performance: {str(e)}")
            suggestions.append({
                "type": "error",
                "priority": "low",
                "message": "Unable to analyze performance data",
                "recommendation": "Check widget analytics configuration"
            })
        
        return suggestions

    def generate_widget_embed_code(self, chatbot_id: str, config_id: Optional[str] = None) -> Dict[str, str]:
        """Generate various embed code options for a widget"""
        logger.info(f"🔗 Generating embed code for chatbot {chatbot_id}")
        
        try:
            # Get chatbot info
            chatbot_response = self.supabase.table("chatbots").select("*").eq("id", chatbot_id).execute()
            if not chatbot_response.data:
                raise ValueError("Chatbot not found")
            
            chatbot = chatbot_response.data[0]
            
            # Get configuration if specified
            widget_config = {}
            if config_id:
                config_response = self.supabase.table("widget_configurations").select("*").eq("id", config_id).eq("chatbot_id", chatbot_id).execute()
                if config_response.data:
                    config = config_response.data[0]
                    widget_config = {
                        "theme": config.get("theme", "light"),
                        "position": config.get("position", "bottom-right"),
                        "primaryColor": config.get("primary_color", "#3b82f6"),
                        "maxWidth": str(config.get("max_width", 400)),
                        "maxHeight": str(config.get("max_height", 600)),
                        "autoOpen": str(config.get("auto_open", False)).lower(),
                        "enableVoice": str(chatbot.get("behavior_config", {}).get("enableVoice", False)).lower()
                    }
            
            # Base URLs (would be configurable in production)
            base_url = "https://api.yourdomain.com"  # Replace with actual API URL
            widget_url = "https://cdn.yourdomain.com/widget.js"  # Replace with actual CDN URL
            
            # Generate script tag embed
            data_attrs = "\n".join([f'  data-{key.lower().replace("_", "-")}="{value}"' for key, value in widget_config.items()])
            
            script_embed = f'''<!-- Chatbot Widget -->
<script 
  src="{widget_url}"
  data-chatbot-id="{chatbot_id}"
  data-base-url="{base_url}"
{data_attrs}></script>'''
            
            # Generate manual JavaScript embed
            config_js = ", ".join([f'{key}: "{value}"' if isinstance(value, str) else f'{key}: {value}' for key, value in widget_config.items()])
            
            manual_embed = f'''<!-- Include widget script -->
<script src="{widget_url}"></script>

<!-- Initialize widget -->
<script>
  window.ChatbotWidget.init({{
    chatbotId: '{chatbot_id}',
    baseUrl: '{base_url}',
    {config_js}
  }});
</script>'''
            
            # Generate React component embed
            react_props = ", ".join([f'{key}="{value}"' if isinstance(value, str) else f'{key}={{{value}}}' for key, value in widget_config.items()])
            
            react_embed = f'''import {{ ChatbotWidget }} from '@chatbot-saas/react-widget';

function App() {{
  return (
    <div>
      <ChatbotWidget 
        chatbotId="{chatbot_id}"
        baseUrl="{base_url}"
        {react_props}
      />
    </div>
  );
}}'''
            
            # Generate Vue component embed
            vue_props = ", ".join([f':{key.replace("_", "-")}="{value}"' if isinstance(value, str) else f':{key.replace("_", "-")}="{value}"' for key, value in widget_config.items()])
            
            vue_embed = f'''<template>
  <div>
    <chatbot-widget
      chatbot-id="{chatbot_id}"
      base-url="{base_url}"
      {vue_props}
    />
  </div>
</template>

<script>
import {{ ChatbotWidget }} from '@chatbot-saas/vue-widget';

export default {{
  components: {{
    ChatbotWidget
  }}
}};
</script>'''
            
            logger.info("✅ Widget embed codes generated successfully")
            
            return {
                "script_tag": script_embed,
                "manual_js": manual_embed,
                "react": react_embed,
                "vue": vue_embed,
                "config_used": widget_config
            }
            
        except Exception as e:
            logger.error(f"💥 Error generating embed code: {str(e)}")
            raise ValueError(f"Failed to generate embed code: {str(e)}")

# Create singleton instance
widget_service = WidgetService()