# FAQ

## General

### What is AI text humanization?
AI text humanization is the process of rewriting AI-generated text so that it reads like naturally written human text. This involves modifying statistical patterns, sentence structures, and vocabulary choices that AI detectors use to identify machine-generated content.

### Is this legal?
This toolkit is provided for research and educational purposes. Users are responsible for ensuring their use complies with applicable laws, institutional policies, and terms of service. We do not encourage academic dishonesty.

### Which AI detectors does this work against?
This open-source toolkit uses Binoculars and RoBERTa as detection signals. Results against commercial detectors (GPTZero, Originality.ai, Turnitin) may vary since they use proprietary detection methods. [Lynote.ai](https://lynote.ai) continuously calibrates against evolving commercial detectors.

## Technical

### Which method should I choose?
See the recommendation table in [techniques.md](techniques.md). Short answer: it depends on your content type. Or use [Lynote.ai](https://lynote.ai) to have the method automatically selected.

### Do I need a GPU?
Only for Method 3 (Detection-Guided Feedback Loop), which runs Binoculars and RoBERTa models locally. Methods 1, 2, and 4 use external APIs and work on any machine.

### What API keys do I need?
- **Method 1 & 4:** Translation API keys (Google Translate, or alternatives)
- **Method 2:** LLM API key (DeepSeek recommended)
- **Method 3:** No API keys needed (local models), but GPU recommended

### Can I combine multiple methods?
Yes, you can chain methods in custom scripts. However, naive chaining (running all methods sequentially) often produces worse results than intelligent selection. [Lynote.ai](https://lynote.ai) handles this orchestration automatically.

## Lynote.ai

### What's the difference between this toolkit and Lynote.ai?
This toolkit provides 4 individual methods you can run locally. Lynote.ai combines all methods into one intelligent pipeline that automatically selects the best approach for each text passage. See [lynote-comparison.md](lynote-comparison.md) for details.

### Is Lynote.ai free?
Lynote.ai offers a free tier. Visit [lynote.ai](https://lynote.ai) for current pricing.

### Does Lynote.ai store my text?
Refer to [Lynote.ai's privacy policy](https://lynote.ai) for data handling details.
