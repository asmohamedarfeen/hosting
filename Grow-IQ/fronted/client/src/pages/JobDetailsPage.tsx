import React, { useEffect, useState } from "react";
import { useRoute, useLocation } from "wouter";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ArrowLeft, MapPin, Clock, DollarSign, Building } from "lucide-react";

type JobDetail = {
  id: number;
  company: string;
  logo?: string | null;
  title: string;
  location: string;
  posted_at?: string | null;
  timePosted?: string;
  description: string;
  job_type?: string;
  jobType?: string;
  salary_range?: string;
  salary?: string;
  requirements?: string[];
  responsibilities?: string[];
  benefits?: string[];
};

export const JobDetailsPage = (): JSX.Element => {
  const [match, params] = useRoute("/job/:id");
  const [location, setLocation] = useLocation();
  
  const jobId = params?.id ? parseInt(params.id) : NaN;
  const [job, setJob] = useState<JobDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchJob = async () => {
      if (Number.isNaN(jobId)) {
        setError("Invalid job id");
        setLoading(false);
        return;
      }
      setError(null);
      setLoading(true);
      try {
        // There is no dedicated job-by-id API; reuse the search endpoint and pick the match
        const res = await fetch("/api/jobs/search", { credentials: "include" });
        if (!res.ok) throw new Error("Failed to load job");
        const data = await res.json();
        const found = (data?.jobs || []).find((j: any) => j.id === jobId);
        if (!found) {
          setError("Job not found");
          setJob(null);
        } else {
          const mapped: JobDetail = {
            id: found.id,
            company: found.company,
            title: found.title,
            location: found.location,
            description: found.description,
            job_type: found.job_type,
            jobType: found.job_type,
            salary_range: found.salary_range,
            salary: found.salary_range,
            posted_at: found.posted_at,
            requirements: found.requirements || [],
            responsibilities: found.responsibilities || [],
            benefits: found.benefits || [],
          };
          setJob(mapped);
        }
      } catch (e: any) {
        setError(e?.message || "Failed to load job");
      } finally {
        setLoading(false);
      }
    };
    fetchJob();
  }, [jobId]);

  const handleBack = () => {
    setLocation("/home");
  };

  const handleApply = () => {
    if (job) setLocation(`/apply/${job.id}`);
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
        {loading && (
          <div className="text-center text-sm text-gray-600">Loading job…</div>
        )}
        {error && !loading && (
          <div className="text-center text-sm text-red-600 mb-4">{error}</div>
        )}
        {!loading && !error && job && (
        <Card className="w-full rounded-2xl border border-solid border-[#673ab733] shadow-[2px_0px_2px_#673ab740,0px_2px_2px_#673ab740] overflow-hidden">
          <CardHeader className="p-8">
            <div className="flex items-start gap-6">
              <div className="w-24 h-24 rounded-lg border border-[#673ab7] flex items-center justify-center p-2">
                {job.logo ? (
                  <img
                    className="w-full h-full object-contain"
                    alt={`${job.company} logo`}
                    src={job.logo}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-[#673ab7]">{job.company?.[0] || "J"}</div>
                )}
              </div>
              
              <div className="flex-1">
                <h1 className="font-h5 font-[number:var(--h5-font-weight)] text-[#673ab7] text-[length:var(--h5-font-size)] tracking-[var(--h5-letter-spacing)] leading-[var(--h5-line-height)] mb-2">
                  {job.title}
                </h1>
                
                <div className="flex items-center gap-2 mb-4">
                  <Building className="w-4 h-4 text-[#00000080]" />
                  <span className="font-body font-[number:var(--body-font-weight)] text-[#00000080] text-[length:var(--body-font-size)]">
                    {job.company}
                  </span>
                </div>

                <div className="flex items-center gap-6 mb-4">
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-[#00000080]" />
                    <span className="font-body font-[number:var(--body-font-weight)] text-[#00000080] text-[length:var(--body-font-size)]">
                      {job.location}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-[#00000080]" />
                    <span className="font-body font-[number:var(--body-font-weight)] text-[#00000080] text-[length:var(--body-font-size)]">
                      {job.timePosted || "Recently"}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-[#00000080]" />
                    <span className="font-body font-[number:var(--body-font-weight)] text-[#00000080] text-[length:var(--body-font-size)]">
                      {job.salary || job.salary_range}
                    </span>
                  </div>
                </div>

                <div className="flex gap-4">
                  <Badge
                    variant="outline"
                    className="bg-[#00bfa61a] rounded-sm border-[0.4px] border-solid border-[#673ab780]"
                  >
                    <span className="font-caption text-primay">
                      {job.jobType || job.job_type || "Job"}
                    </span>
                  </Badge>
                  
                  <Button
                    onClick={handleApply}
                    className="bg-[#673ab7] hover:bg-[#673ab7]/90 text-white"
                  >
                    Apply Now
                  </Button>
                </div>
              </div>
            </div>
          </CardHeader>

          <Separator className="mx-8" />

          <CardContent className="p-8 space-y-8">
            {/* Job Description */}
            <div>
              <h2 className="font-h5 text-[#673ab7] text-xl mb-4">Job Description</h2>
              <p className="font-caption text-[#000000b2] text-base leading-relaxed">
                {job.description}
              </p>
            </div>

            {/* Requirements */}
            <div>
              <h2 className="font-h5 text-[#673ab7] text-xl mb-4">Requirements</h2>
              <ul className="space-y-2">
                {(job.requirements || []).map((req, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-[#673ab7] rounded-full mt-2 flex-shrink-0" />
                    <span className="font-caption text-[#000000b2] text-base">
                      {req}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Responsibilities */}
            <div>
              <h2 className="font-h5 text-[#673ab7] text-xl mb-4">Key Responsibilities</h2>
              <ul className="space-y-2">
                {(job.responsibilities || []).map((resp, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-[#00bfa6] rounded-full mt-2 flex-shrink-0" />
                    <span className="font-caption text-[#000000b2] text-base">
                      {resp}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Benefits */}
            <div>
              <h2 className="font-h5 text-[#673ab7] text-xl mb-4">Benefits & Perks</h2>
              <ul className="space-y-2">
                {(job.benefits || []).map((benefit, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-[#00bfa6] rounded-full mt-2 flex-shrink-0" />
                    <span className="font-caption text-[#000000b2] text-base">
                      {benefit}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Apply Section */}
            <div className="bg-[#673ab710] rounded-lg p-6 text-center">
              <h3 className="font-h5 text-[#673ab7] text-lg mb-2">Ready to Apply?</h3>
              <p className="font-caption text-[#000000b2] mb-4">
                Join {job.company} and take the next step in your career journey.
              </p>
              <Button
                onClick={handleApply}
                className="bg-[#673ab7] hover:bg-[#673ab7]/90 text-white px-8"
              >
                Apply for this Position
              </Button>
            </div>
          </CardContent>
        </Card>
        )}
      </div>
    </div>
  );
};