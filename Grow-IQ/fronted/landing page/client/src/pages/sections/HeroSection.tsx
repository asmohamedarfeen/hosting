import React from "react";

export const HeroSection = (): JSX.Element => {
  return (
    <section className="flex flex-col w-full items-center gap-4 relative">
      <div className="flex flex-col items-start gap-2 relative w-full max-w-[769px]">
        <h1 className="relative w-full [font-family:'Sora',Helvetica] font-bold text-[#000000] text-[23px] text-center tracking-[0] leading-[normal]">
          AI-Powered Career Path: Precision. Speed. Success.
        </h1>

        <h2 className="relative w-full [font-family:'Sora',Helvetica] font-semibold text-[#000000] text-lg text-center tracking-[0] leading-[normal]">
          We Don&apos;t Just List Jobs. We Find Your Job.
        </h2>
      </div>

      <p className="relative w-full max-w-[769px] min-h-[101px] font-body font-[number:var(--body-font-weight)] text-[#000000] text-[length:var(--body-font-size)] text-center tracking-[var(--body-letter-spacing)] leading-[var(--body-line-height)] [font-style:var(--body-font-style)]">
        Our advanced AI system analyzes your resume, academic background,
        skills, certifications, and experience to calculate a personalized
        profile score. Using this, we match you with the most relevant job
        opportunities — not just by keywords, but by true fit. Say goodbye to
        endless searching — let AI find where you truly belong.
      </p>
    </section>
  );
};
