import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import NotFound from "@/pages/not-found";
import { BubbleAnimation } from "@/components/ui/bubble-animation";
import { PageTransitionWithBounce } from "@/components/ui/bounce-animation";
import { usePageTransition } from "@/hooks/usePageTransition";

import { JobNavBar } from "@/pages/JobNavBar";
import { JobDetailsPage } from "@/pages/JobDetailsPage";
import { ApplyJobPage } from "@/pages/ApplyJobPage";
import { UserProfilePage } from "@/pages/UserProfilePage";
import { CompanyProfilePage } from "@/pages/CompanyProfilePage";
import { DashboardPage } from "@/pages/DashboardPage";
import { LoginPage } from "@/pages/LoginPage";
import { SettingsPage } from "@/pages/SettingsPage";

function Router() {
  return (
    <Switch>
      {/* Add pages below */}
      <Route path="/" component={JobNavBar} />
      <Route path="/job/:id" component={JobDetailsPage} />
      <Route path="/apply/:id" component={ApplyJobPage} />
      <Route path="/profile" component={UserProfilePage} />
      <Route path="/company/:id" component={CompanyProfilePage} />
      <Route path="/dashboard" component={DashboardPage} />
      <Route path="/login" component={LoginPage} />
      <Route path="/settings" component={SettingsPage} />
      {/* Fallback to 404 */}
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  const { isTransitioning } = usePageTransition();
  
  return (
    <QueryClientProvider client={queryClient}>
      <div className="relative min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100">
        {/* Background pattern */}
        <div className="absolute inset-0 bg-grid-pattern opacity-5" />
        
        {/* Main content with bounce transitions */}
        <PageTransitionWithBounce 
          isTransitioning={isTransitioning}
          animationType="elastic"
          className="relative z-10"
        >
          <Toaster />
          <Router />
        </PageTransitionWithBounce>
        
        {/* Optional bubble animation overlay */}
        <BubbleAnimation isVisible={isTransitioning} />
      </div>
    </QueryClientProvider>
  );
}

export default App;
