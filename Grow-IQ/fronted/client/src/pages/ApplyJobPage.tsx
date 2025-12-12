import React, { useState } from "react";
import { useRoute, useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { ArrowLeft, Upload, CheckCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";

// Job data - will be fetched from API
const sampleJobs: any[] = [];

export const ApplyJobPage = (): JSX.Element => {
  const [match, params] = useRoute("/apply/:id");
  const [location, setLocation] = useLocation();
  const [isSubmitted, setIsSubmitted] = useState(false);
  
  // Job data should be fetched from API based on jobId
  const jobId = params?.id ? parseInt(params.id) : null;
  const job = sampleJobs.find(j => j.id === jobId) || null;

  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    coverLetter: "",
    experience: "",
    resume: null as File | null
  });

  const handleBack = () => {
    if (jobId) {
      setLocation(`/job/${jobId}`);
    } else {
      setLocation("/jobs");
    }
  };

  // If no job found, redirect to jobs page
  if (!job && jobId) {
    return (
      <div className="bg-neutral-100 min-h-screen flex items-center justify-center">
        <Card>
          <CardContent className="p-8 text-center">
            <h2 className="font-h5 text-[#673ab7] mb-4">Job Not Found</h2>
            <p className="font-caption text-[#000000b2] mb-6">
              The job you're looking for doesn't exist or has been removed.
            </p>
            <Button
              onClick={() => setLocation("/jobs")}
              className="bg-[#673ab7] hover:bg-[#673ab7]/90 text-white"
            >
              Browse Jobs
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // If no jobId provided, redirect to jobs page
  if (!jobId) {
    setLocation("/jobs");
    return <div></div>;
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setFormData(prev => ({ ...prev, resume: file }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, this would submit to an API
    setIsSubmitted(true);
  };

  if (isSubmitted) {
    return (
      <div className="bg-neutral-100 min-h-screen">
        {/* Header */}
        <header className="w-full h-[82px] bg-[#673ab799] border-b-[0.5px] border-solid border-[#673ab733] relative">
          <div className="flex items-center px-[100px] py-0 h-full">
            <div className="bg-gradient-to-r from-[#673ab7] to-[#00bfa6] bg-clip-text text-transparent [font-family:'Sora',Helvetica] font-bold text-2xl leading-normal">
              GrowIQ
            </div>
          </div>
        </header>

        <div className="max-w-2xl mx-auto p-8">
          <Card className="text-center">
            <CardContent className="p-8">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h1 className="font-h5 text-[#673ab7] text-2xl mb-4">Application Submitted!</h1>
              <p className="font-caption text-[#000000b2] mb-6">
                {job ? (
                  <>Thank you for applying to the {job.title} position at {job.company}. We'll review your application and get back to you soon.</>
                ) : (
                  <>Your application has been submitted. We'll review it and get back to you soon.</>
                )}
              </p>
              <div className="space-y-3">
                <Button
                  onClick={() => setLocation("/jobs")}
                  className="bg-[#673ab7] hover:bg-[#673ab7]/90 text-white"
                >
                  Browse More Jobs
                </Button>
                {job && jobId && (
                  <>
                    <br />
                    <Button
                      variant="outline"
                      onClick={() => setLocation(`/job/${jobId}`)}
                      className="border-[#673ab7] text-[#673ab7]"
                    >
                      Back to Job Details
                    </Button>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

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
            Back to Job
          </Button>
          <div className="bg-gradient-to-r from-[#673ab7] to-[#00bfa6] bg-clip-text text-transparent [font-family:'Sora',Helvetica] font-bold text-2xl leading-normal">
            GrowIQ
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto p-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Job Info Sidebar */}
          <div className="lg:col-span-1">
            <Card className="sticky top-8">
              <CardHeader>
                <CardTitle className="font-h5 text-[#673ab7]">Applying For</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {job ? (
                  <>
                    <div className="flex items-center gap-3">
                      {job.logo && (
                        <img
                          className="w-12 h-12 object-contain border border-[#673ab7] rounded p-1"
                          alt={`${job.company} logo`}
                          src={job.logo}
                        />
                      )}
                      <div>
                        <h3 className="font-body text-[#673ab7] font-semibold">{job.title}</h3>
                        <p className="font-caption text-[#000000b2]">{job.company}</p>
                      </div>
                    </div>
                    
                    <Separator />
                    
                    <div className="space-y-2">
                      {job.location && (
                        <p className="font-caption text-[#000000b2]">
                          <strong>Location:</strong> {job.location}
                        </p>
                      )}
                      {job.salary && (
                        <p className="font-caption text-[#000000b2]">
                          <strong>Salary:</strong> {job.salary}
                        </p>
                      )}
                      {job.jobType && (
                        <Badge variant="outline" className="bg-[#00bfa61a] border-[#673ab780]">
                          <span className="font-caption text-primay">{job.jobType}</span>
                        </Badge>
                      )}
                    </div>
                  </>
                ) : (
                  <p className="font-caption text-[#000000b2]">Loading job details...</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Application Form */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="font-h5 text-[#673ab7]">Application Form</CardTitle>
                <p className="font-caption text-[#000000b2]">
                  Please fill out all required fields to submit your application.
                </p>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Personal Information */}
                  <div className="space-y-4">
                    <h3 className="font-body text-[#673ab7] font-semibold">Personal Information</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="firstName" className="font-caption">First Name *</Label>
                        <Input
                          id="firstName"
                          required
                          value={formData.firstName}
                          onChange={(e) => handleInputChange("firstName", e.target.value)}
                          className="border-[#673ab733]"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="lastName" className="font-caption">Last Name *</Label>
                        <Input
                          id="lastName"
                          required
                          value={formData.lastName}
                          onChange={(e) => handleInputChange("lastName", e.target.value)}
                          className="border-[#673ab733]"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="email" className="font-caption">Email Address *</Label>
                        <Input
                          id="email"
                          type="email"
                          required
                          value={formData.email}
                          onChange={(e) => handleInputChange("email", e.target.value)}
                          className="border-[#673ab733]"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="phone" className="font-caption">Phone Number *</Label>
                        <Input
                          id="phone"
                          type="tel"
                          required
                          value={formData.phone}
                          onChange={(e) => handleInputChange("phone", e.target.value)}
                          className="border-[#673ab733]"
                        />
                      </div>
                    </div>
                  </div>

                  <Separator />

                  {/* Professional Information */}
                  <div className="space-y-4">
                    <h3 className="font-body text-[#673ab7] font-semibold">Professional Information</h3>
                    
                    <div className="space-y-2">
                      <Label htmlFor="experience" className="font-caption">Years of Experience *</Label>
                      <Input
                        id="experience"
                        required
                        value={formData.experience}
                        onChange={(e) => handleInputChange("experience", e.target.value)}
                        placeholder="e.g., 2-3 years"
                        className="border-[#673ab733]"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="resume" className="font-caption">Resume/CV *</Label>
                      <div className="border-2 border-dashed border-[#673ab733] rounded-lg p-6 text-center">
                        <Upload className="w-8 h-8 text-[#673ab7] mx-auto mb-2" />
                        <Label htmlFor="resume" className="cursor-pointer">
                          <span className="font-caption text-[#673ab7]">Click to upload</span>
                          <span className="font-caption text-[#000000b2]"> or drag and drop</span>
                          <br />
                          <span className="font-caption text-[#000000b2] text-sm">PDF, DOC, DOCX (max 5MB)</span>
                        </Label>
                        <Input
                          id="resume"
                          type="file"
                          required
                          onChange={handleFileChange}
                          accept=".pdf,.doc,.docx"
                          className="hidden"
                        />
                        {formData.resume && (
                          <p className="mt-2 font-caption text-[#673ab7]">
                            Selected: {formData.resume.name}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>

                  <Separator />

                  {/* Cover Letter */}
                  <div className="space-y-4">
                    <h3 className="font-body text-[#673ab7] font-semibold">Cover Letter</h3>
                    <div className="space-y-2">
                      <Label htmlFor="coverLetter" className="font-caption">
                        Tell us why you're interested in this role
                      </Label>
                      <Textarea
                        id="coverLetter"
                        rows={6}
                        value={formData.coverLetter}
                        onChange={(e) => handleInputChange("coverLetter", e.target.value)}
                        placeholder="Share your motivation, relevant experience, and what makes you a great fit for this position..."
                        className="border-[#673ab733] resize-none"
                      />
                    </div>
                  </div>

                  {/* Submit Button */}
                  <div className="pt-4">
                    <Button
                      type="submit"
                      className="w-full bg-[#673ab7] hover:bg-[#673ab7]/90 text-white py-3"
                    >
                      Submit Application
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};