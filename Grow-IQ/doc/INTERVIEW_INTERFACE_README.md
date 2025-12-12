# Mock Interview Interface

This document describes the new Google Meet-like mock interview interface that has been added to the Qrow IQ platform.

## Overview

The mock interview interface provides a professional, video-conference-like experience for conducting AI-powered mock interviews. Users can practice their interview skills with real-time video, audio recording, and AI-powered question generation and evaluation.

## Features

### 🎥 Video Interface
- **Camera Integration**: Enable/disable webcam during interviews
- **Video Controls**: Toggle video on/off with visual feedback
- **Responsive Layout**: Adapts to different screen sizes

### 🎤 Audio Recording
- **Microphone Access**: Record answers to interview questions
- **Recording Controls**: Start/stop recording with visual indicators
- **Answer Processing**: Automatic audio processing and evaluation

### 📝 Question Management
- **Dynamic Questions**: AI-generated questions based on job descriptions
- **Question Navigation**: Move between questions with progress tracking
- **Question Types**: Support for technical, behavioral, general, and leadership interviews

### 📊 Progress Tracking
- **Real-time Progress**: Visual progress bar and completion percentage
- **Timer Display**: Interview duration and answer recording time
- **Score Tracking**: Individual question scores and overall performance

### 💬 Interactive Features
- **Chat System**: Internal messaging during interviews
- **Notes Taking**: Built-in note-taking with auto-save
- **Feedback Tab**: Real-time feedback and scoring display

## How to Use

### 1. Starting an Interview

1. Navigate to the home page
2. Scroll to the "Mock Interview System" section
3. Enter a job description in the text area
4. Select interview type (Technical, Behavioral, General, or Leadership)
5. Choose the number of questions (5, 6, 8, or 10)
6. Click "Start Interview"

### 2. Interview Interface

Once the interview starts, you'll be redirected to the interview interface with:

- **Left Panel**: Video display and current question
- **Right Panel**: Interview controls and progress
- **Bottom Panel**: Chat, notes, and feedback tabs

### 3. Answering Questions

1. **Read the Question**: Current question is displayed prominently
2. **Start Recording**: Click "Start Answer" to begin recording
3. **Speak Your Answer**: Answer the question clearly
4. **Stop Recording**: Click "Stop Recording" when finished
5. **Get Feedback**: View your score and feedback in the feedback tab

### 4. Navigation

- **Previous/Next**: Navigate between questions
- **Skip Question**: Skip questions you don't want to answer
- **Repeat Question**: Hear the question again
- **End Interview**: Complete the interview early if needed

## Technical Implementation

### Backend Integration

The interface integrates with the existing `interview.py` backend through:

- **Question Generation**: `/interview/generate-questions` endpoint
- **Answer Evaluation**: `/interview/evaluate-answer` endpoint
- **Session Management**: `/interview/start-session` endpoint
- **Results Saving**: `/interview/save-results` endpoint

### Frontend Architecture

- **HTML Template**: `templates/interview_interface.html`
- **CSS Styling**: `static/css/interview_interface.css`
- **JavaScript Logic**: `static/js/interview_interface.js`

### Key Components

1. **InterviewInterface Class**: Main controller for all interview functionality
2. **Media Handling**: WebRTC integration for video and audio
3. **State Management**: Local storage for interview data persistence
4. **Real-time Updates**: Dynamic UI updates and progress tracking

## File Structure

```
Qrow IQ/
├── templates/
│   └── interview_interface.html          # Main interview interface template
├── static/
│   ├── css/
│   │   └── interview_interface.css      # Interview interface styles
│   └── js/
│       └── interview_interface.js       # Interview interface logic
├── interview_routes.py                   # Backend interview routes
├── interview.py                          # Core interview logic
└── test_interview_interface.html        # Testing interface
```

## Testing

### Test the Interface

1. **Direct Test**: Visit `/test-interview` to test with sample data
2. **Integration Test**: Use the mock interview section on the home page
3. **Sample Data**: Test with predefined interview scenarios

### Test Scenarios

- **Basic Functionality**: Camera, microphone, and question navigation
- **Audio Recording**: Record and process interview answers
- **Progress Tracking**: Verify progress bars and timers work correctly
- **Responsive Design**: Test on different screen sizes

## Browser Compatibility

The interface requires modern browsers with support for:

- **WebRTC**: For camera and microphone access
- **MediaRecorder API**: For audio recording
- **ES6+ Features**: Modern JavaScript functionality
- **CSS Grid/Flexbox**: Advanced layout features

### Supported Browsers

- Chrome 66+
- Firefox 60+
- Safari 14+
- Edge 79+

## Security Considerations

- **Media Permissions**: Users must explicitly grant camera/microphone access
- **Data Privacy**: Interview data is stored locally by default
- **HTTPS Required**: Media access requires secure connections
- **User Authentication**: Interview access requires user login

## Future Enhancements

### Planned Features

1. **Speech-to-Text**: Real-time transcription of answers
2. **Video Recording**: Save interview videos for review
3. **AI Interviewer**: Virtual interviewer with facial expressions
4. **Multi-language Support**: Support for different languages
5. **Interview Templates**: Predefined interview scenarios

### Technical Improvements

1. **WebSocket Integration**: Real-time communication
2. **Database Storage**: Persistent interview history
3. **Analytics Dashboard**: Detailed performance metrics
4. **Mobile App**: Native mobile application
5. **Offline Support**: Work without internet connection

## Troubleshooting

### Common Issues

1. **Camera Not Working**
   - Check browser permissions
   - Ensure HTTPS connection
   - Try refreshing the page

2. **Microphone Access Denied**
   - Grant microphone permissions
   - Check system audio settings
   - Restart browser if needed

3. **Questions Not Loading**
   - Check internet connection
   - Verify backend is running
   - Check browser console for errors

4. **Interface Not Responsive**
   - Check browser compatibility
   - Clear browser cache
   - Try different browser

### Debug Mode

Enable debug mode by opening browser console and setting:
```javascript
localStorage.setItem('debug_mode', 'true');
```

## Support

For technical support or feature requests:

1. Check the browser console for error messages
2. Verify all required files are present
3. Ensure backend services are running
4. Test with the provided test interface

## License

This interview interface is part of the Qrow IQ platform and follows the same licensing terms.
