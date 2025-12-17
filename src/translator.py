"""
Translation utility for converting Czech text to English
Uses deep-translator library for reliable translation
"""

import logging
from typing import Optional
import time

logger = logging.getLogger(__name__)

# Try to import deep-translator, fallback to None if not available
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    logger.warning("deep-translator not installed. Translation will be disabled. Install with: pip install deep-translator")


class TextTranslator:
    """Utility class for translating Czech text to English"""
    
    def __init__(self):
        self.translator = None
        self.last_translation_time = 0
        self.min_delay = 0.1  # Minimum delay between translations (100ms) to avoid rate limiting
        self.enabled = TRANSLATOR_AVAILABLE
        
        if self.enabled:
            try:
                self.translator = GoogleTranslator(source='cs', target='en')
                logger.info("Translation service initialized (Czech -> English)")
            except Exception as e:
                logger.warning(f"Failed to initialize translator: {e}")
                self.enabled = False
        else:
            logger.warning("Translation disabled - deep-translator not installed")
    
    def is_czech_text(self, text: str) -> bool:
        """
        Detect if text is likely in Czech language
        Uses common Czech characters and words
        """
        if not text or len(text.strip()) < 3:
            return False
        
        # Common Czech characters
        czech_chars = 'áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ'
        has_czech_chars = any(char in text for char in czech_chars)
        
        # Common Czech words
        czech_words = [
            'bouda', 'chata', 'horská', 'hora', 'vrchol', 'cesta', 'přístup',
            'otevřeno', 'sezóna', 'voda', 'zdroj', 'studna', 'potok',
            'majitel', 'správce', 'vlastník', 'kontakt', 'telefon', 'email',
            'popis', 'informace', 'upravit', 'vložil', 'celoročně'
        ]
        text_lower = text.lower()
        has_czech_words = any(word in text_lower for word in czech_words)
        
        return has_czech_chars or has_czech_words
    
    def translate(self, text: str, force: bool = False) -> Optional[str]:
        """
        Translate Czech text to English
        
        Args:
            text: Text to translate
            force: Force translation even if text doesn't appear to be Czech
        
        Returns:
            Translated text, or original text if translation fails or is not needed
        """
        if not self.enabled or not self.translator:
            return text
        
        if not text or len(text.strip()) < 3:
            return text
        
        # Check if translation is needed
        if not force and not self.is_czech_text(text):
            return text
        
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_translation_time
        if time_since_last < self.min_delay:
            time.sleep(self.min_delay - time_since_last)
        
        try:
            # Clean text (remove extra whitespace)
            clean_text = ' '.join(text.split())
            
            # Limit text length to avoid API issues (Google Translate has limits)
            if len(clean_text) > 5000:
                clean_text = clean_text[:5000]
                logger.warning(f"Text truncated to 5000 characters for translation")
            
            # Translate
            translated = self.translator.translate(clean_text)
            self.last_translation_time = time.time()
            
            # Return translated text if different, otherwise original
            if translated and translated.strip() and translated != clean_text:
                logger.debug(f"Translated: '{clean_text[:50]}...' -> '{translated[:50]}...'")
                return translated.strip()
            else:
                return text
                
        except Exception as e:
            logger.warning(f"Translation failed for text '{text[:50]}...': {e}")
            return text  # Return original text on error
    
    def translate_dict_fields(self, data: dict, fields_to_translate: list) -> dict:
        """
        Translate specific fields in a dictionary
        
        Args:
            data: Dictionary containing data to translate
            fields_to_translate: List of field names to translate
        
        Returns:
            Dictionary with translated fields
        """
        if not self.enabled:
            return data
        
        result = data.copy()
        
        for field in fields_to_translate:
            if field in result and result[field]:
                original = result[field]
                if isinstance(original, str) and original.strip():
                    translated = self.translate(original)
                    if translated != original:
                        result[field] = translated
                        logger.debug(f"Translated field '{field}': {original[:50]}... -> {translated[:50]}...")
        
        return result


# Global translator instance
_translator_instance = None

def get_translator() -> TextTranslator:
    """Get or create the global translator instance"""
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = TextTranslator()
    return _translator_instance

