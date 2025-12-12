import { useState, useCallback } from 'react';
import { useLocation } from 'wouter';

export const usePageTransition = () => {
  const [location, setLocation] = useLocation();
  const [isTransitioning, setIsTransitioning] = useState(false);

  const navigateWithBubbles = useCallback((path: string) => {
    if (path === location) return; // Don't transition to same page
    
    setIsTransitioning(true);
    
    // Start bubble animation
    setTimeout(() => {
      setLocation(path);
      
      // End transition after navigation
      setTimeout(() => {
        setIsTransitioning(false);
      }, 500); // Short delay to allow page to start loading
    }, 200); // Brief delay to show bubble start
  }, [location, setLocation]);

  return {
    location,
    isTransitioning,
    navigateWithBubbles,
    setLocation: navigateWithBubbles // Override default setLocation
  };
};