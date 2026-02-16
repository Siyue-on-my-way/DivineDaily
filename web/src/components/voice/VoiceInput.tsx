import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import './VoiceInput.css';

interface Props {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

export default function VoiceInput({ onTranscript, disabled = false }: Props) {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState('');
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [audioLevel, setAudioLevel] = useState(0);
  
  const recognitionRef = useRef<any>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  useEffect(() => {
    // 检查浏览器支持
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      setError('您的浏览器不支持语音识别功能');
      return;
    }

    // 初始化语音识别
    const recognition = new SpeechRecognition();
    recognition.lang = 'zh-CN';
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onresult = (event: any) => {
      const current = event.resultIndex;
      const transcriptText = event.results[current][0].transcript;
      setTranscript(transcriptText);

      // 如果是最终结果
      if (event.results[current].isFinal) {
        onTranscript(transcriptText);
        setIsRecording(false);
        stopAudioAnalysis();
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      
      if (event.error === 'not-allowed') {
        setError('请允许使用麦克风权限');
        setHasPermission(false);
      } else if (event.error === 'no-speech') {
        setError('未检测到语音，请重试');
      } else {
        setError('语音识别失败，请重试');
      }
      
      setIsRecording(false);
      stopAudioAnalysis();
    };

    recognition.onend = () => {
      setIsRecording(false);
      stopAudioAnalysis();
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      stopAudioAnalysis();
    };
  }, [onTranscript]);

  const startRecording = async () => {
    if (disabled) return;

    setError('');
    setTranscript('');

    try {
      // 请求麦克风权限
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setHasPermission(true);

      // 启动音频分析
      startAudioAnalysis(stream);

      // 启动语音识别
      if (recognitionRef.current) {
        recognitionRef.current.start();
        setIsRecording(true);
      }
    } catch (err) {
      console.error('Failed to start recording:', err);
      setError('无法访问麦克风，请检查权限设置');
      setHasPermission(false);
    }
  };

  const stopRecording = () => {
    if (recognitionRef.current && isRecording) {
      recognitionRef.current.stop();
    }
    setIsRecording(false);
    stopAudioAnalysis();
  };

  const startAudioAnalysis = (stream: MediaStream) => {
    try {
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 256;

      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);

      const updateAudioLevel = () => {
        if (analyserRef.current) {
          analyserRef.current.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
          setAudioLevel(average);
          animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
        }
      };

      updateAudioLevel();
    } catch (err) {
      console.error('Failed to start audio analysis:', err);
    }
  };

  const stopAudioAnalysis = () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    setAudioLevel(0);
  };

  const requestPermission = async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
      setHasPermission(true);
      setError('');
    } catch (err) {
      setError('无法获取麦克风权限');
      setHasPermission(false);
    }
  };

  if (hasPermission === false) {
    return (
      <div className="voice-input">
        <div className="voice-input__permission">
          <div className="voice-input__permission-icon">🎤</div>
          <div className="voice-input__permission-text">
            需要麦克风权限才能使用语音输入功能
          </div>
          <button
            className="voice-input__permission-button"
            onClick={requestPermission}
          >
            授予权限
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="voice-input">
      {/* 录音按钮 */}
      <motion.button
        className={`voice-input__button ${
          isRecording ? 'voice-input__button--recording' : ''
        } ${disabled ? 'voice-input__button--disabled' : ''}`}
        onMouseDown={startRecording}
        onMouseUp={stopRecording}
        onMouseLeave={stopRecording}
        onTouchStart={startRecording}
        onTouchEnd={stopRecording}
        disabled={disabled}
        whileHover={!disabled ? { scale: 1.05 } : {}}
        whileTap={!disabled ? { scale: 0.95 } : {}}
      >
        {isRecording ? '🔴' : '🎤'}
      </motion.button>

      {/* 提示文字 */}
      <div
        className={`voice-input__hint ${
          isRecording ? 'voice-input__hint--recording' : ''
        }`}
      >
        {isRecording ? '松开发送' : '按住说话'}
      </div>

      {/* 波形显示 */}
      {isRecording && (
        <motion.div
          className="voice-input__waveform"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          {Array.from({ length: 10 }).map((_, i) => (
            <div
              key={i}
              className="voice-input__wave-bar voice-input__wave-bar--recording"
              style={{
                height: `${Math.max(10, (audioLevel / 255) * 40 + Math.random() * 20)}px`,
                animationDelay: `${i * 0.1}s`
              }}
            />
          ))}
        </motion.div>
      )}

      {/* 识别结果 */}
      {transcript && (
        <motion.div
          className="voice-input__result"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {transcript}
        </motion.div>
      )}

      {/* 错误提示 */}
      {error && (
        <motion.div
          className="voice-input__error"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {error}
        </motion.div>
      )}
    </div>
  );
}
