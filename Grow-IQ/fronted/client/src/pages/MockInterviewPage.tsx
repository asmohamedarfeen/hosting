import React from "react";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { usePageTransition } from "@/contexts/TransitionContext";
import { 
  MessageCircle, 
  Target, 
  Users, 
  Award, 
  Clock, 
  CheckCircle,
  ArrowRight,
  Lightbulb,
  TrendingUp,
  Video,
  Mic,
  FileText,
  BarChart3
} from "lucide-react";

export const MockInterviewPage = (): JSX.Element => {
  const [location, setLocation] = useLocation();
  const { navigateWithBubbles } = usePageTransition();

  const features = [
    {
      icon: MessageCircle,
      title: "Realistic Practice",
      description: "Experience interview scenarios that mirror real-world situations"
    },
    {
      icon: Target,
      title: "Role-Specific Questions",
      description: "Practice with questions tailored to your target job role"
    },
    {
      icon: Users,
      title: "Expert Feedback",
      description: "Get detailed feedback from experienced interviewers"
    },
    {
      icon: Award,
      title: "STAR Method Training",
      description: "Learn structured response techniques for behavioral questions"
    },
    {
      icon: Clock,
      title: "Time Management",
      description: "Practice answering questions within time constraints"
    },
    {
      icon: CheckCircle,
      title: "Confidence Building",
      description: "Build confidence through repeated practice sessions"
    }
  ];

  const benefits = [
    "Improve communication skills",
    "Identify areas for improvement",
    "Get familiar with interview formats",
    "Practice under pressure",
    "Refine your answers",
    "Gain insights into interviewer perception"
  ];

  const handleVideoInterview = () => {
    // Navigate to Google Meet-style interview
    navigateWithBubbles("/mock-interview/video");
  };

  const handleViewReports = () => {
    // Navigate to reports page
    navigateWithBubbles("/mock-interview/reports");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-purple-100 text-purple-800 px-4 py-2 rounded-full text-sm font-medium mb-6">
            <MessageCircle className="w-4 h-4" />
            Mock Interview Preparation
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Master Your Interview Skills
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Practice makes perfect. Take our comprehensive mock interview to build confidence and excel in your real interviews.
          </p>
        </div>

        {/* Main Content Card */}
        <Card className="mb-8 shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="text-center pb-6">
            <CardTitle className="text-3xl font-bold text-gray-900 mb-4">
              What is a Mock Interview?
            </CardTitle>
          </CardHeader>
          <CardContent className="px-8 pb-8">
            <div className="prose prose-lg max-w-none text-gray-700 leading-relaxed">
              <p className="text-lg mb-6">
                A mock interview is a simulated job interview designed to help candidates prepare for real interviews. 
                It mimics the actual interview setting and allows individuals to practice answering both common and 
                role-specific questions. These practice sessions are typically conducted by mentors, peers, career 
                coaches, or even AI tools, and are often followed by feedback to help improve performance.
              </p>
              
              <p className="text-lg mb-6">
                The goal is to build confidence, improve communication skills, and identify areas for improvement, 
                whether in answering behavioral questions or solving technical problems. Mock interviews can be 
                customized based on the job you're applying for—such as technical roles, HR screenings, or 
                case-based positions—and are a valuable way to prepare for the pressure and format of real interviews.
              </p>
              
              <p className="text-lg">
                Many candidates use mock interviews to refine their answers, get familiar with structured response 
                techniques like the STAR method, and gain insights into how interviewers might perceive them.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card key={index} className="p-6 text-center hover:shadow-lg transition-shadow duration-300 border-0 bg-white/60 backdrop-blur-sm">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Icon className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 text-sm">
                  {feature.description}
                </p>
              </Card>
            );
          })}
        </div>

        {/* Benefits Section */}
        <Card className="mb-8 shadow-xl border-0 bg-gradient-to-r from-purple-500 to-blue-600 text-white">
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-center mb-4">
              Key Benefits of Mock Interviews
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {benefits.map((benefit, index) => (
                <div key={index} className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-300 flex-shrink-0" />
                  <span className="text-white/90">{benefit}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Call to Action */}
        <Card className="text-center shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardContent className="py-12">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Target className="w-8 h-8 text-purple-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Ready to Ace Your Interview?
            </h2>
            <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
              Experience a realistic video interview and get personalized feedback to improve your interview performance.
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 max-w-2xl mx-auto">
              <div className="flex items-center gap-2 text-blue-800">
                <Mic className="w-5 h-5" />
                <span className="font-semibold">Smart Auto Voice Input</span>
              </div>
              <p className="text-blue-700 text-sm mt-1">
                The microphone will automatically start recording when the AI finishes speaking and stop when you finish talking. No need to press the mic button! You can also toggle auto-mode on/off during the interview.
              </p>
            </div>
            
            <div className="max-w-md mx-auto">
              {/* Video Call Interview */}
              <Card className="border-2 border-gray-200 hover:border-green-300 transition-all duration-300">
                <CardContent className="p-6">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Video className="w-6 h-6 text-green-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    Video Call Interview
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Google Meet-style video interview experience
                  </p>
                  <Button
                    onClick={handleVideoInterview}
                    className="w-full bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
                  >
                    <Video className="w-4 h-4 mr-2" />
                    Start Video Interview
                  </Button>
                </CardContent>
              </Card>
              
              {/* View Reports Button */}
              <div className="mt-4">
                <Button
                  onClick={handleViewReports}
                  variant="outline"
                  className="w-full border-purple-300 text-purple-700 hover:bg-purple-50"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  View Interview Reports
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Additional Info */}
        <div className="mt-12 text-center">
          <div className="inline-flex items-center gap-2 text-gray-500 text-sm">
            <Lightbulb className="w-4 h-4" />
            <span>Tip: Practice regularly to see the best results</span>
          </div>
        </div>
      </div>
    </div>
  );
};
