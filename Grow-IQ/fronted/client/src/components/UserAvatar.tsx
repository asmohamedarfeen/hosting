import React from "react";
import { User } from "lucide-react";

interface UserAvatarProps {
  user: {
    id?: number;
    profile_pic?: string;
    profile_image?: string;
    profile_image_url?: string;
    full_name?: string;
    username?: string;
  };
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
  showName?: boolean;
  showTitle?: boolean;
  title?: string;
  clickable?: boolean;
  onUserClick?: (userId: number) => void;
}

export const UserAvatar: React.FC<UserAvatarProps> = ({
  user,
  size = "md",
  className = "",
  showName = false,
  showTitle = false,
  title,
  clickable = false,
  onUserClick
}) => {
  const getImageUrl = (): string => {
    const raw = user.profile_pic || user.profile_image || user.profile_image_url;
    if (!raw || raw === 'default-avatar.svg') return ""; // Return empty string to trigger fallback
    if (typeof raw === "string" && (raw.startsWith("http://") || raw.startsWith("https://"))) {
      return raw;
    }
    // If it starts with /static/, it's already a full path from the main app - use relative URL
    if (typeof raw === "string" && raw.startsWith("/static/")) {
      return raw; // Use relative URL - browser will resolve it correctly
    }
    // Otherwise, construct the relative path
    return `/static/uploads/${raw}`;
  };

  const getSizeClasses = () => {
    switch (size) {
      case "sm":
        return "w-6 h-6";
      case "md":
        return "w-10 h-10";
      case "lg":
        return "w-16 h-16";
      case "xl":
        return "w-24 h-24";
      default:
        return "w-10 h-10";
    }
  };

  const getIconSize = () => {
    switch (size) {
      case "sm":
        return "w-3 h-3";
      case "md":
        return "w-5 h-5";
      case "lg":
        return "w-8 h-8";
      case "xl":
        return "w-12 h-12";
      default:
        return "w-5 h-5";
    }
  };

  const displayName = user.full_name || user.username || "User";

  const handleClick = () => {
    if (clickable && user.id && onUserClick) {
      onUserClick(user.id);
    }
  };

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div 
        className={`${getSizeClasses()} rounded-full overflow-hidden border border-[#673ab733] flex items-center justify-center bg-[#673ab7] ${
          clickable ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''
        }`}
        onClick={handleClick}
      >
        {getImageUrl() ? (
          <img
            src={getImageUrl()}
            alt={displayName}
            className="w-full h-full object-cover"
          />
        ) : (
          <User className={`${getIconSize()} text-white`} />
        )}
      </div>
      {showName && (
        <div className="flex flex-col">
          <span 
            className={`font-medium text-gray-900 ${
              clickable ? 'cursor-pointer hover:text-purple-600 transition-colors' : ''
            }`}
            onClick={handleClick}
          >
            {displayName}
          </span>
          {(showTitle && title) && (
            <span className="text-sm text-gray-500">{title}</span>
          )}
        </div>
      )}
    </div>
  );
};
