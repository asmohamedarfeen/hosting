import React, { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Input } from "@/components/ui/input";
import { Search, Filter, Send, MapPin, Clock, DollarSign, Building, Check, Star, Share2, MoreHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";

type JobItem = {
  id: number;
  company: string;
  logo?: string | null;
  title: string;
  location: string;
  timePosted?: string;
  description: string;
  jobType?: string;
  salary?: string;
  salary_range?: string;
};

export const JobListSection = (): JSX.Element => {
  const [, setLocation] = useLocation();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedLocation, setSelectedLocation] = useState("");
  const [selectedJobType, setSelectedJobType] = useState("");
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [applyingJobs, setApplyingJobs] = useState<Set<number>>(new Set());
  const [appliedJobs, setAppliedJobs] = useState<Set<number>>(new Set());
  const [selectedJob, setSelectedJob] = useState<JobItem | null>(null);

  // Fetch jobs from backend
  const fetchJobs = async () => {
    setError(null);
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.set("q", searchTerm);
      if (selectedLocation) params.set("location", selectedLocation);
      if (selectedJobType) params.set("job_type", selectedJobType);
      const qs = params.toString();
      const url = qs ? `/api/jobs/search?${qs}` : "/api/jobs/search";
      const res = await fetch(url, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to load jobs");
      const data = await res.json();
      const apiJobs: JobItem[] = (data?.jobs || []).map((j: any) => ({
        id: j.id,
        company: j.company,
        title: j.title,
        location: j.location,
        description: j.description,
        jobType: j.job_type,
        salary: j.salary_range || j.salary,
        logo: null,
      }));
      setJobs(apiJobs);
    } catch (e: any) {
      setError(e?.message || "Failed to load jobs");
      setJobs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Client-side filter (only use jobs from database, no fallback)
  const sourceJobs = jobs;
  const filteredJobs = sourceJobs.filter(job => {
    const matchesSearch = job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLocation = !selectedLocation || job.location.toLowerCase().includes(selectedLocation.toLowerCase());
    const jobTypeValue = (job.jobType || (job as any).job_type || "").toString();
    const matchesJobType = !selectedJobType || jobTypeValue.toLowerCase().includes(selectedJobType.toLowerCase());
    
    return matchesSearch && matchesLocation && matchesJobType;
  });

  const handleJobClick = (jobId: number) => {
    const job = filteredJobs.find(j => j.id === jobId);
    if (job) {
      setSelectedJob(job);
    }
  };

  // Handle job application
  const handleApply = async (jobId: number, event: React.MouseEvent) => {
    event.stopPropagation(); // Prevent card click
    
    if (applyingJobs.has(jobId) || appliedJobs.has(jobId)) {
      return;
    }

    setApplyingJobs(prev => new Set(prev).add(jobId));

    try {
      const formData = new FormData();
      formData.append('job_id', jobId.toString());
      formData.append('cover_letter', ''); // Optional cover letter
      formData.append('resume_path', ''); // Optional resume path

      const response = await fetch('/api/jobs/apply', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      if (response.ok) {
        setAppliedJobs(prev => new Set(prev).add(jobId));
        // Show success message (you could add a toast notification here)
        alert('Application submitted successfully!');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to apply for job');
      }
    } catch (error) {
      console.error('Error applying for job:', error);
      alert(error instanceof Error ? error.message : 'Failed to apply for job');
    } finally {
      setApplyingJobs(prev => {
        const newSet = new Set(prev);
        newSet.delete(jobId);
        return newSet;
      });
    }
  };

  return (
    <div className="w-full h-full flex flex-col">
      {/* Search and Filter Section */}
      <div className="bg-gradient-to-r from-white to-neutral-50 p-6 border-b border-[#673ab733] shadow-sm">
        <div className="max-w-7xl mx-auto space-y-4">
          {/* Search Bar */}
          <div className="relative max-w-2xl mx-auto">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-[#673ab7] w-5 h-5" />
            <Input
              placeholder="Search jobs, companies, or keywords..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-12 pr-4 py-3 text-lg border-2 border-[#673ab733] focus:border-[#673ab7] rounded-xl shadow-sm"
            />
          </div>
          
          {/* Filters */}
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
                className="w-full h-11 px-4 border-2 border-[#673ab733] rounded-lg focus:border-[#673ab7] focus:outline-none bg-white"
              >
                <option value="">All Job Types</option>
                <option value="full-time">Full-time</option>
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
              </select>
            </div>
            <Button
              variant="outline"
              onClick={() => {
                setSearchTerm("");
                setSelectedLocation("");
                setSelectedJobType("");
                fetchJobs();
              }}
              className="border-2 border-[#673ab7] text-[#673ab7] px-6 py-2.5"
            >
              <Filter className="w-5 h-5 mr-2" />
              Clear Filters
            </Button>
          </div>
          
          {/* Results Count */}
          <div className="text-center text-sm text-[#000000b2] font-medium">
            {loading ? "Loading jobs…" : (error ? error : `Showing ${filteredJobs.length} of ${jobs.length} jobs`)}
          </div>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Column - Job List */}
        <div className="w-1/2 border-r border-gray-200 overflow-y-auto">
          <div className="p-4 space-y-3">
          {(!loading && filteredJobs.length === 0) ? (
            <div className="text-center py-12">
              <p className="text-[#000000b2] text-lg mb-4">No jobs found matching your criteria</p>
                <Button
                onClick={() => {
                  setSearchTerm("");
                  setSelectedLocation("");
                  setSelectedJobType("");
                  fetchJobs();
                }}
                  className="bg-gradient-to-r from-[#673ab7] to-[#5e35b1]"
              >
                Clear All Filters
                </Button>
            </div>
          ) : (
            filteredJobs.map((job) => (
              <Card
                key={job.id}
                onClick={() => handleJobClick(job.id)}
                  className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                    selectedJob?.id === job.id 
                      ? 'border-[#673ab7] bg-blue-50' 
                      : 'border-gray-200 hover:border-[#673ab7]'
                  }`}
              >
                  <CardContent className="p-4">
                    <div className="flex items-start space-x-3">
                      {/* Company Logo */}
                      <div className="w-12 h-12 rounded-lg border border-gray-200 flex items-center justify-center flex-shrink-0">
                {job.logo ? (
                  <img
                            className="w-8 h-8 object-cover"
                    alt={`${job.company} logo`}
                    src={job.logo}
                  />
                ) : (
                          <div className="w-8 h-8 flex items-center justify-center text-sm text-[#673ab7] font-semibold">
                            {job.company[0] || "J"}
                          </div>
                )}
              </div>

                      {/* Job Info */}
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-900 text-lg truncate">
                  {job.title}
                        </h3>
                        <p className="text-sm text-gray-600 truncate">{job.company}</p>
                        <div className="flex items-center space-x-4 mt-1 text-xs text-gray-500">
                          <span className="flex items-center">
                            <MapPin className="w-3 h-3 mr-1" />
                    {job.location}
                          </span>
                          <span className="flex items-center">
                            <Clock className="w-3 h-3 mr-1" />
                    {job.timePosted || "Recently"}
                          </span>
                  </div>
                        <div className="flex items-center space-x-2 mt-2">
                          <Badge variant="outline" className="text-xs">
                    {job.jobType || (job as any).job_type || "Job"}
                </Badge>
                          <Badge variant="outline" className="text-xs">
                    {(job.salary || (job as any).salary_range || "").toString()}
                </Badge>
                        </div>
              </div>

              {/* Apply Button */}
                      <div className="flex-shrink-0">
                {appliedJobs.has(job.id) ? (
                  <Badge className="bg-green-100 text-green-800 border-green-200">
                    Applied ✓
                  </Badge>
                ) : (
                  <button
                    onClick={(e) => handleApply(job.id, e)}
                    disabled={applyingJobs.has(job.id)}
                            className="inline-flex items-center gap-1 px-3 py-1.5 bg-[#673ab7] text-white rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                            <Send className="w-3 h-3" />
                    {applyingJobs.has(job.id) ? "Applying..." : "Apply"}
                  </button>
                )}
                      </div>
              </div>
                </CardContent>
              </Card>
            ))
          )}
          </div>
        </div>

        {/* Right Column - Job Details */}
        <div className="w-1/2 overflow-y-auto bg-gray-50">
          {selectedJob ? (
            <div className="p-6">
              {/* Job Header */}
              <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 rounded-lg border border-gray-200 flex items-center justify-center">
                      {selectedJob.logo ? (
                        <img
                          className="w-12 h-12 object-cover"
                          alt={`${selectedJob.company} logo`}
                          src={selectedJob.logo}
                        />
                      ) : (
                        <div className="w-12 h-12 flex items-center justify-center text-2xl text-[#673ab7] font-semibold">
                          {selectedJob.company[0] || "J"}
                        </div>
                      )}
                    </div>
                    <div>
                      <h1 className="text-2xl font-bold text-gray-900">{selectedJob.title}</h1>
                      <p className="text-lg text-gray-600">{selectedJob.company}</p>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm">
                      <Share2 className="w-4 h-4 mr-2" />
                      Share
                    </Button>
                    <Button variant="outline" size="sm">
                      <MoreHorizontal className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                {/* Job Metadata */}
                <div className="flex items-center space-x-6 text-sm text-gray-600 mb-4">
                  <span className="flex items-center">
                    <MapPin className="w-4 h-4 mr-2" />
                    {selectedJob.location}
                  </span>
                  <span className="flex items-center">
                    <Clock className="w-4 h-4 mr-2" />
                    {selectedJob.timePosted || "Recently"}
                  </span>
                  <span className="flex items-center">
                    <DollarSign className="w-4 h-4 mr-2" />
                    {(selectedJob.salary || (selectedJob as any).salary_range || "").toString()}
                  </span>
                </div>

                {/* Job Type Tags */}
                <div className="flex items-center space-x-2 mb-6">
                  <Badge className="bg-green-100 text-green-800 border-green-200">
                    <Check className="w-3 h-3 mr-1" />
                    {selectedJob.jobType || (selectedJob as any).job_type || "Job"}
                  </Badge>
                  <Badge className="bg-blue-100 text-blue-800 border-blue-200">
                    Remote
                  </Badge>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-3">
                  <Button 
                    className="bg-[#673ab7] hover:bg-[#673ab7]/90 text-white px-6 py-3"
                    onClick={(e) => handleApply(selectedJob.id, e)}
                    disabled={applyingJobs.has(selectedJob.id) || appliedJobs.has(selectedJob.id)}
                  >
                    <Send className="w-4 h-4 mr-2" />
                    {applyingJobs.has(selectedJob.id) ? 'Applying...' : appliedJobs.has(selectedJob.id) ? 'Applied' : 'Apply Now'}
                  </Button>
                  <Button variant="outline" className="px-6 py-3">
                    <Star className="w-4 h-4 mr-2" />
                    Save
                  </Button>
                </div>
              </div>

              {/* Job Description */}
              <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Job Description</h2>
                <p className="text-gray-700 leading-relaxed">{selectedJob.description}</p>
              </div>

              {/* AI-Powered Features */}
              <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">How your profile and resume fit this job</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Get AI-powered advice on this job and more exclusive features with Premium. Try Premium for ₹0
                </p>
                <div className="space-y-3">
                  <Button variant="outline" className="w-full justify-start">
                    <Star className="w-4 h-4 mr-3" />
                    Show match details
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Star className="w-4 h-4 mr-3" />
                    Tailor my resume
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Star className="w-4 h-4 mr-3" />
                    Practice an interview
                  </Button>
                </div>
              </div>

              {/* Meet the hiring team */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Meet the hiring team</h3>
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center">
                    <span className="text-sm font-semibold text-gray-600">SK</span>
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">Surekha Kumar</p>
                    <p className="text-sm text-gray-600">Senior Executive- HR &TA|| HR MBA @{selectedJob.company} Technologies</p>
                    <p className="text-xs text-gray-500">3rd connection</p>
                  </div>
                  <Button variant="outline" size="sm">
                    Message
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Building className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Select a job to view details</h3>
                <p className="text-gray-500">Choose a job from the list to see more information</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
