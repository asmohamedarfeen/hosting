import React from "react";
import { Button } from "@/components/ui/button";

export const StatsSection = (): JSX.Element => {
  const navigationItems = [
    { text: "Top Collabs", width: "w-[108px]" },
    { text: "Inside Story", width: "w-[110px]" },
    { text: "Let's Talk", width: "w-[82px]" },
  ];

  return (
    <header className="flex w-full items-center justify-between gap-8 px-8 py-8 relative">
      <a 
        href="#" 
        className="relative w-fit bg-[linear-gradient(274deg,rgba(103,58,183,1)_0%,rgba(0,191,166,1)_100%)] [-webkit-background-clip:text] bg-clip-text [-webkit-text-fill-color:transparent] [text-fill-color:transparent] [font-family:'Sora',Helvetica] font-bold text-transparent text-2xl tracking-[0] leading-[normal] hover:opacity-80 transition-opacity"
        data-testid="brand-logo"
      >
        GrowIQ
      </a>

      <nav className="inline-flex items-center justify-center gap-16 relative flex-[0_0_auto]">
        <ul className="flex items-center gap-16">
          {navigationItems.map((item, index) => (
            <li key={index} className={`relative ${item.width} h-[23px]`}>
              <a 
                href="#" 
                className="absolute w-full h-full top-0 left-0 font-body font-[number:var(--body-font-weight)] text-black/75 text-[length:var(--body-font-size)] tracking-[var(--body-letter-spacing)] leading-[var(--body-line-height)] [font-style:var(--body-font-style)] cursor-pointer hover:opacity-80 transition-opacity flex items-center justify-center"
                data-testid={`nav-${item.text.toLowerCase().replace(' ', '-')}`}
              >
                {item.text}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      <div className="flex items-center gap-8 relative">
        <Button
          variant="outline"
          className="inline-flex items-center justify-center gap-2.5 px-8 py-4 bg-[#ffffff] rounded-[100px] border-0 h-auto hover:bg-gray-50 transition-colors"
          data-testid="button-login"
          onClick={() => {
            console.log('Log Me In button clicked');
            window.location.replace('http://localhost:8000/login');
          }}
        >
          <span className="relative w-fit mt-[-1.00px] [font-family:'Sora',Helvetica] font-bold text-black/75 text-sm tracking-[0] leading-[normal]">
            Log Me In
          </span>
        </Button>

        <Button 
          className="flex w-[180px] items-center justify-center gap-2.5 px-8 py-4 bg-purple-600 rounded-[100px] h-auto hover:bg-purple-700 transition-colors" 
          data-testid="button-begin-journey-header"
          onClick={() => {
            console.log('Begin Journey header button clicked');
            window.location.assign('/auth/signup');
          }}
        >
          <span className="relative w-fit mt-[-1.00px] [font-family:'Sora',Helvetica] font-bold text-[#ffffff] text-sm tracking-[0] leading-[normal]">
            Begin Journey
          </span>
        </Button>
      </div>
    </header>
  );
};
