import React, { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Input } from "@/components/ui/input";
import { Search, Filter } from "lucide-react";
import { BounceButton } from "@/components/ui/bounce-animation";
import { usePageTransition } from "@/hooks/usePageTransition";

const jobListings = [
  {
    id: 1,
    company: "Infosys Ltd",
    logo: "/figmaAssets/image-18.png",
    title: "Associate Business Analyst",
    location: "Bengaluru, Karnataka",
    timePosted: "2 hours ago",
    description:
      "Join Infosys as an Associate Business Analyst and play a vital role in project delivery, data analysis, and stakeholder communication. You'll work with cross-functional teams to gather requirements, analyze business needs, and contribute to digital transformation solutions for global clients.",
    jobType: "Full-time",
    salary: "₹6 LPA – ₹8 LPA",
  },
  {
    id: 2,
    company: "TCS",
    logo: "/figmaAssets/th--8--1.png",
    title: "Cloud Support Engineer",
    location: "Chennai, Tamil Nadu",
    timePosted: "5 hours ago",
    description:
      "TCS is seeking a Cloud Support Engineer responsible for managing and supporting Azure and AWS-based environments. You'll troubleshoot deployment issues, assist DevOps workflows, and ensure uptime and performance of cloud resources.",
    jobType: "Full-time",
    salary: "₹7.5 LPA – ₹10 LPA",
  },
  {
    id: 3,
    company: "HCL Tech",
    logo: "/figmaAssets/th--4--1.png",
    title: "UI/UX Designer – Mid Level",
    location: "Noida, Uttar Pradesh",
    timePosted: "1 day ago",
    description:
      "We're looking for a creative UI/UX Designer to join our product team. You will design mobile and web interfaces for enterprise software, participate in user research, and turn ideas into functional, delightful user experiences using Figma and Adobe XD.",
    jobType: "Full-time / Hybrid",
    salary: "₹9 LPA – ₹12 LPA",
  },
  {
    id: 4,
    company: "Accenture",
    logo: "/figmaAssets/th--2--1.png",
    title: "Cybersecurity Analyst",
    location: "Gurugram, Haryana",
    timePosted: "8 hours ago",
    description:
      "Accenture is hiring a Cybersecurity Analyst to monitor, detect, and respond to cyber threats using modern tools and SIEM systems. You'll work in a fast-paced security team environment focused on keeping critical systems secure.",
    jobType: "Full-time",
    salary: "₹10 LPA – ₹14 LPA",
  },
  {
    id: 5,
    company: "Zoho",
    logo: "/figmaAssets/th--1--1.png",
    title: "Software Developer – Backend (Python)",
    location: "Coimbatore, Tamil Nadu",
    timePosted: "3 hours ago",
    description:
      "At Zoho, we are looking for backend Python developers to build high-performance APIs, design scalable backend architecture, and collaborate with product teams. Experience with Django, Flask, or FastAPI and cloud platforms is a big plus.",
    jobType: "Full-time / Remote",
    salary: "₹8.5 LPA – ₹11 LPA",
  },
];

