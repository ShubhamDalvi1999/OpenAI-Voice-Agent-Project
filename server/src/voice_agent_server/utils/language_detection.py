"""
Language detection utilities for the voice agent server.
Provides functions to detect user language and map to appropriate voice settings.
"""

import re
from typing import Dict, Optional
from ..core.config import ServerConfig

# Language detection patterns
LANGUAGE_PATTERNS = {
    "es": re.compile(r'\b(el|la|de|que|y|en|un|es|se|no|te|lo|le|da|su|por|son|con|para|al|del|los|las|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|aplicación|trabajo|empresa|posición|ingeniero|desarrollador|software|solicitud|agregar|actualizar|estado|nota|seguimiento)\b', re.IGNORECASE),
    "fr": re.compile(r'\b(le|la|de|et|que|en|un|est|se|ne|te|du|des|sur|pour|avec|par|dans|les|une|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|candidature|travail|entreprise|poste|ingénieur|développeur|logiciel|ajouter|mettre|état|note|suivi)\b', re.IGNORECASE),
    "de": re.compile(r'\b(der|die|das|und|oder|in|auf|mit|von|zu|für|bei|nach|über|unter|durch|gegen|ohne|um|an|am|im|zum|zur|ein|eine|einen|einem|einer|eines|bewerbung|arbeit|unternehmen|position|ingenieur|entwickler|software|hinzufügen|aktualisieren|status|notiz|verfolgung)\b', re.IGNORECASE),
    "en": re.compile(r'\b(the|and|or|in|on|at|to|for|of|with|by|from|up|about|into|through|during|before|after|above|below|between|among|under|over|around|near|far|here|there|where|when|why|how|what|who|which|that|this|these|those|a|an|is|are|was|were|be|been|being|have|has|had|do|does|did|will|would|could|should|may|might|must|can|shall|application|job|company|position|engineer|developer|software|add|update|status|note|track)\b', re.IGNORECASE)
}

# Language-specific success messages
LANGUAGE_MESSAGES = {
    "en": {
        "application_added": "I've added your application for {role_title} at {company}",
        "status_updated": "Status updated to {status} for {company} {role_title}",
        "note_added": "Note added for {company} {role_title}",
        "followup_scheduled": "Follow-up scheduled for {company} on {date}",
        "applications_found": "Found {count} applications matching your criteria",
        "pipeline_summary": "Here's your job application pipeline summary"
    },
    "es": {
        "application_added": "He agregado tu solicitud para {role_title} en {company}",
        "status_updated": "Estado actualizado a {status} para {company} {role_title}",
        "note_added": "Nota agregada para {company} {role_title}",
        "followup_scheduled": "Seguimiento programado para {company} el {date}",
        "applications_found": "Se encontraron {count} solicitudes que coinciden con tus criterios",
        "pipeline_summary": "Aquí está el resumen de tu pipeline de solicitudes de trabajo"
    },
    "fr": {
        "application_added": "J'ai ajouté votre candidature pour {role_title} chez {company}",
        "status_updated": "Statut mis à jour à {status} pour {company} {role_title}",
        "note_added": "Note ajoutée pour {company} {role_title}",
        "followup_scheduled": "Suivi programmé pour {company} le {date}",
        "applications_found": "Trouvé {count} candidatures correspondant à vos critères",
        "pipeline_summary": "Voici le résumé de votre pipeline de candidatures"
    },
    "de": {
        "application_added": "Ich habe Ihre Bewerbung für {role_title} bei {company} hinzugefügt",
        "status_updated": "Status aktualisiert auf {status} für {company} {role_title}",
        "note_added": "Notiz hinzugefügt für {company} {role_title}",
        "followup_scheduled": "Nachfassung geplant für {company} am {date}",
        "applications_found": "Gefunden {count} Bewerbungen, die Ihren Kriterien entsprechen",
        "pipeline_summary": "Hier ist die Zusammenfassung Ihres Bewerbungspipelines"
    }
}

def detect_language(text: str) -> str:
    """
    Detect the language of the input text based on common words and patterns.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Language code (en, es, fr, de) or 'en' as default
    """
    if not text or not isinstance(text, str):
        return "en"
    
    # Count matches for each language
    language_scores = {}
    
    for lang_code, pattern in LANGUAGE_PATTERNS.items():
        matches = pattern.findall(text)
        language_scores[lang_code] = len(matches)
    
    # Return the language with the highest score, or English as default
    if language_scores:
        detected_language = max(language_scores, key=language_scores.get)
        # Only return detected language if it has at least 2 matches
        if language_scores[detected_language] >= 2:
            return detected_language
    
    return "en"

def get_voice_for_language(language: str, config: Optional[ServerConfig] = None) -> str:
    """
    Get the appropriate voice for the given language.
    
    Args:
        language: Language code (en, es, fr, de)
        config: Server configuration (optional)
        
    Returns:
        Voice name for the language
    """
    if config:
        return config.voice_language_mapping.get(language, config.default_voice)
    
    # Default voice mapping
    default_voices = {
        "en": "alloy",
        "es": "nova",
        "fr": "echo", 
        "de": "onyx"
    }
    
    return default_voices.get(language, "alloy")

def get_localized_message(language: str, message_key: str, **kwargs) -> str:
    """
    Get a localized message for the given language and message key.
    
    Args:
        language: Language code (en, es, fr, de)
        message_key: Key for the message type
        **kwargs: Format parameters for the message
        
    Returns:
        Localized message string
    """
    messages = LANGUAGE_MESSAGES.get(language, LANGUAGE_MESSAGES["en"])
    message_template = messages.get(message_key, messages.get("application_added", "Message not found"))
    
    try:
        return message_template.format(**kwargs)
    except KeyError:
        # If formatting fails, return the template as-is
        return message_template

def is_language_supported(language: str, config: Optional[ServerConfig] = None) -> bool:
    """
    Check if a language is supported by the system.
    
    Args:
        language: Language code to check
        config: Server configuration (optional)
        
    Returns:
        True if language is supported, False otherwise
    """
    if config:
        return language in config.supported_languages
    
    # Default supported languages
    return language in ["en", "es", "fr", "de"]

def get_supported_languages(config: Optional[ServerConfig] = None) -> list:
    """
    Get list of supported languages.
    
    Args:
        config: Server configuration (optional)
        
    Returns:
        List of supported language codes
    """
    if config:
        return config.supported_languages
    
    return ["en", "es", "fr", "de"]
