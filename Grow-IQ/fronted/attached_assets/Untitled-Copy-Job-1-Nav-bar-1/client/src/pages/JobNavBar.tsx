import React from "react";
import { NavigationHeader } from "@/components/ui/navigation-header";
import { JobListSection } from "./sections/JobListSection";

export const JobNavBar = (): JSX.Element => {

  return (
    <div className="bg-neutral-100 w-screen min-h-screen flex flex-col" style={{ transform: 'none' }}>
      <NavigationHeader title="Jobs" showBackButton={false} />

      {/* Main Content Area - properly aligned */}
      <main className="flex-1 bg-white shadow-inner ml-[102px]">
        <JobListSection />
      </main>
    </div>
  );
};
