import React from "react";
import { Button } from "@/components/ui/button";
import { CallToActionSection } from "./sections/CallToActionSection";
import { CompaniesSection } from "./sections/CompaniesSection";
import { HeroSection } from "./sections/HeroSection";
import { OpportunitiesSection } from "./sections/OpportunitiesSection";
import { StatsSection } from "./sections/StatsSection";

const companyNames = [
  "Wipro",
  "Zoho",
  "Accenture", 
  "TCS",
  "Infosys",
  "Microsoft",
  "Google",
  "Amazon",
  "Deloitte",
  "IBM",
  "Oracle",
  "Capgemini"
];

export const LandingPage = (): JSX.Element => {
  return (
    <div className="bg-neutral-100 overflow-hidden w-full relative">
      {/* Background decorative elements */}
      <div className="fixed top-[-250px] left-[-276px] w-[500px] h-[500px] bg-orange-500 rounded-[250px] blur-[250px] opacity-50 pointer-events-none" />
      <div className="fixed top-[590px] left-[1190px] w-[500px] h-[500px] bg-orange-500 rounded-[250px] blur-[250px] opacity-50 pointer-events-none" />

      {/* Main content sections */}
      <div className="flex flex-col w-full">
        {/* Header/Navigation */}
        <StatsSection />

        {/* Main Hero Section - "Your Next Career Move Starts Here" */}
        <CompaniesSection />

        {/* Secondary Hero Section - "Where your career takes off" */}
        <section className="w-full px-8 py-16 relative">
          <div className="max-w-7xl mx-auto text-center">
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-8 [font-family:'Sora',Helvetica]">
              <span className="bg-[linear-gradient(274deg,rgba(103,58,183,1)_0%,rgba(0,191,166,1)_100%)] [-webkit-background-clip:text] bg-clip-text [-webkit-text-fill-color:transparent] [text-fill-color:transparent]">
                Where Your Career Takes Off
              </span>
              <br />
              <span className="text-black">Tech or Core</span>
            </h1>
            <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
              Join thousands of students landing jobs in both tech and core industries. 
              Explore companies, apply to real roles, get expert advice — all in one platform.
            </p>
            <div className="flex justify-center gap-6">
              <Button 
                className="px-8 py-4 bg-purple-600 text-white rounded-full text-lg font-bold hover:bg-purple-700 transition-colors" 
                data-testid="button-begin-journey"
                onClick={() => {
                  console.log('Begin Journey button clicked');
                  window.location.assign('/auth/signup');
                }}
              >
                Begin Journey
              </Button>
              <Button 
                variant="outline" 
                className="px-8 py-4 bg-white border-2 border-gray-300 rounded-full text-lg font-bold hover:bg-gray-50 transition-colors" 
                data-testid="button-explore-companies"
                onClick={() => {
                  console.log('Explore Companies button clicked');
                  window.location.replace('http://localhost:8000/login');
                }}
              >
                Explore Companies
              </Button>
            </div>
          </div>
        </section>

        {/* Company names marquee */}
        <section className="w-full py-8 px-8 relative">
          <div className="w-full max-w-[1440px] mx-auto h-[100px] overflow-hidden">
            <div className="flex items-center gap-[80px] animate-marquee" style={{ '--duration': '30s', '--gap': '80px' } as React.CSSProperties}>
              {companyNames.map((companyName: string, index: number) => (
                <div
                  key={`company-${index}`}
                  className="flex-shrink-0 text-4xl font-bold text-gray-700 hover:text-primary transition-colors duration-300 whitespace-nowrap"
                  data-testid={`text-company-${companyName}`}
                >
                  {companyName}
                </div>
              ))}
              {/* Duplicate for seamless loop */}
              {companyNames.map((companyName: string, index: number) => (
                <div
                  key={`company-duplicate-${index}`}
                  className="flex-shrink-0 text-4xl font-bold text-gray-700 hover:text-primary transition-colors duration-300 whitespace-nowrap"
                  data-testid={`text-company-duplicate-${companyName}`}
                >
                  {companyName}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Features Section - Platform Benefits */}
        <section className="w-full py-16 px-8 bg-white">
          <div className="max-w-7xl mx-auto">
            <h2 className="text-5xl font-bold text-center mb-4 [font-family:'Sora',Helvetica]">
              <span className="bg-[linear-gradient(274deg,rgba(103,58,183,1)_0%,rgba(0,191,166,1)_100%)] [-webkit-background-clip:text] bg-clip-text [-webkit-text-fill-color:transparent] [text-fill-color:transparent]">
                Explore Companies.
              </span>
              <br />
              <span className="text-black">Apply to Real Roles. Get Expert Advice.</span>
            </h2>
            <p className="text-xl text-center text-gray-600 mb-12 max-w-3xl mx-auto">
              All in one integrated platform designed for your career success
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center p-8 rounded-2xl bg-gradient-to-br from-purple-50 to-teal-50">
                <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-teal-600 rounded-full mx-auto mb-6 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold mb-4 text-gray-900">Verified Companies</h3>
                <p className="text-gray-600">Connect with top-tier companies across tech and core industries. Every opportunity is verified and legitimate.</p>
              </div>

              <div className="text-center p-8 rounded-2xl bg-gradient-to-br from-orange-50 to-yellow-50">
                <div className="w-16 h-16 bg-gradient-to-r from-orange-600 to-yellow-600 rounded-full mx-auto mb-6 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold mb-4 text-gray-900">Expert Guidance</h3>
                <p className="text-gray-600">Get personalized advice from industry experts and career coaches who understand your field.</p>
              </div>

              <div className="text-center p-8 rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full mx-auto mb-6 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold mb-4 text-gray-900">Real Opportunities</h3>
                <p className="text-gray-600">Access genuine job openings with direct recruiter contact. No fake listings, just real career opportunities.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Why GrowIQ Section */}
        <OpportunitiesSection />

        {/* AI-Powered Career Path Section */}
        <HeroSection />

        {/* Testimonials Section */}
        <section className="w-full py-20 bg-white">
          <div className="max-w-7xl mx-auto px-8">
            <h2 className="text-5xl font-bold text-center mb-4 [font-family:'Sora',Helvetica]">
              <span className="bg-[linear-gradient(274deg,rgba(103,58,183,1)_0%,rgba(0,191,166,1)_100%)] [-webkit-background-clip:text] bg-clip-text [-webkit-text-fill-color:transparent] [text-fill-color:transparent]">
                Success Stories
              </span>
            </h2>
            <p className="text-xl text-center text-gray-600 mb-16 max-w-3xl mx-auto">
              Hear from students who transformed their careers with GrowIQ
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="bg-gradient-to-br from-purple-50 to-teal-50 rounded-2xl p-8 relative overflow-hidden" data-testid="testimonial-priya">
                <div className="relative z-10">
                  <div className="flex items-center mb-6">
                    <img
                      className="w-16 h-16 rounded-full object-cover mr-4"
                      alt="Priya Sharma"
                      src="/landing/figmaAssets/image-12.png"
                    />
                    <div>
                      <h4 className="font-bold text-lg text-gray-900">Priya Sharma</h4>
                      <p className="text-gray-600">Software Engineer at Google</p>
                    </div>
                  </div>
                  <p className="text-gray-700 italic leading-relaxed">
                    "GrowIQ helped me land my dream job at Google! The AI matching was incredibly accurate, and the expert guidance made all the difference in my interview preparation."
                  </p>
                  <div className="flex text-yellow-400 mt-4">
                    {"★".repeat(5)}
                  </div>
                </div>
                <div className="absolute top-4 right-4 text-6xl text-purple-200 opacity-50">"</div>
              </div>

              <div className="bg-gradient-to-br from-orange-50 to-yellow-50 rounded-2xl p-8 relative overflow-hidden" data-testid="testimonial-rajesh">
                <div className="relative z-10">
                  <div className="flex items-center mb-6">
                    <img
                      className="w-16 h-16 rounded-full object-cover mr-4"
                      alt="Rajesh Kumar"
                      src="/landing/figmaAssets/image-13.png"
                    />
                    <div>
                      <h4 className="font-bold text-lg text-gray-900">Rajesh Kumar</h4>
                      <p className="text-gray-600">Data Analyst at Wipro</p>
                    </div>
                  </div>
                  <p className="text-gray-700 italic leading-relaxed">
                    "From college to corporate in just 3 months! The platform connected me directly with hiring managers, and the process was completely transparent."
                  </p>
                  <div className="flex text-yellow-400 mt-4">
                    {"★".repeat(5)}
                  </div>
                </div>
                <div className="absolute top-4 right-4 text-6xl text-orange-200 opacity-50">"</div>
              </div>

              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8 relative overflow-hidden" data-testid="testimonial-anita">
                <div className="relative z-10">
                  <div className="flex items-center mb-6">
                    <img
                      className="w-16 h-16 rounded-full object-cover mr-4"
                      alt="Anita Patel"
                      src="/landing/figmaAssets/image-12.png"
                    />
                    <div>
                      <h4 className="font-bold text-lg text-gray-900">Anita Patel</h4>
                      <p className="text-gray-600">Marketing Manager at TCS</p>
                    </div>
                  </div>
                  <p className="text-gray-700 italic leading-relaxed">
                    "The career guidance was phenomenal! I switched from engineering to marketing and found my passion. The mentors really understood my goals."
                  </p>
                  <div className="flex text-yellow-400 mt-4">
                    {"★".repeat(5)}
                  </div>
                </div>
                <div className="absolute top-4 right-4 text-6xl text-blue-200 opacity-50">"</div>
              </div>
            </div>
          </div>
        </section>

        {/* Success Stories/Stats Section */}
        <CallToActionSection />

        {/* Final CTA Section */}
        <section className="w-full py-16 px-8 bg-gradient-to-r from-purple-600 to-teal-600">
          <div className="max-w-4xl mx-auto text-center text-white">
            <h2 className="text-5xl font-bold mb-6 [font-family:'Sora',Helvetica]">
              Ready to Take Off?
            </h2>
            <p className="text-xl mb-8 opacity-90">
              Join thousands of students who have already found their dream careers. 
              Your next opportunity is just one click away.
            </p>
            <div className="flex justify-center gap-6">
              <Button 
                className="px-8 py-4 bg-white text-purple-600 rounded-full text-lg font-bold hover:bg-gray-100 transition-colors" 
                data-testid="button-create-profile-final"
                onClick={() => window.location.replace('http://localhost:8000/login')}
              >
                Create Your Profile Now
              </Button>
              <Button 
                variant="outline" 
                className="px-8 py-4 bg-transparent border-2 border-white text-white rounded-full text-lg font-bold hover:bg-white/10 transition-colors" 
                data-testid="button-learn-more"
                onClick={() => window.location.replace('http://localhost:8000/login')}
              >
                Learn More
              </Button>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="w-full bg-gray-900 text-white py-16">
          <div className="max-w-7xl mx-auto px-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
              {/* Brand Section */}
              <div className="col-span-1 md:col-span-2">
                <div className="relative w-fit bg-[linear-gradient(274deg,rgba(103,58,183,1)_0%,rgba(0,191,166,1)_100%)] [-webkit-background-clip:text] bg-clip-text [-webkit-text-fill-color:transparent] [text-fill-color:transparent] [font-family:'Sora',Helvetica] font-bold text-3xl tracking-[0] leading-[normal] mb-4">
                  GrowIQ
                </div>
                <p className="text-gray-300 mb-6 max-w-md">
                  Where your career takes off. Connect with top companies, access real opportunities, and get expert guidance for both tech and core industries.
                </p>
                <div className="flex space-x-4">
                  <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center cursor-pointer hover:bg-purple-500 transition-colors" data-testid="link-twitter" aria-label="Follow us on Twitter">
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M6.29 18.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0020 3.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.073 4.073 0 01.8 7.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 010 16.407a11.616 11.616 0 006.29 1.84"/>
                    </svg>
                  </a>
                  <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center cursor-pointer hover:bg-blue-500 transition-colors" data-testid="link-linkedin" aria-label="Connect on LinkedIn">
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M16.338 16.338H13.67V12.16c0-.995-.017-2.277-1.387-2.277-1.39 0-1.601 1.086-1.601 2.207v4.248H8.014v-8.59h2.559v1.174h.037c.356-.675 1.227-1.387 2.526-1.387 2.703 0 3.203 1.778 3.203 4.092v4.711zM5.005 6.575a1.548 1.548 0 11-.003-3.096 1.548 1.548 0 01.003 3.096zm-1.337 9.763H6.34v-8.59H3.667v8.59zM17.668 1H2.328C1.595 1 1 1.581 1 2.298v15.403C1 18.418 1.595 19 2.328 19h15.34c.734 0 1.332-.582 1.332-1.299V2.298C19 1.581 18.402 1 17.668 1z"/>
                    </svg>
                  </a>
                  <a href="https://instagram.com" target="_blank" rel="noopener noreferrer" className="w-10 h-10 bg-pink-600 rounded-full flex items-center justify-center cursor-pointer hover:bg-pink-500 transition-colors" data-testid="link-instagram" aria-label="Follow us on Instagram">
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M12.017 1.985a1.014 1.014 0 00-.277-.17c-.366-.156-.824-.14-1.267.15a1.014 1.014 0 00-.432.58c-.046.236-.029.477.063.69a.946.946 0 00.411.53c.3.164.677.158.97-.007.295-.165.49-.44.55-.752.062-.313-.013-.638-.189-.904-.176-.265-.466-.489-.829-.617z" clipRule="evenodd"/>
                    </svg>
                  </a>
                </div>
              </div>

              {/* Quick Links */}
              <div>
                <h4 className="font-bold text-lg mb-4">Quick Links</h4>
                <ul className="space-y-3">
                  <li><a href="http://localhost:8000/login" className="text-gray-300 hover:text-white transition-colors" data-testid="link-about">About Us</a></li>
                  <li><a href="http://localhost:8000/login" className="text-gray-300 hover:text-white transition-colors" data-testid="link-how-it-works">How It Works</a></li>
                  <li><a href="http://localhost:8000/login" className="text-gray-300 hover:text-white transition-colors" data-testid="link-pricing">Pricing</a></li>
                  <li><a href="http://localhost:8000/login" className="text-gray-300 hover:text-white transition-colors" data-testid="link-success-stories">Success Stories</a></li>
                  <li><a href="http://localhost:8000/login" className="text-gray-300 hover:text-white transition-colors" data-testid="link-blog">Blog</a></li>
                </ul>
              </div>

              {/* Support */}
              <div>
                <h4 className="font-bold text-lg mb-4">Support</h4>
                <ul className="space-y-3">
                  <li><a href="http://localhost:8000/login" className="text-gray-300 hover:text-white transition-colors" data-testid="link-help-center">Help Center</a></li>
                  <li><a href="http://localhost:8000/login" className="text-gray-300 hover:text-white transition-colors" data-testid="link-contact">Contact Us</a></li>
                  <li><a href="http://localhost:8000/login" className="text-gray-300 hover:text-white transition-colors" data-testid="link-privacy">Privacy Policy</a></li>
                  <li><a href="http://localhost:8000/login" className="text-gray-300 hover:text-white transition-colors" data-testid="link-terms">Terms of Service</a></li>
                  <li><a href="http://localhost:8000/login" className="text-gray-300 hover:text-white transition-colors" data-testid="link-careers">Careers</a></li>
                </ul>
              </div>
            </div>

            {/* Bottom Bar */}
            <div className="border-t border-gray-700 pt-8 text-center">
              <p className="text-gray-400">
                © {new Date().getFullYear()} GrowIQ. All rights reserved. Empowering careers across tech and core industries.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};
