import React, { createContext, useContext, useState, useCallback, ReactNode, useRef } from 'react';
import { useLocation } from 'wouter';

// Animation timing constants
const ANIM_DELAY_MS = 200;
const ANIM_DURATION_MS = 1200;

interface TransitionContextType {
  location: string;
  isTransitioning: boolean;
  navigateWithBubbles: (path: string) => void;
}

const TransitionContext = createContext<TransitionContextType | undefined>(undefined);

interface TransitionProviderProps {
  children: ReactNode;
}

export const TransitionProvider: React.FC<TransitionProviderProps> = ({ children }) => {
  const [location, setLocation] = useLocation();
  const [isTransitioning, setIsTransitioning] = useState(false);
  const transitioningRef = useRef(false);

  const navigateWithBubbles = useCallback((path: string) => {
    if (path === location) return; // Don't transition to same page
    if (transitioningRef.current) return; // Guard against re-entrancy
    
    transitioningRef.current = true;
    setIsTransitioning(true);
    
    // Start animation immediately
    const navigateTimer = setTimeout(() => {
      setLocation(path);
    }, ANIM_DELAY_MS);
    
    // End transition after animation completes
    const completeTimer = setTimeout(() => {
      setIsTransitioning(false);
      transitioningRef.current = false;
    }, ANIM_DELAY_MS + ANIM_DURATION_MS);
    
    // Cleanup function in case component unmounts
    return () => {
      clearTimeout(navigateTimer);
      clearTimeout(completeTimer);
      transitioningRef.current = false;
    };
  }, [location, setLocation]);

  return (
    <TransitionContext.Provider 
      value={{
        location,
        isTransitioning,
        navigateWithBubbles,
      }}
    >
      {children}
    </TransitionContext.Provider>
  );
};

export const usePageTransition = () => {
  const context = useContext(TransitionContext);
  if (context === undefined) {
    throw new Error('usePageTransition must be used within a TransitionProvider');
  }
  return context;
};