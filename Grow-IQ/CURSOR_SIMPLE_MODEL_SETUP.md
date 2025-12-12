# Cursor LM Studio Setup - Simple Version

## 📋 Step-by-Step Instructions

### Step 1: Add Model Name (Current Dialog)

In the dialog you see now with "Enter model name":

1. **Enter**: `LM Studio Local` (or any name you prefer)
2. **Click**: "Add"

This will add the model to your list.

### Step 2: Configure API Settings

After clicking "Add", you need to configure the API settings separately:

**Option A: In the Models Section Settings**

1. **Stay in Settings** (or reopen Settings with `Cmd+Shift+J`)
2. **Go to**: Models section (left sidebar)
3. **Look for these options** (usually at the top of the Models section):
   - **"OpenAI API Key"** field
   - **"Override OpenAI Base URL"** checkbox/toggle
   - **"Base URL"** field

4. **Configure**:
   - **OpenAI API Key**: Enter `lmstudio` (any placeholder)
   - **Enable/Check**: "Override OpenAI Base URL" (toggle it ON)
   - **Base URL**: Enter `http://localhost:1234/v1`

5. **Save/Verify**: Click "Verify" or "Save" button

**Option B: Global Settings**

The API configuration might be in the **general settings**, not in the Models section:

1. **Settings** → Look for:
   - **"OpenAI API Key"**
   - **"Custom API Endpoint"**
   - **"Override Base URL"**

2. **Set**:
   - API Key: `lmstudio`
   - Base URL: `http://localhost:1234/v1`

### Step 3: Select Model in Chat

1. **Open Cursor Chat** (`Cmd+L` or chat icon)
2. **Click model dropdown** (top of chat panel)
3. **Select**: `LM Studio Local`
4. **Start using it!**

## 🔍 Where to Find API Settings

If you can't find the API settings, try:

### Method 1: Search in Settings
- In Settings, use the **search box** at the top
- Search for: `openai`, `api`, `base url`, or `endpoint`
- This will show relevant settings

### Method 2: Settings Sections to Check
Look in these sections:
- **"Models"** section (most likely)
- **"Features"** section
- **"General"** section
- **"AI Settings"** section

### Method 3: Command Palette
- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
- Type: `model` or `openai`
- Look for commands related to model configuration

## ✅ Quick Checklist

- [ ] Entered model name in the "Add" dialog: `LM Studio Local`
- [ ] Clicked "Add"
- [ ] Found Settings → Models section
- [ ] Set OpenAI API Key to: `lmstudio`
- [ ] Enabled "Override OpenAI Base URL"
- [ ] Set Base URL to: `http://localhost:1234/v1`
- [ ] Clicked "Verify" or "Save"
- [ ] LM Studio is running on localhost:1234
- [ ] Model loaded in LM Studio
- [ ] Selected "LM Studio Local" in chat dropdown

## ⚠️ Important Notes

1. **Model ID**: With this setup, Cursor will auto-detect the model from LM Studio. You don't need to manually enter the model ID.

2. **Model Selection**: After configuring the Base URL, when you select "LM Studio Local" in the chat, Cursor will automatically use whatever model is currently loaded in LM Studio.

3. **Multiple Models**: If you want to use a specific model, load it in LM Studio first, then use Cursor - it will use that model.

## 🧪 Test It

1. Make sure LM Studio is running with a model loaded
2. Open Cursor chat (`Cmd+L`)
3. Select "LM Studio Local" from the dropdown
4. Type: "Hello, can you help me?"
5. You should get a response from your local model!

## 📸 Visual Guide of What to Look For

After clicking "Add" in the dialog, in Settings → Models section, you should see something like:

```
┌─────────────────────────────────────┐
│ Models                              │
├─────────────────────────────────────┤
│ Available Models:                   │
│ • LM Studio Local                   │
│ • Claude 3.5 Sonnet                 │
│ • GPT-4                             │
├─────────────────────────────────────┤
│ OpenAI API Key:                     │
│ [lmstudio_________________]          │
│                                     │
│ ☑ Override OpenAI Base URL         │ ← Check this!
│ Base URL:                           │
│ [http://localhost:1234/v1_______]   │
│                                     │
│ [ Verify ] [ Save ]                 │
└─────────────────────────────────────┘
```

If your interface looks different, the settings might be in a different location, but the same values need to be set.

