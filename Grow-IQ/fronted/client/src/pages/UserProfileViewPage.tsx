import React, { useEffect, useState } from "react";
import { useRoute, useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { usePageTransition } from "@/contexts/TransitionContext";
import { UserAvatar } from "@/components/UserAvatar";
import { 
  ArrowLeft, 
  MapPin, 
  Mail, 
  Phone, 
  Globe, 
  Linkedin, 
  Github, 
  Briefcase,
  Award,
  GraduationCap,
  Calendar,
  User,
  ExternalLink,
  FileText,
  TrendingUp
} from "lucide-react";

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

export const UserProfileViewPage = (): JSX.Element => {
  const [, params] = useRoute("/user/:id");
  const [location, setLocation] = useLocation();
  const { navigateWithBubbles } = usePageTransition();
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [resumeScores, setResumeScores] = useState<{ summary?: { latest_score?: number } } | null>(null);
  const [scoreLoading, setScoreLoading] = useState(true);

  const userId = params?.id;

  useEffect(() => {
    if (!userId) {
      setError("User ID not provided");
      setLoading(false);
      return;
    }

    const fetchUserProfile = async () => {
      try {
        setLoading(true);
        const res = await fetch(`/auth/profile/${userId}`, { 
          credentials: "include" 
        });
        
        if (!res.ok) {
          if (res.status === 404) {
            throw new Error("User not found");
          } else if (res.status === 403) {
            throw new Error("You don't have permission to view this profile");
          } else {
            throw new Error("Failed to load user profile");
          }
        }
        
        const profile = await res.json();
        setUserProfile(profile);
      } catch (e: any) {
        setError(e.message || "Failed to load user profile");
      } finally {
        setLoading(false);
      }
    };

    fetchUserProfile();
  }, [userId]);

  useEffect(() => {
    if (!userId) return;
    let mounted = true;
    (async () => {
      try {
        // Try HR-scoped endpoints; fall back silently if not available
        const atsRes = await fetch(`/api/hr/applicants/${userId}/resume-scores`, { credentials: "include" }).catch(() => null);
        if (mounted) {
          if (atsRes && atsRes.ok) {
            const data = await atsRes.json().catch(() => null);
            setResumeScores(data);
          }
        }
      } catch (_) {
        // ignore; show no scores
      } finally {
        if (mounted) setScoreLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [userId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center">
        <Card className="max-w-2xl w-full mx-4">
          <CardContent className="py-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading profile...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !userProfile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center">
        <Card className="max-w-2xl w-full mx-4">
          <CardContent className="py-12 text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <User className="w-8 h-8 text-red-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              {error || "Profile not found"}
            </h2>
            <p className="text-gray-600 mb-6">
              {error === "User not found" 
                ? "The user you're looking for doesn't exist or has been removed."
                : error === "You don't have permission to view this profile"
                ? "You don't have the necessary permissions to view this profile."
                : "Something went wrong while loading the profile."
              }
            </p>
            <Button
              onClick={() => navigateWithBubbles("/home")}
              className="bg-purple-600 hover:bg-purple-700"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Home
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="max-w-4xl mx-auto p-4">
        {/* Header */}
        <div className="mb-6">
          <Button
            onClick={() => navigateWithBubbles("/home")}
            variant="outline"
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
        </div>

        {/* Profile Header */}
        <Card className="mb-6 shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardContent className="p-8">
            <div className="text-center">
              <div className="flex justify-center mb-6">
                <UserAvatar 
                  user={userProfile} 
                  size="xl"
                  showName={true}
                  showTitle={true}
                  title={userProfile.title}
                />
              </div>
              
              <div className="space-y-2 mb-6">
                <h1 className="text-3xl font-bold text-gray-900">
                  {userProfile.full_name}
                </h1>
                <p className="text-lg text-gray-600">
                  {userProfile.title || 'Professional'}
                </p>
                {userProfile.company && (
                  <p className="text-gray-500">
                    {userProfile.company}
                  </p>
                )}
              </div>

              <div className="flex justify-center gap-2 flex-wrap">
                {userProfile.location && (
                  <Badge variant="outline" className="flex items-center gap-1">
                    <MapPin className="w-3 h-3" />
                    {userProfile.location}
                  </Badge>
                )}
                {userProfile.industry && (
                  <Badge variant="outline" className="bg-blue-50 text-blue-700">
                    {userProfile.industry}
                  </Badge>
                )}
                {userProfile.experience_years && (
                  <Badge variant="outline" className="bg-green-50 text-green-700">
                    {userProfile.experience_years} years experience
                  </Badge>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* About Section */}
            {userProfile.bio && (
              <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="w-5 h-5 text-purple-600" />
                    About
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 leading-relaxed">
                    {userProfile.bio}
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Skills Section */}
            {userProfile.skills && (
              <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="w-5 h-5 text-purple-600" />
                    Skills
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {userProfile.skills.split(',').map((skill, index) => (
                      <Badge key={index} variant="outline" className="bg-purple-50 text-purple-700">
                        {skill.trim()}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Education Section */}
            {userProfile.education && (
              <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <GraduationCap className="w-5 h-5 text-purple-600" />
                    Education
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="whitespace-pre-wrap text-gray-700">
                    {userProfile.education}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Certifications Section */}
            {userProfile.certifications && (
              <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="w-5 h-5 text-purple-600" />
                    Certifications
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="whitespace-pre-wrap text-gray-700">
                    {userProfile.certifications}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Interests Section */}
            {userProfile.interests && (
              <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Briefcase className="w-5 h-5 text-purple-600" />
                    Interests
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700">
                    {userProfile.interests}
                  </p>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Contact Information */}
            <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-lg">Contact Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {userProfile.email && (
                  <div className="flex items-center gap-3">
                    <Mail className="w-4 h-4 text-gray-500" />
                    <span className="text-sm text-gray-600">{userProfile.email}</span>
                  </div>
                )}
                {userProfile.phone && (
                  <div className="flex items-center gap-3">
                    <Phone className="w-4 h-4 text-gray-500" />
                    <span className="text-sm text-gray-600">{userProfile.phone}</span>
                  </div>
                )}
                {userProfile.website && (
                  <div className="flex items-center gap-3">
                    <Globe className="w-4 h-4 text-gray-500" />
                    <a 
                      href={userProfile.website} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline flex items-center gap-1"
                    >
                      Website
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                )}
                {userProfile.linkedin_url && (
                  <div className="flex items-center gap-3">
                    <Linkedin className="w-4 h-4 text-gray-500" />
                    <a 
                      href={userProfile.linkedin_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline flex items-center gap-1"
                    >
                      LinkedIn
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                )}
                {userProfile.github_url && (
                  <div className="flex items-center gap-3">
                    <Github className="w-4 h-4 text-gray-500" />
                    <a 
                      href={userProfile.github_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline flex items-center gap-1"
                    >
                      GitHub
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                )}
                {userProfile.portfolio_url && (
                  <div className="flex items-center gap-3">
                    <Briefcase className="w-4 h-4 text-gray-500" />
                    <a 
                      href={userProfile.portfolio_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline flex items-center gap-1"
                    >
                      Portfolio
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* ATS Score (if available) */}
            <Card>
              <CardHeader>
                <CardTitle className="font-h5 text-[#673ab7] flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  ATS Score
                </CardTitle>
              </CardHeader>
              <CardContent>
                {scoreLoading ? (
                  <div className="text-center text-sm text-gray-600">Loading score...</div>
                ) : resumeScores?.summary?.latest_score != null ? (
                  <div className="text-center py-4">
                    <div className="text-4xl font-bold text-[#673ab7] mb-1">
                      {`${Math.max(0, Number(resumeScores.summary.latest_score || 0))}/100`}
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-3">
                      <div
                        className="bg-[#673ab7] h-2 rounded-full"
                        style={{ width: `${Math.max(0, Math.min(100, Number(resumeScores.summary.latest_score || 0)))}%` }}
                      />
                    </div>
                    <div className="text-xs text-gray-600 mt-2">Latest ATS compatibility score</div>
                  </div>
                ) : (
                  <div className="text-center text-sm text-gray-600">Not available</div>
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
                {scoreLoading ? (
                  <div className="text-center text-sm text-gray-600">Calculating...</div>
                ) : (
                  <div className="text-center py-4">
                    {(() => {
                      const ats = Number(resumeScores?.summary?.latest_score || 0);
                      if (!Number.isFinite(ats) || ats === 0) {
                        return <div className="text-sm text-gray-600">Not available</div>;
                      }
                      const total = Math.max(0, Math.min(100, ats));
                      return (
                        <>
                          <div className="text-4xl font-bold text-[#673ab7] mb-1">{`${total}/100`}</div>
                          <div className="w-full bg-gray-200 rounded-full h-2 mt-3">
                            <div className="bg-[#673ab7] h-2 rounded-full" style={{ width: `${total}%` }} />
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

            {/* Profile Stats */}
            <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-lg">Profile Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-3">
                  <Calendar className="w-4 h-4 text-gray-500" />
                  <div>
                    <div className="text-sm font-medium text-gray-900">Member since</div>
                    <div className="text-xs text-gray-600">
                      {new Date(userProfile.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
                {userProfile.experience_years && (
                  <div className="flex items-center gap-3">
                    <Briefcase className="w-4 h-4 text-gray-500" />
                    <div>
                      <div className="text-sm font-medium text-gray-900">Experience</div>
                      <div className="text-xs text-gray-600">
                        {userProfile.experience_years} years
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};
