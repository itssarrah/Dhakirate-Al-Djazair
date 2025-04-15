import json
import os
from typing import Dict, Optional
import re
from datetime import datetime

class TopicManager:
    def __init__(self, ml_manager):
        self.ml_manager = ml_manager
        self.cache_file = "topic_cache.json"
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        """Load the cache from file or create new if doesn't exist"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading cache: {e}")
            return {}

    def _save_cache(self):
        """Save the current cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def _get_cache_key(self, educational_stage: str, topic: str) -> str:
        """Generate a unique cache key"""
        return f"{educational_stage}:{topic}"

    def _get_from_cache(self, educational_stage: str, topic: str) -> Optional[str]:
        """Retrieve content from cache if exists"""
        cache_key = self._get_cache_key(educational_stage, topic)
        if (cache_key in self.cache):
            cache_entry = self.cache[cache_key]
            # Add timestamp check if you want to expire cache after certain time
            # timestamp = datetime.fromisoformat(cache_entry['timestamp'])
            # if (datetime.now() - timestamp).days > 7:  # Expire after 7 days
            #     return None
            return cache_entry['content']
        return None

    def _add_to_cache(self, educational_stage: str, topic: str, content: str):
        """Add enhanced content to cache"""
        cache_key = self._get_cache_key(educational_stage, topic)
        self.cache[cache_key] = {
            'content': content,
            'timestamp': datetime.now().isoformat(),
        }
        self._save_cache()

    def _parse_markdown_content(self, raw_content: str) -> str:
        """Extract and clean the actual markdown content from LLM response"""
        
        # Remove any "Here's the transformed content:" or similar prefixes
        content = re.sub(r'^.*?(?=##|\n#)', '', raw_content, flags=re.DOTALL)
        
        # Remove any concluding remarks
        content = re.sub(r'\n*(?:Note:|In conclusion:|That\'s it!|The end).*$', '', content, flags=re.DOTALL)
        
        # Ensure proper markdown heading hierarchy
        content = re.sub(r'^#(?!#)', '##', content, flags=re.MULTILINE)
        
        # Clean up multiple newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Clean up spaces around markdown elements
        content = re.sub(r'\*\*\s+', '**', content)  # Clean bold
        content = re.sub(r'\s+\*\*', '**', content)
        content = re.sub(r'_\s+', '_', content)      # Clean italic
        content = re.sub(r'\s+_', '_', content)
        
        # Ensure proper spacing for lists
        content = re.sub(r'(?<=\n)-\s*', '- ', content)
        
        # Clean up blockquotes
        content = re.sub(r'>\s*', '> ', content)
        
        return content.strip()

    def enhance_topic_content(self, topic: str, content: str, educational_stage: str = None) -> str:
        """Convert regular content into well-structured markdown content with caching"""
        
        # Try to get from cache first
        if educational_stage:
            cached_content = self._get_from_cache(educational_stage, topic)
            if cached_content:
                print(f"Cache hit for topic: {topic}")
                return cached_content

        try:
            # Add educational stage-based complexity guidance
            stage_complexity = {
                "PS": "Transform content into very simple, clear explanations. Use basic vocabulary and short sentences.",
                "JS": "Present content clearly with moderate complexity. Define technical terms. Use straightforward examples.",
                "HSS": "Present content with academic depth. Include detailed explanations and historical context.",
                "HSL": "Present content with sophisticated analysis. Include historical interpretations and connections.",
                "UNI": "Present content with advanced academic depth. Include historiographical perspectives."
            }

            stage_prefix = educational_stage[:2] if educational_stage else "JS"
            complexity_guide = stage_complexity.get(stage_prefix, stage_complexity["JS"])

            messages = [
            {"role": "system", "content": """You are an expert history teacher and writer.
            {complexity_guide}
            Educational level: {educational_stage}
            Transform the given historical content into a well-structured markdown lesson appropriate for this educational level.
            Start directly with the markdown content using ## for main sections.
            Do not add any introductory text or concluding remarks.
            
            Follow these rules:
            1. Maintain historical accuracy
            2. Use proper markdown headings (##, ###)
            3. Include bullet points for key events
            4. Add quote blocks for important historical quotes or facts
            5. Use **bold** for key terms and dates
            6. Use *italic* for emphasis
            7. Start with a brief summary section
            8. Use consistent date format
            9. Keep the original Arabic language and stay true to the given content, because it is from school textbooks
            10. Keep paragraphs concise and well-organized"""},
            {"role": "user", "content": f"""
            Topic: {topic}
            Content: {content}
            
            Transform this into a markdown lesson. Start directly with the markdown content."""}
        ]


            raw_response = self.ml_manager.chat_completion(messages)
            enhanced_content = raw_response or content

            # Cache the enhanced content if educational_stage is provided
            if educational_stage:
                self._add_to_cache(educational_stage, topic, enhanced_content)
                print(f"Cached enhanced content for topic: {topic}")

            return enhanced_content
            
        except Exception as e:
            print(f"Error enhancing topic content: {e}")
            return content
