import boto3
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

translate_client = boto3.client('translate')
db_service = boto3.resource('dynamodb')
lang_table = db_service.Table("haptik-language-mapping")


def handle_message_translation(message, user_id, source):
    """
    Handles the translation logic
    """
    logger.info(f"[Language Helper]Source message is: {message}")

    target_lang = "en"
    if source == "user":
        is_switch_message = check_for_language_switching(message, user_id)
        logger.debug(
            f"[Language Helper] is switch message is {is_switch_message}")
        if is_switch_message:
            return message

    source_lang = get_preferred_language(user_id)
    logger.debug(f"[Language Helper] Source Language is {source_lang}")

    if source_lang == "en":
        return message

    if source == "agent":
        source_lang, target_lang = target_lang, source_lang
    return translate_message(message, source_lang, target_lang)


def check_for_language_switching(message: str, user_id: str):
    """
    Checks if user wants to switch language and updates preference in the DB
    Args:
        message: Message sent by user
        user_id: Id of the user
    """
    if "switch to" in message.lower():
        try:
            language = message.lower().split()[2]
        except Exception as e:
            logger.error(f"[Language Helper] Invalid switch intent: {e}")
            return
        logger.debug(
            f"[Language Helper] User : {user_id} wants to switch to {language}")
        lang_code = get_lang_code(language)
        logger.debug(
            f"[Language Helper] Language code for {language} is {lang_code}")
        update_lang_preference(user_id, lang_code)
        return True


def get_lang_code(language):
    """
    Returns the language code for a given language
    """
    language_mappings = {
        "afrikaans": "af",
        "albanian": "sq",
        "amharic": "am",
        "arabic": "ar",
        "armenian": "hy",
        "azerbaijani": "az",
        "bengali": "bn",
        "bosnian": "bs",
        "bulgarian": "bg",
        "catalan": "ca",
        "chinese": "zh",
        "croatian": "hr",
        "czech": "cs",
        "danish": "da",
        "dutch": "nl",
        "english": "en",
        "estonian": "et", 
        "farsi": "fa",
        "tagalog": "tl", 
        "finnish": "fi",
        "french": "fr",
        "georgian": "ka",
        "german": "de", 
        "greek": "el",
        "gujarati": "gu",
        "haitian Creole": "ht", 
        "hausa": "ha",
        "hebrew": "he", 
        "hindi": "hi",
        "hungarian": "hu", 
        "icelandic": "is",
        "indonesian": "id", 
        "italian": "it", 
        "japanese": "ja",
        "kannada": "kn",
        "kazakh": "kk",
        "korean": "ko", 
        "latvian": "lv", 
        "lithuanian": "lt",
        "macedonian": "mk",
        "malay": "ms",
        "malayalam": "ml", 
        "maltese": "mt",
        "mongolian": "mn",
        "norwegian": "no",
        "persian": "fa",
        "pashto": "ps",
        "polish": "pl", 
        "portuguese": "pt", 
        "romanian": "ro",
        "russian": "ru",
        "serbian": "sr", 
        "sinhala": "si",
        "slovak": "sk",
        "slovenian": "sl",
        "somali": "so", 
        "spanish": "es",
        "swahili": "sw",
        "swedish": "sv",
        "tagalog": "tl",
        "tamil": "ta",
        "telugu": "te",
        "thai": "th",
        "turkish": "tr",
        "ukrainian": "uk", 
        "urdu": "ur", 
        "uzbek": "uz", 
        "vietnamese": "vi", 
        "welsh": "cy",
        "chinese traditional": "zh-TW",
        "canadian french": "fr-CA", 
        "mexican spanish": "es-MX",
        "dari": "fa-AF"
    }
    return language_mappings.get(language, "en")


def update_lang_preference(user_id, lang_code):
    """
    Puts the user preference in the dynamodb
    """
    try:
        lang_table.put_item(Item={"user_id": user_id, "pref_lang": lang_code})
        logger.info(
            f"[Language Helper] Updated the preferred language for user: {user_id}")
    except Exception as e:
        logger.error(
            f"[Language Helper] Raised exception while updating lang_code:\n{e}")


def get_preferred_language(user_id):
    """
    Get's preferred language from DynamoDB
    """
    response = lang_table.get_item(Key={"user_id": user_id})
    logger.debug(
        f"[Language Helper] Response of get_item for user: {user_id} is\n{response}")
    if "Item" in response and response["Item"]:
        return response["Item"].get("pref_lang", "en")
    return "en"


def translate_message(message, source_lang, target_lang):
    """
    Translates the given message from source language to target language
    """
    return translate_client.translate_text(Text=message,
                                           SourceLanguageCode=source_lang,
                                           TargetLanguageCode=target_lang).get(
                                               "TranslatedText", message)


