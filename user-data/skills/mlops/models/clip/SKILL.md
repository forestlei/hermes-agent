---
name: clip
description: >
  ML Model Usage Guides — CLIP (vision-language), Whisper (speech recognition), 
  Stable Diffusion (image generation). Zero-shot classification, transcription, 
  and text-to-image with model-specific best practices.
  Covers CLIP, Whisper, and Stable Diffusion models with installation, usage patterns, 
  and integration examples.
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [transformers, torch, pillow]
metadata:
  hermes:
    tags: [Multimodal, CLIP, Vision-Language, Zero-Shot, Image Classification, OpenAI, Image Search, Cross-Modal Retrieval, Content Moderation, Whisper, Speech Recognition, ASR, Transcription, Stable Diffusion, Text-to-Image, Image Generation]

---

# ML Model Usage Guides — CLIP · Whisper · Stable Diffusion

This skill covers three foundational ML models for multimodal AI: vision-language (CLIP), speech recognition (Whisper), and image generation (Stable Diffusion). Each section provides installation, usage patterns, and integration examples.

---

## CLIP - Contrastive Language-Image Pre-Training

OpenAI's model that understands images from natural language.

## When to use CLIP

**Use when:**
- Zero-shot image classification (no training data needed)
- Image-text similarity/matching
- Semantic image search
- Content moderation (detect NSFW, violence)
- Visual question answering
- Cross-modal retrieval (image→text, text→image)

**Metrics**:
- **25,300+ GitHub stars**
- Trained on 400M image-text pairs
- Matches ResNet-50 on ImageNet (zero-shot)
- MIT License

**Use alternatives instead**:
- **BLIP-2**: Better captioning
- **LLaVA**: Vision-language chat
- **Segment Anything**: Image segmentation

## Quick start

### Installation

```bash
pip install git+https://github.com/openai/CLIP.git
pip install torch torchvision ftfy regex tqdm
```

### Zero-shot classification

```python
import torch
import clip
from PIL import Image

# Load model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Load image
image = preprocess(Image.open("photo.jpg")).unsqueeze(0).to(device)

# Define possible labels
text = clip.tokenize(["a dog", "a cat", "a bird", "a car"]).to(device)

# Compute similarity
with torch.no_grad():
    image_features = model.encode_image(image)
    text_features = model.encode_text(text)

    # Cosine similarity
    logits_per_image, logits_per_text = model(image, text)
    probs = logits_per_image.softmax(dim=-1).cpu().numpy()

# Print results
labels = ["a dog", "a cat", "a bird", "a car"]
for label, prob in zip(labels, probs[0]):
    print(f"{label}: {prob:.2%}")
```

## Available models

```python
# Models (sorted by size)
models = [
    "RN50",           # ResNet-50
    "RN101",          # ResNet-101
    "ViT-B/32",       # Vision Transformer (recommended)
    "ViT-B/16",       # Better quality, slower
    "ViT-L/14",       # Best quality, slowest
]

model, preprocess = clip.load("ViT-B/32")
```

| Model | Parameters | Speed | Quality |
|-------|------------|-------|---------|
| RN50 | 102M | Fast | Good |
| ViT-B/32 | 151M | Medium | Better |
| ViT-L/14 | 428M | Slow | Best |

## Image-text similarity

```python
# Compute embeddings
image_features = model.encode_image(image)
text_features = model.encode_text(text)

# Normalize
image_features /= image_features.norm(dim=-1, keepdim=True)
text_features /= text_features.norm(dim=-1, keepdim=True)

# Cosine similarity
similarity = (image_features @ text_features.T).item()
print(f"Similarity: {similarity:.4f}")
```

## Semantic image search

```python
# Index images
image_paths = ["img1.jpg", "img2.jpg", "img3.jpg"]
image_embeddings = []

for img_path in image_paths:
    image = preprocess(Image.open(img_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = model.encode_image(image)
        embedding /= embedding.norm(dim=-1, keepdim=True)
    image_embeddings.append(embedding)

image_embeddings = torch.cat(image_embeddings)

# Search with text query
query = "a sunset over the ocean"
text_input = clip.tokenize([query]).to(device)
with torch.no_grad():
    text_embedding = model.encode_text(text_input)
    text_embedding /= text_embedding.norm(dim=-1, keepdim=True)

# Find most similar images
similarities = (text_embedding @ image_embeddings.T).squeeze(0)
top_k = similarities.topk(3)

for idx, score in zip(top_k.indices, top_k.values):
    print(f"{image_paths[idx]}: {score:.3f}")
```

