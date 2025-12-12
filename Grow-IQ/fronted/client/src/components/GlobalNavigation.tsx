import React, { useState, useRef, useEffect } from "react";
import { useLocation } from "wouter";
import { usePageTransition } from "@/contexts/TransitionContext";
import { BounceButton } from "@/components/ui/bounce-animation";
import { User, GraduationCap, Briefcase, Globe, MoreHorizontal, LogOut, Shield } from "lucide-react";

export const GlobalNavigation = (): JSX.Element => {
  const [location, setLocation] = useLocation();
  const { navigateWithBubbles } = usePageTransition();
  const [isMoreDropdownOpen, setIsMoreDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [isHr, setIsHr] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsMoreDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Detect HR and Admin accounts to show appropriate labels and options
  useEffect(() => {
    let isMounted = true;
    const loadProfile = async () => {
      try {
        const res = await fetch('/auth/profile', { credentials: 'include' });
        if (!res.ok) return;
        const data = await res.json();
        const type = (data?.user_type || data?.role || '').toString().toLowerCase();
        
        const inferredHr = Boolean(
          data?.is_hr === true ||
          type === 'hr' ||
          type === 'human_resources' ||
          type === 'hr_user' ||
          type === 'recruiter' ||
          type === 'domain'
        );
        
        const inferredAdmin = Boolean(
          type === 'admin' ||
          data?.user_type === 'admin' ||
          data?.is_admin === true
        );
        
        if (isMounted) {
          setIsHr(inferredHr);
          setIsAdmin(inferredAdmin);
        }
      } catch (_) {
        // Ignore profile fetch errors for the badge
      }
    };
    loadProfile();
    return () => { isMounted = false; };
  }, []);

  const moreMenuItems = [
    { label: "Workshop", route: "/workshop" },
    { label: "Resume", route: "/resume" },
    { label: "Resumeathon", route: "/resumeathon" },
    // MOCK INTERVIEW MODULE - DISCONNECTED (can be reconnected in future)
    // { label: "Mock Interview", route: "/mock-interview" },
    { label: "Cultural Events", route: "/cultural-events" },
    // HR-only visible item
    ...(isHr ? [{ label: "HR Desk", route: "/hr-desk" }] : []),
    // Admin-only visible item
    ...(isAdmin ? [{ label: "Admin Desk", route: "/admin-desk" }] : []),
  ];

  const navigationItems = [
    {
      icon: User,
      route: "/profile",
      label: "Profile",
      testId: "nav-profile"
    },
    {
      icon: GraduationCap,
      route: "/home",
      label: "Home",
      testId: "nav-home"
    },
    {
      icon: Briefcase,
      route: "/jobs",
      label: "Jobs",
      testId: "nav-jobs"
    },
    {
      icon: Globe,
      route: "/network",
      label: "Network",
      testId: "nav-network"
    },
    {
      icon: MoreHorizontal,
      route: "/more",
      label: "More",
      testId: "nav-more"
    },
    {
      icon: LogOut,
      route: "/login",
      label: "Logout",
      testId: "nav-logout"
    },
  ];

  const handleNavigation = (route: string) => {
    navigateWithBubbles(route);
  };

  const handleMoreClick = () => {
    setIsMoreDropdownOpen(!isMoreDropdownOpen);
  };

  const handleMoreMenuClick = (route: string) => {
    setIsMoreDropdownOpen(false);
    navigateWithBubbles(route);
  };

  // Don't show navigation on login pages
  if (location === "/" || location === "/login") {
    return <></>;
  }

  return (
    <>
      {/* Fixed Navigation Bar - positioned outside page content */}
      <nav className="w-[102px] bg-gradient-to-b from-[#673ab7] to-[#5e35b1] rounded-r-[64px] flex flex-col items-center justify-center py-8 fixed left-0 top-1/2 -translate-y-1/2 z-[9999] shadow-2xl h-[75vh] pointer-events-auto" style={{ position: 'fixed' }}>
        {/* Navigation items - simple icon layout */}
        <div className="flex flex-col items-center justify-center gap-8 flex-1">
          {navigationItems.map((item, index) => {
            const Icon = item.icon;
            const isActive = location === item.route;
            const isMoreButton = item.label === "More";
            
            return (
              <BounceButton
                key={index}
                data-testid={item.testId}
                onClick={isMoreButton ? handleMoreClick : () => handleNavigation(item.route)}
                className={`
                  flex items-center justify-center w-12 h-12 
                  transition-all duration-300 ease-out
                  ${isActive 
                    ? 'text-white transform scale-110' 
                    : 'text-white/90 hover:text-white hover:scale-105'
                  }
                  ${isMoreButton && isMoreDropdownOpen ? 'text-white transform scale-110' : ''}
                `}
                title={item.label}
                variant="ghost"
                size="sm"
                bounceOnClick={true}
              >
                <Icon size={24} strokeWidth={2} />
              </BounceButton>
            );
          })}
        </div>

        {/* More Dropdown Menu */}
        {isMoreDropdownOpen && (
          <div 
            ref={dropdownRef}
            className="absolute left-[102px] bg-gradient-to-b from-[#673ab7] to-[#5e35b1] rounded-lg shadow-2xl z-20 min-w-[200px] py-4 px-6"
            style={{ 
              top: `${(navigationItems.findIndex(item => item.label === "More") - 1) * 56}px`,
              bottom: 'auto'
            }}
          >
            {/* More Title */}
            <div className="flex items-center gap-3 text-white font-semibold text-lg mb-4 pb-2 border-b border-white/20">
              <MoreHorizontal size={20} />
              More
            </div>
            
            {/* More Menu Items */}
            <div className="space-y-2">
              {moreMenuItems.map((menuItem, index) => (
                <button
                  key={index}
                  onClick={() => handleMoreMenuClick(menuItem.route)}
                  className="w-full text-left text-white/90 hover:text-white hover:bg-white/10 rounded-md px-3 py-2 transition-all duration-200 text-base"
                >
                  {menuItem.label}
                </button>
              ))}
            </div>
          </div>
        )}
      </nav>

      {/* HR/Admin Badges */}
      {(isHr || isAdmin) && (
        <div className="fixed top-3 right-4 z-50 flex space-x-2">
          {isHr && (
            <span className="px-2 py-0.5 text-xs font-semibold uppercase tracking-wide rounded-full bg-purple-100 text-purple-700 border border-purple-200">hr</span>
          )}
          {isAdmin && (
            <span className="px-2 py-0.5 text-xs font-semibold uppercase tracking-wide rounded-full bg-red-100 text-red-700 border border-red-200 flex items-center">
              <Shield className="h-3 w-3 mr-1" />
              admin
            </span>
          )}
        </div>
      )}
    </>
  );
};
