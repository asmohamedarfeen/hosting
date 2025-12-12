import React from "react";
import { Button } from "@/components/ui/button";

export const CompaniesSection = (): JSX.Element => {
  return (
    <section className="flex flex-row items-center justify-between w-full relative px-8 md:px-12 lg:px-16 py-16 gap-8 md:gap-12 lg:gap-16">
      {/* Text content - positioned on the left */}
      <div className="flex flex-col flex-[0_1_auto] max-w-[602px] items-start gap-20 relative">
        <div className="flex flex-col items-start gap-8 relative w-full">
          <h1 className="relative w-full [font-family:'Sora',Helvetica] font-bold text-4xl md:text-5xl lg:text-[69px] tracking-[0] leading-[normal]">
            <span className="text-[#000000]">Your </span>
            <span className="text-[#00bfa6]">Next Career</span>
            <span className="text-[#000000]">&nbsp;</span>
            <span className="text-[#00bfa6]">Move</span>
            <span className="text-[#000000]"> Starts Here.</span>
          </h1>

          <div className="flex flex-col h-32 items-start gap-8 relative w-full">
            <p className="relative flex-1 w-full font-body font-[number:var(--body-font-weight)] text-black/50 text-[length:var(--body-font-size)] tracking-[var(--body-letter-spacing)] leading-[var(--body-line-height)] [font-style:var(--body-font-style)]">
              Discover people, companies, and opportunities tailored for your
              industry. Build your presence. Make meaningful connections.
            </p>

            <Button 
              className="inline-flex items-center justify-center gap-2.5 px-8 py-4 bg-purple-600 rounded-[100px] shadow-[0px_7px_15px_#0000001a,0px_27px_27px_#00000017,0px_61px_37px_#0000000d,0px_108px_43px_#00000003,0px_169px_47px_transparent] h-auto hover:bg-purple-700 transition-colors" 
              data-testid="button-get-started"
              onClick={() => {
                console.log('Get Started button clicked');
                window.location.assign('/auth/signup');
              }}
            >
              <span className="[font-family:'Sora',Helvetica] font-bold text-[#ffffff] text-sm tracking-[0] leading-[normal]">
                Get Started
              </span>
            </Button>
          </div>
        </div>
      </div>

      {/* Image container - positioned on the right */}
      <div className="flex items-center justify-center relative flex-shrink-0 flex-[0_0_auto] min-w-[400px] max-w-[600px]">
        <div className="relative w-[76.8px] h-[76.8px] bg-app-secondary rounded-[38.4px] blur-[4.8px]" />

        <img
          className="relative w-full max-w-[532px] h-auto aspect-square"
          alt="Vector"
          src="/landing/figmaAssets/vector-1.svg"
        />

        <div className="inline-flex items-center justify-end gap-4 absolute top-[46px] left-16">
          <div className="flex flex-col w-[220px] items-start gap-4 relative">
            <div className="relative w-[200px] h-[220px] rounded-[150px] bg-[url(/figmaAssets/frame-29.svg)] bg-cover bg-[50%_50%]" />

            <div className="relative w-[200px] h-[220px] rounded-[150px] bg-[url(/figmaAssets/frame-31.svg)] bg-cover bg-[50%_50%]" />
          </div>

          <div className="relative w-[200px] h-[300px] rounded-[150px] bg-[url(/figmaAssets/frame-30.svg)] bg-cover bg-[50%_50%]" />
        </div>

        <div className="absolute top-7 left-[314px] w-8 h-8 rounded-2xl blur-[1.6px] bg-[linear-gradient(326deg,rgba(93,80,198,1)_0%,rgba(248,94,159,1)_100%)]" />

        <img
          className="absolute w-[11.07%] h-[12.03%] top-[79.70%] left-[85.76%]"
          alt="Isologo"
          src="/landing/figmaAssets/isologo.png"
        />
      </div>
    </section>
  );
};