export const JobListSection = (): JSX.Element => {
  const { navigateWithBubbles } = usePageTransition();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedLocation, setSelectedLocation] = useState("");
  const [selectedJobType, setSelectedJobType] = useState("");

  // Filter jobs based on search criteria
  const filteredJobs = jobListings.filter(job => {
    const matchesSearch = job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLocation = !selectedLocation || job.location.toLowerCase().includes(selectedLocation.toLowerCase());
    const matchesJobType = !selectedJobType || job.jobType.toLowerCase().includes(selectedJobType.toLowerCase());
    
    return matchesSearch && matchesLocation && matchesJobType;
  });

  const handleJobClick = (jobId: number) => {
    navigateWithBubbles(`/job/${jobId}`);
  };

  return (
    <div className="w-full h-full flex flex-col">
      {/* Search and Filter Section - perfectly aligned */}
      <div className="bg-gradient-to-r from-white to-neutral-50 p-8 border-b border-[#673ab733] shadow-sm">
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Search Bar - centered and prominent */}
          <div className="relative max-w-2xl mx-auto">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-[#673ab7] w-5 h-5" />
            <Input
              placeholder="Search jobs, companies, or keywords..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-12 pr-4 py-3 text-lg border-2 border-[#673ab733] focus:border-[#673ab7] rounded-xl shadow-sm"
            />
          </div>
          
          {/* Filters - evenly spaced and aligned */}
          <div className="flex justify-center items-center gap-6 flex-wrap">
            <div className="flex-1 min-w-[220px] max-w-[280px]">
              <Input
                placeholder="Enter location..."
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
                className="border-2 border-[#673ab733] focus:border-[#673ab7] rounded-lg py-2.5"
              />
            </div>
            <div className="flex-1 min-w-[180px] max-w-[220px]">
              <select
                value={selectedJobType}
                onChange={(e) => setSelectedJobType(e.target.value)}
                className="w-full h-11 px-4 border-2 border-[#673ab733] rounded-lg focus:border-[#673ab7] focus:outline-none bg-white transition-colors"
              >
                <option value="">All Job Types</option>
                <option value="full-time">Full-time</option>
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
              </select>
            </div>
            <BounceButton
              variant="secondary"
              onClick={() => {
                setSearchTerm("");
                setSelectedLocation("");
                setSelectedJobType("");
              }}
              className="border-2 border-[#673ab7] text-[#673ab7] hover:bg-[#673ab710] transition-all duration-200 px-6 py-2.5"
              size="md"
            >
              <Filter className="w-5 h-5 mr-2" />
              Clear Filters
            </BounceButton>
          </div>
          
          {/* Results Count - centered */}
          <div className="text-center text-sm text-[#000000b2] font-medium">
            Showing {filteredJobs.length} of {jobListings.length} jobs
          </div>
        </div>
      </div>

      {/* Job Listings - properly scrollable and aligned */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-6xl mx-auto p-6">
          <div className="flex flex-col gap-6">
          {filteredJobs.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-[#000000b2] text-lg mb-4">No jobs found matching your criteria</p>
              <BounceButton
                onClick={() => {
                  setSearchTerm("");
                  setSelectedLocation("");
                  setSelectedJobType("");
                }}
                variant="primary"
                size="md"
                className="bg-gradient-to-r from-[#673ab7] to-[#5e35b1] hover:from-[#5e35b1] hover:to-[#673ab7]"
              >
                Clear All Filters
              </BounceButton>
            </div>
          ) : (
            filteredJobs.map((job) => (
              <Card
                key={job.id}
                onClick={() => handleJobClick(job.id)}
                className="w-full h-[227px] rounded-2xl border border-solid border-[#673ab733] shadow-[2px_0px_2px_#673ab740,0px_2px_2px_#673ab740] overflow-hidden cursor-pointer hover:shadow-xl transition-all duration-300 hover:scale-[1.03] hover:rotate-1 active:scale-[0.98] bg-gradient-to-r from-white to-neutral-50"
              >
            <CardContent className="p-0 h-full relative">
              <div className="absolute w-[149px] h-[107px] top-0 left-0 rounded-[16px_8px_8px_0px] overflow-hidden border-r-[0.2px] [border-right-style:solid] border-b-[0.2px] [border-bottom-style:solid] border-[#673ab7] flex items-center justify-center">
                <img
                  className="w-24 h-[60px] object-cover"
                  alt={`${job.company} logo`}
                  src={job.logo}
                />
              </div>

              <div className="absolute top-[38px] left-40 [font-family:'Sora',Helvetica] font-normal text-app-secondary text-[23px] text-center tracking-[0] leading-[normal]">
                {job.company}
              </div>

              <Separator className="absolute w-full h-px top-[107px] left-0" />

              <div className="flex flex-col w-[385px] items-center gap-1 absolute top-[17px] left-[404px]">
                <div className="relative self-stretch mt-[-1.00px] font-h5 font-[number:var(--h5-font-weight)] text-[#673ab7] text-[length:var(--h5-font-size)] text-center tracking-[var(--h5-letter-spacing)] leading-[var(--h5-line-height)] [font-style:var(--h5-font-style)]">
                  {job.title}
                </div>

                <div className="inline-flex items-center justify-center gap-4 relative flex-[0_0_auto]">
                  <div className="relative w-fit mt-[-1.00px] font-body font-[number:var(--body-font-weight)] text-[#00000080] text-[length:var(--body-font-size)] text-center tracking-[var(--body-letter-spacing)] leading-[var(--body-line-height)] [font-style:var(--body-font-style)]">
                    {job.location}
                  </div>

                  <div className="relative w-[5px] h-[5px] bg-[#00000080] rounded-[2.5px]" />

                  <div className="relative w-fit mt-[-1.00px] font-body font-[number:var(--body-font-weight)] text-[#00000080] text-[length:var(--body-font-size)] text-center tracking-[var(--body-letter-spacing)] leading-[var(--body-line-height)] [font-style:var(--body-font-style)]">
                    {job.timePosted}
                  </div>
                </div>
              </div>

              <div className="absolute w-[1056px] top-[125px] left-[63px] font-caption font-[number:var(--caption-font-weight)] text-[#000000b2] text-[length:var(--caption-font-size)] tracking-[var(--caption-letter-spacing)] leading-[var(--caption-line-height)] [font-style:var(--caption-font-style)]">
                {job.description}
              </div>

              <div className="inline-flex items-center gap-4 absolute top-[175px] left-[63px]">
                <Badge
                  variant="outline"
                  className="inline-flex items-center justify-center gap-2.5 p-2.5 bg-[#00bfa61a] rounded-sm border-[0.4px] border-solid border-[#673ab780]"
                >
                  <span className="font-caption font-[number:var(--caption-font-weight)] text-primay text-[length:var(--caption-font-size)] tracking-[var(--caption-letter-spacing)] leading-[var(--caption-line-height)] [font-style:var(--caption-font-style)]">
                    {job.jobType}
                  </span>
                </Badge>

                <Badge
                  variant="outline"
                  className="inline-flex items-center justify-center gap-2.5 p-2.5 bg-[#00bfa61a] rounded-sm border-[0.4px] border-solid border-[#673ab780]"
                >
                  <span className="font-caption font-[number:var(--caption-font-weight)] text-primay text-[length:var(--caption-font-size)] tracking-[var(--caption-letter-spacing)] leading-[var(--caption-line-height)] [font-style:var(--caption-font-style)]">
                    {job.salary}
                  </span>
                </Badge>
              </div>
                </CardContent>
              </Card>
            ))
          )}
          </div>
        </div>
      </div>
    </div>
  );
};
