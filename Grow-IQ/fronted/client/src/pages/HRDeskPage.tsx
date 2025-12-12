import React, { useEffect, useState } from "react";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { UserAvatar } from "@/components/UserAvatar";
import { Plus, Users, Briefcase, MapPin, DollarSign, Calendar, Eye, User, X, Tag } from "lucide-react";

type JobPost = {
  id?: number;
  title: string;
  company: string;
  location: string;
  job_type: string;
  salary_range: string;
  description: string;
  requirements: string;
  benefits: string;
  skills_required: string[];
  application_deadline: string;
  posted_at?: string;
  is_active?: boolean;
};

type JobApplication = {
  id: number;
  job_id?: number;
  applicant_id?: number;
  applicant?: {
    id: number;
    name: string;
    email: string;
    profile_image?: string;
    title?: string;
    company?: string;
    location?: string;
    experience_years?: number;
    skills?: string;
  };
  job?: {
    id: number;
    title: string;
    company: string;
  };
  applied_at: string;
  status: string;
  cover_letter?: string;
  resume_path?: string;
  notes?: string;
};

type UserProfile = {
  id: number;
  username: string;
  email: string;
  full_name: string;
  title?: string;
  company?: string;
  location?: string;
  bio?: string;
  profile_image?: string;
  profile_pic?: string;
  phone?: string;
  website?: string;
  linkedin_url?: string;
  twitter_url?: string;
  github_url?: string;
  industry?: string;
  skills?: string;
  experience_years?: number;
  experience?: string;
  education?: string;
  certifications?: string;
  interests?: string;
  portfolio_url?: string;
  created_at: string;
  updated_at: string;
};

