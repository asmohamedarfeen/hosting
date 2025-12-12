import React from "react";

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout = ({ children }: LayoutProps): JSX.Element => {
  return (
    <div className="bg-neutral-100 w-screen min-h-screen flex flex-col relative" style={{ transform: 'none' }}>
      {/* Main Content Area - properly aligned */}
      <main className="flex-1 bg-white shadow-inner ml-[102px]">
        {children}
      </main>
    </div>
  );
};