import React from "react";
import { useRoute, useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ArrowLeft, MapPin, Users, Calendar, Globe, Star } from "lucide-react";

// Sample company data
const sampleCompanies = [
  {
    id: 1,
    name: "Infosys Ltd",
    logo: "/figmaAssets/image-18.png",
    description: "Infosys is a global leader in next-generation digital services and consulting. We help clients in more than 50 countries to navigate their digital transformation.",
    industry: "Information Technology",
    size: "200,000+ employees",
    founded: "1981",
    headquarters: "Bengaluru, Karnataka, India",
    website: "https://www.infosys.com",
    rating: 4.2,
    benefits: ["Health Insurance", "Flexible Work Hours", "Learning & Development", "Performance Bonus"],
    culture: "Innovation-driven culture with focus on employee growth and digital transformation excellence.",
    openPositions: [
      {
        id: 1,
        title: "Associate Business Analyst",
        location: "Bengaluru, Karnataka",
        type: "Full-time",
        salary: "₹6 LPA – ₹8 LPA"
      },
      {
        id: 2,
        title: "Software Engineer",
        location: "Pune, Maharashtra",
        type: "Full-time",
        salary: "₹7 LPA – ₹10 LPA"
      },
      {
        id: 3,
        title: "Data Analyst",
        location: "Hyderabad, Telangana",
        type: "Full-time",
        salary: "₹6.5 LPA – ₹9 LPA"
      }
    ]
  }
];

export const CompanyProfilePage = (): JSX.Element => {
  const [match, params] = useRoute("/company/:id");
  const [location, setLocation] = useLocation();
  
  const companyId = params?.id ? parseInt(params.id) : 1;
  const company = sampleCompanies.find(c => c.id === companyId) || sampleCompanies[0];

  const handleBack = () => {
    setLocation("/");
  };

  const handleJobClick = (jobId: number) => {
    setLocation(`/job/${jobId}`);
  };

  return (
    <div className="bg-neutral-100 min-h-screen">
      {/* Header */}
      <header className="w-full h-[82px] bg-[#673ab799] border-b-[0.5px] border-solid border-[#673ab733] relative">
        <div className="flex items-center px-[100px] py-0 h-full">
          <Button
            variant="ghost"
            onClick={handleBack}
            className="mr-4 text-white hover:bg-white/10"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Jobs
          </Button>
          <div className="bg-gradient-to-r from-[#673ab7] to-[#00bfa6] bg-clip-text text-transparent [font-family:'Sora',Helvetica] font-bold text-2xl leading-normal">
            GrowIQ
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto p-8">
        {/* Company Header */}
        <Card className="mb-8">
          <CardContent className="p-8">
            <div className="flex items-start gap-6 mb-6">
              <div className="w-24 h-24 rounded-lg border border-[#673ab7] flex items-center justify-center p-2">
                <img
                  className="w-full h-full object-contain"
                  alt={`${company.name} logo`}
                  src={company.logo}
                />
              </div>
              
              <div className="flex-1">
                <h1 className="font-h5 font-[number:var(--h5-font-weight)] text-[#673ab7] text-[length:var(--h5-font-size)] mb-2">
                  {company.name}
                </h1>
                
                <div className="flex items-center gap-6 mb-4">
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-[#00000080]" />
                    <span className="font-body text-[#000000b2]">
                      {company.headquarters}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-[#00000080]" />
                    <span className="font-body text-[#000000b2]">
                      {company.size}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-[#00000080]" />
                    <span className="font-body text-[#000000b2]">
                      Founded {company.founded}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <Star className="w-4 h-4 text-yellow-500" />
                    <span className="font-body text-[#000000b2]">
                      {company.rating}/5.0
                    </span>
                  </div>
                </div>

                <div className="flex gap-4">
                  <Badge variant="outline" className="bg-[#00bfa61a] border-[#673ab780]">
                    <span className="font-caption text-primay">{company.industry}</span>
                  </Badge>
                  
                  <Button
                    onClick={() => window.open(company.website, '_blank')}
                    variant="outline"
                    className="border-[#673ab7] text-[#673ab7]"
                  >
                    <Globe className="w-4 h-4 mr-2" />
                    Visit Website
                  </Button>
                </div>
              </div>
            </div>

            <p className="font-caption text-[#000000b2] text-base leading-relaxed">
              {company.description}
            </p>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Open Positions */}
            <Card>
              <CardHeader>
                <CardTitle className="font-h5 text-[#673ab7]">Open Positions ({company.openPositions.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {company.openPositions.map((job) => (
                    <div 
                      key={job.id}
                      onClick={() => handleJobClick(job.id)}
                      className="border border-[#673ab733] rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-body font-semibold text-[#673ab7] mb-1">{job.title}</h3>
                          <div className="flex items-center gap-4 text-sm text-[#000000b2]">
                            <div className="flex items-center gap-1">
                              <MapPin className="w-3 h-3" />
                              {job.location}
                            </div>
                            <span>•</span>
                            <span>{job.type}</span>
                            <span>•</span>
                            <span>{job.salary}</span>
                          </div>
                        </div>
                        <Button 
                          size="sm"
                          className="bg-[#673ab7] hover:bg-[#673ab7]/90 text-white"
                        >
                          Apply
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Company Culture */}
            <Card>
              <CardHeader>
                <CardTitle className="font-h5 text-[#673ab7]">Company Culture</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="font-caption text-[#000000b2] text-base leading-relaxed">
                  {company.culture}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Company Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="font-h5 text-[#673ab7]">Company Overview</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="font-caption font-semibold mb-1">Industry</p>
                  <p className="font-caption text-[#000000b2]">{company.industry}</p>
                </div>
                
                <Separator />
                
                <div>
                  <p className="font-caption font-semibold mb-1">Company Size</p>
                  <p className="font-caption text-[#000000b2]">{company.size}</p>
                </div>
                
                <Separator />
                
                <div>
                  <p className="font-caption font-semibold mb-1">Founded</p>
                  <p className="font-caption text-[#000000b2]">{company.founded}</p>
                </div>
                
                <Separator />
                
                <div>
                  <p className="font-caption font-semibold mb-1">Headquarters</p>
                  <p className="font-caption text-[#000000b2]">{company.headquarters}</p>
                </div>
              </CardContent>
            </Card>

            {/* Benefits */}
            <Card>
              <CardHeader>
                <CardTitle className="font-h5 text-[#673ab7]">Benefits & Perks</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {company.benefits.map((benefit, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-[#00bfa6] rounded-full" />
                      <span className="font-caption text-[#000000b2]">{benefit}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="font-h5 text-[#673ab7]">Follow Company</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full bg-[#673ab7] hover:bg-[#673ab7]/90 text-white">
                  Follow Company
                </Button>
                <Button 
                  variant="outline"
                  className="w-full border-[#673ab7] text-[#673ab7]"
                >
                  Share Company
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};