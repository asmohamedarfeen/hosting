import React from "react";
import { JobListSection } from "./sections/JobListSection";

export const JobNavBar = (): JSX.Element => {
  return (
    <div className="flex-1 bg-white">
      <JobListSection />
    </div>
  );
};
