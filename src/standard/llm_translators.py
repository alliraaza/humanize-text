import time
import ollama
from rich.console import Console
from ollama import Client
from .utils import _split_text
console = Console()
def translate_with_ollama(text: str, source: str, target: str, base_url: str, model: str,temperature: str,timeout:str,top_p:str,top_k:str, max_tokens:str) -> str:

    """Translates large text using a local Ollama model with chunking and progress logging."""
    client = Client(host=base_url, timeout=timeout)

    # 1. Split text into larger, natural chunks (e.g., max 10,000 characters)
    # Using the paragraph/sentence split function discussed earlier
    chunks = _split_text(text, max_len=10000)
    translated_chunks = []

    # console.print(f"\n🤖 [bold blue]Ollama translation started.[/bold blue]")

    # 2. Open a dynamic progress status spinner
    # with console.status("[bold yellow]Model thinking...[/bold yellow]", spinner="dots") as status:
    for idx, chunk in enumerate(chunks):
        if not chunk.strip():
            translated_chunks.append(chunk)
            continue

        # status.update(f"[bold cyan]⚙️ Translating chunk {idx+1}/{len(chunks)}...[/bold cyan]")

        # System prompt ensures the model acts strictly as a translator
        system_prompt = (
            f"You are a professional translator. Translate the following text from {source} into fluent {target}. "
            "Preserve all original paragraph structures, formatting, lines breaks, and markdown characters. "
            "Do NOT add any commentary, notes, or explanations before or after the translation. "
            "Return ONLY the direct translation."
        )

        try:
            response = client.generate(
                model=model,
                system=system_prompt,
                prompt=chunk,
                options={"temperature": temperature,"top_p":top_p,"top_k":top_k,"num_ctx": max_tokens} # Low temperature keeps it precise
            )

            translated_chunks.append(response['response'].strip())
            # console.log(f"✔️ Chunk {idx+1}/{len(chunks)} processed successfully.")

        except Exception as e:
            console.log(f"❌ Error on chunk {idx+1}: {e}")
            # Append original chunk as fallback instead of crashing the whole pipeline
            translated_chunks.append(chunk)

    # console.print("\n📋 [bold green]ollama translation completed successfully![/bold green]")
    return "\n\n".join(translated_chunks)