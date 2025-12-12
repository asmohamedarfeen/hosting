// DEPRECATED: Use @/contexts/TransitionContext instead
// This file exists for backward compatibility only

import { usePageTransition as useContextTransition } from '@/contexts/TransitionContext';

let hasWarned = false;

export const usePageTransition = () => {
  if (!hasWarned) {
    console.warn('[DEPRECATED] usePageTransition from @/hooks/usePageTransition is deprecated. Use @/contexts/TransitionContext instead.');
    hasWarned = true;
  }
  
  return useContextTransition();
};