import React from "react";
import { BarChart3, User, Settings, LogIn, Bell } from "lucide-react";
import { BounceButton } from "@/components/ui/bounce-animation";
import { usePageTransition } from "@/hooks/usePageTransition";

export const JobBoardSection = (): JSX.Element => {
  const { navigateWithBubbles } = usePageTransition();

  const handleNavigation = (route: string) => {
    navigateWithBubbles(route);
  };

  return (
    <header className="w-full h-[82px] bg-gradient-to-r from-[#673ab7] to-[#673ab7dd] backdrop-blur-sm border-b border-[#673ab766] relative shadow-lg">
      <div className="flex items-center justify-between px-[100px] py-0 h-full">
        <div className="bg-gradient-to-r from-white to-[#00bfa6] bg-clip-text text-transparent [font-family:'Sora',Helvetica] font-bold text-2xl leading-normal animate-fade-in">
          GrowIQ
        </div>
        
        {/* Navigation buttons with bounce effects */}
        <div className="flex items-center gap-2">
          <BounceButton
            variant="ghost"
            onClick={() => handleNavigation("/dashboard")}
            className="text-white hover:bg-white/20 flex items-center gap-2 transition-all duration-200"
            data-testid="header-nav-dashboard"
            size="sm"
          >
            <BarChart3 size={16} />
            Dashboard
          </BounceButton>
          <BounceButton
            variant="ghost"
            onClick={() => handleNavigation("/profile")}
            className="text-white hover:bg-white/20 flex items-center gap-2 transition-all duration-200"
            data-testid="header-nav-profile"
            size="sm"
          >
            <User size={16} />
            Profile
          </BounceButton>
          <BounceButton
            variant="ghost"
            onClick={() => handleNavigation("/settings")}
            className="text-white hover:bg-white/20 flex items-center gap-2 transition-all duration-200"
            data-testid="header-nav-settings"
            size="sm"
          >
            <Settings size={16} />
            Settings
          </BounceButton>
          
          {/* Notification Bell - matching Figma design */}
          <div className="relative mx-2">
            <BounceButton
              variant="ghost"
              className="text-white hover:bg-white/20 p-2 rounded-full"
              size="sm"
            >
              <Bell size={20} />
            </BounceButton>
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-bounce" />
          </div>
          
          <BounceButton
            variant="ghost"
            onClick={() => handleNavigation("/login")}
            className="text-white hover:bg-white/20 flex items-center gap-2 transition-all duration-200"
            data-testid="header-nav-login"
            size="sm"
          >
            <LogIn size={16} />
            Login
          </BounceButton>
        </div>
      </div>

      {/* Centered title with enhanced styling */}
      <div className="absolute top-[34px] left-1/2 transform -translate-x-1/2 [font-family:'Sora',Helvetica] font-semibold text-white text-[23px] leading-normal drop-shadow-md">
        Jobs
      </div>
      
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent pointer-events-none" />
    </header>
  );
};
