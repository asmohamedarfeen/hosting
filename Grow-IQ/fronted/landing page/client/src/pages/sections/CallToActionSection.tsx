import React from "react";
import { Card, CardContent } from "@/components/ui/card";

export const CallToActionSection = (): JSX.Element => {
  const statsData = [
    {
      number: "5K +",
      description: "Companies hire on ",
      highlight: "Dies",
    },
    {
      number: "200K +",
      description: "Jobs posted monthly on ",
      highlight: "Dice",
    },
    {
      number: "7M +",
      description: "Tech professional trust ",
      highlight: "Dice",
    },
  ];

  return (
    <section className="w-full bg-neutral-100 py-16">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex flex-col gap-11">
          <header className="flex items-center gap-4 w-fit">
            <h2 className="bg-[linear-gradient(274deg,rgba(103,58,183,1)_0%,rgba(0,191,166,1)_100%)] [-webkit-background-clip:text] bg-clip-text [-webkit-text-fill-color:transparent] [text-fill-color:transparent] [font-family:'Sora',Helvetica] font-semibold text-transparent text-[28px] text-center tracking-[0] leading-[normal]">
              Dice By The Number
            </h2>
            <img
              className="w-[65px] h-[169.95px]"
              alt="Objects"
              src="/landing/figmaAssets/objects-1.svg"
            />
          </header>

          <div className="flex items-center justify-center gap-16">
            {statsData.map((stat, index) => (
              <Card
                key={index}
                className="w-80 h-[280px] flex items-center justify-center p-16 rounded-[32px] border-[none] before:content-[''] before:absolute before:inset-0 before:p-0.5 before:rounded-[32px] before:[background:linear-gradient(274deg,rgba(103,58,183,1)_0%,rgba(0,191,166,1)_100%)] before:[-webkit-mask:linear-gradient(#fff_0_0)_content-box,linear-gradient(#fff_0_0)] before:[-webkit-mask-composite:xor] before:[mask-composite:exclude] before:z-[1] before:pointer-events-none relative"
              >
                <CardContent className="flex flex-col items-center gap-4 p-0">
                  <div className="font-h2 font-[number:var(--h2-font-weight)] text-[#000000] text-[length:var(--h2-font-size)] text-center tracking-[var(--h2-letter-spacing)] leading-[var(--h2-line-height)] [font-style:var(--h2-font-style)]">
                    {stat.number}
                  </div>
                  <div className="font-body font-[number:var(--body-font-weight)] text-[length:var(--body-font-size)] text-center tracking-[var(--body-letter-spacing)] leading-[var(--body-line-height)] [font-style:var(--body-font-style)]">
                    <span className="text-[#00bfa699]">{stat.description}</span>
                    <span className="text-[#673ab7]">{stat.highlight}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
