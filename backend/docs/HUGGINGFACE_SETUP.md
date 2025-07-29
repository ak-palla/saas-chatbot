# Hugging Face Embeddings Setup Guide

## Overview

Phase 2 now uses **Hugging Face Sentence Transformers** instead of OpenAI embeddings. This provides:

- ✅ **No API costs** - Models run locally
- ✅ **No quota limits** - Unlimited usage
- ✅ **Better privacy** - Data stays on your machine
- ✅ **Multiple model options** - Choose the best model for your needs
- ✅ **Offline capability** - Works without internet after model download

## Quick Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `transformers==4.36.2` - Hugging Face transformers library
- `sentence-transformers==2.2.2` - Sentence embedding models
- `torch==2.1.2` - PyTorch backend
- `huggingface-hub==0.19.4` - Model hub integration

### 2. Get Hugging Face Token (Optional)

1. Go to https://huggingface.co/settings/tokens
2. Create a new token with 'read' permissions
3. Add to your `.env` file:

```env
HUGGINGFACE_API_TOKEN=hf_your_token_here
```

**Note:** Token is optional for public models, but recommended for faster downloads and access to gated models.

### 3. Update Vector Database

Run the updated SQL setup to handle 384D embeddings:

```bash
# Connect to your Supabase database and run:
psql -h your_supabase_host -U postgres -d postgres -f vector_setup.sql
```

## Available Models

The service supports multiple embedding models:

### 1. all-MiniLM-L6-v2 (Default) ⭐
- **Dimension:** 384
- **Speed:** Very Fast
- **Quality:** Good
- **Best for:** Most general use cases, development

### 2. all-mpnet-base-v2
- **Dimension:** 768  
- **Speed:** Medium
- **Quality:** High
- **Best for:** Production applications requiring high accuracy

### 3. all-MiniLM-L12-v2
- **Dimension:** 384
- **Speed:** Fast
- **Quality:** Better than L6
- **Best for:** Balance between speed and quality

## Configuration

### Environment Variables

Add to your `.env` file:

```env
# Hugging Face (Recommended)
HUGGINGFACE_API_TOKEN=hf_your_token_here

# OpenAI (Optional backup - will be deprecated)
OPENAI_API_KEY=your_openai_key_here
```

### Model Selection

The service automatically loads the default model (`all-MiniLM-L6-v2`) on startup. You can:

1. **Use default model** - No configuration needed
2. **Switch models at runtime** - Via API calls
3. **Set different model** - Modify `DEFAULT_MODEL` in `embedding_service.py`

## Hardware Requirements

### Minimum Requirements
- **RAM:** 2GB available
- **Storage:** 500MB for default model
- **CPU:** Any modern CPU (Intel/AMD)

### Recommended Requirements
- **RAM:** 4GB+ available
- **Storage:** 2GB+ for multiple models
- **GPU:** CUDA-compatible GPU (optional, for speed)

### GPU Support

If you have a CUDA-compatible GPU:

```bash
# Install CUDA-enabled PyTorch
pip install torch==2.1.2+cu118 -f https://download.pytorch.org/whl/torch_stable.html
```

The service will automatically detect and use GPU acceleration.

## Model Download & Caching

### First-Time Setup

When you first start the service:

1. **Default model downloads** automatically (~90MB)
2. **Models are cached** locally in `~/.cache/huggingface/`
3. **Subsequent starts** are instant (no download)

### Manual Model Download (Optional)

```python
from sentence_transformers import SentenceTransformer

# Pre-download models
SentenceTransformer('all-MiniLM-L6-v2')
SentenceTransformer('all-mpnet-base-v2')
```

## API Usage

### Basic Embedding Generation

```python
from app.services.embedding_service import embedding_service

# Generate single embedding
embedding = await embedding_service.generate_embedding("Hello world")
print(f"Embedding dimension: {len(embedding)}")  # 384

# Generate batch embeddings  
texts = ["Text 1", "Text 2", "Text 3"]
embeddings = await embedding_service.generate_embeddings_batch(texts)
print(f"Generated {len(embeddings)} embeddings")
```

