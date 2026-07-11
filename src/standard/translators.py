"""Translation engines: Google Translate and Niutrans."""

import httpx
from deep_translator import GoogleTranslator

from openai import OpenAI


def google_translate(text: str, source: str, target: str) -> str:
    """Translate text using Google Translate.

    Args:
        text: Text to translate.
        source: Source language code.
        target: Target language code.

    Returns:
        Translated text.
    """
    translator = GoogleTranslator(source=source, target=target)

    # Handle long texts by chunking (Google has ~5000 char limit)
    if len(text) > 4500:
        chunks = _split_text(text, max_len=4500)
        return " ".join(translator.translate(chunk) for chunk in chunks)

    return translator.translate(text)


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

def _split_text(text: str, max_len: int = 4500) -> list[str]:
    """Split text into chunks at sentence boundaries."""
    import re
    sentences = re.split(r'(?<=[.!?。！？])\s+', text)
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 > max_len:
            if current:
                chunks.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()

    if current:
        chunks.append(current)

    return chunks if chunks else [text]
