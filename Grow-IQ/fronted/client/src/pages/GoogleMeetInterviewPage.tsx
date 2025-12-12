import React, { useState, useEffect, useRef } from "react";
import { useLocation } from "wouter";

// Voice-to-text removed
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { usePageTransition } from "@/contexts/TransitionContext";
import { 
  ArrowLeft, 
  Clock, 
  CheckCircle, 
  Play, 
  Pause, 
  RotateCcw,
  Target,
  Award,
  Trophy,
  Send,
  Loader2,
  User,
  Bot,
  Mic,
  MicOff,
  Video,
  VideoOff,
  Phone,
  PhoneOff,
  Settings,
  MoreVertical,
  ScreenShare,
  Grid3X3,
  Volume2,
  VolumeX,
  Camera,
  CameraOff,
  Maximize,
  Minimize
} from "lucide-react";

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

export const GoogleMeetInterviewPage = (): JSX.Element => {
  const [location, setLocation] = useLocation();
  const { navigateWithBubbles } = usePageTransition();
  
  // Interview setup state
  const [jobRole, setJobRole] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [isSetupComplete, setIsSetupComplete] = useState(false);
  
  // Interview session state
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentMessage, setCurrentMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isInterviewStarted, setIsInterviewStarted] = useState(false);
  const [isInterviewCompleted, setIsInterviewCompleted] = useState(false);

  // Video call UI state
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [participants, setParticipants] = useState(2);
  const [callDuration, setCallDuration] = useState(0);
  const [isCallActive, setIsCallActive] = useState(false);
  
  // TTS and Camera state
  const [isTTSEnabled, setIsTTSEnabled] = useState(true);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [userVideoStream, setUserVideoStream] = useState<MediaStream | null>(null);
  const [userVideoRef, setUserVideoRef] = useState<HTMLVideoElement | null>(null);
  const [isCameraLoading, setIsCameraLoading] = useState(false);
  
  // STT recording state (Python backend)
  const [isRecording, setIsRecording] = useState(false);
  const [isAutoSending, setIsAutoSending] = useState(false);
  const [isProcessingSpeech, setIsProcessingSpeech] = useState(false);
  const [isAutoRecording, setIsAutoRecording] = useState(false);
  const [isAutoModeEnabled, setIsAutoModeEnabled] = useState(true);
  const [isWaitingForUserSpeech, setIsWaitingForUserSpeech] = useState(false);
  const [isAutoSubmitting, setIsAutoSubmitting] = useState(false);

  // Audio recording refs
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const sourceNodeRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const recordedBuffersRef = useRef<Float32Array[]>([]);
  const recordingSampleRateRef = useRef<number>(44100);
  // Enhanced silence detection configuration
  const silenceThresholdRef = useRef<number>(0.005); // RMS threshold (0-1) - more sensitive for better detection
  const silenceMsRef = useRef<number>(1500); // stop after 1.5s of silence for better UX
  const maxRecordMsRef = useRef<number>(30000); // hard cap at 30s for interview responses
  const recordStartTimeRef = useRef<number>(0);
  const lastSpeechTimeRef = useRef<number>(0);
  const speechDetectedRef = useRef<boolean>(false); // Track if any speech was detected
  const consecutiveSilenceFramesRef = useRef<number>(0); // Count consecutive silent frames
  const minSpeechDurationRef = useRef<number>(500); // Minimum 500ms of speech before considering it valid
  
  // Interview tracking
  const [questionCount, setQuestionCount] = useState(0);
  const [totalScore, setTotalScore] = useState(0);
  const [maxQuestions] = useState(10);
  const [isEndingInterview, setIsEndingInterview] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const callTimerRef = useRef<NodeJS.Timeout | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const speechSynthesis = useRef<SpeechSynthesisUtterance | null>(null);
  const processingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Timer effect
  useEffect(() => {
    if (isCallActive) {
      callTimerRef.current = setInterval(() => {
        setCallDuration(prev => prev + 1);
      }, 1000);
    } else {
      if (callTimerRef.current) {
        clearInterval(callTimerRef.current);
      }
    }

    return () => {
      if (callTimerRef.current) {
        clearInterval(callTimerRef.current);
      }
    };
  }, [isCallActive]);

  // Check authentication on component mount
  useEffect(() => {
    const checkAuthOnMount = async () => {
      const isAuthenticated = await checkAuth();
      if (!isAuthenticated) {
        alert("Please log in to access mock interviews");
        navigateWithBubbles("/auth/login");
      }
    };
    checkAuthOnMount();
  }, []);

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      // Clear processing timeout
      if (processingTimeoutRef.current) {
        clearTimeout(processingTimeoutRef.current);
        processingTimeoutRef.current = null;
      }
    };
  }, []);

  // Auto scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-start recording when AI finishes speaking
  useEffect(() => {
    if (isAutoModeEnabled && !isRecording && !isSpeaking && isInterviewStarted && !isInterviewCompleted) {
      // Check if the last message was from AI
      const lastMessage = messages[messages.length - 1];
      if (lastMessage && lastMessage.sender === 'ai') {
        // Wait a bit for TTS to finish, then start recording
        const timer = setTimeout(() => {
          if (!isRecording && !isSpeaking) {
            setIsWaitingForUserSpeech(true);
            startSTTRecording();
          }
        }, 2000); // 2 second delay after AI message
        
        return () => clearTimeout(timer);
      }
    }
  }, [messages, isSpeaking, isAutoModeEnabled, isRecording, isInterviewStarted, isInterviewCompleted]);

  // Voice-to-text removed: initialization effect removed

  // Handle video stream assignment when video element is available
  useEffect(() => {
    if (userVideoStream && videoRef.current) {
      const videoElement = videoRef.current;
      videoElement.srcObject = userVideoStream;
      videoElement.onloadedmetadata = () => {
        console.log('Video metadata loaded, starting playback');
        videoElement.play().catch(console.error);
      };
    }
  }, [userVideoStream]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCamera();
      window.speechSynthesis.cancel();
      // Voice-to-text removed
    };
  }, []);

  // Format call duration
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // ---- STT via Python service ----
  const startSTTRecording = async () => {
    if (isRecording) return;
    try {
      setIsProcessingSpeech(true);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioContextRef.current = audioContext;
      recordingSampleRateRef.current = audioContext.sampleRate;
      const source = audioContext.createMediaStreamSource(stream);
      sourceNodeRef.current = source;
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;
      recordedBuffersRef.current = [];
      recordStartTimeRef.current = Date.now();
      lastSpeechTimeRef.current = recordStartTimeRef.current;
      speechDetectedRef.current = false;
      consecutiveSilenceFramesRef.current = 0;
      processor.onaudioprocess = (event) => {
        const input = event.inputBuffer.getChannelData(0);
        // buffer copy for encoding later
        recordedBuffersRef.current.push(new Float32Array(input));
        
        // Enhanced RMS-based silence detection
        let sumSquares = 0;
        for (let i = 0; i < input.length; i++) {
          const s = input[i];
          sumSquares += s * s;
        }
        const rms = Math.sqrt(sumSquares / input.length);
        const now = Date.now();
        
        // Check if current frame has speech
        const hasSpeech = rms > silenceThresholdRef.current;
        
        if (hasSpeech) {
          lastSpeechTimeRef.current = now;
          speechDetectedRef.current = true;
          consecutiveSilenceFramesRef.current = 0;
        } else {
          consecutiveSilenceFramesRef.current++;
        }
        
        // Only stop if we've detected speech and then had prolonged silence
        const hasDetectedSpeech = speechDetectedRef.current;
        const hasMinimumSpeech = (now - recordStartTimeRef.current) > minSpeechDurationRef.current;
        const hasProlongedSilence = (now - lastSpeechTimeRef.current) > silenceMsRef.current;
        
        if (hasDetectedSpeech && hasMinimumSpeech && hasProlongedSilence) {
          console.log('Auto-stopping recording: speech detected, minimum duration met, prolonged silence');
          // Detach to prevent repeated stops
          try { processorRef.current && (processorRef.current.onaudioprocess = null as any); } catch {}
          stopSTTRecording();
          return;
        }
        
        // Hard cap maximum duration
        if (now - recordStartTimeRef.current > maxRecordMsRef.current) {
          console.log('Auto-stopping recording: maximum duration reached');
          try { processorRef.current && (processorRef.current.onaudioprocess = null as any); } catch {}
          stopSTTRecording();
          return;
        }
      };
      source.connect(processor);
      processor.connect(audioContext.destination);
      setIsRecording(true);
      setIsAutoRecording(true);
    } catch (e) {
      console.error('Failed to start recording:', e);
      setIsProcessingSpeech(false);
      alert('Microphone access failed. Please allow mic permission.');
    }
  };

  const stopSTTRecording = async () => {
    if (!isRecording) return;
    try {
      setIsRecording(false);
      setIsAutoRecording(false);
      setIsWaitingForUserSpeech(false);
      if (processorRef.current) {
        try { processorRef.current.onaudioprocess = null as any; } catch {}
        processorRef.current.disconnect();
      }
      if (sourceNodeRef.current) {
        sourceNodeRef.current.disconnect();
      }
      if (audioContextRef.current) {
        try { audioContextRef.current.close(); } catch {}
      }
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(t => t.stop());
      }

      const wavBlob = encodeWav(recordedBuffersRef.current, recordingSampleRateRef.current);
      setIsAutoSending(true);
      setIsAutoSubmitting(true);

      // Use the new auto-speech processing endpoint for automatic submission
      const base64Audio = await blobToBase64(wavBlob);
      
      try {
        // Use auto-speech processing endpoint that handles both STT and submission
        const autoSpeechResponse = await fetch('/api/auto-speech/process', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            audio_data: base64Audio,
            session_id: sessionId,
            language: 'en-US',
            auto_submit: true
          })
        });
        
        const autoData = await autoSpeechResponse.json();
        console.log('Auto speech processing result:', autoData);
        
        if (autoData.success && autoData.text) {
          if (autoData.submitted) {
            console.log('Speech automatically submitted to interview');
            // The message is already submitted, just show success feedback
            if (!sessionId) {
              setCurrentMessage(String(autoData.text));
            }
          } else {
            // Fallback: submit manually if auto-submit failed
            if (sessionId) {
              await sendMessageDirectly(String(autoData.text));
            } else {
              setCurrentMessage(String(autoData.text));
            }
          }
        } else {
          // Fallback to original STT if auto-speech fails
          console.warn('Auto-speech failed, falling back to manual STT:', autoData.error);
          
          // First, check if the audio contains voice activity
          let hasVoice = true; // Default to true for manual recordings
          
          if (isAutoRecording) {
            try {
              const vadResponse = await fetch('/api/stt/voice-activity-detection', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                  audio_data: base64Audio, 
                  threshold: 0.005,
                  min_duration: 0.5
                })
              });
              const vadData = await vadResponse.json();
              hasVoice = vadData.success && vadData.has_voice;
              console.log('Voice activity detection:', vadData);
            } catch (err) {
              console.warn('Voice activity detection failed, proceeding with STT:', err);
            }
          }

          if (!hasVoice) {
            console.log('No voice detected, skipping speech recognition');
            alert('No speech detected. Please try speaking louder or closer to the microphone.');
            return;
          }

          // Prefer multipart upload API for reliability
          let data: any = null;
          try {
            const form = new FormData();
            form.append('audio_file', new File([wavBlob], 'recording.wav', { type: 'audio/wav' }));
            form.append('language', 'en-US');
            const respFile = await fetch('/api/stt/speech-to-text-file', {
              method: 'POST',
              body: form,
            });
            data = await respFile.json();
          } catch (err) {
            console.warn('Multipart upload failed, trying base64 API...', err);
            const respB64 = await fetch('/api/stt/speech-to-text', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ audio_data: base64Audio, language: 'en-US' })
            });
            data = await respB64.json();
          }
          if (data && data.success && data.text) {
            if (sessionId) {
              await sendMessageDirectly(String(data.text));
            } else {
              setCurrentMessage(String(data.text));
            }
          } else {
            alert(data?.error || 'Speech recognition failed.');
          }
        }
      } catch (err) {
        console.error('Auto speech processing failed:', err);
        alert('Speech processing failed. Please try again.');
      }
    } catch (e) {
      console.error('Failed to stop/submit recording:', e);
      alert('Speech-to-text failed.');
    } finally {
      setIsAutoSending(false);
      setIsProcessingSpeech(false);
      setIsAutoSubmitting(false);
      recordedBuffersRef.current = [];
      audioContextRef.current = null;
      mediaStreamRef.current = null;
      sourceNodeRef.current = null;
      processorRef.current = null;
      recordStartTimeRef.current = 0;
      lastSpeechTimeRef.current = 0;
    }
  };

  const blobToBase64 = (blob: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(String(reader.result));
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  };

  const encodeWav = (buffers: Float32Array[], sampleRate: number): Blob => {
    let totalLength = 0;
    for (const b of buffers) totalLength += b.length;
    const merged = new Float32Array(totalLength);
    let offset = 0;
    for (const b of buffers) { merged.set(b, offset); offset += b.length; }

    const pcm16 = new DataView(new ArrayBuffer(merged.length * 2));
    let index = 0;
    for (let i = 0; i < merged.length; i++, index += 2) {
      let s = Math.max(-1, Math.min(1, merged[i]));
      pcm16.setInt16(index, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }

    const wavBuffer = new ArrayBuffer(44 + pcm16.byteLength);
    const view = new DataView(wavBuffer);
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + pcm16.byteLength, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeString(view, 36, 'data');
    view.setUint32(40, pcm16.byteLength, true);
    new Uint8Array(wavBuffer, 44).set(new Uint8Array(pcm16.buffer));
    return new Blob([wavBuffer], { type: 'audio/wav' });
  };

  const writeString = (view: DataView, offset: number, str: string) => {
    for (let i = 0; i < str.length; i++) {
      view.setUint8(offset + i, str.charCodeAt(i));
    }
  };

  // Check authentication status
  const checkAuth = async () => {
    try {
      console.log('🔐 Checking authentication...');
      const response = await fetch('/auth/profile', {
        method: 'GET',
        credentials: 'include'
      });
      console.log('🔐 Auth response status:', response.status);
      console.log('🔐 Auth response ok:', response.ok);
      
      if (response.ok) {
        const userData = await response.json();
        console.log('🔐 User authenticated:', userData.username);
        return true;
      } else {
        console.log('🔐 User not authenticated');
        return false;
      }
    } catch (error) {
      console.log('🔐 Auth check error:', error);
      return false;
    }
  };

  // TTS function
  const speakText = (text: string) => {
    console.log('speakText called with:', text);
    console.log('isTTSEnabled:', isTTSEnabled);
    console.log('speechSynthesis available:', 'speechSynthesis' in window);
    
    if (!isTTSEnabled || !('speechSynthesis' in window)) {
      console.log('TTS not available or disabled');
      return;
    }
    
    // Stop any current speech
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 0.8;
    
    console.log('Created utterance, starting speech synthesis');
    
    utterance.onstart = () => {
      console.log('TTS started speaking');
      setIsSpeaking(true);
    };
    utterance.onend = () => {
      console.log('TTS finished');
      setIsSpeaking(false);
      // After AI finishes speaking, auto-start mic recording for user's answer
      setTimeout(() => {
        try {
          if (!isRecording && isCallActive && !isInterviewCompleted) {
            console.log('Auto-starting voice recording after AI speech');
            startSTTRecording();
          }
        } catch (e) {
          console.warn('Failed to auto-start recording after TTS end:', e);
        }
      }, 500); // Increased delay for better UX
    };
    utterance.onerror = (event) => {
      console.log('TTS error:', event);
      setIsSpeaking(false);
      // Even if TTS errors, try to start recording so the user can answer
      setTimeout(() => {
        try {
          if (!isRecording && isCallActive && !isInterviewCompleted) {
            console.log('Auto-starting voice recording after TTS error');
            startSTTRecording();
          }
        } catch (e) {
          console.warn('Failed to auto-start recording after TTS error:', e);
        }
      }, 500); // Increased delay for better UX
    };
    
    speechSynthesis.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  // Initialize camera
  const initializeCamera = async () => {
    setIsCameraLoading(true);
    try {
      console.log('Requesting camera access...');
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        }, 
        audio: true 
      });
      
      console.log('Camera stream obtained:', stream);
      setUserVideoStream(stream);
      
      // Wait for the video element to be available
      const videoElement = videoRef.current;
      if (videoElement) {
        videoElement.srcObject = stream;
        videoElement.onloadedmetadata = () => {
          console.log('Video metadata loaded, starting playback');
          videoElement.play().catch(console.error);
        };
      } else {
        console.warn('Video element not found');
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      alert('Camera access denied. Please allow camera permission and refresh the page.');
      // Camera access denied, continue without video
    } finally {
      setIsCameraLoading(false);
    }
  };

  // Stop camera
  const stopCamera = () => {
    if (userVideoStream) {
      userVideoStream.getTracks().forEach(track => track.stop());
      setUserVideoStream(null);
    }
  };

  // Voice-to-text removed: controls removed

  // Calculate score for a response
  const calculateResponseScore = (response: string): number => {
    const words = response.trim().split(/\s+/).length;
    let score = 0;
    
    // Base score for having a response
    if (words > 0) score += 1;
    
    // Length bonus (more detailed responses get higher scores)
    if (words >= 10) score += 2; // Good length
    if (words >= 20) score += 2; // Very detailed
    if (words >= 30) score += 1; // Excellent detail
    
    // Quality indicators (simple heuristics)
    const qualityWords = ['experience', 'skills', 'project', 'team', 'challenge', 'solution', 'learned', 'improved', 'achieved', 'developed'];
    const qualityCount = qualityWords.filter(word => 
      response.toLowerCase().includes(word)
    ).length;
    score += qualityCount; // 1 point per quality word
    
    // Technical terms bonus
    const techWords = ['technology', 'framework', 'algorithm', 'database', 'api', 'frontend', 'backend', 'testing', 'deployment', 'optimization'];
    const techCount = techWords.filter(word => 
      response.toLowerCase().includes(word)
    ).length;
    score += techCount * 0.5; // 0.5 points per tech word
    
    return Math.min(score, 10); // Cap at 10 points per question
  };

  // Force send message directly (for speech recognition)
  const sendMessageDirectly = async (messageText: string) => {
    console.log('🚀 sendMessageDirectly called with:', messageText);
    console.log('🔑 Current sessionId:', sessionId);
    console.log('📝 Message trimmed:', messageText.trim());
    console.log('🔍 Session ID type:', typeof sessionId);
    console.log('🔍 Session ID length:', sessionId ? sessionId.length : 'null');
    
    // Clear the processing timeout since we're now sending
    if (processingTimeoutRef.current) {
      clearTimeout(processingTimeoutRef.current);
      processingTimeoutRef.current = null;
    }
    
    if (!messageText.trim() || !sessionId) {
      console.log('❌ Cannot send message - missing text or sessionId');
      console.log('📝 Message text:', messageText);
      console.log('🔑 Session ID:', sessionId);
      console.log('🔍 Message trimmed check:', messageText.trim());
      console.log('🔍 Session ID check:', !!sessionId);
      setIsProcessingSpeech(false);
      return;
    }

    console.log('Force sending message:', messageText);
    setIsAutoSending(true);

    // Calculate score for this response
    const responseScore = calculateResponseScore(messageText);
    console.log('Response score:', responseScore);
    setTotalScore(prev => prev + responseScore);

    const userMessage: Message = {
      id: Date.now().toString(),
      content: messageText,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage("");
    setIsLoading(true);

    try {
      const requestBody = {
        message: messageText,
        session_id: sessionId
      };
      console.log('📤 Sending request to /mock-interview/video/message');
      console.log('📦 Request body:', requestBody);
      console.log('🍪 Credentials: include');
      
      const response = await fetch('/mock-interview/video/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(requestBody)
      });
      
      console.log('📡 Response status:', response.status);
      console.log('📡 Response ok:', response.ok);

      if (!response.ok) {
        console.log('❌ Response not ok:', response.status);
        if (response.status === 401) {
          console.log('🔐 Authentication required, redirecting to login');
          navigateWithBubbles("/auth/login");
          return;
        }
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      console.log('🤖 AI Response received:', data);
      console.log('🤖 AI Reply:', data.reply);
      
      // Increment question count for AI responses
      setQuestionCount(prev => prev + 1);
      console.log(`📊 Question ${questionCount + 1}/${maxQuestions}`);
      
      // Check if we've reached the maximum number of questions
      if (questionCount + 1 >= maxQuestions) {
        console.log('Maximum questions reached, ending interview');
        setIsInterviewCompleted(true);
        setIsCallActive(false);
        return; // Don't process the AI response, just end
      }
      
      // Check if interview is completed by AI
      if (data.reply.includes("Thank you for the interview") || 
          data.reply.includes("Goodbye")) {
        setIsInterviewCompleted(true);
        setIsCallActive(false);
      }

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.reply,
        sender: 'ai',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
      
      // Speak the AI response
      console.log('AI response received:', data.reply);
      console.log('TTS enabled:', isTTSEnabled);
      if (isTTSEnabled) {
        console.log('Speaking AI response:', data.reply);
        speakText(data.reply);
      }

    } catch (error) {
      console.error('❌ Error sending message:', error);
      console.error('❌ Error details:', {
        message: messageText,
        sessionId: sessionId,
        error: error
      });
      alert('Failed to send message. Please try again.');
    } finally {
      console.log('✅ Finally block - resetting states');
      setIsLoading(false);
      setIsAutoSending(false);
      setIsProcessingSpeech(false);
    }
  };

  // API functions
  const startInterviewSession = async () => {
    if (!jobRole.trim()) {
      alert("Please enter a job role");
      return;
    }

    console.log('🎯 Starting interview session...');
    console.log('📝 Job role:', jobRole);
    console.log('📝 Job description:', jobDescription);

    // Check authentication first
    console.log('🔐 Checking authentication before starting interview...');
    const isAuthenticated = await checkAuth();
    if (!isAuthenticated) {
      console.log('❌ User not authenticated, redirecting to login');
      alert("Please log in to start a mock interview");
      navigateWithBubbles("/auth/login");
      return;
    }

    console.log('✅ User authenticated, proceeding with interview start');
    setIsLoading(true);
    try {
      const requestBody = {
        job_role: jobRole,
        job_desc: jobDescription || `General interview for ${jobRole} position`
      };
      console.log('📤 Sending request to /mock-interview/video/start');
      console.log('📦 Request body:', requestBody);

      const response = await fetch('/mock-interview/video/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(requestBody),
      });

      console.log('📡 Response status:', response.status);
      console.log('📡 Response ok:', response.ok);

      if (!response.ok) {
        console.log('❌ Failed to start interview session');
        if (response.status === 401) {
          console.log('🔐 Authentication required, redirecting to login');
          alert("Please log in to start a mock interview");
          navigateWithBubbles("/auth/login");
          return;
        }
        throw new Error('Failed to start interview session');
      }

      const data = await response.json();
      console.log('✅ Interview session started successfully');
      console.log('🔑 Session ID:', data.session_id);
      console.log('📝 Initial prompt:', data.initial_prompt);
      
      setSessionId(data.session_id);
      setIsSetupComplete(true);
      setIsInterviewStarted(true);
      setIsCallActive(true);
      
      // Initialize camera
      await initializeCamera();
      
      // Add initial AI message
      const initialMessage: Message = {
        id: Date.now().toString(),
        content: data.initial_prompt,
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages([initialMessage]);
      
      // Speak the initial message
      if (isTTSEnabled) {
        speakText(data.initial_prompt);
      }
    } catch (error) {
      console.error('Error starting interview:', error);
      alert('Failed to start interview. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || !sessionId || isLoading) {
      console.log('❌ Cannot send message - missing requirements:', {
        message: currentMessage.trim(),
        sessionId: !!sessionId,
        isLoading
      });
      return;
    }

    console.log('📤 Sending message via sendMessage function');
    console.log('📝 Message:', currentMessage);
    console.log('🔑 Session ID:', sessionId);

    // Clear the processing timeout since we're now sending
    if (processingTimeoutRef.current) {
      clearTimeout(processingTimeoutRef.current);
      processingTimeoutRef.current = null;
    }

    // Calculate score for this response
    const responseScore = calculateResponseScore(currentMessage);
    console.log('Response score:', responseScore);
    setTotalScore(prev => prev + responseScore);

    const userMessage: Message = {
      id: Date.now().toString(),
      content: currentMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage("");
    setIsLoading(true);

    try {
      const requestBody = {
        session_id: sessionId,
        message: currentMessage
      };
      console.log('📤 Sending request to /mock-interview/video/message');
      console.log('📦 Request body:', requestBody);

      const response = await fetch('/mock-interview/video/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(requestBody),
      });

      console.log('📡 Response status:', response.status);
      console.log('📡 Response ok:', response.ok);

      if (!response.ok) {
        if (response.status === 401) {
          alert("Please log in to continue the interview");
          navigateWithBubbles("/auth/login");
          return;
        }
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      
      // Increment question count for AI responses
      setQuestionCount(prev => prev + 1);
      console.log(`Question ${questionCount + 1}/${maxQuestions}`);
      
      // Check if we've reached the maximum number of questions
      if (questionCount + 1 >= maxQuestions) {
        console.log('Maximum questions reached, ending interview');
        setIsInterviewCompleted(true);
        setIsCallActive(false);
        return; // Don't process the AI response, just end
      }
      
      // Check if interview is completed by AI
      if (data.reply.includes("Thank you for the interview") || 
          data.reply.includes("Goodbye")) {
        setIsInterviewCompleted(true);
        setIsCallActive(false);
      }

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.reply,
        sender: 'ai',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
      
      // Speak the AI response
      if (isTTSEnabled) {
        speakText(data.reply);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
      setIsProcessingSpeech(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const endCall = () => {
    const confirmEnd = window.confirm(
      `Are you sure you want to end the interview?\n\n` +
      `Current Progress: ${questionCount}/${maxQuestions} questions answered\n` +
      `Current Score: ${totalScore} points\n\n` +
      `This will calculate your final score based on your responses so far.`
    );
    
    if (confirmEnd) {
      endInterview();
    }
  };

  // End interview manually
  const endInterview = async () => {
    console.log('Interview ended manually');
    console.log(`Final score: ${totalScore}/${maxQuestions * 10} (${questionCount} questions answered)`);
    console.log(`Score percentage: ${Math.round((totalScore / (maxQuestions * 10)) * 100)}%`);
    
    setIsEndingInterview(true);
    
    // Stop all ongoing processes
    window.speechSynthesis.cancel();
    if (userVideoStream) {
      userVideoStream.getTracks().forEach(track => track.stop());
    }
    
    try {
      // Call backend to generate AI report
      if (sessionId) {
        console.log('📤 Sending request to end interview and generate AI report');
        const response = await fetch('/mock-interview/end-interview', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            session_id: sessionId
          })
        });

        if (response.ok) {
          const data = await response.json();
          console.log('✅ Interview ended successfully, AI report generated:', data);
          
          // Show success message
          setMessages(prev => [...prev, {
            id: `ai-${Date.now()}`,
            content: `🎉 Interview completed! Your AI-generated report is ready. You can view it in the Reports section.`,
            sender: 'ai',
            timestamp: new Date()
          }]);
        } else {
          console.error('❌ Failed to end interview:', response.statusText);
          setMessages(prev => [...prev, {
            id: `ai-${Date.now()}`,
            content: `Interview ended, but there was an issue generating the report. Please try again later.`,
            sender: 'ai',
            timestamp: new Date()
          }]);
        }
      }
    } catch (error) {
      console.error('❌ Error ending interview:', error);
      setMessages(prev => [...prev, {
        id: `ai-${Date.now()}`,
        content: `Interview ended, but there was an issue generating the report. Please try again later.`,
        sender: 'ai',
        timestamp: new Date()
      }]);
    }
    
    // Add a small delay to show the ending state
    setTimeout(() => {
      setIsInterviewCompleted(true);
      setIsCallActive(false);
      setIsEndingInterview(false);
    }, 2000);
  };

  const resetInterview = () => {
    setJobRole("");
    setJobDescription("");
    setIsSetupComplete(false);
    setSessionId(null);
    setMessages([]);
    setCurrentMessage("");
    setIsLoading(false);
    setIsInterviewStarted(false);
    setIsInterviewCompleted(false);
    setIsCallActive(false);
    setCallDuration(0);
    setQuestionCount(0);
    setTotalScore(0);
    setIsEndingInterview(false);
    
    // Clean up camera and TTS
    stopCamera();
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
    
    setIsProcessingSpeech(false);
    
    // Clear processing timeout
    if (processingTimeoutRef.current) {
      clearTimeout(processingTimeoutRef.current);
      processingTimeoutRef.current = null;
    }
  };

  // Interview completed screen
  if (isInterviewCompleted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
        <Card className="max-w-2xl w-full text-center shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardContent className="py-12">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Award className="w-10 h-10 text-green-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              Interview Completed!
            </h1>
            <p className="text-lg text-gray-600 mb-4">
              Great job! You've completed the mock interview.
            </p>
            
            {/* Score Display */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 mb-6 border border-blue-200">
              <div className="flex items-center justify-center mb-4">
                <Trophy className="w-8 h-8 text-yellow-500 mr-2" />
                <h2 className="text-2xl font-bold text-gray-800">Your Score</h2>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">{totalScore}</div>
                  <div className="text-sm text-gray-600">Points Earned</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600">{maxQuestions * 10}</div>
                  <div className="text-sm text-gray-600">Total Possible</div>
                </div>
              </div>
              
              <div className="text-center mb-4">
                <div className="text-4xl font-bold text-green-600">
                  {Math.round((totalScore / (maxQuestions * 10)) * 100)}%
                </div>
                <div className="text-sm text-gray-600">Overall Performance</div>
              </div>
              
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-700">
                  {questionCount} of {maxQuestions} Questions Answered
                </div>
                <div className="text-sm text-gray-500">
                  Duration: {formatDuration(callDuration)}
                </div>
              </div>
            </div>
            
            {/* Performance Rating */}
            <div className="mb-8">
              {(() => {
                const percentage = (totalScore / (maxQuestions * 10)) * 100;
                let rating = "";
                let color = "";
                if (percentage >= 80) {
                  rating = "Excellent! Outstanding performance!";
                  color = "text-green-600";
                } else if (percentage >= 60) {
                  rating = "Good job! Well done!";
                  color = "text-blue-600";
                } else if (percentage >= 40) {
                  rating = "Not bad! Keep practicing!";
                  color = "text-yellow-600";
                } else {
                  rating = "Keep practicing! You can do better!";
                  color = "text-orange-600";
                }
                return (
                  <div className={`text-lg font-semibold ${color}`}>
                    {rating}
                  </div>
                );
              })()}
            </div>
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button
                  onClick={() => navigateWithBubbles("/mock-interview/reports")}
                  className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
                >
                  <Award className="w-4 h-4 mr-2" />
                  View AI Report
                </Button>
              <Button
                onClick={() => navigateWithBubbles("/mock-interview")}
                variant="outline"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Overview
              </Button>
              <Button
                onClick={resetInterview}
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Start New Interview
              </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Interview setup screen
  if (!isSetupComplete) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center p-4">
        <Card className="max-w-2xl w-full shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl font-bold text-gray-900 mb-4">
              AI Mock Interview Setup
            </CardTitle>
            <p className="text-lg text-gray-600">
              Configure your mock interview with AI-powered questions tailored to your target role.
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center gap-3 p-4 bg-purple-50 rounded-lg">
                <Video className="w-6 h-6 text-purple-600" />
                <div>
                  <div className="font-semibold text-gray-900">Video Call Style</div>
                  <div className="text-sm text-gray-600">Google Meet interface</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-4 bg-blue-50 rounded-lg">
                <Target className="w-6 h-6 text-blue-600" />
                <div>
                  <div className="font-semibold text-gray-900">Role-Specific</div>
                  <div className="text-sm text-gray-600">Tailored to your job</div>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="jobRole" className="text-sm font-medium text-gray-700">
                  Job Role *
                </Label>
                <Input
                  id="jobRole"
                  type="text"
                  placeholder="e.g., Software Engineer, Data Scientist, Product Manager"
                  value={jobRole}
                  onChange={(e) => setJobRole(e.target.value)}
                  className="mt-1"
                />
              </div>
              
              <div>
                <Label htmlFor="jobDescription" className="text-sm font-medium text-gray-700">
                  Job Description (Optional)
                </Label>
                <Textarea
                  id="jobDescription"
                  placeholder="Paste the job description here for more targeted questions..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  className="mt-1 min-h-[100px]"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Leave empty for general interview questions
                </p>
              </div>
            </div>

            <div className="space-y-4">
              {/* Camera Test Section */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Camera Test</h4>
                <div className="flex items-center gap-4">
                  <Button
                    onClick={initializeCamera}
                    variant="outline"
                    size="sm"
                    disabled={isCameraLoading}
                  >
                    {isCameraLoading ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <Camera className="w-4 h-4 mr-2" />
                    )}
                    {isCameraLoading ? 'Testing...' : 'Test Camera'}
                  </Button>
                  {userVideoStream && (
                    <div className="text-sm text-green-600 flex items-center gap-1">
                      <CheckCircle className="w-4 h-4" />
                      Camera working
                    </div>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Test your camera before starting the interview. Make sure to allow camera permission when prompted.
                </p>
              </div>

              <div className="flex gap-4">
                <Button
                  onClick={() => navigateWithBubbles("/mock-interview")}
                  variant="outline"
                  className="flex-1"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back
                </Button>
                <Button
                  onClick={startInterviewSession}
                  disabled={isLoading || !jobRole.trim()}
                  className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Video className="w-4 h-4 mr-2" />
                  )}
                  {isLoading ? 'Starting...' : 'Join Interview'}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Main Google Meet-style interface
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Top Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-1">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="text-sm font-medium">Recording</span>
            </div>
            <div className="text-sm text-gray-300">
              {formatDuration(callDuration)}
            </div>
            <Badge variant="secondary" className="bg-blue-600 text-white">
              {jobRole}
            </Badge>
            <Badge variant="secondary" className="bg-orange-600 text-white">
              Question {questionCount + 1}/{maxQuestions}
            </Badge>
            <Badge variant="secondary" className={`${isTTSEnabled ? 'bg-green-600' : 'bg-gray-600'} text-white`}>
              {isTTSEnabled ? '🔊 AI Voice On' : '🔇 AI Voice Off'}
            </Badge>
            
            {isEndingInterview && (
              <Badge variant="secondary" className="bg-orange-600 text-white animate-pulse">
                🔄 Ending Interview...
              </Badge>
            )}
            {isAutoSending && (
              <Badge variant="secondary" className="bg-green-600 text-white animate-pulse">
                📤 Auto-Submitting...
              </Badge>
            )}
            {isAutoRecording && (
              <Badge variant="secondary" className="bg-blue-600 text-white animate-pulse">
                🎤 Auto Recording...
              </Badge>
            )}
            {isSpeaking && (
              <Badge variant="secondary" className="bg-blue-600 text-white animate-pulse">
                🔊 AI Speaking...
              </Badge>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              onClick={() => setIsFullscreen(!isFullscreen)}
              variant="ghost"
              size="sm"
              className="text-gray-300 hover:text-white"
            >
              {isFullscreen ? <Minimize className="w-4 h-4" /> : <Maximize className="w-4 h-4" />}
            </Button>
            <Button
              onClick={() => navigateWithBubbles("/mock-interview")}
              variant="ghost"
              size="sm"
              className="text-gray-300 hover:text-white"
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      <div className="flex h-[calc(100vh-30px)]">
        {/* Main Video Area */}
        <div className="flex-1 flex flex-col">
          {/* Video Grid */}
          <div className="flex-1 bg-gray-800 p-4">
            <div className="grid grid-cols-2 gap-4 h-full">
              {/* User Video */}
              <div className="bg-gray-700 rounded-lg flex items-center justify-center relative group overflow-hidden min-h-[300px]">
                {isCameraLoading ? (
                  <div className="text-center">
                    <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
                      <Loader2 className="w-10 h-10 text-white animate-spin" />
                    </div>
                    <div className="text-sm text-gray-300">Starting Camera...</div>
                  </div>
                ) : userVideoStream && !isVideoOff ? (
                  <div className="w-full h-full relative">
                    <video
                      ref={videoRef}
                      autoPlay
                      muted
                      playsInline
                      className="w-full h-full object-cover rounded-lg"
                      style={{ transform: 'scaleX(-1)' }} // Mirror the video
                    />
                    <div className="absolute top-2 left-2 bg-black/50 px-2 py-1 rounded text-xs text-white">
                      Live
                    </div>
                  </div>
                ) : (
                  <div className="text-center">
                    <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                      <User className="w-10 h-10 text-white" />
                    </div>
                    <div className="text-sm text-gray-300">You</div>
                    {isVideoOff && (
                      <div className="absolute inset-0 bg-gray-800 rounded-lg flex items-center justify-center">
                        <CameraOff className="w-8 h-8 text-gray-400" />
                      </div>
                    )}
                  </div>
                )}
                <div className="absolute bottom-2 left-2 bg-black/50 px-2 py-1 rounded text-xs">
                  {isMuted ? <MicOff className="w-3 h-3" /> : <Mic className="w-3 h-3" />}
                </div>
                
                {isAutoSending && (
                  <div className="absolute top-2 right-2 bg-green-600 px-2 py-1 rounded text-xs animate-pulse">
                    📤 Auto-Submitting...
                  </div>
                )}
                
                {isAutoRecording && (
                  <div className="absolute top-2 left-2 bg-blue-600 px-2 py-1 rounded text-xs animate-pulse">
                    🎤 Auto Recording...
                  </div>
                )}
                {currentMessage && isProcessingSpeech && (
                  <div className="absolute bottom-2 right-2 bg-black/70 px-2 py-1 rounded text-xs text-white max-w-[200px]">
                    <div className="text-yellow-300">📝 Captured:</div>
                    <div className="truncate">{currentMessage}</div>
                  </div>
                )}
              </div>

              {/* AI Interviewer Video */}
              <div className="bg-gray-700 rounded-lg flex items-center justify-center relative group">
                <div className="text-center">
                  <div className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4 ${
                    isSpeaking ? 'bg-green-600 animate-pulse' : 'bg-purple-600'
                  }`}>
                    <Bot className="w-10 h-10 text-white" />
                  </div>
                  <div className="text-sm text-gray-300">AI Interviewer</div>
                  <div className="text-xs text-gray-400 mt-1">
                    {isSpeaking ? 'Speaking...' : 'Always on'}
                  </div>
                </div>
                <div className="absolute bottom-2 left-2 bg-black/50 px-2 py-1 rounded text-xs">
                  <Mic className="w-3 h-3" />
                </div>
                {isSpeaking && (
                  <div className="absolute top-2 right-2 bg-green-600 px-2 py-1 rounded text-xs">
                    🔊
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Bottom Controls */}
          <div className="bg-gray-800 border-t border-gray-700 px-6 py-4">
            <div className="flex items-center justify-center gap-4">
              <Button
                onClick={() => setIsMuted(!isMuted)}
                variant="ghost"
                size="sm"
                className={`rounded-full w-12 h-12 ${
                  isMuted ? 'bg-red-600 hover:bg-red-700' : 'bg-gray-600 hover:bg-gray-500'
                }`}
              >
                {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </Button>

              <Button
                onClick={() => {
                  if (isVideoOff) {
                    // Turn camera on
                    initializeCamera();
                    setIsVideoOff(false);
                  } else {
                    // Turn camera off
                    stopCamera();
                    setIsVideoOff(true);
                  }
                }}
                variant="ghost"
                size="sm"
                className={`rounded-full w-12 h-12 ${
                  isVideoOff ? 'bg-red-600 hover:bg-red-700' : 'bg-gray-600 hover:bg-gray-500'
                }`}
                title={isVideoOff ? 'Turn Camera On' : 'Turn Camera Off'}
              >
                {isVideoOff ? <VideoOff className="w-5 h-5" /> : <Video className="w-5 h-5" />}
              </Button>

              {/* Record answer (send to Python STT) */}
              <Button
                onClick={() => {
                  if (isRecording) { stopSTTRecording(); } else { startSTTRecording(); }
                }}
                variant="ghost"
                size="sm"
                className={`rounded-full w-12 h-12 transition-all duration-300 ${
                  isRecording ? 'bg-red-600 hover:bg-red-700 animate-pulse shadow-lg shadow-red-500/50' : 
                  isWaitingForUserSpeech ? 'bg-yellow-600 hover:bg-yellow-700 animate-pulse shadow-lg shadow-yellow-500/50' :
                  isAutoSubmitting ? 'bg-blue-600 hover:bg-blue-700 animate-pulse shadow-lg shadow-blue-500/50' :
                  isAutoModeEnabled ? 'bg-green-600 hover:bg-green-700 shadow-lg shadow-green-500/30' :
                  'bg-blue-600 hover:bg-blue-700'
                }`}
                title={
                  isRecording ? 'Auto-recording... Click to stop manually' : 
                  isWaitingForUserSpeech ? 'Waiting for your speech...' :
                  isAutoSubmitting ? 'Processing and submitting your speech...' :
                  isAutoModeEnabled ? 'Auto-recording enabled - Click for manual control' :
                  'Start Manual Recording'
                }
              >
                {isRecording ? <MicOff className="w-5 h-5" /> : 
                 isWaitingForUserSpeech ? <Mic className="w-5 h-5" /> :
                 <Mic className="w-5 h-5" />}
              </Button>

              <Button
                onClick={() => {
                  setIsTTSEnabled(!isTTSEnabled);
                  if (!isTTSEnabled) {
                    window.speechSynthesis.cancel();
                    setIsSpeaking(false);
                  }
                }}
                variant="ghost"
                size="sm"
                className={`rounded-full w-12 h-12 ${
                  isTTSEnabled ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-600 hover:bg-gray-500'
                }`}
                title={isTTSEnabled ? 'Disable AI Voice' : 'Enable AI Voice'}
              >
                {isTTSEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
              </Button>

              {/* Auto-recording toggle */}
              <Button
                onClick={() => setIsAutoModeEnabled(!isAutoModeEnabled)}
                variant="ghost"
                size="sm"
                className={`rounded-full w-12 h-12 ${
                  isAutoModeEnabled ? 'bg-purple-600 hover:bg-purple-700' : 'bg-gray-600 hover:bg-gray-500'
                }`}
                title={isAutoModeEnabled ? 'Disable Auto-Recording' : 'Enable Auto-Recording'}
              >
                <Settings className="w-5 h-5" />
              </Button>

              

              {isSpeaking && (
                <Button
                  onClick={() => {
                    window.speechSynthesis.cancel();
                    setIsSpeaking(false);
                  }}
                  variant="ghost"
                  size="sm"
                  className="rounded-full w-12 h-12 bg-yellow-600 hover:bg-yellow-700"
                  title="Stop Speaking"
                >
                  <Pause className="w-5 h-5" />
                </Button>
              )}

              {/* Enhanced Auto-recording status indicator */}
              {isAutoModeEnabled && (isWaitingForUserSpeech || isRecording || isAutoSubmitting) && (
                <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium transition-all duration-300 ${
                  isWaitingForUserSpeech ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' :
                  isRecording ? 'bg-red-100 text-red-800 border border-red-200' :
                  isAutoSubmitting ? 'bg-blue-100 text-blue-800 border border-blue-200' :
                  'bg-purple-100 text-purple-800 border border-purple-200'
                }`}>
                  <div className={`w-2 h-2 rounded-full animate-pulse ${
                    isWaitingForUserSpeech ? 'bg-yellow-600' :
                    isRecording ? 'bg-red-600' :
                    isAutoSubmitting ? 'bg-blue-600' :
                    'bg-purple-600'
                  }`}></div>
                  {isWaitingForUserSpeech ? 'Waiting for your speech...' : 
                   isRecording ? 'Auto-recording... Speak now!' : 
                   isAutoSubmitting ? 'Processing and submitting...' :
                   'Auto-mode active'}
                </div>
              )}

              <Button
                onClick={() => setIsScreenSharing(!isScreenSharing)}
                variant="ghost"
                size="sm"
                className={`rounded-full w-12 h-12 ${
                  isScreenSharing ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-600 hover:bg-gray-500'
                }`}
              >
                <ScreenShare className="w-5 h-5" />
              </Button>


              <Button
                onClick={endCall}
                variant="ghost"
                size="sm"
                disabled={isEndingInterview}
                className={`rounded-full w-12 h-12 ${
                  isEndingInterview 
                    ? 'bg-orange-600 hover:bg-orange-700' 
                    : 'bg-red-600 hover:bg-red-700'
                }`}
                title={isEndingInterview ? "Ending Interview..." : "End Interview"}
              >
                {isEndingInterview ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <PhoneOff className="w-5 h-5" />
                )}
              </Button>
            </div>
          </div>
        </div>
        {/* Right Sidebar: Questions / Chat */}
        <div className="w-80 bg-gray-800 border-l border-gray-700 flex flex-col">
          {/* Sidebar Header */}
          <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
            <div className="text-sm font-semibold text-gray-200">Questions</div>
            <Badge variant="secondary" className="bg-blue-600 text-white">
              {messages.filter(m => m.sender === 'ai').length}
            </Badge>
          </div>

          {/* Questions List */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            {messages.filter(m => m.sender === 'ai').length === 0 ? (
              <div className="text-xs text-gray-400">AI questions will appear here.</div>
            ) : (
              messages
                .filter(m => m.sender === 'ai')
                .map(m => (
                  <div key={m.id} className="bg-gray-700/70 border border-gray-600 rounded-lg p-3 text-sm text-gray-100">
                    {m.content}
                    <div className="mt-2 text-[10px] text-gray-400">
                      {new Date(m.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Compose Box */}
          <div className="border-t border-gray-700 p-3">
            <div className="flex items-center gap-2">
              <Input
                placeholder="Type your answer..."
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyDown={handleKeyPress}
                className="bg-gray-900 text-gray-100 border-gray-700"
                disabled={isLoading || !sessionId}
              />
              <Button
                onClick={sendMessage}
                disabled={isLoading || !currentMessage.trim() || !sessionId}
                className="bg-blue-600 hover:bg-blue-700"
                title={!sessionId ? 'Start interview to send' : 'Send message'}
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
            
          </div>
        </div>
      </div>
    </div>
  );
};
