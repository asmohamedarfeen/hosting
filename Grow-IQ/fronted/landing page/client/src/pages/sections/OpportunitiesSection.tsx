import React, { useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";

export const OpportunitiesSection = (): JSX.Element => {
  useEffect(() => {
    // Move carousel navigation buttons down
    const moveButtonsDown = () => {
      const buttons = document.querySelectorAll('button[class*="rounded-full"][class*="absolute"], button[class*="rounded-full"][class*="bg-purple"], button[class*="rounded-full"][class*="bg-white"][class*="border"]');
      buttons.forEach((btn) => {
        const element = btn as HTMLElement;
        if (element.closest('.opportunities-section') || 
            element.closest('section[class*="relative"][class*="py-20"]')) {
          // Move buttons down by changing top position
          const currentTop = element.style.top || window.getComputedStyle(element).top;
          if (currentTop && currentTop !== 'auto') {
            const topValue = parseInt(currentTop);
            element.style.top = `${topValue + 100}px`; // Move down by 100px
          } else {
            element.style.top = '200px'; // Set to 200px from top if no existing top value
          }
        }
      });
    };
    
    moveButtonsDown();
    // Also move after a short delay in case buttons are added dynamically
    const timer = setTimeout(moveButtonsDown, 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <section className="relative w-full py-20 bg-neutral-100 overflow-hidden opportunities-section">
      {/* Background decorative vector */}
      <img
        className="absolute w-[155.74%] h-[130.94%] top-[21.32%] left-[-39.07%] opacity-20"
        alt="Background Vector"
        src="/landing/figmaAssets/vector.svg"
      />

      <div className="max-w-7xl mx-auto px-8 relative z-10">
        <h2 className="text-center mb-16 bg-[linear-gradient(274deg,rgba(103,58,183,1)_0%,rgba(0,191,166,1)_100%)] [-webkit-background-clip:text] bg-clip-text [-webkit-text-fill-color:transparent] [text-fill-color:transparent] [font-family:'Sora',Helvetica] font-semibold text-5xl tracking-[0] leading-[normal]" data-testid="heading-why-growiq">
          Why GrowIQ?
        </h2>

        {/* Move carousel navigation buttons down */}
        <style>{`
          .opportunities-section button[class*="rounded-full"][class*="absolute"],
          .opportunities-section button[class*="bg-purple"][class*="rounded-full"],
          .opportunities-section button[class*="bg-white"][class*="rounded-full"][class*="border"] {
            top: 200px !important;
          }
        `}</style>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* First Card */}
          <Card className="relative bg-white rounded-3xl shadow-lg border-0 overflow-hidden transform hover:scale-105 transition-transform duration-300" data-testid="card-fresh-opportunities">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-50 to-teal-50 opacity-50" />
            <CardContent className="relative z-10 p-8 text-center">
              <div className="mb-6">
                <img
                  className="mx-auto w-24 h-24 object-contain"
                  alt="Fresh Opportunities Icon"
                  src="/landing/figmaAssets/group-9239.png"
                />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4 [font-family:'Sora',Helvetica]" data-testid="text-fresh-opportunities-title">
                New Month, New Opportunities
              </h3>
              <p className="text-lg text-gray-600 leading-relaxed" data-testid="text-fresh-opportunities-description">
                Stay ahead with fresh listings! Every month brings new openings — be the first to discover what's next.
              </p>
            </CardContent>
          </Card>

          {/* Second Card */}
          <Card className="relative bg-white rounded-3xl shadow-lg border-0 overflow-hidden transform hover:scale-105 transition-transform duration-300" data-testid="card-real-jobs">
            <div className="absolute inset-0 bg-gradient-to-br from-orange-50 to-yellow-50 opacity-50" />
            <CardContent className="relative z-10 p-8 text-center">
              <div className="mb-6">
                <img
                  className="mx-auto w-24 h-24 object-contain"
                  alt="Real Jobs Icon"
                  src="/landing/figmaAssets/group-9241.png"
                />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4 [font-family:'Sora',Helvetica]" data-testid="text-real-jobs-title">
                Real Jobs. Real HR Reach Outs. Guaranteed.
              </h3>
              <p className="text-lg text-gray-600 leading-relaxed" data-testid="text-real-jobs-description">
                Genuine roles, verified recruiters — no gimmicks, just results. Connect directly with hiring managers.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Success Metrics Row */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 text-center relative">
          <div className="bg-white rounded-2xl p-6 shadow-md">
            <div className="text-3xl font-bold text-purple-600 mb-2">98%</div>
            <div className="text-gray-600">Success Rate</div>
          </div>
          <div className="bg-white rounded-2xl p-6 shadow-md">
            <div className="text-3xl font-bold text-teal-600 mb-2">500+</div>
            <div className="text-gray-600">Companies</div>
          </div>
          <div className="bg-white rounded-2xl p-6 shadow-md">
            <div className="text-3xl font-bold text-orange-600 mb-2">10K+</div>
            <div className="text-gray-600">Jobs Posted</div>
          </div>
          <div className="bg-white rounded-2xl p-6 shadow-md relative">
            <div className="text-3xl font-bold text-blue-600 mb-2">24/7</div>
            <div className="text-gray-600">Support</div>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-10 right-10 flex items-center space-x-4">
          <img
            className="w-20 h-20 opacity-80"
            alt="Decorative Element 1"
            src="/landing/figmaAssets/group-9237.png"
          />
          <img
            className="w-32 h-32 opacity-80"
            alt="Decorative Element 2"
            src="/landing/figmaAssets/group-9236.png"
          />
        </div>
      </div>
    </section>
  );
};
