import React from "react";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { NavigationHeader } from "@/components/ui/navigation-header";
import { Briefcase, Eye, Heart, TrendingUp, Calendar, MapPin } from "lucide-react";

export const DashboardPage = (): JSX.Element => {
  const [location, setLocation] = useLocation();

  const stats = {
    appliedJobs: 12,
    viewedJobs: 45,
    savedJobs: 8,
    profileViews: 23
  };

  const recentApplications = [
    {
      id: 1,
      company: "Infosys Ltd",
      position: "Associate Business Analyst",
      status: "Under Review",
      appliedDate: "2024-01-10",
      statusColor: "bg-yellow-100 text-yellow-800"
    },
    {
      id: 2,
      company: "TCS",
      position: "Cloud Support Engineer",
      status: "Interview Scheduled",
      appliedDate: "2024-01-08",
      statusColor: "bg-blue-100 text-blue-800"
    },
    {
      id: 3,
      company: "HCL Tech",
      position: "UI/UX Designer",
      status: "Application Sent",
      appliedDate: "2024-01-06",
      statusColor: "bg-green-100 text-green-800"
    }
  ];

  const savedJobs = [
    {
      id: 4,
      company: "Zoho",
      logo: "/figmaAssets/th--1--1.png",
      position: "Software Developer – Backend (Python)",
      location: "Coimbatore, Tamil Nadu",
      salary: "₹8.5 LPA – ₹11 LPA",
      jobType: "Full-time / Remote"
    },
    {
      id: 5,
      company: "Accenture",
      logo: "/figmaAssets/th--2--1.png",
      position: "Cybersecurity Analyst",
      location: "Gurugram, Haryana",
      salary: "₹10 LPA – ₹14 LPA",
      jobType: "Full-time"
    }
  ];


  const handleJobClick = (jobId: number) => {
    setLocation(`/job/${jobId}`);
  };

  return (
    <div className="bg-neutral-100 min-h-screen">
      <NavigationHeader title="Dashboard" />

      <div className="max-w-6xl mx-auto p-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="font-h5 text-[#673ab7] text-2xl mb-2">Welcome back, John! 👋</h1>
          <p className="font-caption text-[#000000b2]">Here's your job search activity and recommendations.</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6 text-center">
              <Briefcase className="w-8 h-8 text-[#673ab7] mx-auto mb-2" />
              <h3 className="font-h5 text-2xl text-[#673ab7] mb-1">{stats.appliedJobs}</h3>
              <p className="font-caption text-[#000000b2]">Jobs Applied</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6 text-center">
              <Eye className="w-8 h-8 text-[#00bfa6] mx-auto mb-2" />
              <h3 className="font-h5 text-2xl text-[#673ab7] mb-1">{stats.viewedJobs}</h3>
              <p className="font-caption text-[#000000b2]">Jobs Viewed</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6 text-center">
              <Heart className="w-8 h-8 text-red-500 mx-auto mb-2" />
              <h3 className="font-h5 text-2xl text-[#673ab7] mb-1">{stats.savedJobs}</h3>
              <p className="font-caption text-[#000000b2]">Saved Jobs</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6 text-center">
              <TrendingUp className="w-8 h-8 text-green-500 mx-auto mb-2" />
              <h3 className="font-h5 text-2xl text-[#673ab7] mb-1">{stats.profileViews}</h3>
              <p className="font-caption text-[#000000b2]">Profile Views</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Applications */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="font-h5 text-[#673ab7]">Recent Applications</CardTitle>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setLocation("/profile")}
                className="border-[#673ab7] text-[#673ab7]"
              >
                View All
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentApplications.map((app) => (
                  <div key={app.id} className="border border-[#673ab733] rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-body font-semibold text-[#673ab7]">{app.position}</h3>
                        <p className="font-caption text-[#000000b2]">{app.company}</p>
                      </div>
                      <Badge className={app.statusColor}>
                        {app.status}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-[#000000b2]">
                      <Calendar className="w-4 h-4" />
                      Applied on {new Date(app.appliedDate).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Saved Jobs */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="font-h5 text-[#673ab7]">Saved Jobs</CardTitle>
              <Button
                variant="outline"
                size="sm"
                className="border-[#673ab7] text-[#673ab7]"
              >
                View All
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {savedJobs.map((job) => (
                  <div 
                    key={job.id}
                    onClick={() => handleJobClick(job.id)}
                    className="border border-[#673ab733] rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start gap-3">
                      <img
                        className="w-12 h-12 object-contain border border-[#673ab7] rounded p-1"
                        alt={`${job.company} logo`}
                        src={job.logo}
                      />
                      <div className="flex-1">
                        <h3 className="font-body font-semibold text-[#673ab7] mb-1">{job.position}</h3>
                        <p className="font-caption text-[#000000b2] mb-2">{job.company}</p>
                        <div className="flex items-center gap-4 text-xs text-[#000000b2]">
                          <div className="flex items-center gap-1">
                            <MapPin className="w-3 h-3" />
                            {job.location}
                          </div>
                          <span>•</span>
                          <span>{job.salary}</span>
                        </div>
                      </div>
                      <Badge variant="outline" className="bg-[#00bfa61a] border-[#673ab780]">
                        {job.jobType}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="font-h5 text-[#673ab7]">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button
                onClick={() => setLocation("/")}
                className="bg-[#673ab7] hover:bg-[#673ab7]/90 text-white h-16"
              >
                <div className="text-center">
                  <Briefcase className="w-6 h-6 mx-auto mb-1" />
                  <span>Browse Jobs</span>
                </div>
              </Button>
              
              <Button
                onClick={() => setLocation("/profile")}
                variant="outline"
                className="border-[#673ab7] text-[#673ab7] h-16"
              >
                <div className="text-center">
                  <TrendingUp className="w-6 h-6 mx-auto mb-1" />
                  <span>Update Profile</span>
                </div>
              </Button>
              
              <Button
                onClick={() => setLocation("/settings")}
                variant="outline"
                className="border-[#673ab7] text-[#673ab7] h-16"
              >
                <div className="text-center">
                  <Eye className="w-6 h-6 mx-auto mb-1" />
                  <span>Job Alerts</span>
                </div>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};