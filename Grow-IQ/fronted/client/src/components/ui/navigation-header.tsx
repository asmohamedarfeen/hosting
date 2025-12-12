import React from "react";
import { ArrowLeft, Home, BarChart3, User, Settings, LogIn, Bell } from "lucide-react";
import { usePageTransition } from "@/hooks/usePageTransition";
import { BounceButton } from "@/components/ui/bounce-animation";

interface NavigationHeaderProps {
  title: string;
  showBackButton?: boolean;
  backTo?: string;
}

export const NavigationHeader = ({ 
  title, 
  showBackButton = true, 
  backTo = "/" 
}: NavigationHeaderProps): JSX.Element => {
  const { navigateWithBubbles } = usePageTransition();

  const handleNavigation = (route: string) => {
    navigateWithBubbles(route);
  };

  const handleBack = () => {
    navigateWithBubbles(backTo);
  };

  // Temporarily disable the top navigation bar per request
  return <></>;
};