## Content moderation

```python
# Define categories
categories = [
    "safe for work",
    "not safe for work",
    "violent content",
    "graphic content"
]

text = clip.tokenize(categories).to(device)

# Check image
with torch.no_grad():
    logits_per_image, _ = model(image, text)
    probs = logits_per_image.softmax(dim=-1)

# Get classification
max_idx = probs.argmax().item()
max_prob = probs[0, max_idx].item()

print(f"Category: {categories[max_idx]} ({max_prob:.2%})")
```

## Batch processing

```python
# Process multiple images
images = [preprocess(Image.open(f"img{i}.jpg")) for i in range(10)]
images = torch.stack(images).to(device)

with torch.no_grad():
    image_features = model.encode_image(images)
    image_features /= image_features.norm(dim=-1, keepdim=True)

# Batch text
texts = ["a dog", "a cat", "a bird"]
text_tokens = clip.tokenize(texts).to(device)

with torch.no_grad():
    text_features = model.encode_text(text_tokens)
    text_features /= text_features.norm(dim=-1, keepdim=True)

# Similarity matrix (10 images × 3 texts)
similarities = image_features @ text_features.T
print(similarities.shape)  # (10, 3)
```

## Integration with vector databases

```python
# Store CLIP embeddings in Chroma/FAISS
import chromadb

client = chromadb.Client()
collection = client.create_collection("image_embeddings")

# Add image embeddings
for img_path, embedding in zip(image_paths, image_embeddings):
    collection.add(
        embeddings=[embedding.cpu().numpy().tolist()],
        metadatas=[{"path": img_path}],
        ids=[img_path]
    )

# Query with text
query = "a sunset"
text_embedding = model.encode_text(clip.tokenize([query]))
results = collection.query(
    query_embeddings=[text_embedding.cpu().numpy().tolist()],
    n_results=5
)
```

## Best practices

1. **Use ViT-B/32 for most cases** - Good balance
2. **Normalize embeddings** - Required for cosine similarity
3. **Batch processing** - More efficient
4. **Cache embeddings** - Expensive to recompute
5. **Use descriptive labels** - Better zero-shot performance
6. **GPU recommended** - 10-50× faster
7. **Preprocess images** - Use provided preprocess function

## Performance

| Operation | CPU | GPU (V100) |
|-----------|-----|------------|
| Image encoding | ~200ms | ~20ms |
| Text encoding | ~50ms | ~5ms |
| Similarity compute | <1ms | <1ms |

## Limitations

1. **Not for fine-grained tasks** - Best for broad categories
2. **Requires descriptive text** - Vague labels perform poorly
3. **Biased on web data** - May have dataset biases
4. **No bounding boxes** - Whole image only
5. **Limited spatial understanding** - Position/counting weak

## Resources

- **GitHub**: https://github.com/openai/CLIP ⭐ 25,300+
- **Paper**: https://arxiv.org/abs/2103.00020
- **Colab**: https://colab.research.google.com/github/openai/clip/
## Whisper — Speech Recognition (reference)

OpenAI's Whisper for automatic speech recognition, transcription, and translation. Supports 99 languages with robust performance on noisy audio.

**Key capabilities:** transcription (any→same language), translation (any→English), language identification, voice activity detection.

**Models:** tiny (39M) → base (74M) → small (244M) → medium (769M) → large-v3 (1550M). Use `small` for most tasks; `large-v3` for best accuracy.

**Quick start:** `pip install openai-whisper` → `model = whisper.load_model("small")` → `result = model.transcribe("audio.mp3")`

**Full reference → `references/whisper.md`**

---

## Stable Diffusion — Image Generation (reference)

Latent diffusion model for text-to-image, image-to-image, inpainting, and upscaling. Runs locally with consumer GPUs (6GB+ VRAM).

**Key variants:** SD 1.5 (fast, 512×512), SD 2.1 (better quality, 768×768), SDXL (high quality, 1024×1024), Stable Cascade (multi-stage).

**Quick start:** `pip install diffusers transformers accelerate` → `from diffusers import StableDiffusionPipeline` → generate from text prompts.

**Full reference → `references/stable-diffusion.md`**

---

- **License**: MIT


