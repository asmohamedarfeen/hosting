import React, { useState } from "react";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { NavigationHeader } from "@/components/ui/navigation-header";
import { Edit3, MapPin, Mail, Phone, Calendar, Briefcase } from "lucide-react";

export const UserProfilePage = (): JSX.Element => {
  const [location, setLocation] = useLocation();
  const [isEditing, setIsEditing] = useState(false);
  
  const [profileData, setProfileData] = useState({
    firstName: "John",
    lastName: "Doe",
    email: "john.doe@email.com",
    phone: "+91 98765 43210",
    location: "Mumbai, Maharashtra",
    title: "Software Developer",
    experience: "3 years",
    bio: "Passionate software developer with 3 years of experience in full-stack development. Skilled in React, Node.js, and cloud technologies.",
    skills: ["React", "Node.js", "TypeScript", "AWS", "MongoDB"],
    education: "B.Tech Computer Science - IIT Mumbai (2021)"
  });

  const [applications] = useState([
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
      company: "Accenture",
      position: "Cybersecurity Analyst",
      status: "Rejected",
      appliedDate: "2024-01-05",
      statusColor: "bg-red-100 text-red-800"
    }
  ]);


  const handleSave = () => {
    setIsEditing(false);
    // In a real app, this would save to API
  };

  const handleInputChange = (field: string, value: string) => {
    setProfileData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="bg-neutral-100 min-h-screen">
      {/* Header */}
      <NavigationHeader title="My Profile" />

      <div className="max-w-6xl mx-auto p-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Info */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="font-h5 text-[#673ab7]">Personal Information</CardTitle>
                <Button
                  variant="outline"
                  onClick={() => isEditing ? handleSave() : setIsEditing(true)}
                  className="border-[#673ab7] text-[#673ab7]"
                >
                  <Edit3 className="w-4 h-4 mr-2" />
                  {isEditing ? "Save" : "Edit"}
                </Button>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="font-caption">First Name</Label>
                    {isEditing ? (
                      <Input
                        value={profileData.firstName}
                        onChange={(e) => handleInputChange("firstName", e.target.value)}
                        className="border-[#673ab733]"
                      />
                    ) : (
                      <p className="font-body text-[#000000b2]">{profileData.firstName}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label className="font-caption">Last Name</Label>
                    {isEditing ? (
                      <Input
                        value={profileData.lastName}
                        onChange={(e) => handleInputChange("lastName", e.target.value)}
                        className="border-[#673ab733]"
                      />
                    ) : (
                      <p className="font-body text-[#000000b2]">{profileData.lastName}</p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="font-caption">Email</Label>
                    <div className="flex items-center gap-2">
                      <Mail className="w-4 h-4 text-[#673ab7]" />
                      {isEditing ? (
                        <Input
                          value={profileData.email}
                          onChange={(e) => handleInputChange("email", e.target.value)}
                          className="border-[#673ab733]"
                        />
                      ) : (
                        <p className="font-body text-[#000000b2]">{profileData.email}</p>
                      )}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label className="font-caption">Phone</Label>
                    <div className="flex items-center gap-2">
                      <Phone className="w-4 h-4 text-[#673ab7]" />
                      {isEditing ? (
                        <Input
                          value={profileData.phone}
                          onChange={(e) => handleInputChange("phone", e.target.value)}
                          className="border-[#673ab733]"
                        />
                      ) : (
                        <p className="font-body text-[#000000b2]">{profileData.phone}</p>
                      )}
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="font-caption">Location</Label>
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-[#673ab7]" />
                    {isEditing ? (
                      <Input
                        value={profileData.location}
                        onChange={(e) => handleInputChange("location", e.target.value)}
                        className="border-[#673ab733]"
                      />
                    ) : (
                      <p className="font-body text-[#000000b2]">{profileData.location}</p>
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="font-caption">Professional Title</Label>
                  <div className="flex items-center gap-2">
                    <Briefcase className="w-4 h-4 text-[#673ab7]" />
                    {isEditing ? (
                      <Input
                        value={profileData.title}
                        onChange={(e) => handleInputChange("title", e.target.value)}
                        className="border-[#673ab733]"
                      />
                    ) : (
                      <p className="font-body text-[#000000b2]">{profileData.title}</p>
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="font-caption">Bio</Label>
                  {isEditing ? (
                    <Textarea
                      value={profileData.bio}
                      onChange={(e) => handleInputChange("bio", e.target.value)}
                      className="border-[#673ab733] resize-none"
                      rows={3}
                    />
                  ) : (
                    <p className="font-body text-[#000000b2]">{profileData.bio}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label className="font-caption">Skills</Label>
                  <div className="flex flex-wrap gap-2">
                    {profileData.skills.map((skill, index) => (
                      <Badge
                        key={index}
                        variant="outline"
                        className="bg-[#00bfa61a] border-[#673ab780]"
                      >
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Applications History */}
            <Card>
              <CardHeader>
                <CardTitle className="font-h5 text-[#673ab7]">Application History</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {applications.map((app) => (
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
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="font-h5 text-[#673ab7]">Profile Strength</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-[#673ab7] h-2 rounded-full" style={{ width: "75%" }}></div>
                  </div>
                  <p className="font-caption text-[#000000b2]">75% Complete</p>
                  
                  <Separator />
                  
                  <div className="space-y-2">
                    <p className="font-caption font-semibold">Improve your profile:</p>
                    <ul className="space-y-1 text-sm text-[#000000b2]">
                      <li>• Add a profile photo</li>
                      <li>• Upload your resume</li>
                      <li>• Add more skills</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="font-h5 text-[#673ab7]">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button
                  onClick={() => setLocation("/")}
                  className="w-full bg-[#673ab7] hover:bg-[#673ab7]/90 text-white"
                >
                  Browse Jobs
                </Button>
                <Button
                  variant="outline"
                  className="w-full border-[#673ab7] text-[#673ab7]"
                >
                  Download Resume
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setLocation("/settings")}
                  className="w-full border-[#673ab7] text-[#673ab7]"
                >
                  Account Settings
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};