### Model Information

```python
# Get current model info
info = embedding_service.get_model_info()
print(f"Current model: {info['model_name']}")
print(f"Dimension: {info['embedding_dimension']}")
print(f"Device: {info['device']}")
```

### Switch Models

```python
# Switch to higher quality model
success = embedding_service.switch_model('all-mpnet-base-v2')
if success:
    print("Switched to high-quality model")
```

## Testing

### Quick Test

```bash
cd backend
python -c "
from app.services.embedding_service import embedding_service
import asyncio

async def test():
    emb = await embedding_service.generate_embedding('test')
    print(f'✅ Generated {len(emb)}D embedding')
    print(f'Model: {embedding_service.current_model_name}')

asyncio.run(test())
"
```

### Full Test Suite

```bash
python test_phase2_complete.py
```

Should now show **100% success rate** with no quota errors!

## Troubleshooting

### Model Download Issues

**Problem:** Model download fails
**Solution:**
```bash
# Check internet connection
ping huggingface.co

# Clear cache and retry
rm -rf ~/.cache/huggingface/
```

### Memory Issues

**Problem:** Out of memory errors
**Solution:**
```python
# Use smaller model
embedding_service.switch_model('all-MiniLM-L6-v2')

# Or reduce batch size in document processing
```

### GPU Not Detected

**Problem:** CUDA available but not used
**Solution:**
```bash
# Check CUDA installation
python -c "import torch; print(torch.cuda.is_available())"

# Reinstall PyTorch with CUDA
pip install torch==2.1.2+cu118 -f https://download.pytorch.org/whl/torch_stable.html
```

### Slow Performance

**Problem:** Embeddings generation is slow
**Solutions:**
1. **Use GPU:** Install CUDA PyTorch
2. **Smaller model:** Switch to `all-MiniLM-L6-v2`
3. **Batch processing:** Process multiple texts together

## Migration from OpenAI

If you're migrating from OpenAI embeddings:

### 1. Existing Data
- **Old embeddings:** Will continue to work
- **New embeddings:** Will use HuggingFace (384D)
- **Mixed dimensions:** Handled automatically

### 2. Database Update
```sql
-- Update vector function for new dimension
-- Run vector_setup.sql to update functions
```

### 3. Environment Variables
```env
# Remove OpenAI dependency
# OPENAI_API_KEY=...  # Can remove

# Add HuggingFace
HUGGINGFACE_API_TOKEN=hf_your_token_here
```

## Performance Comparison

| Model | Dimension | Speed | Quality | Memory | Use Case |
|-------|-----------|--------|---------|---------|-----------|
| MiniLM-L6-v2 | 384 | ⚡⚡⚡ | ⭐⭐⭐ | 90MB | Development, Fast |
| MiniLM-L12-v2 | 384 | ⚡⚡ | ⭐⭐⭐⭐ | 120MB | Balanced |
| MPNet-base-v2 | 768 | ⚡ | ⭐⭐⭐⭐⭐ | 420MB | Production, High Quality |

## Benefits

### Cost Savings
- **OpenAI:** ~$0.0001 per 1K tokens = $10-100+ per month
- **HuggingFace:** $0 after initial setup ✅

### Performance
- **OpenAI:** Network latency + API limits
- **HuggingFace:** Local processing, unlimited usage ✅

### Privacy
- **OpenAI:** Data sent to external servers
- **HuggingFace:** Data stays on your machine ✅

### Reliability
- **OpenAI:** Subject to API outages and quota limits
- **HuggingFace:** Always available once installed ✅

## Next Steps

1. **Install dependencies:** `pip install -r requirements.txt`
2. **Add HF token:** Update your `.env` file
3. **Run tests:** `python test_phase2_complete.py`
4. **Start building:** Create knowledge-enabled chatbots!

Your Phase 2 implementation is now **cost-free and quota-unlimited**! 🎉