# LM Studio + Cursor Quick Setup

## ✅ Verified Status

- ✅ **LM Studio Server**: Running at `http://localhost:1234`
- ✅ **Available Models Detected**:
  - `ai models/llama/deepseek-coder-v2-lite-instruct-q4_k_m.gguf`
  - `ai models/llama/meta-llama-3-8b-instruct-q4_k_m.gguf`
  - `text-embedding-nomic-embed-text-v1.5`

## 🚀 Quick Setup (2 Minutes)

### Step 1: Open Cursor Settings
Press: **`Cmd+Shift+J`** (Mac) or **`Ctrl+Shift+J`** (Windows/Linux)

### Step 2: Add Custom Model
1. In Settings sidebar, find **"Models"** or **"AI Models"** section
2. Click **"Add Model"** or **"Custom Model"**

### Step 3: Enter Configuration
Fill in these exact values:

| Field | Value |
|-------|-------|
| **Model Name** | `LM Studio Local` |
| **OpenAI API Key** | `lmstudio` (or any placeholder) |
| **Override OpenAI Base URL** | `http://localhost:1234/v1` |
| **Model ID** | `ai models/llama/meta-llama-3-8b-instruct-q4_k_m.gguf` |

**Alternative Model IDs:**
- `ai models/llama/deepseek-coder-v2-lite-instruct-q4_k_m.gguf` (Better for coding)
- `text-embedding-nomic-embed-text-v1.5` (For embeddings)

### Step 4: Save & Verify
1. Click **"Save and Verify"**
2. You should see: ✅ **Connection successful**
3. If not, ensure LM Studio server is running

### Step 5: Restart Cursor
- **Close Cursor completely**
- **Reopen Cursor**
- This applies the model configuration

### Step 6: Select the Model
1. Open Cursor chat (click chat icon or press `Cmd+L` / `Ctrl+L`)
2. In the model selector dropdown (top of chat panel)
3. Select **"LM Studio Local"**
4. Start chatting!

## 🧪 Test Connection

Verify LM Studio is working:

```bash
# Test API endpoint
curl http://localhost:1234/v1/models

# Test chat (replace model ID with yours)
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ai models/llama/meta-llama-3-8b-instruct-q4_k_m.gguf",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 50
  }'
```

## ⚠️ Troubleshooting

### "Connection Failed"
- ✅ Ensure LM Studio is running
- ✅ Check server is started: LM Studio → Developer tab → "Start Server"
- ✅ Verify port is `1234` (check LM Studio settings)

### "Model Not Found"
- ✅ Make sure you've loaded a model in LM Studio
- ✅ Use the exact model ID from `curl http://localhost:1234/v1/models`
- ✅ Model must be loaded in LM Studio's Chat tab

### "API Key Error"
- ✅ Use any placeholder value like `lmstudio` or `local`
- ✅ LM Studio doesn't require authentication
- ✅ Cursor just needs a value in that field

### Slow Responses
- ✅ Normal for local LLMs
- ✅ Consider using a smaller quantized model (Q4_K_M or Q3_K_M)
- ✅ Close other applications to free up RAM/VRAM

## 📋 Model Comparison

| Model | Best For | Size |
|-------|----------|------|
| `deepseek-coder-v2-lite-instruct-q4_k_m` | **Coding tasks** | ~2.5GB |
| `meta-llama-3-8b-instruct-q4_k_m` | **General purpose** | ~4.7GB |

**Recommendation**: Use `deepseek-coder-v2-lite` for coding assistance in Cursor.

## 💡 Pro Tips

1. **Keep LM Studio Running**: Server must stay active when using the model
2. **Model Selection**: Switch models in Cursor without restart if both are loaded in LM Studio
3. **Resource Usage**: Monitor RAM/VRAM usage - local models are memory-intensive
4. **Multiple Models**: You can add multiple models to Cursor and switch between them

## ✅ Checklist

Before using:
- [ ] LM Studio is open and running
- [ ] Server is started (Developer tab → Start Server)
- [ ] At least one model is loaded in LM Studio
- [ ] Model configured in Cursor Settings
- [ ] Connection verified successfully
- [ ] Cursor restarted
- [ ] Model selected in chat dropdown

## 🎯 You're Done!

Your local LLM is now configured in Cursor. Use it just like any other AI model, but everything runs locally on your machine for privacy and offline use.

