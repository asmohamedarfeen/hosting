import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FileText, Download, Eye, Upload, Zap } from "lucide-react";
import { ResumeTester } from "@/components/ResumeTester";

export const ResumePage = (): JSX.Element => {
  const [selectedTemplate, setSelectedTemplate] = useState("modern");
  const [showResumeTester, setShowResumeTester] = useState(false);
  const [atsScore, setAtsScore] = useState<number>(() => {
    const stored = Number(localStorage.getItem('ats_latest_score') || '0');
    return Number.isFinite(stored) ? stored : 0;
  });

  const resumeTemplates = [
    {
      id: "modern",
      name: "Modern Professional",
      description: "Clean and contemporary design perfect for tech roles",
      preview: "/figmaAssets/resume-modern.jpg",
      rating: 4.9,
      downloads: 1240,
      category: "professional",
      features: ["ATS Friendly", "Modern Layout", "Tech Focused"]
    },
    {
      id: "classic",
      name: "Classic Executive",
      description: "Traditional format ideal for senior positions",
      preview: "/figmaAssets/resume-classic.jpg",
      rating: 4.7,
      downloads: 890,
      category: "executive",
      features: ["Executive Style", "Traditional", "Leadership Focus"]
    },
    {
      id: "creative",
      name: "Creative Portfolio",
      description: "Eye-catching design for creative professionals",
      preview: "/figmaAssets/resume-creative.jpg",
      rating: 4.8,
      downloads: 650,
      category: "creative",
      features: ["Visual Appeal", "Portfolio Ready", "Creative Fields"]
    },
    {
      id: "minimal",
      name: "Minimal Clean",
      description: "Simple and elegant layout for any industry",
      preview: "/figmaAssets/resume-minimal.jpg",
      rating: 4.6,
      downloads: 1100,
      category: "general",
      features: ["Minimalist", "Versatile", "Clean Design"]
    }
  ];

  const loadLatestAtsScore = async () => {
    try {
      const res = await fetch('/api/resume-scores', { credentials: 'include' });
      if (!res.ok) return;
      const data = await res.json();
      let latest: number | undefined;
      if (data && data.summary && typeof data.summary.latest_score !== 'undefined') {
        latest = Number(data.summary.latest_score);
      } else if (data && Array.isArray(data.resume_scores) && data.resume_scores.length > 0) {
        latest = Number(data.resume_scores[0].total_score);
      }
      if (Number.isFinite(latest) && (latest as number) > 0) {
        setAtsScore(latest as number);
        localStorage.setItem('ats_latest_score', String(latest));
      }
    } catch (_) {
      // Do not overwrite existing score on failure
    }
  };

  // Load latest ATS score
  useEffect(() => {
    loadLatestAtsScore();
  }, []);

  const categories = [
    { id: "all", label: "All Templates", count: resumeTemplates.length },
    { id: "professional", label: "Professional", count: resumeTemplates.filter(t => t.category === "professional").length },
    { id: "executive", label: "Executive", count: resumeTemplates.filter(t => t.category === "executive").length },
    { id: "creative", label: "Creative", count: resumeTemplates.filter(t => t.category === "creative").length },
    { id: "general", label: "General", count: resumeTemplates.filter(t => t.category === "general").length }
  ];

  // Show resume tester if activated
  if (showResumeTester) {
    return (
      <ResumeTester 
        onClose={() => setShowResumeTester(false)} 
        onScored={(score) => {
          setAtsScore(score);
          localStorage.setItem('ats_latest_score', String(score));
        }}
      />
    );
  }

  return (
    <div className="bg-neutral-100 min-h-screen">
      
      <div className="max-w-6xl mx-auto p-8">
        {/* Header Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Build Your Perfect Resume</h1>
          <p className="text-gray-600 text-lg">
            Create professional resumes that get noticed by recruiters and pass ATS filters.
          </p>
        </div>


        {/* ATS Checker Section */}
        <div className="mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Zap className="h-5 w-5 text-blue-600" />
                <span>ATS Checker</span>
              </CardTitle>
              <p className="text-sm text-gray-600">
                Optimize your resume for Applicant Tracking Systems
              </p>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                {/* ATS Score Display */}
                <div className="mb-6">
                  <div className="text-6xl font-bold text-blue-600 mb-2">
                    {atsScore}
                  </div>
                  <div className="text-2xl font-semibold text-gray-700 mb-1">
                    ATS Score
                  </div>
                  <div className="text-sm text-gray-500">
                    Overall compatibility with Applicant Tracking Systems
                  </div>
                </div>
                
                {/* Progress Bar */}
                <div className="w-full bg-gray-200 rounded-full h-3 mb-6">
                  <div 
                    className="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all duration-1000"
                    style={{ width: `${atsScore}%` }}
                  ></div>
                </div>
                
                {/* Action Button */}
                <Button 
                  className="w-full bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700 text-white font-semibold py-3 px-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300" 
                  onClick={() => setShowResumeTester(true)}
                >
                  <Zap className="h-5 w-5 mr-2" />
                  Analyze Your Resume
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Resume Templates Section */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Resume Templates</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {resumeTemplates.map((template) => (
              <Card key={template.id} className="group hover:shadow-lg transition-shadow duration-300">
                <div className="aspect-[3/4] bg-gray-100 rounded-t-lg overflow-hidden">
                  <img 
                    src={template.preview} 
                    alt={template.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                </div>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-lg">{template.name}</h3>
                    <Badge variant="secondary">{template.category}</Badge>
                  </div>
                  <p className="text-gray-600 text-sm mb-4">{template.description}</p>
                  
                  <div className="flex flex-wrap gap-1 mb-4">
                    {template.features.map((feature, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {feature}
                      </Badge>
                    ))}
                  </div>
                  
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                    <div className="flex items-center">
                      <span className="text-yellow-500">★</span>
                      <span className="ml-1">{template.rating}</span>
                    </div>
                    <div>{template.downloads} downloads</div>
                  </div>
                  
                  <div className="flex space-x-2">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="flex-1"
                      onClick={() => setSelectedTemplate(template.id)}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      Preview
                    </Button>
                    <Button 
                      size="sm" 
                      className="flex-1 bg-[#673ab7] hover:bg-[#673ab7]/90"
                    >
                      <Download className="h-4 w-4 mr-1" />
                      Download
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};