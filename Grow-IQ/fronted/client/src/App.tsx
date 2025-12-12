import { Switch, Route, useLocation } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import NotFound from "@/pages/not-found";
import { BubbleAnimation } from "@/components/ui/bubble-animation";
import { FigmaPageTransition } from "@/components/ui/figma-gradient-ball";
import { TransitionProvider, usePageTransition } from "@/contexts/TransitionContext";

import { HomePage } from "@/pages/HomePage";
import LandingPage from "@/pages/LandingPage";
import { JobNavBar } from "@/pages/JobNavBar";
import { Layout } from "@/components/Layout";
import { GlobalNavigation } from "@/components/GlobalNavigation";
import { JobDetailsPage } from "@/pages/JobDetailsPage";
import { ApplyJobPage } from "@/pages/ApplyJobPage";
import { UserProfilePage } from "@/pages/UserProfilePage";
import { CompanyProfilePage } from "@/pages/CompanyProfilePage";
import { DashboardPage } from "@/pages/DashboardPage";
import { LoginPage } from "@/pages/LoginPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { WorkshopPage } from "@/pages/WorkshopPage";
import { ResumePage } from "@/pages/ResumePage";
import { ResumeathonPage } from "@/pages/ResumeathonPage";
import { CulturalEventsPage } from "@/pages/CulturalEventsPage";
import { HRDeskPage } from "@/pages/HRDeskPage";
// MOCK INTERVIEW MODULE - DISCONNECTED (can be reconnected in future)
// import { MockInterviewPage } from "@/pages/MockInterviewPage";
// import { MockInterviewReportsPage } from "@/pages/MockInterviewReportsPage";
// import { GoogleMeetInterviewPage } from "@/pages/GoogleMeetInterviewPage";
import { UserProfileViewPage } from "@/pages/UserProfileViewPage";
import { NetworkPage } from "@/pages/NetworkPage";
import { MessagingPage } from "@/pages/MessagingPage";
import { AdminDashboard } from "@/pages/AdminDashboard";
import { AdminDesk } from "@/pages/AdminDesk";
import { WorkshopParticipantsPage } from "@/pages/WorkshopParticipantsPage";
import CulturalParticipantsPage from "./pages/CulturalParticipantsPage";

function Router() {
  return (
    <Switch>
      {/* Add pages below */}
      <Route path="/" component={LandingPage} />
      <Route path="/home" component={HomePage} />
      <Route path="/jobs" component={JobNavBar} />
      <Route path="/course/:id" component={WorkshopPage} />
      <Route path="/job/:id" component={JobDetailsPage} />
      <Route path="/apply/:id" component={ApplyJobPage} />
      <Route path="/profile" component={UserProfilePage} />
      <Route path="/user/:id" component={UserProfileViewPage} />
      <Route path="/company/:id" component={CompanyProfilePage} />
      <Route path="/dashboard" component={DashboardPage} />
      <Route path="/login" component={LoginPage} />
      <Route path="/signup" component={LoginPage} />
      {/* Support auth-prefixed routes served by backend */}
      <Route path="/auth/login" component={LoginPage} />
      <Route path="/auth/signup" component={LoginPage} />
      <Route path="/settings" component={SettingsPage} />
      {/* More dropdown pages */}
      <Route path="/workshop" component={WorkshopPage} />
      <Route path="/workshop/:id/participants" component={WorkshopParticipantsPage} />
      <Route path="/resume" component={ResumePage} />
      <Route path="/resumeathon" component={ResumeathonPage} />
      <Route path="/cultural-events/:id/participants" component={CulturalParticipantsPage} />
      {/* MOCK INTERVIEW MODULE - DISCONNECTED (can be reconnected in future)
      <Route path="/mock-interview" component={MockInterviewPage} />
      <Route path="/mock-interview/video" component={GoogleMeetInterviewPage} />
      <Route path="/mock-interview/reports" component={MockInterviewReportsPage} />
      */}
      <Route path="/cultural-events" component={CulturalEventsPage} />
      {/* HR-only page (navigable via HR Desk in More menu). Using Home for now; replace with actual HR desk page when available. */}
      <Route path="/hr-desk" component={HRDeskPage} />
      {/* Network and Messaging pages */}
      <Route path="/network" component={NetworkPage} />
      <Route path="/messaging" component={MessagingPage} />
      {/* Admin Dashboard */}
      <Route path="/admin" component={AdminDashboard} />
      {/* Admin Desk */}
      <Route path="/admin-desk" component={AdminDesk} />
      {/* Fallback to 404 */}
      <Route component={NotFound} />
    </Switch>
  );
}

function AppContent() {
  const { isTransitioning } = usePageTransition();
  const [location] = useLocation();
  const showLayout = !(location === "/" || location === "/login");
  const hideGlobalNav = location === "/auth/login" || location === "/login";

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100">
      {/* Global Navigation - fixed to screen */}
      {!hideGlobalNav && <GlobalNavigation />}
      
      {/* Background pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5" />
      
      {/* Main content with Figma gradient ball transitions */}
      <FigmaPageTransition 
        isTransitioning={isTransitioning}
        ballSize="xl"
        bounceType="medium"
        className="relative z-10"
      >
        <Toaster />
        {showLayout ? (
          <Layout>
            <Router />
          </Layout>
        ) : (
          <Router />
        )}
      </FigmaPageTransition>
      
      {/* Optional bubble animation overlay */}
      <BubbleAnimation isVisible={isTransitioning} />
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TransitionProvider>
        <AppContent />
      </TransitionProvider>
    </QueryClientProvider>
  );
}

export default App;
