# Speech Recognition Features

This document describes the speech recognition capabilities added to the Video Call Interview system.

## Features Implemented

### 1. Browser-Based Speech Recognition (Primary)
- **Technology**: Web Speech API (SpeechRecognition)
- **Browser Support**: Chrome, Edge, Safari (with limitations)
- **Real-time**: Yes, immediate response
- **Accuracy**: Good for most use cases
- **Setup**: No additional installation required

### 2. Python-Based Speech Recognition (Alternative)
- **Technology**: Google Speech Recognition API via Python
- **Accuracy**: Higher accuracy for complex speech
- **Setup**: Requires additional Python service
- **Use Case**: When browser recognition is not available or needs higher accuracy

## Frontend Implementation

### Speech Recognition Controls
- **Voice Input Button**: Blue microphone button to start/stop listening
- **Visual Indicators**: 
  - "🎤 Listening..." when actively listening
  - "🎤 Voice Ready" when ready to listen
  - Pulsing animation during listening
- **Auto-send**: Automatically sends recognized text as message
- **Error Handling**: Graceful fallback when speech recognition fails

### Integration with Interview Flow
1. User clicks voice input button
2. Browser requests microphone permission
3. User speaks their response
4. Speech is converted to text
5. Text is automatically sent as a message
6. AI responds with TTS

## Backend Services

### Speech Recognition Service (Optional)
- **Port**: 8001
- **Endpoints**:
  - `POST /speech-to-text`: Convert base64 audio to text
  - `POST /speech-to-text-file`: Convert uploaded audio file to text
  - `GET /health`: Health check

### Installation
```bash
# Install Python dependencies
pip install -r requirements_speech.txt

# Start the speech recognition service
python start_speech_service.py
```

## Browser Compatibility

### Supported Browsers
- **Chrome**: Full support
- **Edge**: Full support
- **Safari**: Limited support (may require user gesture)
- **Firefox**: Not supported (uses different API)

### Fallback Behavior
- If speech recognition is not supported, the voice input button is hidden
- Users can still type their responses manually
- All other features (TTS, camera, etc.) work normally

## Usage Instructions

### For Users
1. **Start Interview**: Click "Join Interview" to begin
2. **Enable Voice Input**: Click the blue microphone button
3. **Speak Response**: Wait for "Listening..." indicator, then speak
4. **Auto-send**: Your speech will be automatically converted and sent
5. **AI Response**: AI will respond with voice (if TTS enabled)

### For Developers
1. **Browser API**: Uses `window.SpeechRecognition` or `window.webkitSpeechRecognition`
2. **Event Handling**: Listens for `onstart`, `onresult`, `onend`, `onerror` events
3. **Error Handling**: Graceful degradation when speech recognition fails
4. **TypeScript**: Full type definitions for Speech Recognition API

## Technical Details

### Speech Recognition Configuration
```typescript
recognition.continuous = false;      // Single recognition per start
recognition.interimResults = false;  // Only final results
recognition.lang = 'en-US';          // English language
```

### Audio Processing
- **Format**: WebM or WAV (browser dependent)
- **Quality**: Browser-optimized for speech recognition
- **Latency**: Near real-time processing

### Error Handling
- **Permission Denied**: Graceful fallback to text input
- **Network Issues**: Local processing (browser-based)
- **Recognition Errors**: User feedback and retry option

## Future Enhancements

### Planned Features
1. **Multiple Languages**: Support for different languages
2. **Voice Commands**: Special commands for interview control
3. **Audio Quality**: Enhanced audio preprocessing
4. **Offline Mode**: Local speech recognition when online services unavailable

### Integration Opportunities
1. **Real-time Translation**: Multi-language interview support
2. **Voice Analysis**: Emotion and confidence detection
3. **Custom Models**: Domain-specific speech recognition models

## Troubleshooting

### Common Issues
1. **Microphone Not Working**: Check browser permissions
2. **Poor Recognition**: Ensure good audio quality and clear speech
3. **Browser Not Supported**: Use Chrome or Edge for best experience
4. **Permission Denied**: Allow microphone access when prompted

### Debug Information
- Check browser console for speech recognition errors
- Verify microphone permissions in browser settings
- Test with simple phrases first

## Security Considerations

### Privacy
- **Local Processing**: Browser-based recognition processes audio locally
- **No Storage**: Audio is not stored or transmitted
- **Permission Required**: User must explicitly grant microphone access

### Data Handling
- **Temporary**: Audio data exists only during recognition
- **No Persistence**: No audio files are saved
- **Secure**: Uses HTTPS for all communications

## Performance

### Optimization
- **Minimal Latency**: Direct browser API usage
- **Resource Efficient**: No additional server processing for basic recognition
- **Scalable**: Browser handles multiple concurrent recognitions

### Monitoring
- **Success Rate**: Track recognition success/failure rates
- **Response Time**: Monitor time from speech to text
- **User Experience**: Collect feedback on recognition accuracy
