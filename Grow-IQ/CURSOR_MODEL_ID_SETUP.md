# Where to Set Model ID in Cursor Settings

## 📍 Exact Location Guide

### Step 1: Open Cursor Settings
- **Method 1**: Press `Cmd+Shift+J` (Mac) or `Ctrl+Shift+J` (Windows/Linux)
- **Method 2**: Click the ⚙️ **gear icon** in the top-right corner of Cursor

### Step 2: Navigate to Models Section

In the Settings panel that opens, look in the **left sidebar** for one of these:
- **"Models"** (most common)
- **"AI Models"**
- **"Custom Models"**
- **"Model Settings"**

Click on it to expand the section.

### Step 3: Click "Add Model" Button

Once in the Models section, you'll see:
- A list of existing models (if any)
- An **"Add Model"** button (usually at the top)
- OR an **"+"** button
- OR **"Add Custom Model"** button

Click that button.

### Step 4: The Model Configuration Form

A form/dialog will appear with several fields. The **Model ID** field is typically:

**Option A: In a Text Field Named "Model ID"**
```
┌─────────────────────────────────────────┐
│ Add Custom Model                        │
├─────────────────────────────────────────┤
│ Model Name:                             │
│ [_____________________________]         │
│                                         │
│ OpenAI API Key:                         │
│ [_____________________________]         │
│                                         │
│ Override Base URL:                      │
│ [http://localhost:1234/v1        ]     │
│                                         │
│ Model ID:                               │
│ [_____________________________]   ← HERE!
│                                         │
│ [  Save  ]  [  Cancel  ]               │
└─────────────────────────────────────────┘
```

**Option B: Sometimes it's called "Model Name" or "Model Identifier"**

If you don't see "Model ID" field, it might be:
- The same field as "Model Name" (enter the full model ID there)
- A dropdown that you need to fill
- A field labeled "Model Identifier"

### Step 5: Enter Your Model ID

In the **Model ID** field (or Model Name/Identifier field), enter:

**For general purpose (recommended to start):**
```
ai models/llama/meta-llama-3-8b-instruct-q4_k_m.gguf
```

**For coding-focused tasks:**
```
ai models/llama/deepseek-coder-v2-lite-instruct-q4_k_m.gguf
```

**For embeddings:**
```
text-embedding-nomic-embed-text-v1.5
```

### Step 6: Complete All Fields

Make sure to fill in ALL fields:

| Field | Value to Enter |
|-------|---------------|
| **Model Name** | `LM Studio Local` (or any name you prefer) |
| **OpenAI API Key** | `lmstudio` (any placeholder - LM Studio doesn't need auth) |
| **Override Base URL** | `http://localhost:1234/v1` |
| **Model ID** | `ai models/llama/meta-llama-3-8b-instruct-q4_k_m.gguf` |

### Step 7: Save and Verify

1. Click **"Save"** or **"Add Model"** button
2. Click **"Verify"** or **"Test Connection"** if available
3. You should see: ✅ **"Connection successful"** or **"Model added successfully"**

## 🔍 Can't Find the Model ID Field?

### If Cursor UI Looks Different:

**Alternative Method 1: Check Model Dropdown**
- Sometimes Cursor auto-detects models from the API
- After setting Base URL to `http://localhost:1234/v1`, Cursor might list available models
- Click the dropdown and select your model

**Alternative Method 2: Settings Search**
- In Cursor Settings, use the search box at the top
- Search for: `model`, `openai`, `api`, or `base url`
- This will filter settings to show model-related options

**Alternative Method 3: Command Palette**
- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
- Type: `Model` or `Add Model`
- Select the relevant command

## ⚠️ Troubleshooting

### Model ID Field Not Visible
- **Solution**: Make sure you've clicked "Add Model" or "+" button first
- The field appears AFTER you click "Add Model"

### Wrong Model ID Format
- **Solution**: Use the EXACT model ID from LM Studio
- Check available models: `curl http://localhost:1234/v1/models`
- Copy the exact `"id"` value from the response

### Model ID Doesn't Work
- **Solution**: Ensure:
  1. LM Studio is running
  2. Model is loaded in LM Studio (Chat tab)
  3. Server is started (Developer tab → Start Server)
  4. Model ID matches exactly (case-sensitive)

## 🎯 Quick Checklist

Before setting Model ID:
- [ ] LM Studio is running
- [ ] At least one model is loaded in LM Studio
- [ ] LM Studio server is started (localhost:1234)
- [ ] Cursor Settings is open
- [ ] "Models" section is visible
- [ ] "Add Model" button is clicked
- [ ] Form/dialog with fields is open
- [ ] Model ID field is visible (or Model Name/Identifier field)

## 💡 Pro Tip

If you're not sure which Model ID to use:
1. Open terminal
2. Run: `curl http://localhost:1234/v1/models`
3. Copy the `"id"` value from the response
4. Paste it into the Model ID field

## 📸 Visual Reference

The Model ID field typically appears in this order in the form:
1. **Model Name** (top)
2. **OpenAI API Key** (middle)
3. **Override Base URL** (middle)
4. **Model ID** (bottom, or after Base URL)

If your Cursor version looks different, the field might be:
- Combined with "Model Name"
- In a dropdown menu
- Auto-detected after setting Base URL