export const HRDeskPage = (): JSX.Element => {
  const [, setLocation] = useLocation();
  const [jobs, setJobs] = useState<JobPost[]>([]);
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showJobForm, setShowJobForm] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [viewingProfile, setViewingProfile] = useState<JobApplication | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [skillInput, setSkillInput] = useState("");

  const [jobForm, setJobForm] = useState<JobPost>({
    title: "",
    company: "",
    location: "",
    job_type: "full-time",
    salary_range: "",
    description: "",
    requirements: "",
    benefits: "",
    skills_required: [],
    application_deadline: "",
  });

  // Fetch HR's posted jobs
  const fetchJobs = async () => {
    try {
      const res = await fetch("/hr/jobs", { credentials: "include" });
      if (!res.ok) throw new Error("Failed to load jobs");
      const data = await res.json();
      setJobs(data.jobs || []);
    } catch (e: any) {
      setError(e?.message || "Failed to load jobs");
    }
  };

  // Fetch applications for all jobs
  const fetchApplications = async () => {
    try {
      // Backend applications endpoint lives under /hr, not /api/hr
      const res = await fetch("/hr/applications", { credentials: "include" });
      if (!res.ok) throw new Error("Failed to load applications");
      const data = await res.json();
      setApplications(data.applications || []);
    } catch (e: any) {
      setError(e?.message || "Failed to load applications");
    }
  };

  // Skills management functions
  const addSkill = () => {
    if (skillInput.trim() && !jobForm.skills_required.includes(skillInput.trim())) {
      setJobForm({
        ...jobForm,
        skills_required: [...jobForm.skills_required, skillInput.trim()]
      });
      setSkillInput("");
    }
  };

  const removeSkill = (skillToRemove: string) => {
    setJobForm({
      ...jobForm,
      skills_required: jobForm.skills_required.filter(skill => skill !== skillToRemove)
    });
  };

  const handleSkillKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addSkill();
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchJobs(), fetchApplications()]);
      setLoading(false);
    };
    loadData();
  }, []);

  // Handle ESC key to close job form modal
  useEffect(() => {
    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && showJobForm) {
        setShowJobForm(false);
      }
    };

    if (showJobForm) {
      document.addEventListener('keydown', handleEscKey);
      return () => {
        document.removeEventListener('keydown', handleEscKey);
      };
    }
  }, [showJobForm]);

  const handleJobSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      Object.entries(jobForm).forEach(([key, value]) => {
        if (key === 'skills_required' && Array.isArray(value)) {
          // Handle skills array separately
          value.forEach((skill, index) => {
            formData.append(`skills_required[${index}]`, skill);
          });
        } else {
          formData.append(key, String(value));
        }
      });

      const res = await fetch("/hr/jobs/create", {
        method: "POST",
        body: formData,
        credentials: "include",
      });

      if (!res.ok) throw new Error("Failed to create job");
      
      setShowJobForm(false);
      setJobForm({
        title: "",
        company: "",
        location: "",
        job_type: "full-time",
        salary_range: "",
        description: "",
        requirements: "",
        benefits: "",
        skills_required: [],
        application_deadline: "",
      });
      setSkillInput("");
      await fetchJobs();
    } catch (e: any) {
      setError(e?.message || "Failed to create job");
    }
  };

  const handleApplicationStatusUpdate = async (applicationId: number, status: string) => {
    try {
      // Map UI statuses to backend accepted values
      const statusMap: Record<string, string> = {
        under_review: "reviewed",
        interview_scheduled: "interview",
        accepted: "hired",
        rejected: "rejected",
        pending: "pending",
      };
      const mapped = statusMap[status] || status;

      const res = await fetch(`/hr/applications/${applicationId}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: mapped }),
        credentials: "include",
      });

      if (!res.ok) throw new Error("Failed to update status");
      await fetchApplications();
    } catch (e: any) {
      setError(e?.message || "Failed to update status");
    }
  };

  // Fetch user profile by ID
  const fetchUserProfile = async (userId: number) => {
    setProfileLoading(true);
    try {
      const res = await fetch(`/auth/profile/${userId}`, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to load user profile");
      const profile = await res.json();
      setUserProfile(profile);
    } catch (e: any) {
      setError(e?.message || "Failed to load user profile");
    } finally {
      setProfileLoading(false);
    }
  };

  // Handle viewing applicant profile
  const handleViewProfile = (application: JobApplication) => {
    setViewingProfile(application);
    if (application.applicant?.id) {
      fetchUserProfile(application.applicant.id);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "pending": return "bg-yellow-100 text-yellow-800";
      case "under_review": return "bg-blue-100 text-blue-800";
      case "interview_scheduled": return "bg-purple-100 text-purple-800";
      case "accepted": return "bg-green-100 text-green-800";
      case "rejected": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const filteredApplications = selectedJobId 
    ? applications.filter(app => (app?.job?.id === selectedJobId))
    : applications;

  return (
    <div className="max-w-7xl mx-auto p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-[#673ab7] mb-2">HR Desk</h1>
        <p className="text-gray-600">Manage job postings and review applications</p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <Tabs defaultValue="jobs" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="jobs" className="flex items-center gap-2">
            <Briefcase className="w-4 h-4" />
            Job Postings
          </TabsTrigger>
          <TabsTrigger value="applications" className="flex items-center gap-2">
            <Users className="w-4 h-4" />
            Applications ({applications.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="jobs" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Your Job Postings</h2>
            <Button
              onClick={() => setShowJobForm(true)}
              className="bg-[#673ab7] hover:bg-[#673ab7]/90 text-white shadow-lg hover:shadow-xl transition-all duration-300 font-semibold px-6 py-3"
            >
              <Plus className="w-4 h-4 mr-2" />
              Post New Job
            </Button>
          </div>

          {loading ? (
            <div className="text-center py-8">Loading jobs...</div>
          ) : jobs.length === 0 ? (
            <Card>
              <CardContent className="text-center py-8">
                <Briefcase className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No jobs posted yet</p>
                <Button
                  onClick={() => setShowJobForm(true)}
                  className="mt-4 bg-[#673ab7] hover:bg-[#673ab7]/90 text-white shadow-lg hover:shadow-xl transition-all duration-300 font-semibold px-6 py-3"
                >
                  Post Your First Job
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {jobs.map((job) => (
                <Card key={job.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">{job.title}</CardTitle>
                        <p className="text-gray-600">{job.company}</p>
                      </div>
                      <Badge variant="outline" className="bg-green-100 text-green-800">
                        {job.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                      <div className="flex items-center gap-1">
                        <MapPin className="w-4 h-4" />
                        {job.location}
                      </div>
                      <div className="flex items-center gap-1">
                        <DollarSign className="w-4 h-4" />
                        {job.salary_range}
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {job.application_deadline}
                      </div>
                    </div>
                    <p className="text-gray-700 text-sm mb-3 line-clamp-2">{job.description}</p>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedJobId(job.id || null)}
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        View Applications
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="applications" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Job Applications</h2>
            {selectedJobId && (
              <Button
                variant="outline"
                onClick={() => setSelectedJobId(null)}
              >
                Show All Applications
              </Button>
            )}
          </div>

          {loading ? (
            <div className="text-center py-8">Loading applications...</div>
          ) : filteredApplications.length === 0 ? (
            <Card>
              <CardContent className="text-center py-8">
                <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">
                  {selectedJobId ? "No applications for this job" : "No applications yet"}
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {filteredApplications.map((application) => (
                <Card key={application.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="font-semibold text-lg">{application?.applicant?.name}</h3>
                        <p className="text-gray-600">{application?.applicant?.email}</p>
                        <p className="text-sm text-gray-500">
                          Applied for: {application?.job?.title} at {application?.job?.company}
                        </p>
                        <p className="text-sm text-gray-500">
                          Applied on: {new Date(application?.applied_at).toLocaleDateString()}
                        </p>
                      </div>
                      <Badge className={getStatusColor(application.status)}>
                        {application.status.replace('_', ' ').toUpperCase()}
                      </Badge>
                    </div>

                    {application.cover_letter && (
                      <div className="mb-4">
                        <h4 className="font-medium mb-2">Cover Letter:</h4>
                        <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
                          {application.cover_letter}
                        </p>
                      </div>
                    )}

                    <div className="flex gap-2 flex-wrap">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setLocation(`/user/${application?.applicant?.id}`)}
                        className="flex items-center gap-1"
                      >
                        <User className="w-4 h-4" />
                        View Profile
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleApplicationStatusUpdate(application.id, "under_review")}
                      >
                        Under Review
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleApplicationStatusUpdate(application.id, "interview_scheduled")}
                      >
                        Schedule Interview
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleApplicationStatusUpdate(application.id, "accepted")}
                      >
                        Accept
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleApplicationStatusUpdate(application.id, "rejected")}
                      >
                        Reject
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Job Posting Modal */}
      {showJobForm && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          onClick={(e) => {
            // Close modal when clicking on backdrop
            if (e.target === e.currentTarget) {
              setShowJobForm(false);
            }
          }}
        >
          <Card className="w-full max-w-4xl max-h-[95vh] overflow-y-auto bg-white shadow-2xl">
            <CardHeader className="bg-gradient-to-r from-[#673ab7] to-[#5e35b1] text-white rounded-t-lg relative">
              <CardTitle className="flex items-center space-x-2 pr-12">
                <Briefcase className="h-6 w-6" />
                <span>Post New Job</span>
              </CardTitle>
              <p className="text-[#673ab7]/80">Create a compelling job posting to attract top talent</p>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowJobForm(false)}
                className="absolute top-3 right-3 text-white hover:bg-white/30 hover:text-white bg-white/10 border border-white/30 rounded-lg p-2 h-10 w-10 flex items-center justify-center transition-all duration-200 shadow-lg hover:shadow-xl"
                aria-label="Close"
                title="Close (ESC)"
              >
                <X className="h-6 w-6 font-bold" />
              </Button>
            </CardHeader>
            <CardContent className="p-6 bg-white">
              <form onSubmit={handleJobSubmit} className="space-y-6">
                {/* Basic Information Section */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">Basic Information</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="title" className="text-sm font-medium text-gray-700">Job Title *</Label>
                      <Input
                        id="title"
                        value={jobForm.title}
                        onChange={(e) => setJobForm({...jobForm, title: e.target.value})}
                        placeholder="e.g., Senior Software Engineer"
                        className="mt-1"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="company" className="text-sm font-medium text-gray-700">Company *</Label>
                      <Input
                        id="company"
                        value={jobForm.company}
                        onChange={(e) => setJobForm({...jobForm, company: e.target.value})}
                        placeholder="e.g., Tech Corp Inc."
                        className="mt-1"
                        required
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="location" className="text-sm font-medium text-gray-700">Location *</Label>
                      <Input
                        id="location"
                        value={jobForm.location}
                        onChange={(e) => setJobForm({...jobForm, location: e.target.value})}
                        placeholder="e.g., San Francisco, CA"
                        className="mt-1"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="job_type" className="text-sm font-medium text-gray-700">Job Type *</Label>
                      <select
                        id="job_type"
                        value={jobForm.job_type}
                        onChange={(e) => setJobForm({...jobForm, job_type: e.target.value})}
                        className="w-full p-3 border border-gray-300 rounded-md mt-1 focus:ring-2 focus:ring-[#673ab7] focus:border-transparent"
                        required
                      >
                        <option value="full-time">Full-time</option>
                        <option value="part-time">Part-time</option>
                        <option value="contract">Contract</option>
                        <option value="remote">Remote</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="salary_range" className="text-sm font-medium text-gray-700">Salary Range</Label>
                    <Input
                      id="salary_range"
                      value={jobForm.salary_range}
                      onChange={(e) => setJobForm({...jobForm, salary_range: e.target.value})}
                      placeholder="e.g., $80,000 - $120,000"
                      className="mt-1"
                    />
                  </div>
                </div>

                {/* Skills Required Section */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">Skills Required</h3>
                  
                  <div>
                    <Label className="text-sm font-medium text-gray-700">Add Required Skills</Label>
                    <div className="mt-1 flex gap-2">
                      <div className="flex-1 relative">
                        <Input
                          value={skillInput}
                          onChange={(e) => setSkillInput(e.target.value)}
                          onKeyPress={handleSkillKeyPress}
                          placeholder="e.g., React, Python, Machine Learning"
                          className="pr-10"
                        />
                        <Tag className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                      </div>
                      <Button
                        type="button"
                        onClick={addSkill}
                        disabled={!skillInput.trim()}
                        className="bg-[#673ab7] hover:bg-[#673ab7]/90 text-white"
                      >
                        <Plus className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  {/* Skills Tags Display */}
                  {jobForm.skills_required.length > 0 && (
                    <div className="space-y-2">
                      <Label className="text-sm font-medium text-gray-700">Selected Skills:</Label>
                      <div className="flex flex-wrap gap-2">
                        {jobForm.skills_required.map((skill, index) => (
                          <Badge
                            key={index}
                            variant="secondary"
                            className="bg-[#673ab7]/10 text-[#673ab7] border-[#673ab7]/20 px-3 py-1 flex items-center gap-2"
                          >
                            {skill}
                            <button
                              type="button"
                              onClick={() => removeSkill(skill)}
                              className="ml-1 hover:bg-[#673ab7]/20 rounded-full p-0.5"
                            >
                              <X className="h-3 w-3" />
                            </button>
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Job Details Section */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">Job Details</h3>
                  
                  <div>
                    <Label htmlFor="description" className="text-sm font-medium text-gray-700">Job Description *</Label>
                    <Textarea
                      id="description"
                      value={jobForm.description}
                      onChange={(e) => setJobForm({...jobForm, description: e.target.value})}
                      rows={4}
                      placeholder="Describe the role, responsibilities, and what makes this opportunity unique..."
                      className="mt-1"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="requirements" className="text-sm font-medium text-gray-700">Requirements & Qualifications</Label>
                    <Textarea
                      id="requirements"
                      value={jobForm.requirements}
                      onChange={(e) => setJobForm({...jobForm, requirements: e.target.value})}
                      rows={3}
                      placeholder="List the required qualifications, experience, and education..."
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <Label htmlFor="benefits" className="text-sm font-medium text-gray-700">Benefits & Perks</Label>
                    <Textarea
                      id="benefits"
                      value={jobForm.benefits}
                      onChange={(e) => setJobForm({...jobForm, benefits: e.target.value})}
                      rows={3}
                      placeholder="List the benefits, perks, and what candidates can expect..."
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <Label htmlFor="application_deadline" className="text-sm font-medium text-gray-700">Application Deadline</Label>
                    <Input
                      id="application_deadline"
                      type="date"
                      value={jobForm.application_deadline}
                      onChange={(e) => setJobForm({...jobForm, application_deadline: e.target.value})}
                      className="mt-1"
                    />
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 pt-6 border-t border-gray-200">
                  <Button 
                    type="submit" 
                    className="flex-1 bg-gradient-to-r from-[#673ab7] to-[#5e35b1] hover:from-[#673ab7]/90 hover:to-[#5e35b1]/90 text-white font-semibold py-3"
                  >
                    <Briefcase className="h-4 w-4 mr-2" />
                    Post Job
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowJobForm(false)}
                    className="px-6 py-3"
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Applicant Profile Modal */}
      {viewingProfile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Applicant Profile</CardTitle>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setViewingProfile(null);
                  setUserProfile(null);
                }}
              >
                Close
              </Button>
            </CardHeader>
            <CardContent className="space-y-6">
              {profileLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#673ab7] mx-auto"></div>
                  <p className="mt-2 text-gray-600">Loading profile...</p>
                </div>
              ) : userProfile ? (
                <>
                  {/* Profile Header */}
                  <div className="text-center border-b pb-6">
                    <div className="flex justify-center mb-4">
                      <UserAvatar 
                        user={userProfile} 
                        size="xl"
                        showName={true}
                        showTitle={true}
                        title={userProfile.title}
                      />
                    </div>
                    <p className="text-gray-500 mb-4">{userProfile.email}</p>
                    <div className="flex justify-center gap-2">
                      <Badge className={getStatusColor(viewingProfile.status)}>
                        {viewingProfile.status.replace('_', ' ').toUpperCase()}
                      </Badge>
                      {userProfile.location && (
                        <Badge variant="outline" className="flex items-center gap-1">
                          <MapPin className="w-3 h-3" />
                          {userProfile.location}
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* Application Details */}
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold mb-3 text-lg">Application Details</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Job Applied For:</span>
                        <p className="text-gray-600">{viewingProfile.job_title}</p>
                      </div>
                      <div>
                        <span className="font-medium">Company:</span>
                        <p className="text-gray-600">{viewingProfile.job_company}</p>
                      </div>
                      <div>
                        <span className="font-medium">Applied Date:</span>
                        <p className="text-gray-600">
                          {new Date(viewingProfile.applied_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div>
                        <span className="font-medium">Status:</span>
                        <p className="text-gray-600 capitalize">
                          {viewingProfile.status.replace('_', ' ')}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Professional Information */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Bio */}
                    {userProfile.bio && (
                      <div>
                        <h3 className="font-semibold mb-2 text-lg">About</h3>
                        <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">
                          {userProfile.bio}
                        </p>
                      </div>
                    )}

                    {/* Skills */}
                    {userProfile.skills && (
                      <div>
                        <h3 className="font-semibold mb-2 text-lg">Skills</h3>
                        <div className="flex flex-wrap gap-2">
                          {userProfile.skills.split(',').map((skill, index) => (
                            <Badge key={index} variant="outline" className="bg-blue-50 text-blue-700">
                              {skill.trim()}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Experience */}
                    {userProfile.experience_years && (
                      <div>
                        <h3 className="font-semibold mb-2 text-lg">Experience</h3>
                        <p className="text-gray-700">
                          {userProfile.experience_years} years of experience
                        </p>
                        {userProfile.experience && (
                          <p className="text-sm text-gray-600">
                            Level: {userProfile.experience}
                          </p>
                        )}
                      </div>
                    )}

                    {/* Industry */}
                    {userProfile.industry && (
                      <div>
                        <h3 className="font-semibold mb-2 text-lg">Industry</h3>
                        <p className="text-gray-700">{userProfile.industry}</p>
                      </div>
                    )}

                    {/* Education */}
                    {userProfile.education && (
                      <div className="md:col-span-2">
                        <h3 className="font-semibold mb-2 text-lg">Education</h3>
                        <div className="bg-gray-50 p-3 rounded-lg">
                          <p className="text-gray-700 whitespace-pre-wrap">
                            {userProfile.education}
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Certifications */}
                    {userProfile.certifications && (
                      <div className="md:col-span-2">
                        <h3 className="font-semibold mb-2 text-lg">Certifications</h3>
                        <div className="bg-gray-50 p-3 rounded-lg">
                          <p className="text-gray-700 whitespace-pre-wrap">
                            {userProfile.certifications}
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Interests */}
                    {userProfile.interests && (
                      <div className="md:col-span-2">
                        <h3 className="font-semibold mb-2 text-lg">Interests</h3>
                        <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">
                          {userProfile.interests}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Contact Information */}
                  <div className="border-t pt-6">
                    <h3 className="font-semibold mb-3 text-lg">Contact Information</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {userProfile.phone && (
                        <div className="flex items-center gap-2">
                          <span className="font-medium">Phone:</span>
                          <span className="text-gray-600">{userProfile.phone}</span>
                        </div>
                      )}
                      {userProfile.website && (
                        <div className="flex items-center gap-2">
                          <span className="font-medium">Website:</span>
                          <a href={userProfile.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                            {userProfile.website}
                          </a>
                        </div>
                      )}
                      {userProfile.linkedin_url && (
                        <div className="flex items-center gap-2">
                          <span className="font-medium">LinkedIn:</span>
                          <a href={userProfile.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                            View Profile
                          </a>
                        </div>
                      )}
                      {userProfile.github_url && (
                        <div className="flex items-center gap-2">
                          <span className="font-medium">GitHub:</span>
                          <a href={userProfile.github_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                            View Profile
                          </a>
                        </div>
                      )}
                      {userProfile.portfolio_url && (
                        <div className="flex items-center gap-2">
                          <span className="font-medium">Portfolio:</span>
                          <a href={userProfile.portfolio_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                            View Portfolio
                          </a>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Cover Letter */}
                  {viewingProfile.cover_letter && (
                    <div className="border-t pt-6">
                      <h3 className="font-semibold mb-2 text-lg">Cover Letter</h3>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="text-gray-700 whitespace-pre-wrap">
                          {viewingProfile.cover_letter}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Resume */}
                  {viewingProfile.resume_path && (
                    <div className="border-t pt-6">
                      <h3 className="font-semibold mb-2 text-lg">Resume</h3>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="text-sm text-gray-600 mb-2">
                          Resume file: {viewingProfile.resume_path}
                        </p>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => window.open(viewingProfile.resume_path, '_blank')}
                        >
                          View Resume
                        </Button>
                      </div>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="border-t pt-6">
                    <h3 className="font-semibold mb-3 text-lg">Application Actions</h3>
                    <div className="flex gap-2 flex-wrap">
                      <Button
                        onClick={() => handleApplicationStatusUpdate(viewingProfile.id, "under_review")}
                        className="flex-1 min-w-[120px]"
                      >
                        Mark as Under Review
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => handleApplicationStatusUpdate(viewingProfile.id, "interview_scheduled")}
                        className="flex-1 min-w-[120px]"
                      >
                        Schedule Interview
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => handleApplicationStatusUpdate(viewingProfile.id, "accepted")}
                        className="flex-1 min-w-[120px]"
                      >
                        Accept
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => handleApplicationStatusUpdate(viewingProfile.id, "rejected")}
                        className="flex-1 min-w-[120px]"
                      >
                        Reject
                      </Button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-600">Failed to load user profile</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};
