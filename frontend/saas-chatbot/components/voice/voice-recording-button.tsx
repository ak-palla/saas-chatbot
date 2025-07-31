import { Button } from '@/components/ui/button';
import { Mic, MicOff, Loader2 } from 'lucide-react';
import { AudioLevelIndicator } from './audio-level-indicator';
import { cn } from '@/lib/utils';

interface VoiceRecordingButtonProps {
  isRecording: boolean;
  isProcessing: boolean;
  audioLevel: number;
  duration: number;
  isDisabled?: boolean;
  onStartRecording: () => void;
  onStopRecording: () => void;
  className?: string;
}

export function VoiceRecordingButton({
  isRecording,
  isProcessing,
  audioLevel,
  duration,
  isDisabled = false,
  onStartRecording,
  onStopRecording,
  className
}: VoiceRecordingButtonProps) {
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleClick = () => {
    if (isRecording) {
      onStopRecording();
    } else {
      onStartRecording();
    }
  };

  return (
    <div className={cn('flex flex-col items-center space-y-2', className)}>
      <Button
        variant={isRecording ? 'destructive' : 'outline'}
        size="icon"
        onClick={handleClick}
        disabled={isDisabled || isProcessing}
        className={cn(
          'relative transition-all duration-200',
          isRecording && 'animate-pulse bg-red-500 hover:bg-red-600',
          !isRecording && 'hover:scale-105'
        )}
      >
        {isProcessing ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : isRecording ? (
          <MicOff className="h-4 w-4" />
        ) : (
          <Mic className="h-4 w-4" />
        )}
        
        {/* Recording indicator ring */}
        {isRecording && (
          <div className="absolute inset-0 rounded-full border-2 border-red-300 animate-ping" />
        )}
      </Button>

      {/* Audio level indicator - only show when recording */}
      {isRecording && (
        <div className="flex flex-col items-center space-y-1">
          <AudioLevelIndicator 
            level={audioLevel} 
            isRecording={isRecording}
            className="w-16"
          />
          <div className="text-xs text-muted-foreground font-mono">
            {formatDuration(duration)}
          </div>
        </div>
      )}

      {/* Status text */}
      <div className="text-xs text-center text-muted-foreground">
        {isProcessing ? (
          'Processing...'
        ) : isRecording ? (
          'Recording...'
        ) : (
          'Hold to record'
        )}
      </div>
    </div>
  );
}