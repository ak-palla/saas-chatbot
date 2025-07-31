import { useState, useRef, useCallback } from 'react';

export interface AudioRecorderConfig {
  mimeType?: string;
  audioBitsPerSecond?: number;
  timeslice?: number;
  onDataAvailable?: (data: Blob) => void;
  onError?: (error: Error) => void;
  onStart?: () => void;
  onStop?: () => void;
}

export interface AudioRecorderState {
  isRecording: boolean;
  isSupported: boolean;
  duration: number;
  audioLevel: number;
}

export function useAudioRecorder(config: AudioRecorderConfig = {}) {
  const [state, setState] = useState<AudioRecorderState>({
    isRecording: false,
    isSupported: typeof window !== 'undefined' && 'mediaRecorder' in window,
    duration: 0,
    audioLevel: 0,
  });

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(0);
  const durationIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const {
    mimeType = 'audio/webm;codecs=opus',
    audioBitsPerSecond = 128000,
    timeslice = 1000,
    onDataAvailable,
    onError,
    onStart,
    onStop,
  } = config;

  const updateAudioLevel = useCallback(() => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);

    // Calculate RMS (root mean square) for audio level
    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
      sum += (dataArray[i] / 255) ** 2;
    }
    const rms = Math.sqrt(sum / dataArray.length);
    const audioLevel = Math.min(rms * 100, 100); // Scale to 0-100

    setState(prev => ({ ...prev, audioLevel }));

    if (state.isRecording) {
      animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
    }
  }, [state.isRecording]);

  const updateDuration = useCallback(() => {
    if (startTimeRef.current) {
      const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
      setState(prev => ({ ...prev, duration: elapsed }));
    }
  }, []);

  const startRecording = useCallback(async () => {
    if (!state.isSupported) {
      const error = new Error('MediaRecorder is not supported in this browser');
      onError?.(error);
      return;
    }

    if (state.isRecording) {
      return;
    }

    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 44100,
        },
      });

      streamRef.current = stream;

      // Set up audio analysis for level monitoring
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 256;

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported(mimeType) ? mimeType : 'audio/webm',
        audioBitsPerSecond,
      });

      mediaRecorderRef.current = mediaRecorder;

      // Set up event handlers
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          onDataAvailable?.(event.data);
        }
      };

      mediaRecorder.onstart = () => {
        startTimeRef.current = Date.now();
        setState(prev => ({ ...prev, isRecording: true, duration: 0 }));
        
        // Start duration timer
        durationIntervalRef.current = setInterval(updateDuration, 1000);
        
        // Start audio level monitoring
        updateAudioLevel();
        
        onStart?.();
      };

      mediaRecorder.onstop = () => {
        setState(prev => ({ ...prev, isRecording: false, audioLevel: 0 }));
        
        // Clear timers
        if (durationIntervalRef.current) {
          clearInterval(durationIntervalRef.current);
          durationIntervalRef.current = null;
        }
        
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
          animationFrameRef.current = null;
        }
        
        onStop?.();
      };

      mediaRecorder.onerror = (event) => {
        const error = new Error(`MediaRecorder error: ${event.error?.message || 'Unknown error'}`);
        onError?.(error);
        stopRecording();
      };

      // Start recording
      mediaRecorder.start(timeslice);
    } catch (error) {
      const recordingError = error instanceof Error 
        ? error 
        : new Error('Failed to start recording');
      onError?.(recordingError);
      stopRecording();
    }
  }, [state.isSupported, state.isRecording, mimeType, audioBitsPerSecond, timeslice, onDataAvailable, onError, onStart, onStop, updateAudioLevel, updateDuration]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && state.isRecording) {
      mediaRecorderRef.current.stop();
    }

    // Clean up stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    // Clean up audio context
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    // Clean up refs
    mediaRecorderRef.current = null;
    analyserRef.current = null;
    startTimeRef.current = 0;

    // Clear timers
    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
      durationIntervalRef.current = null;
    }

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
  }, [state.isRecording]);

  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current && state.isRecording) {
      mediaRecorderRef.current.pause();
    }
  }, [state.isRecording]);

  const resumeRecording = useCallback(() => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.resume();
    }
  }, []);

  return {
    ...state,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
  };
}