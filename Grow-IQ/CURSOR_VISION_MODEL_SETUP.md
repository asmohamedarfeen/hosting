# Fix: Vision-Enabled Model Setup for Cursor

## ⚠️ Problem

You're getting the error: **"Trying to submit images without a vision-enabled model selected"**

**Reason**: Your current LM Studio models don't support image understanding:
- ❌ `deepseek-coder-v2-lite-instruct` - Coding model, no vision
- ❌ `meta-llama-3-8b-instruct` - General purpose, no vision
- ❌ `text-embedding-nomic-embed-text-v1.5` - Embeddings only

## ✅ Solution: Download a Vision-Enabled Model

### Step 1: Download Vision Model in LM Studio

1. **Open LM Studio**
2. **Go to "Search" tab** (or "Discover" tab)
3. **Search for vision models**, such as:

**Recommended Vision Models:**

#### Option 1: Llama 3.2 Vision (Best for general use)
- Search: `llama 3.2 vision`
- Look for: `llama-3.2-11b-vision-instruct` or similar
- Download a quantized version (Q4_K_M or Q5_K_M)

#### Option 2: Qwen 2 Vision (Great performance)
- Search: `qwen 2 vision`
- Look for: `qwen-2-vl-7b-instruct` or similar
- Download quantized version

#### Option 3: LLaVA (Popular vision model)
- Search: `llava`
- Look for: `llava-1.5-7b` or `llava-1.6-vicuna-7b`
- Download quantized version

#### Option 4: CogVLM (Good for detailed analysis)
- Search: `cogvlm`
- Look for: `cogvlm-chat` variants
- Download quantized version

4. **Click "Download"** on the model you choose
5. **Wait for download to complete**

### Step 2: Load Vision Model in LM Studio

1. **Go to "Chat" tab** in LM Studio
2. **Click "Select a model to load"**
3. **Choose your vision model** (the one you just downloaded)
4. **Wait for model to load** (may take a minute)

### Step 3: Verify Vision Model is Available

Check that your vision model is loaded:

```bash
curl http://localhost:1234/v1/models
```

You should see your new vision model in the list.

### Step 4: Configure Vision Model in Cursor

1. **Open Cursor Settings** (`Cmd+Shift+J`)
2. **Go to Models section**
3. **If you haven't added a model yet:**
   - Click "Add Model"
   - Enter name: `LM Studio Vision`
   - Click "Add"

4. **Configure API Settings:**
   - **OpenAI API Key**: `lmstudio`
   - **Override OpenAI Base URL**: Check this box
   - **Base URL**: `http://localhost:1234/v1`

5. **Save/Verify**: Click "Verify" or "Save"

### Step 5: Select Vision Model in Chat

1. **Open Cursor Chat** (`Cmd+L`)
2. **Click model dropdown** (top of chat panel)
3. **Select your vision model**: `LM Studio Vision`
4. **Now you can upload images!**

## 🎯 Quick Model Recommendations

### Best for Coding + Vision:
- **DeepSeek-V2-Coder** (if available with vision)
- **Qwen 2.5 Coder with Vision**

### Best for General Vision:
- **Llama 3.2 11B Vision** - Great balance
- **LLaVA 1.6** - Very popular, well-tested

### Best for Detailed Image Analysis:
- **CogVLM** - Excellent for complex images
- **Qwen 2 VL 7B** - Great performance

### Lightweight Options (Less RAM):
- **LLaVA 1.5 7B** - Good performance, lower memory
- **Qwen 2 VL 2B** - Small but capable

## 📋 Step-by-Step: Quick Setup

1. ✅ Open LM Studio
2. ✅ Search tab → Search for "llava" or "vision"
3. ✅ Download `llava-1.6-vicuna-7b` (or similar)
4. ✅ Chat tab → Load the vision model
5. ✅ Verify: `curl http://localhost:1234/v1/models`
6. ✅ Cursor Settings → Models → Configure Base URL
7. ✅ Select vision model in Cursor chat
8. ✅ Upload image and test!

## 🧪 Test Vision Model

After setting up:

1. **Open Cursor Chat** (`Cmd+L`)
2. **Select your vision model**
3. **Upload an image** (use the image upload button)
4. **Ask**: "What do you see in this image?"
5. **The model should describe the image!**

## ⚠️ Troubleshooting

### Model Doesn't Appear in Cursor
- **Solution**: Make sure LM Studio server is running
- Check: `curl http://localhost:1234/v1/models`
- Restart LM Studio if needed

### Still Getting Vision Error
- **Solution**: Ensure vision model is loaded in LM Studio (Chat tab)
- Make sure you selected the vision model in Cursor chat dropdown
- Restart Cursor if needed

### Model Too Slow
- **Solution**: Download a smaller quantized version (Q4_K_M or Q3_K_M)
- Close other applications to free up RAM
- Use a smaller vision model (7B instead of 11B)

### Out of Memory
- **Solution**: 
  - Download smaller quantized model (Q4 or Q3)
  - Close other applications
  - Use a smaller model (2B or 3B instead of 7B+)

## 💡 Pro Tips

1. **Model Size vs Quality**: 
   - Larger models (11B+) = Better understanding but slower
   - Smaller models (7B) = Faster but may miss details
   - Quantized (Q4/Q5) = Good balance

2. **Multiple Models**: 
   - You can have both coding and vision models loaded
   - Switch between them in Cursor as needed

3. **Memory Management**:
   - Vision models use more RAM than text-only models
   - Keep one model loaded at a time if you have limited RAM

## 📚 Resources

- **LM Studio Model Library**: https://lmstudio.ai/models
- **Vision Model Comparison**: Search for "vision model benchmark"
- **Model Quantization Guide**: Check LM Studio documentation

## ✅ Checklist

Before testing:
- [ ] Vision model downloaded in LM Studio
- [ ] Vision model loaded in LM Studio (Chat tab)
- [ ] LM Studio server running (localhost:1234)
- [ ] Cursor configured with Base URL: `http://localhost:1234/v1`
- [ ] Vision model selected in Cursor chat dropdown
- [ ] Image ready to test

