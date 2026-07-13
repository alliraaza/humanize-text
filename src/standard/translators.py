"""Translation engines: LLM Translate and Libre."""

import httpx
from deep_translator import GoogleTranslator

from openai import OpenAI


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

def llm_translate(text: str, source: str, target: str, base_url: str, model: str,temperature: str,timeout:str,top_p:str,top_k:str, max_tokens:str) -> str:

    # changed the Niutrans translation function to use llm translation to avoid api calls
    client = OpenAI(
         base_url=base_url,
         api_key="ollama",
         timeout=timeout,
        )

    prompt = f"""
    Translate the following text from {source} to {target}.
    Return only the translated text.
    
    {text}
    """
    response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            top_p=top_p,
            # max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

    return response.choices[0].message.content.strip()

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

import re

def _split_text(text: str, max_len: int = 4000) -> list[str]:
    """
    Split text into chunks at natural paragraph/sentence boundaries,
    ensuring no chunk exceeds max_len while preserving line breaks.
    """
    if not text or len(text) <= max_len:
        return [text]

    chunks = []

    # 1. First attempt splitting on double newlines (paragraphs)
    paragraphs = text.split("\n\n")
    current_chunk = ""

    for para in paragraphs:
        # If adding this paragraph fits in current chunk
        if len(current_chunk) + len(para) + 2 <= max_len:
            current_chunk = f"{current_chunk}\n\n{para}".strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)

            # If a single paragraph itself is over max_len, split it by sentences
            if len(para) > max_len:
                sub_chunks = _split_paragraph_by_sentences(para, max_len)
                chunks.extend(sub_chunks[:-1])
                current_chunk = sub_chunks[-1]
            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def _split_paragraph_by_sentences(paragraph: str, max_len: int) -> list[str]:
    """Helper: Splits an oversized paragraph by sentence punctuation or hard slices."""
    # Split by standard end-of-sentence punctuation while keeping original space
    sentences = re.split(r'(?<=[.!?。！？])\s+', paragraph)
    chunks = []
    current = ""

    for sentence in sentences:
        # Hard fallback: single sentence exceeds max_len -> hard slice it
        if len(sentence) > max_len:
            if current:
                chunks.append(current)
                current = ""
            for i in range(0, len(sentence), max_len):
                chunks.append(sentence[i : i + max_len])
            continue

        if len(current) + len(sentence) + 1 > max_len:
            if current:
                chunks.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip() if current else sentence

    if current:
        chunks.append(current)

    return chunks