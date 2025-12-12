import React, { useEffect, useRef, useState } from "react";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Edit3, MapPin, Mail, Phone, Calendar, Briefcase, FileText, TrendingUp } from "lucide-react";

export const UserProfilePage = (): JSX.Element => {
  const [location, setLocation] = useLocation();
  const [isEditing, setIsEditing] = useState(false);
  
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isHr, setIsHr] = useState(false);
  const [profileData, setProfileData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    location: "",
    title: "",
    experience: "",
    bio: "",
    skills: [] as string[],
    education: "",
    username: ""
  });
  const [profileImageUrl, setProfileImageUrl] = useState<string>("");
  const [isUploading, setIsUploading] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);
  const [newSkill, setNewSkill] = useState("");
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  
  // Resume scores state
  const [resumeScores, setResumeScores] = useState({
    resume_scores: [] as any[],
    summary: {
      total_tests: 0,
      average_score: 0,
      best_score: 0,
      latest_score: 0
    }
  });
  const [resumeScoresLoading, setResumeScoresLoading] = useState(true);


  // Applications state
  const [applications, setApplications] = useState<any[]>([]);
  const [applicationsLoading, setApplicationsLoading] = useState(true);

  // Fetch resume scores from backend
  useEffect(() => {
    let isMounted = true;
    (async () => {
      try {
        const res = await fetch("/api/resume-scores", { credentials: "include" });
        if (res.ok) {
          const data = await res.json();
          if (isMounted) {
            // If API has no tests yet but we have a recent local score, use it as a fallback display
            const localLatest = Number(localStorage.getItem('ats_latest_score') || '0');
            if (
              data && data.summary && Number(data.summary.latest_score || 0) === 0 &&
              Number.isFinite(localLatest) && localLatest > 0
            ) {
              setResumeScores({
                resume_scores: data.resume_scores || [],
                summary: {
                  total_tests: data.summary.total_tests || 0,
                  average_score: data.summary.average_score || localLatest,
                  best_score: Math.max(Number(data.summary.best_score || 0), localLatest),
                  latest_score: localLatest
                }
              });
            } else {
              setResumeScores(data);
            }
          }
        } else if (res.status === 401) {
          // User not authenticated, show empty state
          if (isMounted) {
            setResumeScores({
              resume_scores: [],
              summary: {
                total_tests: 0,
                average_score: 0,
                best_score: 0,
                latest_score: 0
              }
            });
          }
        }
      } catch (error) {
        console.error("Error fetching resume scores:", error);
      } finally {
        if (isMounted) {
          setResumeScoresLoading(false);
        }
      }
    })();
    return () => { isMounted = false; };
  }, []);


  // Sync with localStorage updates (e.g., after ATS test on Resume page)
  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === 'ats_latest_score') {
        const next = Number(e.newValue || '0');
        if (Number.isFinite(next) && next > 0) {
          setResumeScores(prev => ({
            resume_scores: prev.resume_scores,
            summary: {
              total_tests: prev.summary.total_tests,
              average_score: prev.summary.average_score || next,
              best_score: Math.max(Number(prev.summary.best_score || 0), next),
              latest_score: next
            }
          }));
        }
      }
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  // Fetch profile from backend
  useEffect(() => {
    let isMounted = true;
    (async () => {
      try {
        const res = await fetch("/auth/profile", { credentials: "include" });
        if (res.status === 401) {
          // User not authenticated, show guest mode
          if (isMounted) {
            setLoading(false);
            setErrorMessage(null);
          }
          return;
        }
        if (!res.ok) {
          const text = await res.text();
          throw new Error(text);
        }
        const user = await res.json();
        if (!isMounted) return;
        const type = (user?.user_type || user?.role || "").toString().toLowerCase();
        const inferredHr = Boolean(
          user?.is_hr === true ||
          type === "hr" ||
          type === "human_resources" ||
          type === "hr_user" ||
          type === "domain" ||
          type === "recruiter"
        );
        setIsHr(inferredHr);
        // Map backend fields to UI state
        const fullName: string = user.full_name || user.fullName || "";
        const [firstName, ...rest] = fullName.split(" ");
        const lastName = rest.join(" ");
        setProfileData({
          firstName: firstName || "",
          lastName,
          email: user.email || "",
          phone: user.phone || "",
          location: user.location || "",
          title: user.title || "",
          experience: (user.experience_years ? `${user.experience_years} years` : (user.experience || "")),
          bio: user.bio || "",
          skills: Array.isArray(user.skills)
            ? user.skills
            : (typeof user.skills === "string" && user.skills ? user.skills.split(",").map((s: string) => s.trim()).filter(Boolean) : []),
          education: user.education || "",
          username: user.username || "",
        });
        const imageUrl =
          user.profile_pic || user.profile_image_url || user.profile_image || "/static/uploads/default-avatar.svg";
        setProfileImageUrl(imageUrl as string);
      } catch (err: any) {
        setErrorMessage("Failed to load profile");
      } finally {
        setLoading(false);
      }
    })();
    return () => {
      isMounted = false;
    };
  }, [setLocation]);

  // Fetch user's job applications
  useEffect(() => {
    let isMounted = true;
    (async () => {
      try {
        const res = await fetch("/api/user/applications", { credentials: "include" });
        if (res.status === 401) {
          // User not authenticated, show empty applications
          if (isMounted) {
            setApplications([]);
            setApplicationsLoading(false);
          }
          return;
        }
        if (!res.ok) {
          throw new Error("Failed to fetch applications");
        }
        const data = await res.json();
        if (isMounted) {
          setApplications(data.applications || []);
          setApplicationsLoading(false);
        }
      } catch (err: any) {
        console.error("Error fetching applications:", err);
        if (isMounted) {
          setApplications([]);
          setApplicationsLoading(false);
        }
      }
    })();
    return () => {
      isMounted = false;
    };
  }, []);


  const handleSave = async () => {
    setSavingProfile(true);
    setErrorMessage(null);
    try {
      const payload: any = {
        first_name: profileData.firstName,
        last_name: profileData.lastName,
        email: profileData.email,
        phone: profileData.phone,
        location: profileData.location,
        title: profileData.title,
        bio: profileData.bio,
        skills: profileData.skills,
        education: profileData.education
      };
      const res = await fetch('/api/profile/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        const text = await res.text().catch(() => '');
        throw new Error(text || 'Failed to save profile');
      }
      setIsEditing(false);
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to save profile');
    } finally {
      setSavingProfile(false);
    }
  };

  const handleAddSkill = () => {
    const skill = newSkill.trim();
    if (!skill) return;
    if (profileData.skills.includes(skill)) {
      setNewSkill("");
      return;
    }
    setProfileData(prev => ({ ...prev, skills: [...prev.skills, skill] }));
    setNewSkill("");
  };

  const handleRemoveSkill = (skill: string) => {
    setProfileData(prev => ({ ...prev, skills: prev.skills.filter(s => s !== skill) }));
  };

  const handleInputChange = (field: string, value: string) => {
    setProfileData(prev => ({ ...prev, [field]: value }));
  };

  const handleSelectPhoto = () => {
    fileInputRef.current?.click();
  };

  const handleUploadPhoto: React.ChangeEventHandler<HTMLInputElement> = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploading(true);
    setErrorMessage(null);
    try {
      const form = new FormData();
      form.append("profile_picture", file);
      const res = await fetch("/api/upload-profile-picture", {
        method: "POST",
        body: form,
        credentials: "include",
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data?.success) {
        throw new Error(data?.message || "Failed to upload profile picture");
      }
      if (data.file_url) {
        setProfileImageUrl(data.file_url as string);
      }
    } catch (err: any) {
      setErrorMessage(err?.message || "Upload failed");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-8 relative">
        {isHr && (
          <div className="absolute top-3 right-3 w-3 h-3 rounded-full bg-green-500 shadow-[0_0_0_2px_#fff]" title="HR Account" />
        )}
        {loading && (
          <div className="text-center text-sm text-gray-600">Loading profile…</div>
        )}
        {errorMessage && (
          <div className="text-center text-sm text-red-600 mb-4">{errorMessage}</div>
        )}
        {!loading && !errorMessage && !profileData.firstName && (
          <div className="text-center text-sm text-blue-600 mb-4 bg-blue-50 p-4 rounded-lg">
            <p className="font-semibold">Welcome to Glow IQ!</p>
            <p>You're viewing in guest mode. <button onClick={() => setLocation("/login")} className="text-blue-600 underline hover:text-blue-800">Sign in</button> to access your full profile and save your resume scores.</p>
          </div>
        )}
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
                {/* Profile Photo */}
                <div className="flex items-center gap-6">
                  <img
                    src={profileImageUrl || "/static/uploads/default-avatar.svg"}
                    alt="Profile"
                    className="w-24 h-24 rounded-full object-cover border border-[#673ab733]"
                  />
                  <div className="space-y-2">
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      onChange={handleUploadPhoto}
                      className="hidden"
                    />
                    <Button
                      type="button"
                      onClick={handleSelectPhoto}
                      disabled={isUploading}
                      className="bg-[#673ab7] hover:bg-[#673ab7]/90 text-white"
                    >
                      {isUploading ? "Uploading..." : "Change Profile Photo"}
                    </Button>
                    <p className="text-xs text-gray-500">JPG, PNG, or WebP up to 2MB.</p>
                  </div>
                </div>
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
                  {isEditing && (
                    <div className="flex gap-2">
                      <Input
                        value={newSkill}
                        onChange={(e) => setNewSkill(e.target.value)}
                        placeholder="Add a skill"
                        className="border-[#673ab733]"
                        onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAddSkill(); } }}
                      />
                      <Button type="button" onClick={handleAddSkill} className="bg-[#673ab7] hover:bg-[#673ab7]/90 text-white">Add</Button>
                    </div>
                  )}
                  <div className="flex flex-wrap gap-2">
                    {profileData.skills.map((skill, index) => (
                      <div key={index} className="flex items-center gap-1 bg-[#00bfa61a] border border-[#673ab780] rounded px-2 py-1">
                        <span className="text-sm">{skill}</span>
                        {isEditing && (
                          <button
                            type="button"
                            onClick={() => handleRemoveSkill(skill)}
                            className="text-[#673ab7] hover:text-[#5329a0] text-xs"
                            aria-label={`Remove ${skill}`}
                          >
                            ×
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="font-caption">Education Qualification</Label>
                  {isEditing ? (
                    <Input
                      value={profileData.education}
                      onChange={(e) => handleInputChange("education", e.target.value)}
                      placeholder="e.g., B.Tech in CSE, XYZ University, 2022"
                      className="border-[#673ab733]"
                    />
                  ) : (
                    <p className="font-body text-[#000000b2]">{profileData.education || "Not specified"}</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Applications History */}
            <Card>
              <CardHeader>
                <CardTitle className="font-h5 text-[#673ab7]">Application History</CardTitle>
              </CardHeader>
              <CardContent>
                {applicationsLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="text-sm text-[#000000b2]">Loading applications...</div>
                  </div>
                ) : applications.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-8 text-center">
                    <Briefcase className="w-12 h-12 text-[#673ab733] mb-4" />
                    <p className="font-body text-[#000000b2] mb-2">No applications yet</p>
                    <p className="font-caption text-[#000000b2]">Start applying to jobs to see your application history here.</p>
                    <Button 
                      onClick={() => setLocation("/jobs")}
                      className="mt-4 bg-[#673ab7] hover:bg-[#5a2d91]"
                    >
                      Browse Jobs
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {applications.map((app) => (
                      <div key={app.id} className="border border-[#673ab733] rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="font-body font-semibold text-[#673ab7]">{app.position}</h3>
                            <p className="font-caption text-[#000000b2]">{app.company}</p>
                            {app.location && (
                              <p className="font-caption text-[#000000b2] text-xs mt-1">
                                <MapPin className="w-3 h-3 inline mr-1" />
                                {app.location}
                              </p>
                            )}
                          </div>
                          <Badge className={app.statusColor}>
                            {app.status}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-[#000000b2]">
                          <Calendar className="w-4 h-4" />
                          Applied on {new Date(app.appliedDate).toLocaleDateString()}
                        </div>
                        {app.job_type && (
                          <div className="mt-2">
                            <Badge variant="outline" className="text-xs">
                              {app.job_type.replace('_', ' ').toUpperCase()}
                            </Badge>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
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

            {/* ATS Score (mirrors Resume page ATS Checker) */}
            <Card>
              <CardHeader>
                <CardTitle className="font-h5 text-[#673ab7] flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  ATS Score
                </CardTitle>
              </CardHeader>
              <CardContent>
                {resumeScoresLoading ? (
                  <div className="text-center text-sm text-gray-600">Loading score...</div>
                ) : (
                  <div className="text-center py-4">
                    <div className="text-4xl font-bold text-[#673ab7] mb-1">
                      {(() => {
                        const local = Number(localStorage.getItem('ats_latest_score') || '0');
                        const api = Number(resumeScores?.summary?.latest_score || 0);
                        const score = Number.isFinite(local) && local > 0 ? local : api;
                        return `${Math.max(0, score)}/100`;
                      })()}
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-3">
                      <div
                        className="bg-[#673ab7] h-2 rounded-full"
                        style={{ width: `${(() => {
                          const local = Number(localStorage.getItem('ats_latest_score') || '0');
                          const api = Number(resumeScores?.summary?.latest_score || 0);
                          const score = Number.isFinite(local) && local > 0 ? local : api;
                          return Math.max(0, Math.min(100, score));
                        })()}%` }}
                      />
                    </div>
                    <div className="text-xs text-gray-600 mt-2">Latest ATS compatibility score</div>
                    <Button
                      onClick={() => setLocation("/resume")}
                      className="w-full mt-4 bg-[#673ab7] hover:bg-[#673ab7]/90 text-white"
                    >
                      Check / Improve Score
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Total Score */}
            <Card>
              <CardHeader>
                <CardTitle className="font-h5 text-[#673ab7] flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Total Score
                </CardTitle>
              </CardHeader>
              <CardContent>
                {resumeScoresLoading ? (
                  <div className="text-center text-sm text-gray-600">Calculating...</div>
                ) : (
                  <div className="text-center py-4">
                    {(() => {
                      const localAts = Number(localStorage.getItem('ats_latest_score') || '0');
                      const apiAts = Number(resumeScores?.summary?.latest_score || 0);
                      const ats = Number.isFinite(localAts) && localAts > 0 ? localAts : apiAts;
                      const total = Math.max(0, Math.min(100, ats));
                      return (
                        <>
                          <div className="text-4xl font-bold text-[#673ab7] mb-1">{`${total}/100`}</div>
                          <div className="w-full bg-gray-200 rounded-full h-2 mt-3">
                            <div
                              className="bg-[#673ab7] h-2 rounded-full"
                              style={{ width: `${total}%` }}
                            />
                          </div>
                          <div className="text-xs text-gray-600 mt-2">
                            Based on ATS Score ({total}/100)
                          </div>
                        </>
                      );
                    })()}
                  </div>
                )}
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
                  onClick={() => setLocation("/resume")}
                  variant="outline"
                  className="w-full border-[#673ab7] text-[#673ab7]"
                >
                  Resume Tester
                </Button>
                {profileData.firstName ? (
                  <>
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
                  </>
                ) : (
                  <Button
                    variant="outline"
                    onClick={() => setLocation("/login")}
                    className="w-full border-[#673ab7] text-[#673ab7]"
                  >
                    Sign In
                  </Button>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
    </div>
  );
};