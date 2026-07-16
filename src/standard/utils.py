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