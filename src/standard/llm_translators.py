import time
import ollama
from rich.console import Console
import openai
from openai import OpenAI
from ollama import Client
from .utils import _split_text

class LLMTranslator:
    def __init__(self):
        # 1. Map string flags directly to the method references
        self._dispatch_map = {
            "ollama": self.translate_with_ollama,
            "openrouter": self.llm_translate,
            "deepseek": self.llm_translate,
        }
    def translate(self, text: str, flag: str, source: str, target: str, base_url: str, model: str,temperature: str,timeout:str,top_p:str,top_k:str, max_tokens:str,api_key: str) -> str:
        # 2. Retrieve the method using the flag.
        # Use .get() to provide a fallback/default method if the flag doesn't exist.
        method = self._dispatch_map.get(flag)

        if not method:
            raise ValueError(f"Unknown flag: '{flag}'. Valid options are: {list(self._dispatch_map.keys())}")

        # 3. Call the selected method and pass the arguments
        return method(text,source,target,base_url,model,temperature,timeout,top_p,top_k,max_tokens,api_key)

    def translate_with_ollama(self,text: str, source: str, target: str, base_url: str, model: str,temperature: str,timeout:str,top_p:str,top_k:str, max_tokens:str,api_key: str) -> str:
        base_url = base_url.removesuffix("/v1")
        console = Console()
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

    def llm_translate(self,text: str, source: str, target: str, base_url: str, model: str,temperature: str,timeout:str,top_p:str,top_k:str, max_tokens:str,api_key: str) -> str:

        # changed the Niutrans translation function to use llm translation to avoid api calls
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
        )

        # prompt = f"""
        # Translate the following text from {source} to {target}.
        # Return only the translated text.
        #
        # {text}
        # """

        prompt = f"""
        Task: Act as a professional human translator. 
        Instructions: Translate the following source text accurately into fluent, natural, and idiomatic from {source} to {target}. 
        Maintain the original tone and context perfectly. Do not include any meta-commentary, explanations, or introductory text. Return ONLY the final translated text.
        
        Source Text to Translate:
        \"\"\"
        {text}
        \"\"\"
        """

        max_retries = 3
        backoff_delay = 2.0

        for attempt in range(max_retries + 1):
            try:
                # Your original code block
                response = client.chat.completions.create(
                    model=model,
                    temperature=temperature,
                    top_p=top_p,
                    # max_tokens=max_tokens,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                # Break out of retry loop on success
                break

            except openai.RateLimitError as e:
                # Explicitly handles 429 errors
                if attempt == max_retries:
                    print(f"Rate limit exceeded. Max retries reached. Error: {e}")
                    return ""

                print(f"Rate limited (429). Retrying in {backoff_delay} seconds...")
                time.sleep(backoff_delay)
                backoff_delay *= 2  # Exponential backoff (2s, 4s, 8s...)

            except openai.BadRequestError as e:
                # Explicitly handles 400 errors (Wrong model names, bad formatting)
                print(f"Bad Request Error (400): {e.message}")
                print("Check your model string variable or message payload structure.")
                return ""

            except openai.APIConnectionError as e:
                # Handles network drops / DNS issues
                print(f"Network Connection Error: Failed to connect to server. {e}")
                if attempt == max_retries:
                    return ""
                time.sleep(1)

            except openai.APIStatusError as e:
                # Catch-all for other non-200 HTTP statuses (401 Unauthorized, 500 Server Error)
                print(f"API Status Error ({e.status_code}): {e.message}")
                return ""

            except Exception as e:
                # Absolute fallback safety net
                print(f"Unexpected non-API error occurred: {e}")
                return ""
        # Extract the message object safely
        message = response.choices[0].message

        # 1. Check if the model refused to answer due to safety filters
        if hasattr(message, 'refusal') and message.refusal:
            raise ValueError(f"Translation refused by model: {message.refusal}")

        # 2. Extract content safely with a fallback if it evaluates to None
        raw_content = message.content
        # print(f"raw_content: {raw_content}")
        if raw_content is None:
            # Option A: Return a fallback empty string
            return ""
            # Option B: Or raise a clean error so your application knows the translation failed
            # raise RuntimeError("LLM returned an empty or invalid response body.")

        return raw_content.strip()
        # return response.choices[0].message.content.strip()