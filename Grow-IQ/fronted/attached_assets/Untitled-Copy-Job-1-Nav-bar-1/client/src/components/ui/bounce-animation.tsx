import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface BounceAnimationProps {
  isVisible: boolean;
  onAnimationComplete?: () => void;
  className?: string;
  type?: 'bounce' | 'elastic' | 'spring';
}

export const BounceAnimation: React.FC<BounceAnimationProps> = ({
  isVisible,
  onAnimationComplete,
  className,
  type = 'bounce'
}) => {
  const [particles, setParticles] = useState<Array<{
    id: number;
    x: number;
    y: number;
    size: number;
    color: string;
    delay: number;
    bounceHeight: number;
  }>>([]);

  useEffect(() => {
    if (isVisible) {
      // Generate bounce particles
      const newParticles = Array.from({ length: 12 }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 40 + 15, // 15-55px
        color: i % 2 === 0 ? 'rgba(103, 58, 183, 0.8)' : 'rgba(0, 191, 166, 0.8)',
        delay: Math.random() * 0.3,
        bounceHeight: Math.random() * 60 + 40, // 40-100px bounce
      }));
      
      setParticles(newParticles);
      
      // Call completion callback after animation
      setTimeout(() => {
        setParticles([]);
        onAnimationComplete?.();
      }, 1500); // 1.5s total animation
    } else {
      setParticles([]);
    }
  }, [isVisible, onAnimationComplete]);

  if (!isVisible && particles.length === 0) return null;

  return (
    <div 
      className={cn(
        "fixed inset-0 z-[100] pointer-events-none overflow-hidden",
        className
      )}
    >
      {particles.map((particle) => (
        <div
          key={particle.id}
          className={cn(
            "absolute rounded-full",
            type === 'bounce' && "animate-bounce-custom",
            type === 'elastic' && "animate-elastic",
            type === 'spring' && "animate-spring"
          )}
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            width: `${particle.size}px`,
            height: `${particle.size}px`,
            backgroundColor: particle.color,
            boxShadow: `0 0 20px ${particle.color}`,
            animationDelay: `${particle.delay}s`,
            animationDuration: '1.2s',
            animationFillMode: 'forwards',
            transform: 'translateY(0)',
          }}
        />
      ))}
      
      {/* Overlay effect during transition */}
      <div 
        className={cn(
          "absolute inset-0 bg-gradient-to-br from-purple-500/10 to-teal-500/10",
          "backdrop-blur-sm transition-opacity duration-500",
          isVisible ? "opacity-100" : "opacity-0"
        )}
      />
    </div>
  );
};

// Enhanced page transition with bounce effects
interface PageTransitionWithBounceProps {
  children: React.ReactNode;
  isTransitioning?: boolean;
  className?: string;
  animationType?: 'bounce' | 'elastic' | 'spring';
}

export const PageTransitionWithBounce: React.FC<PageTransitionWithBounceProps> = ({
  children,
  isTransitioning = false,
  className,
  animationType = 'bounce'
}) => {
  const [showAnimation, setShowAnimation] = useState(false);
  const [contentVisible, setContentVisible] = useState(true);

  useEffect(() => {
    if (isTransitioning) {
      setContentVisible(false);
      setShowAnimation(true);
    }
  }, [isTransitioning]);

  const handleAnimationComplete = () => {
    setShowAnimation(false);
    setContentVisible(true);
  };

  return (
    <div className={cn("relative", className)}>
      <BounceAnimation 
        isVisible={showAnimation}
        onAnimationComplete={handleAnimationComplete}
        type={animationType}
      />
      <div 
        className={cn(
          "transition-all duration-500 ease-in-out",
          contentVisible 
            ? "opacity-100 transform translate-y-0 scale-100" 
            : "opacity-0 transform translate-y-4 scale-95"
        )}
      >
        {children}
      </div>
    </div>
  );
};

// Button with bounce effect
interface BounceButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  bounceOnClick?: boolean;
}

export const BounceButton: React.FC<BounceButtonProps> = ({
  children,
  className,
  variant = 'primary',
  size = 'md',
  bounceOnClick = true,
  onClick,
  ...props
}) => {
  const [isBouncing, setIsBouncing] = useState(false);

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (bounceOnClick) {
      setIsBouncing(true);
      setTimeout(() => setIsBouncing(false), 300);
    }
    onClick?.(e);
  };

  const variantClasses = {
    primary: "bg-gradient-to-r from-purple-600 to-teal-500 text-white hover:from-purple-700 hover:to-teal-600",
    secondary: "bg-white text-purple-600 border-2 border-purple-600 hover:bg-purple-50",
    ghost: "text-purple-600 hover:bg-purple-50"
  };

  const sizeClasses = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg"
  };

  return (
    <button
      className={cn(
        "font-medium rounded-lg transition-all duration-200 ease-in-out",
        "active:scale-95 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2",
        variantClasses[variant],
        sizeClasses[size],
        isBouncing && "animate-bounce-click",
        className
      )}
      onClick={handleClick}
      {...props}
    >
      {children}
    </button>
  );
};