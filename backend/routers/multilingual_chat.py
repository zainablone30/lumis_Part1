# backend/routers/multilingual_chat.py
from fastapi import APIRouter, UploadFile, File
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../multilingual"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../llm_core"))

from asr_multilingual import MultilingualASR
from translation_service import TranslationService
from tts_multilingual import MultilingualTTS
from language_detector import LanguageDetector
from llm_engine import LumisLLMEngine

router = APIRouter(prefix="/multilingual", tags=["Multilingual"])

asr = MultilingualASR()
translator = TranslationService()
tts = MultilingualTTS()
lang_detector = LanguageDetector()
engines = {}


def get_engine(user_id, user_name):
    if user_id not in engines:
        engines[user_id] = LumisLLMEngine(user_id=user_id, user_name=user_name)
    return engines[user_id]


@router.post("/voice_chat")
async def multilingual_voice_chat(
    user_id: str, user_name: str, detected_emotion: str, audio: UploadFile = File(...)
):
    temp_path = f"/tmp/{audio.filename}"
    with open(temp_path, "wb") as f:
        f.write(await audio.read())

    asr_result = asr.transcribe(temp_path)
    user_lang = lang_detector.resolve(asr_result["language"], asr_result["text"])

    # Translate to English for the fine-tuned LLM
    english_input = translator.translate(asr_result["text"], user_lang, "en")

    engine = get_engine(user_id, user_name)
    llm_result = engine.chat(english_input, detected_emotion)

    # Translate reply back to the user's language
    localized_reply = translator.translate(llm_result["reply"], "en", user_lang)

    out_audio = f"/tmp/lumis_reply_{user_id}.wav"
    tts.synthesize(localized_reply, user_lang, out_audio)

    return {
        "detected_language": user_lang,
        "transcribed_text": asr_result["text"],
        "reply_text": localized_reply,
        "reply_audio_path": out_audio,
        "crisis_flag": llm_result["crisis_flag"],
    }