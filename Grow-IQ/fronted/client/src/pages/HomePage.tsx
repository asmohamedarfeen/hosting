import React, { useEffect, useState } from "react";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { BounceButton } from "@/components/ui/bounce-animation";
import { usePageTransition } from "@/contexts/TransitionContext";
import { UserAvatar } from "@/components/UserAvatar";
import { 
  GraduationCap, 
  BookOpen, 
  Users, 
  Trophy, 
  TrendingUp, 
  Calendar, 
  ArrowRight, 
  Star,
  Clock,
  Target,
  Briefcase,
  Award,
  User,
  Globe,
  MoreHorizontal,
  LogOut,
  Flame
} from "lucide-react";
import { Calendar as CalendarComponent } from "@/components/ui/calendar";

export const HomePage = (): JSX.Element => {
  const [location] = useLocation();
  const { navigateWithBubbles } = usePageTransition();
  const [isMoreDropdownOpen, setIsMoreDropdownOpen] = useState(false);

  const stats = {
    totalCourses: 150,
    enrolledStudents: 1250,
    certificates: 320,
    skillBadges: 89
  };

  // Social feed state
  const [newPost, setNewPost] = useState("");
  const [posting, setPosting] = useState(false);
  const [feedError, setFeedError] = useState<string | null>(null);
  const [posts, setPosts] = useState<Array<any>>([]);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [expandedComments, setExpandedComments] = useState<Record<number, boolean>>({});
  const [commentsByPost, setCommentsByPost] = useState<Record<number, any[]>>({});
  const [commentDrafts, setCommentDrafts] = useState<Record<number, string>>({});

  // Calendar and streak state
  const [calendarData, setCalendarData] = useState<any[]>([]);
  const [streakStats, setStreakStats] = useState<any>(null);
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date());
  const [calendarLoading, setCalendarLoading] = useState(true);

  const handleUserClick = (userId: number) => {
    navigateWithBubbles(`/user/${userId}`);
  };

  // Fetch calendar and streak data
  const fetchCalendarData = async () => {
    try {
      setCalendarLoading(true);
      const currentDate = new Date();
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth() + 1;

      const [calendarRes, statsRes] = await Promise.all([
        fetch(`/api/streaks/get-calendar-data?year=${year}&month=${month}`, {
          credentials: "include"
        }),
        fetch("/api/streaks/get-streak-stats", {
          credentials: "include"
        })
      ]);

      if (calendarRes.ok) {
        const calendarResult = await calendarRes.json();
        setCalendarData(calendarResult.calendar_data || []);
      }

      if (statsRes.ok) {
        const statsResult = await statsRes.json();
        setStreakStats(statsResult);
      }
    } catch (error) {
      console.error("Error fetching calendar data:", error);
    } finally {
      setCalendarLoading(false);
    }
  };

  // Get calendar data for a specific date
  const getCalendarDataForDate = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    return calendarData.find(day => day.date === dateStr);
  };

  // Custom day renderer for the calendar
  const renderDay = (date: Date) => {
    const dayData = getCalendarDataForDate(date);
    const isToday = date.toDateString() === new Date().toDateString();
    
    return (
      <div className={`relative w-full h-full flex items-center justify-center text-xs ${
        isToday ? 'bg-blue-100 rounded-full' : ''
      }`}>
        <span className={isToday ? 'font-bold text-blue-600' : ''}>
          {date.getDate()}
        </span>
        {dayData?.has_activity && (
          <div className="absolute top-0 right-0 w-2 h-2 bg-green-500 rounded-full"></div>
        )}
        {dayData?.streak_count > 0 && (
          <div className="absolute bottom-0 right-0 w-1 h-1 bg-yellow-500 rounded-full"></div>
        )}
      </div>
    );
  };

  const fetchPosts = async () => {
    setFeedError(null);
    try {
      const res = await fetch("/social/posts", { credentials: "include" });
      if (!res.ok) throw new Error("Failed to load posts");
      const data = await res.json();
      setPosts(Array.isArray(data) ? data : []);
    } catch (e: any) {
      setFeedError(e?.message || "Failed to load posts");
    }
  };

  useEffect(() => {
    // Check if user is authenticated before fetching posts
    const checkAuthAndFetchPosts = async () => {
      try {
        const res = await fetch("/auth/profile", { credentials: "include" });
        if (res.status === 401) {
          // Not authenticated, redirect to login
          navigateWithBubbles("/login");
          return;
        }
        // User is authenticated, fetch posts and calendar data
        fetchPosts();
        fetchCalendarData();
      } catch (e) {
        console.error("Auth check failed:", e);
        navigateWithBubbles("/login");
      }
    };
    
    checkAuthAndFetchPosts();
    // Refresh calendar/stats on window focus
    const onFocus = () => fetchCalendarData();
    window.addEventListener('focus', onFocus);
    return () => {
      window.removeEventListener('focus', onFocus);
    };
  }, []);

  const quickActions = [
    {
      title: "Browse Jobs",
      description: "Explore career opportunities",
      icon: Briefcase,
      route: "/jobs",
      color: "bg-blue-100 text-blue-800"
    },
    {
      title: "View Workshops",
      description: "Join skill-building sessions",
      icon: Users,
      route: "/workshop",
      color: "bg-green-100 text-green-800"
    },
    {
      title: "Cultural Events",
      description: "Connect with community",
      icon: Star,
      route: "/cultural-events",
      color: "bg-yellow-100 text-yellow-800"
    }
  ];


  const handleCourseClick = (courseId: number) => {
    navigateWithBubbles(`/course/${courseId}`);
  };

  const handleQuickAction = (route: string) => {
    navigateWithBubbles(route);
  };

  const navigationItems = [
    {
      icon: User,
      route: "/profile",
      label: "Profile",
      testId: "nav-profile"
    },
    {
      icon: GraduationCap,
      route: "/",
      label: "Home",
      testId: "nav-home"
    },
    {
      icon: Briefcase,
      route: "/jobs",
      label: "Jobs",
      testId: "nav-jobs"
    },
    {
      icon: Globe,
      route: "/network",
      label: "Network",
      testId: "nav-network"
    },
    {
      icon: MoreHorizontal,
      route: "#",
      label: "More",
      testId: "nav-more"
    },
    {
      icon: LogOut,
      route: "/logout",
      label: "Logout",
      testId: "nav-logout"
    }
  ];

  const moreDropdownItems = [
    { label: "Workshop", route: "/workshop" },
    { label: "Resume", route: "/resume" },
    { label: "Cultural Events", route: "/cultural-events" }
  ];

  const handleNavigation = (route: string) => {
    navigateWithBubbles(route);
  };

  const handleMoreClick = () => {
    setIsMoreDropdownOpen(!isMoreDropdownOpen);
  };

  const handleMoreDropdownClick = (route: string) => {
    setIsMoreDropdownOpen(false);
    navigateWithBubbles(route);
  };

  const getGeneralStreak = (): number => {
    try {
      const list = streakStats?.streaks as Array<any>;
      if (Array.isArray(list)) {
        const general = list.find((s) => s.activity_type === 'general');
        if (general && typeof general.current_streak === 'number') {
          return general.current_streak;
        }
      }
      if (typeof streakStats?.total_current_streak === 'number') {
        return streakStats.total_current_streak;
      }
    } catch {}
    return 0;
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case "Beginner": return "bg-green-100 text-green-800";
      case "Intermediate": return "bg-yellow-100 text-yellow-800";
      case "Advanced": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getAuthorImageUrl = (post: any): string => {
    const a = post?.author || {};
    const raw = a.profile_image || a.profile_pic || a.profile_image_url;
    if (!raw) return "/static/uploads/default-avatar.svg";
    if (typeof raw === "string" && (raw.startsWith("http://") || raw.startsWith("https://") || raw.startsWith("/"))) {
      return raw;
    }
    return `/static/uploads/${raw}`;
  };

  return (
    <div className="flex-1 overflow-auto">
          <div className="max-w-6xl mx-auto p-8">
            {/* Welcome Section */}
            <div className="mb-8">
              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                Welcome to <span className="text-purple-600">GrowIQ</span> Education
              </h1>
              <p className="text-xl text-gray-600 mb-6">
                Accelerate your career with cutting-edge courses, expert workshops, and hands-on learning experiences.
              </p>
              
              <div className="flex flex-wrap gap-4">
                <Button 
                  size="lg" 
                  onClick={() => navigateWithBubbles("/workshop")}
                  className="flex items-center space-x-2"
                >
                  <BookOpen className="h-5 w-5" />
                  <span>Explore Courses</span>
                </Button>
                <Button 
                  size="lg" 
                  variant="outline"
                  onClick={() => navigateWithBubbles("/jobs")}
                  className="flex items-center space-x-2"
                >
                  <Briefcase className="h-5 w-5" />
                  <span>Find Jobs</span>
                </Button>
              </div>
            </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-blue-100 rounded-full">
                  <BookOpen className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{stats.totalCourses}+</p>
                  <p className="text-sm text-gray-600">Courses Available</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-green-100 rounded-full">
                  <Users className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{stats.enrolledStudents.toLocaleString()}</p>
                  <p className="text-sm text-gray-600">Active Learners</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-purple-100 rounded-full">
                  <Award className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{stats.certificates}</p>
                  <p className="text-sm text-gray-600">Certificates Earned</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-yellow-100 rounded-full">
                  <Trophy className="h-6 w-6 text-yellow-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{stats.skillBadges}</p>
                  <p className="text-sm text-gray-600">Skill Badges</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {quickActions.map((action, index) => (
              <Card 
                key={index} 
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => handleQuickAction(action.route)}
              >
                <CardContent className="p-6">
                  <div className="flex flex-col items-center text-center space-y-4">
                    <div className={`p-4 rounded-full ${action.color}`}>
                      <action.icon className="h-8 w-8" />
                    </div>
                    <div>
                      <h3 className="font-semibold mb-2">{action.title}</h3>
                      <p className="text-sm text-gray-600 mb-4">{action.description}</p>
                      <Button size="sm" variant="outline" className="w-full">
                        <ArrowRight className="h-4 w-4 ml-2" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Current Trends + Post Composer */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="h-6 w-6" />
                    <span>Current Trends</span>
                  </div>
                  <div />
                </CardTitle>
              </CardHeader>
              <CardContent>
                {/* Composer */}
                <div className="mb-6">
                  <Textarea
                    value={newPost}
                    onChange={(e) => setNewPost(e.target.value)}
                    placeholder="Share what's happening..."
                    className="border-[#673ab733] resize-y"
                    rows={3}
                  />
                  <div className="flex items-center gap-3 mt-2">
                    <label className="text-sm text-gray-700 cursor-pointer">
                      <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={(e) => setImageFile(e.target.files?.[0] || null)}
                      />
                      <span className="underline">Attach image</span>
                      {imageFile && <span className="ml-2 text-xs text-gray-500">{imageFile.name}</span>}
                    </label>
                    <label className="text-sm text-gray-700 cursor-pointer">
                      <input
                        type="file"
                        accept="video/*"
                        className="hidden"
                        onChange={(e) => setVideoFile(e.target.files?.[0] || null)}
                      />
                      <span className="underline">Attach video</span>
                      {videoFile && <span className="ml-2 text-xs text-gray-500">{videoFile.name}</span>}
                    </label>
                  </div>
                  <div className="flex justify-end mt-2">
                    <Button
                      size="sm"
                      disabled={!newPost.trim() || posting}
                      onClick={async () => {
                        setPosting(true);
                        setFeedError(null);
                        try {
                          const form = new FormData();
                          form.append("content", newPost.trim());
                          if (imageFile) form.append("image", imageFile);
                          if (videoFile) form.append("video", videoFile);
                          const res = await fetch("/social/posts/create", {
                            method: "POST",
                            body: form,
                            credentials: "include",
                          });
                          const data = await res.json().catch(() => ({}));
                          if (!res.ok) throw new Error(data?.detail || data?.message || "Failed to post");
                          setNewPost("");
                          setImageFile(null);
                          setVideoFile(null);
                          fetchPosts();
                        } catch (err: any) {
                          setFeedError(err?.message || "Failed to post");
                        } finally {
                          setPosting(false);
                        }
                      }}
                      className="bg-[#673ab7] hover:bg-[#673ab7]/90 text-white"
                    >
                      {posting ? "Posting..." : "Post"}
                    </Button>
                  </div>
                </div>

                {feedError && (
                  <div className="text-sm text-red-600 mb-3 flex items-center justify-between">
                    <span>{feedError}</span>
                    <Button size="sm" variant="outline" onClick={fetchPosts}>Retry</Button>
                  </div>
                )}

                {/* Feed */}
                <div className="space-y-4">
                  {posts.map((post) => (
                    <div key={post.id} className="p-4 border rounded-lg">
                      <div className="flex items-start gap-3 mb-2">
                        <UserAvatar 
                          user={post.author || {}} 
                          size="md"
                          showName={true}
                          showTitle={true}
                          title={post.author?.title}
                          clickable={true}
                          onUserClick={handleUserClick}
                        />
                        <div className="flex-1">
                          <div className="text-xs text-gray-500 mt-1">{new Date(post.created_at).toLocaleString()}</div>
                        </div>
                      </div>
                      <div className="text-gray-800 whitespace-pre-wrap mb-2">{post.content}</div>
                      {post.image_path && (
                        <img src={`/static/uploads/${post.image_path}`} className="rounded-md max-h-80 object-cover" />
                      )}
                      {post.video_path && (
                        <video controls className="rounded-md w-full max-h-96">
                          <source src={`/static/uploads/${post.video_path}`} />
                        </video>
                      )}
                      <div className="text-sm text-gray-600 mt-2 flex items-center gap-4">
                        <button
                          className={`text-sm ${post.is_liked ? "text-[#673ab7] font-semibold" : "text-gray-600"}`}
                          onClick={async () => {
                            try {
                              const res = await fetch(`/social/posts/${post.id}/like`, {
                                method: "POST",
                                credentials: "include",
                              });
                              const data = await res.json();
                              setPosts((prev) => prev.map((p) => (p.id === post.id ? { ...p, is_liked: data.is_liked, likes_count: data.likes_count } : p)));
                            } catch {}
                          }}
                        >
                          {post.is_liked ? "Unlike" : "Like"} • {post.likes_count}
                        </button>
                        <button
                          className="text-sm text-gray-600"
                          onClick={async () => {
                            const open = !expandedComments[post.id];
                            setExpandedComments({ ...expandedComments, [post.id]: open });
                            if (open && !commentsByPost[post.id]) {
                              try {
                                const res = await fetch(`/social/posts/${post.id}/comments`, { credentials: "include" });
                                const data = await res.json();
                                setCommentsByPost({ ...commentsByPost, [post.id]: data });
                              } catch {}
                            }
                          }}
                        >
                          Comments • {post.comments_count}
                        </button>
                      </div>

                      {expandedComments[post.id] && (
                        <div className="mt-3 space-y-3">
                          <div className="space-y-3">
                            {(commentsByPost[post.id] || []).map((c) => (
                              <div key={c.id} className="flex items-start gap-3">
                                <UserAvatar 
                                  user={c.author || {}} 
                                  size="sm"
                                  clickable={true}
                                  onUserClick={handleUserClick}
                                />
                                <div className="flex-1">
                                  <div className="text-sm">
                                    <span 
                                      className="font-medium text-gray-900 cursor-pointer hover:text-purple-600 transition-colors"
                                      onClick={() => c.author?.id && handleUserClick(c.author.id)}
                                    >
                                      {c.author?.full_name || "User"}
                                    </span>
                                    <span className="text-gray-600 ml-2">{c.content}</span>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                          <div className="flex items-start gap-2">
                            <Textarea
                              rows={2}
                              className="flex-1 border-[#673ab733]"
                              placeholder="Write a comment..."
                              value={commentDrafts[post.id] || ""}
                              onChange={(e) => setCommentDrafts({ ...commentDrafts, [post.id]: e.target.value })}
                            />
                            <Button
                              size="sm"
                              disabled={!commentDrafts[post.id]?.trim()}
                              onClick={async () => {
                                const content = (commentDrafts[post.id] || "").trim();
                                if (!content) return;
                                try {
                                  const form = new FormData();
                                  form.append("content", content);
                                  const res = await fetch(`/social/posts/${post.id}/comments`, {
                                    method: "POST",
                                    body: form,
                                    credentials: "include",
                                  });
                                  const data = await res.json();
                                  setCommentDrafts({ ...commentDrafts, [post.id]: "" });
                                  const resList = await fetch(`/social/posts/${post.id}/comments`, { credentials: "include" });
                                  const list = await resList.json();
                                  setCommentsByPost({ ...commentsByPost, [post.id]: list });
                                  setPosts((prev) => prev.map((p) => (p.id === post.id ? { ...p, comments_count: data.comments_count ?? p.comments_count + 1 } : p)));
                                } catch {}
                              }}
                              className="bg-[#673ab7] hover:bg-[#673ab7]/90 text-white"
                            >
                              Comment
                            </Button>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                  {(!feedError && posts.length === 0) && (
                    <div className="text-sm text-gray-500">No posts yet. Be the first to post!</div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Calendar */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Calendar className="h-5 w-5" />
                  <span>Calendar</span>
                  <div className="ml-auto flex items-center space-x-2 text-sm text-orange-600">
                    <Flame className="h-4 w-4" />
                    <span>{getGeneralStreak()} day streak</span>
                    <button
                      onClick={fetchCalendarData}
                      className="ml-2 px-2 py-1 text-xs rounded border border-orange-300 text-orange-700 hover:bg-orange-50"
                      aria-label="Refresh streaks"
                    >
                      Refresh
                    </button>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <h3 className="text-lg font-semibold mb-4">Activity Calendar</h3>
                  {calendarLoading ? (
                    <div className="flex items-center justify-center py-8">
                      <div className="text-sm text-gray-500">Loading calendar...</div>
                    </div>
                  ) : (
                    <div className="flex justify-center">
                      <CalendarComponent
                        mode="single"
                        selected={selectedDate}
                        onSelect={setSelectedDate}
                        showOutsideDays={true}
                        fixedWeeks={true}
                        className="rounded-lg border-0 w-full max-w-sm mx-auto"
                        classNames={{
                          months: "flex flex-col space-y-3",
                          month: "space-y-3",
                          caption: "flex justify-center pt-3 relative items-center mb-3",
                          caption_label: "text-base font-semibold text-gray-800",
                          nav: "space-x-1 flex items-center",
                          nav_button: "h-8 w-8 bg-transparent p-0 opacity-70 hover:opacity-100 text-gray-600 hover:bg-gray-100 rounded-full",
                          nav_button_previous: "absolute left-3",
                          nav_button_next: "absolute right-3",
                          table: "w-full border-collapse",
                          head_row: "flex justify-between mb-2",
                          head_cell: "text-gray-600 rounded-md w-9 font-medium text-[0.7rem] text-center py-2",
                          row: "flex w-full justify-between mb-1",
                          cell: "h-14 w-9 text-center p-0 relative",
                          day: "h-auto p-0 font-normal aria-selected:opacity-100",
                          day_selected: "bg-transparent",
                          day_today: "bg-transparent",
                          day_outside: "day-outside text-gray-300",
                          day_disabled: "text-gray-300",
                          day_hidden: "invisible",
                        }}
                        components={{
                          Day: ({ date, ...props }) => {
                            const dayData = getCalendarDataForDate(date);
                            const isToday = date.toDateString() === new Date().toDateString();
                            const hasActivity = dayData?.has_activity;
                            const streakCount = dayData?.streak_count || 0;
                            const isCurrentMonth = date.getMonth() === new Date().getMonth();
                            
                            return (
                              <div 
                                {...props}
                                className="relative w-full h-full flex flex-col items-center justify-center cursor-pointer p-1"
                              >
                                {/* Date number in a circle */}
                                <div className={`w-7 h-7 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
                                  isToday 
                                    ? 'bg-green-500 text-white shadow-md' 
                                    : hasActivity && isCurrentMonth
                                      ? 'bg-gray-100 text-gray-700 hover:bg-gray-200' 
                                      : isCurrentMonth
                                        ? 'text-gray-700 hover:bg-gray-50'
                                        : 'text-gray-300'
                                }`}>
                                  {date.getDate()}
                                </div>
                                
                                {/* Activity dots below the date - only show for current month */}
                                {isCurrentMonth && (
                                  <div className="flex space-x-0.5 mt-1">
                                    {hasActivity && (
                                      <div className={`w-1.5 h-1.5 rounded-full ${
                                        streakCount > 0 ? 'bg-green-500' : 'bg-red-500'
                                      }`}></div>
                                    )}
                                    {streakCount > 0 && (
                                      <div className="w-1.5 h-1.5 rounded-full bg-yellow-400"></div>
                                    )}
                                  </div>
                                )}
                              </div>
                            );
                          }
                        }}
                      />
                    </div>
                  )}
                  
                  {/* Legend */}
                  <div className="mt-4 flex justify-center space-x-4 text-xs text-gray-600">
                    <div className="flex items-center space-x-1">
                      <div className="w-1.5 h-1.5 bg-red-500 rounded-full"></div>
                      <span>Activity</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                      <span>Streak</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <div className="w-1.5 h-1.5 bg-yellow-400 rounded-full"></div>
                      <span>Reward</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                        <span className="text-white text-xs font-medium">12</span>
                      </div>
                      <span>Today</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Your Progress section removed per request */}
          </div>
        </div>
      </div>
    </div>
  );
};