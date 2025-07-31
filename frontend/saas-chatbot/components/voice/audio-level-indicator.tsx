import { cn } from '@/lib/utils';

interface AudioLevelIndicatorProps {
  level: number; // 0-100
  isRecording: boolean;
  className?: string;
}

export function AudioLevelIndicator({ level, isRecording, className }: AudioLevelIndicatorProps) {
  const bars = Array.from({ length: 8 }, (_, i) => {
    const threshold = (i + 1) * 12.5; // Each bar represents 12.5% increment
    const isActive = level >= threshold;
    
    return (
      <div
        key={i}
        className={cn(
          'w-1 bg-muted-foreground/30 rounded-full transition-all duration-150',
          isActive && isRecording && 'bg-primary',
          i < 3 && 'h-2', // Short bars
          i >= 3 && i < 6 && 'h-3', // Medium bars
          i >= 6 && 'h-4' // Tall bars
        )}
      />
    );
  });

  return (
    <div className={cn('flex items-end space-x-0.5', className)}>
      {bars}
    </div>
  );
}