"""Translation engines: LLM Translate and Libre."""

import httpx
from deep_translator import GoogleTranslator

from .utils import _split_text

def google_translate(text: str, source: str, target: str) -> str:
    translator = GoogleTranslator(source=source, target=target)
    # 1. Quick check: Translate immediately if under character limit
    if len(text) <= 4500:
        return translator.translate(text)

    # 2. Split large text into chunks
    chunks = _split_text(text, max_len=4500)
    translated_chunks = []

    for chunk in chunks:
        # Skip empty or whitespace-only chunks
        if not chunk.strip():
            translated_chunks.append(chunk)
            continue

        try:
            translated_text = translator.translate(chunk)
            translated_chunks.append(translated_text)

            # Small delay to prevent Google Translate rate limits/IP blocks
            time.sleep(0.3)

        except Exception as e:
            print(f"⚠️ Translation error on chunk: {e}")
            # Fall back to original chunk on error to prevent total failure
            translated_chunks.append(chunk)

    # 3. Join chunks (adjust delimiter based on how _split_text works, e.g., "\n" or "")
    return "\n".join(translated_chunks)

import requests
def libre_translate(text: str, source: str, target: str, libre_url:str) -> str:
    """Translate text using Libre Translate local.

    Args:
        text: Text to translate.
        source: Source language code.
        target: Target language code.

    Returns:
        Translated text.
    """

    try:
        r = requests.post(
            libre_url,
            json={
                "q": text,
                "source": source,
                "target": target,
                "format": "text"
            }
        )
        return r.json()["translatedText"]
    except:
        return text   # fallback

# def _split_text(text: str, max_len: int = 4500) -> list[str]:
#     """Split text into chunks at sentence boundaries."""
#     import re
#     sentences = re.split(r'(?<=[.!?。！？])\s+', text)
#     chunks = []
#     current = ""
#
#     for sentence in sentences:
#         if len(current) + len(sentence) + 1 > max_len:
#             if current:
#                 chunks.append(current)
#             current = sentence
#         else:
#             current = f"{current} {sentence}".strip()
#
#     if current:
#         chunks.append(current)
#
#     return chunks if chunks else [text]

