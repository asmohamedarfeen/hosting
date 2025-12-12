# LM Studio + Cursor Integration Guide

## ✅ Current Status

✅ **LM Studio Server**: Running at `http://localhost:1234`
✅ **Available Models**:
  - `ai models/llama/deepseek-coder-v2-lite-instruct-q4_k_m.gguf`
  - `ai models/llama/meta-llama-3-8b-instruct-q4_k_m.gguf`
  - `text-embedding-nomic-embed-text-v1.5`

## 📋 Configuration Methods

### Method 1: Configure via Cursor Settings UI (Recommended for AI Chat)

**Step 1: Open Cursor Settings**
- Press `Cmd+Shift+J` (Mac) or `Ctrl+Shift+J` (Windows/Linux)
- Or click the gear icon ⚙️ in the top right corner

**Step 2: Navigate to Models Section**
- In the Settings sidebar, find "Models" or "AI Models"
- Click on "Add Model" or "Custom Model"

**Step 3: Configure Local LLM**
- **Model Name**: Enter a name like "LM Studio Local" or the model name
- **OpenAI API Key**: Enter a placeholder value (e.g., `lmstudio` or `local`)
- **Override OpenAI Base URL**: Enter `http://localhost:1234/v1`
- **Model ID**: Enter one of your model IDs:
  - `ai models/llama/deepseek-coder-v2-lite-instruct-q4_k_m.gguf`
  - `ai models/llama/meta-llama-3-8b-instruct-q4_k_m.gguf`
  - `text-embedding-nomic-embed-text-v1.5`

**Step 4: Save and Verify**
- Click "Save and Verify" to test the connection
- You should see a success message if LM Studio is running

**Step 5: Select the Model**
- In Cursor's chat panel, open the model selector dropdown
- Select your configured "LM Studio Local" model
- Start using it for AI assistance!

### Method 2: Add to MCP Configuration (For Extended Features)

The MCP configuration has been updated to include LM Studio support. This allows Cursor to use LM Studio for extended tool capabilities.

## 🧪 Testing the Connection

You can verify LM Studio is working with:

```bash
# Test API endpoint
curl http://localhost:1234/v1/models

# Test chat completion
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ai models/llama/meta-llama-3-8b-instruct-q4_k_m.gguf",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7
  }'
```

## 🔧 Troubleshooting

### Issue: Connection Failed
- **Solution**: Ensure LM Studio is running and the server is started
- Check that the port is `1234` (can be changed in LM Studio settings)
- Verify in LM Studio: Developer tab → Server should show "Running"

### Issue: Model Not Found
- **Solution**: Make sure the model ID matches exactly what's in LM Studio
- Check available models with: `curl http://localhost:1234/v1/models`
- Use the exact model ID from the response

### Issue: API Key Error
- **Solution**: Use any placeholder value for the API key (e.g., `lmstudio`)
- LM Studio doesn't require authentication, but Cursor needs a value there

### Issue: Slow Responses
- **Solution**: This is normal for local LLMs
- Consider using a smaller quantized model (Q4_K_M or lower)
- Ensure you have enough RAM/VRAM allocated

## 📝 Important Notes

1. **Keep LM Studio Running**: The local server must be running whenever you use the model in Cursor
2. **Model Selection**: Choose the model that best fits your needs:
   - `deepseek-coder-v2-lite` - Better for coding tasks
   - `meta-llama-3-8b` - More general purpose
3. **Performance**: Local LLMs may be slower than cloud APIs but provide privacy
4. **Resource Usage**: Monitor your system resources as local models can be memory-intensive

## 🔄 Restart Required

After configuration:
1. **Restart Cursor** to apply the model configuration
2. Select your LM Studio model from the dropdown in the chat panel
3. Start using your local LLM!

## 🎯 Quick Start Checklist

- [ ] LM Studio is running on localhost:1234
- [ ] At least one model is loaded in LM Studio
- [ ] Cursor Settings → Models → Add Model configured
- [ ] Base URL set to: `http://localhost:1234/v1`
- [ ] Model ID matches LM Studio model
- [ ] Cursor restarted
- [ ] Model selected in Cursor chat panel
- [ ] Test with a simple prompt

## 📚 Additional Resources

- **LM Studio Docs**: https://lmstudio.ai/docs
- **LM Studio Server**: https://lmstudio.ai/docs/developer/core/server
- **Cursor Documentation**: https://cursordocs.com

