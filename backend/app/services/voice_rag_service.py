"""
Voice-Optimized RAG Service
Handles voice-specific query enhancement and response formatting for RAG
"""

import re
import logging
from typing import List, Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)


class VoiceRAGService:
    """Service for optimizing RAG for voice interactions"""
    
    def __init__(self):
        self.common_filler_words = {
            "um", "uh", "ah", "er", "like", "you know", "so", "well", 
            "basically", "actually", "literally", "kind of", "sort of"
        }
        
        self.voice_question_patterns = {
            "what": ["what is", "what are", "what does", "what's"],
            "how": ["how do", "how does", "how can", "how to"],
            "why": ["why is", "why do", "why does", "why would"],
            "when": ["when is", "when did", "when does", "when will"],
            "where": ["where is", "where can", "where do", "where does"],
            "who": ["who is", "who was", "who can", "who does"]
        }
    
    def enhance_voice_query(self, raw_transcription: str) -> str:
        """
        Enhance voice query by cleaning up speech artifacts and improving clarity
        
        Args:
            raw_transcription: Raw STT output
            
        Returns:
            Enhanced query text optimized for RAG
        """
        try:
            # Step 1: Basic cleanup
            enhanced_query = self._clean_transcription(raw_transcription)
            
            # Step 2: Expand contractions and abbreviations
            enhanced_query = self._expand_speech_patterns(enhanced_query)
            
            # Step 3: Improve question formation
            enhanced_query = self._improve_question_structure(enhanced_query)
            
            # Step 4: Add context hints for RAG
            enhanced_query = self._add_context_hints(enhanced_query)
            
            logger.info(f"Voice query enhanced: '{raw_transcription}' -> '{enhanced_query}'")
            return enhanced_query
            
        except Exception as e:
            logger.error(f"Voice query enhancement failed: {str(e)}")
            return raw_transcription
    
    def _clean_transcription(self, text: str) -> str:
        """Remove filler words, repeated words, and clean up transcription"""
        
        # Convert to lowercase for processing
        words = text.lower().split()
        cleaned_words = []
        last_word = ""
        
        for word in words:
            # Remove punctuation for comparison
            clean_word = re.sub(r'[^\w\s]', '', word)
            
            # Skip filler words
            if clean_word in self.common_filler_words:
                continue
            
            # Skip repeated words (common in speech)
            if clean_word == last_word and len(clean_word) > 2:
                continue
            
            cleaned_words.append(word)
            last_word = clean_word
        
        # Reconstruct with proper capitalization
        result = " ".join(cleaned_words)
        
        # Capitalize first word and after punctuation
        result = re.sub(r'(^|[.!?]\s+)([a-z])', 
                       lambda m: m.group(1) + m.group(2).upper(), 
                       result)
        
        return result.strip()
    
    def _expand_speech_patterns(self, text: str) -> str:
        """Expand common speech contractions and patterns"""
        
        expansions = {
            "what's": "what is",
            "how's": "how is", 
            "where's": "where is",
            "when's": "when is",
            "who's": "who is",
            "why's": "why is",
            "can't": "cannot",
            "won't": "will not",
            "don't": "do not",
            "doesn't": "does not",
            "didn't": "did not",
            "isn't": "is not",
            "aren't": "are not",
            "wasn't": "was not",
            "weren't": "were not",
            "i'm": "I am",
            "you're": "you are",
            "we're": "we are",
            "they're": "they are"
        }
        
        result = text
        for contraction, expansion in expansions.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(contraction) + r'\b'
            result = re.sub(pattern, expansion, result, flags=re.IGNORECASE)
        
        return result
    
    def _improve_question_structure(self, text: str) -> str:
        """Improve question structure for better RAG retrieval"""
        
        text_lower = text.lower().strip()
        
        # Check if it's already a well-formed question
        if text_lower.endswith('?'):
            return text
        
        # Detect question intent and improve structure
        for question_type, patterns in self.voice_question_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    # Ensure question ends with question mark
                    if not text.endswith('?'):
                        text += '?'
                    break
        
        # Handle implicit questions (statements that are actually questions)
        implicit_patterns = [
            r'\btell me about\b',
            r'\bi want to know\b',
            r'\bi need to understand\b',
            r'\bcan you explain\b',
            r'\bhelp me with\b'
        ]
        
        for pattern in implicit_patterns:
            if re.search(pattern, text_lower):
                if not text.endswith('?'):
                    text += '?'
                break
        
        return text
    
    def _add_context_hints(self, text: str) -> str:
        """Add subtle context hints to improve RAG retrieval"""
        
        # This is a placeholder for future enhancements
        # Could add domain-specific keywords or context expansion
        return text
    
    def format_response_for_voice(
        self, 
        response_text: str, 
        contexts: List[str] = None,
        max_length: int = 300
    ) -> str:
        """
        Format response text for optimal voice synthesis and listening
        
        Args:
            response_text: Original response text
            contexts: Retrieved contexts (for citation info)
            max_length: Maximum response length for voice
            
        Returns:
            Voice-optimized response text
        """
        try:
            # Step 1: Basic voice formatting
            formatted_response = self._format_for_speech(response_text)
            
            # Step 2: Add natural speech patterns
            formatted_response = self._add_speech_patterns(formatted_response)
            
            # Step 3: Manage length for voice
            formatted_response = self._manage_voice_length(formatted_response, max_length)
            
            # Step 4: Add citations in voice-friendly format
            if contexts:
                formatted_response = self._add_voice_citations(formatted_response, len(contexts))
            
            logger.info(f"Response formatted for voice: {len(formatted_response)} chars")
            return formatted_response
            
        except Exception as e:
            logger.error(f"Voice response formatting failed: {str(e)}")
            return response_text
    
    def _format_for_speech(self, text: str) -> str:
        """Format text for natural speech synthesis"""
        
        # Replace common abbreviations with full words
        speech_replacements = {
            r'\bDr\.\b': 'Doctor',
            r'\bMr\.\b': 'Mister', 
            r'\bMrs\.\b': 'Missus',
            r'\bMs\.\b': 'Miss',
            r'\bProf\.\b': 'Professor',
            r'\betc\.\b': 'etcetera',
            r'\be\.g\.\b': 'for example',
            r'\bi\.e\.\b': 'that is',
            r'\bvs\.\b': 'versus',
            r'\bUS\b': 'United States',
            r'\bUK\b': 'United Kingdom',
            r'\bAPI\b': 'A P I',
            r'\bURL\b': 'U R L',
            r'\bHTML\b': 'H T M L',
            r'\bCSS\b': 'C S S',
            r'\bJSON\b': 'J S O N',
            r'\bXML\b': 'X M L'
        }
        
        result = text
        for pattern, replacement in speech_replacements.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Handle numbers and dates better for speech
        # Convert large numbers to spoken form
        result = re.sub(r'\b(\d{4})\b', r'\1', result)  # Keep years as is
        
        # Add pauses for better speech flow
        result = re.sub(r'([.!?])\s*', r'\1 ', result)  # Ensure space after punctuation
        result = re.sub(r'([,;:])\s*', r'\1 ', result)  # Space after commas/colons
        
        return result.strip()
    
    def _add_speech_patterns(self, text: str) -> str:
        """Add natural speech patterns and transitions"""
        
        # Add conversation starters for more natural flow
        if not any(text.lower().startswith(starter) for starter in 
                  ['well', 'so', 'basically', 'actually', 'let me', 'according to']):
            
            # Choose appropriate starter based on content
            if '?' in text:
                text = "Let me explain. " + text
            elif any(word in text.lower() for word in ['because', 'since', 'due to']):
                text = "Well, " + text
            elif text.lower().startswith(('the', 'a ', 'an ')):
                text = "So, " + text
        
        # Add natural transitions for complex responses
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) > 3:
            # Add transition words between sentences
            transitions = ["Additionally", "Furthermore", "Also", "Moreover", "In fact"]
            for i in range(1, min(len(sentences)-1, 3)):
                if sentences[i].strip() and len(sentences[i].strip()) > 20:
                    sentences[i] = f"{transitions[i-1]}, {sentences[i].strip()}"
            
            text = '. '.join(filter(None, sentences)) + '.'
        
        return text
    
    def _manage_voice_length(self, text: str, max_length: int) -> str:
        """Manage response length for voice output"""
        
        if len(text) <= max_length:
            return text
        
        # Find natural break points
        sentences = re.split(r'[.!?]+', text)
        
        # Build response up to max length
        result_sentences = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_length = len(sentence) + 2  # +2 for punctuation and space
            
            if current_length + sentence_length <= max_length:
                result_sentences.append(sentence)
                current_length += sentence_length
            else:
                # If we have at least one sentence, stop here
                if result_sentences:
                    break
                else:
                    # If first sentence is too long, truncate it
                    truncated = sentence[:max_length-20] + "..."
                    result_sentences.append(truncated)
                    break
        
        result = '. '.join(result_sentences)
        if result and not result.endswith(('.', '!', '?')):
            result += '.'
        
        # Add continuation hint if truncated
        if len(text) > len(result) + 50:
            result += " Would you like me to continue with more details?"
        
        return result
    
    def _add_voice_citations(self, text: str, context_count: int) -> str:
        """Add voice-friendly citations"""
        
        if context_count == 0:
            return text
        
        # Add citation at the end in natural speech
        if context_count == 1:
            citation = " This information comes from your uploaded document."
        else:
            citation = f" This information comes from {context_count} of your uploaded documents."
        
        return text + citation
    
    def assess_voice_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Assess voice query characteristics to optimize RAG parameters
        
        Args:
            query: Voice query text
            
        Returns:
            Dictionary with query analysis and RAG optimization hints
        """
        try:
            analysis = {
                "query_type": self._classify_query_type(query),
                "complexity": self._assess_query_complexity(query),
                "domain_hints": self._extract_domain_hints(query),
                "response_style": self._determine_response_style(query),
                "rag_params": {}
            }
            
            # Set RAG parameters based on analysis
            if analysis["query_type"] == "factual":
                analysis["rag_params"] = {
                    "max_contexts": 2,
                    "similarity_threshold": 0.8,
                    "use_reranking": True
                }
            elif analysis["query_type"] == "explanatory":
                analysis["rag_params"] = {
                    "max_contexts": 4,
                    "similarity_threshold": 0.7,
                    "use_reranking": True
                }
            elif analysis["query_type"] == "comparative":
                analysis["rag_params"] = {
                    "max_contexts": 5,
                    "similarity_threshold": 0.6,
                    "use_reranking": True
                }
            else:
                analysis["rag_params"] = {
                    "max_contexts": 3,
                    "similarity_threshold": 0.7,
                    "use_reranking": False
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Voice query intent assessment failed: {str(e)}")
            return {
                "query_type": "general",
                "complexity": "moderate", 
                "rag_params": {"max_contexts": 3, "similarity_threshold": 0.7}
            }
    
    def _classify_query_type(self, query: str) -> str:
        """Classify the type of voice query"""
        
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['what is', 'define', 'meaning of']):
            return "factual"
        elif any(word in query_lower for word in ['how to', 'how do', 'explain', 'process']):
            return "explanatory"
        elif any(word in query_lower for word in ['compare', 'difference', 'versus', 'better']):
            return "comparative"
        elif any(word in query_lower for word in ['why', 'reason', 'cause', 'because']):
            return "causal"
        else:
            return "general"
    
    def _assess_query_complexity(self, query: str) -> str:
        """Assess complexity of voice query"""
        
        words = query.split()
        
        if len(words) <= 5:
            return "simple"
        elif len(words) <= 12:
            return "moderate"
        else:
            return "complex"
    
    def _extract_domain_hints(self, query: str) -> List[str]:
        """Extract domain-specific hints from query"""
        
        domain_keywords = {
            "technical": ["api", "code", "programming", "software", "database", "server"],
            "business": ["revenue", "profit", "strategy", "market", "customer", "sales"],
            "medical": ["symptoms", "treatment", "diagnosis", "medicine", "health", "patient"],
            "legal": ["law", "legal", "contract", "regulation", "compliance", "rights"],
            "educational": ["learn", "study", "course", "lesson", "education", "teaching"]
        }
        
        query_lower = query.lower()
        detected_domains = []
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_domains.append(domain)
        
        return detected_domains
    
    def _determine_response_style(self, query: str) -> str:
        """Determine appropriate response style for voice"""
        
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['quick', 'brief', 'short', 'summary']):
            return "concise"
        elif any(word in query_lower for word in ['detail', 'explain', 'elaborate', 'comprehensive']):
            return "detailed"
        else:
            return "balanced"


# Global instance
voice_rag_service = VoiceRAGService()