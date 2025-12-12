import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface BubbleAnimationProps {
  isVisible: boolean;
  onAnimationComplete?: () => void;
  className?: string;
}

export const BubbleAnimation: React.FC<BubbleAnimationProps> = ({
  isVisible,
  onAnimationComplete,
  className
}) => {
  const [bubbles, setBubbles] = useState<Array<{
    id: number;
    x: number;
    y: number;
    size: number;
    duration: number;
    delay: number;
  }>>([]);

  useEffect(() => {
    if (isVisible) {
      // Generate random bubbles
      const newBubbles = Array.from({ length: 15 }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 60 + 20, // 20-80px
        duration: Math.random() * 2 + 1.5, // 1.5-3.5s
        delay: Math.random() * 0.5, // 0-0.5s delay
      }));
      
      setBubbles(newBubbles);
      
      // Call completion callback after animation
      const maxDuration = Math.max(...newBubbles.map(b => b.duration + b.delay));
      setTimeout(() => {
        onAnimationComplete?.();
      }, maxDuration * 1000 + 200); // Add small buffer
    } else {
      setBubbles([]);
    }
  }, [isVisible, onAnimationComplete]);

  if (!isVisible) return null;

  return (
    <div 
      className={cn(
        "fixed inset-0 z-[100] pointer-events-none overflow-hidden",
        className
      )}
    >
      {bubbles.map((bubble) => (
        <div
          key={bubble.id}
          className="absolute rounded-full animate-bubble-float"
          style={{
            left: `${bubble.x}%`,
            top: `${bubble.y}%`,
            width: `${bubble.size}px`,
            height: `${bubble.size}px`,
            background: `linear-gradient(45deg, 
              rgba(103, 58, 183, 0.3), 
              rgba(0, 191, 166, 0.3), 
              rgba(103, 58, 183, 0.1)
            )`,
            backdropFilter: 'blur(2px)',
            border: '1px solid rgba(103, 58, 183, 0.2)',
            animationDuration: `${bubble.duration}s`,
            animationDelay: `${bubble.delay}s`,
            animationFillMode: 'forwards',
          }}
        />
      ))}
    </div>
  );
};

interface PageTransitionProps {
  children: React.ReactNode;
  isTransitioning?: boolean;
  className?: string;
}

export const PageTransition: React.FC<PageTransitionProps> = ({
  children,
  isTransitioning = false,
  className
}) => {
  const [showBubbles, setShowBubbles] = useState(false);
  const [contentVisible, setContentVisible] = useState(true);

  useEffect(() => {
    if (isTransitioning) {
      setContentVisible(false);
      setShowBubbles(true);
    }
  }, [isTransitioning]);

  const handleAnimationComplete = () => {
    setShowBubbles(false);
    setContentVisible(true);
  };

  return (
    <div className={cn("relative", className)}>
      <BubbleAnimation 
        isVisible={showBubbles}
        onAnimationComplete={handleAnimationComplete}
      />
      <div 
        className={cn(
          "transition-opacity duration-300",
          contentVisible ? "opacity-100" : "opacity-0"
        )}
      >
        {children}
      </div>
    </div>
  );
};