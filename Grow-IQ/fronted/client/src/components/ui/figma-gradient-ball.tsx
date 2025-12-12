import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

// Animation timing constants - must match TransitionContext
const ANIM_DURATION_MS = 1200;

interface FigmaGradientBallProps {
  isVisible: boolean;
  onAnimationComplete?: () => void;
  className?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  bounceIntensity?: 'soft' | 'medium' | 'strong';
}

export const FigmaGradientBall: React.FC<FigmaGradientBallProps> = ({
  isVisible,
  onAnimationComplete,
  className,
  size = 'lg',
  bounceIntensity = 'medium'
}) => {
  const [ballPosition, setBallPosition] = useState({ x: 50, y: 50 });
  const [isAnimating, setIsAnimating] = useState(false);

  const sizeClasses = {
    sm: 'w-16 h-16',
    md: 'w-24 h-24', 
    lg: 'w-32 h-32',
    xl: 'w-48 h-48'
  };

  const bounceClasses = {
    soft: 'animate-bounce-custom',
    medium: 'animate-elastic', 
    strong: 'animate-spring'
  };

  useEffect(() => {
    if (isVisible) {
      setIsAnimating(true);
      // Set random starting position
      setBallPosition({
        x: Math.random() * 80 + 10, // 10-90% to keep within viewport
        y: Math.random() * 80 + 10
      });

      // Complete animation after duration
      const timer = setTimeout(() => {
        setIsAnimating(false);
        onAnimationComplete?.();
      }, ANIM_DURATION_MS);

      return () => clearTimeout(timer);
    } else {
      setIsAnimating(false);
    }
  }, [isVisible, onAnimationComplete]);

  if (!isVisible && !isAnimating) return null;

  return (
    <div 
      className={cn(
        "fixed inset-0 z-[100] pointer-events-none overflow-hidden",
        className
      )}
    >
      {/* Main Figma Gradient Ball */}
      <div
        className={cn(
          "absolute rounded-full",
          sizeClasses[size],
          bounceClasses[bounceIntensity],
          isAnimating ? "opacity-100" : "opacity-0"
        )}
        style={{
          left: `${ballPosition.x}%`,
          top: `${ballPosition.y}%`,
          background: `radial-gradient(circle at 30% 30%, 
            rgba(0, 191, 166, 1) 0%,
            rgba(45, 162, 175, 1) 25%,
            rgba(75, 119, 190, 1) 50%,
            rgba(103, 58, 183, 1) 75%,
            rgba(103, 58, 183, 0.9) 100%
          )`,
          boxShadow: `
            0 0 40px rgba(0, 191, 166, 0.4),
            0 0 80px rgba(103, 58, 183, 0.3),
            inset 0 0 20px rgba(255, 255, 255, 0.1)
          `,
          filter: 'blur(0.5px)',
          transform: 'translate(-50%, -50%)',
          animationDuration: '1.2s',
          animationFillMode: 'both',
          transition: 'opacity 0.3s ease-in-out'
        }}
      />
      
      {/* Additional floating particles for enhanced effect */}
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className={cn(
            "absolute rounded-full animate-bubble-float",
            isAnimating ? "opacity-60" : "opacity-0"
          )}
          style={{
            left: `${(ballPosition.x + (Math.random() - 0.5) * 40)}%`,
            top: `${(ballPosition.y + (Math.random() - 0.5) * 40)}%`,
            width: `${Math.random() * 8 + 4}px`,
            height: `${Math.random() * 8 + 4}px`,
            background: `radial-gradient(circle, 
              rgba(0, 191, 166, 0.6) 0%,
              rgba(103, 58, 183, 0.4) 100%
            )`,
            animationDelay: `${Math.random() * 0.5}s`,
            animationDuration: `${Math.random() * 1 + 1.5}s`,
            transform: 'translate(-50%, -50%)',
            transition: 'opacity 0.3s ease-in-out'
          }}
        />
      ))}

      {/* Background overlay effect */}
      <div 
        className={cn(
          "absolute inset-0 transition-opacity duration-500",
          isAnimating ? "opacity-100" : "opacity-0"
        )}
        style={{
          background: `radial-gradient(circle at ${ballPosition.x}% ${ballPosition.y}%, 
            rgba(0, 191, 166, 0.05) 0%,
            rgba(103, 58, 183, 0.05) 50%,
            transparent 70%
          )`
        }}
      />
    </div>
  );
};

// Enhanced page transition with Figma gradient ball
interface FigmaPageTransitionProps {
  children: React.ReactNode;
  isTransitioning?: boolean;
  className?: string;
  ballSize?: 'sm' | 'md' | 'lg' | 'xl';
  bounceType?: 'soft' | 'medium' | 'strong';
}

export const FigmaPageTransition: React.FC<FigmaPageTransitionProps> = ({
  children,
  isTransitioning = false,
  className,
  ballSize = 'lg',
  bounceType = 'medium'
}) => {
  const [showBall, setShowBall] = useState(false);
  const [contentVisible, setContentVisible] = useState(true);

  useEffect(() => {
    if (isTransitioning) {
      setContentVisible(false);
      setShowBall(true);
    }
  }, [isTransitioning]);

  const handleAnimationComplete = () => {
    setShowBall(false);
    setContentVisible(true);
  };

  return (
    <div className={cn("relative", className)}>
      <FigmaGradientBall 
        isVisible={showBall}
        onAnimationComplete={handleAnimationComplete}
        size={ballSize}
        bounceIntensity={bounceType}
      />
      <div 
        className={cn(
          "transition-all duration-700 ease-out",
          contentVisible 
            ? "opacity-100 transform translate-y-0 scale-100" 
            : "opacity-0 transform translate-y-8 scale-95"
        )}
      >
        {children}
      </div>
    </div>
  );
};