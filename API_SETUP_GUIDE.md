# API Setup Guide for LightRAG Agent

This guide explains what API keys you need to set up before running the LightRAG Agent application.

## Required API Keys

### 1. OpenAI API Key (REQUIRED) ⭐
**Purpose**: Core LLM functionality and text embeddings for LightRAG
**Used for**: 
- Text generation and chat responses
- Document embedding generation
- LightRAG knowledge graph construction
- Query processing and response generation

**How to get it**:
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to "API Keys" in your account settings
4. Click "Create new secret key"
5. Copy the key (starts with `sk-...`)

**Pricing**: Pay-per-use based on tokens consumed
- GPT-4o-mini: ~$0.00015-0.0006 per 1K tokens (much cheaper!)
- Text embeddings (v3-small): ~$0.00002 per 1K tokens

> **Note**: This is the ONLY API key you need for the LightRAG application to work!

## Already Configured (No Action Needed)

### 2. Anthropic API Key ✅
**Status**: Already configured in your TaskMaster MCP server
**Used for**: TaskMaster operations (not needed for LightRAG)

### 3. Perplexity API Key ✅
**Status**: Already configured in your TaskMaster MCP server  
**Used for**: TaskMaster research features (not needed for LightRAG)

## Environment Configuration

### Backend Environment Variables
Create a `.env` file in the `backend/` directory with the following:

```env
# REQUIRED - OpenAI Configuration (ONLY thing you need!)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Recommended settings (can customize)
OPENAI_MODEL=gpt-4o-mini             # Fast, cheap, excellent performance (recommended)
OPENAI_EMBEDDING_MODEL=text-embedding-3-small  # Latest embedding model
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.7

# Database Configuration (defaults work with Docker)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
REDIS_URL=redis://localhost:6379

# LightRAG Configuration (matches OpenAI settings)
LIGHTRAG_WORKING_DIR=./lightrag_data
LIGHTRAG_MODEL=gpt-4o-mini
LIGHTRAG_EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Application Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

> **Note**: You don't need Anthropic or Perplexity keys here since they're already configured in your TaskMaster MCP server!

### Frontend Environment Variables
Create a `.env.local` file in the `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## API Key Security Best Practices

### 1. Keep Keys Secure
- **Never commit API keys to version control**
- Store them in `.env` files (already in `.gitignore`)
- Use environment variables in production
- Rotate keys periodically

### 2. Cost Management
- Set usage limits in your OpenAI dashboard
- Monitor token consumption regularly
- Consider using GPT-3.5-turbo for development to reduce costs
- Use smaller embedding models if budget is a concern

### 3. Rate Limiting
- OpenAI has rate limits based on your tier
- Start with lower-tier models during development
- Upgrade as needed for production use

## Testing Your Setup

### 1. Verify OpenAI API Key
```bash
# Test your OpenAI API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer sk-your-api-key-here"
```

### 2. Start the Application
```bash
# Backend (from project root)
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend (from project root)
cd frontend
npm run dev
```

### 3. Check Health Endpoint
Visit: http://localhost:8000/health

Should return:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "lightrag-agent",
  "environment": "development"
}
```

## Common Issues & Solutions

### Issue: "Invalid API Key" Error
**Solution**: 
- Verify the API key is correct
- Check there are no extra spaces
- Ensure the key has the correct permissions

### Issue: "Rate limit exceeded"
**Solution**:
- Wait for the rate limit window to reset
- Consider upgrading your OpenAI plan
- Implement request batching in your application

### Issue: High API Costs
**Solutions**:
- Use `gpt-3.5-turbo` instead of `gpt-4` for development
- Reduce `CHUNK_SIZE` to process smaller text chunks
- Lower `OPENAI_MAX_TOKENS` to limit response length
- Cache responses where possible

## Cost Estimation

For a typical development session (processing a few documents, testing chat):
- **OpenAI GPT-4o-mini**: $0.10-0.50 for most development sessions
- **OpenAI GPT-4o**: $1-5 for the same usage (if you want premium quality)
- **Text Embeddings (v3-small)**: $0.02-0.20 depending on document size

## Production Recommendations

1. **Use GPT-4o for production** - best quality responses
2. **Use GPT-4o-mini for development** - excellent quality, fast, and very cheap
3. **Set up monitoring** - track API usage and costs
4. **Implement caching** - reduce redundant API calls
5. **Use environment variables** - never hardcode keys

## Quick Start Checklist

- [ ] Get OpenAI API key from https://platform.openai.com/
- [ ] Create `backend/.env` file with ONLY your OpenAI API key (that's it!)
- [ ] Create `frontend/.env.local` file with API URLs
- [ ] Test API key with a simple curl request
- [ ] Start the backend and verify health endpoint
- [ ] Start the frontend and test the connection
- [ ] Upload a test document to verify the full pipeline

**Remember**: You already have Anthropic/Perplexity keys in TaskMaster - no need to add them again!

## Support

If you encounter issues:
1. Check the application logs for specific error messages
2. Verify your API keys are valid and have sufficient credits
3. Ensure all environment variables are properly set
4. Check the backend health endpoint responds correctly

---

**Remember**: Keep your API keys secure and never share them publicly! 