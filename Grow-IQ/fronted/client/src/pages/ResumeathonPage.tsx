import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Trophy, Medal, Award, Crown, Zap } from "lucide-react";
import { ResumeTester } from "@/components/ResumeTester";

interface LeaderboardUser {
  rank: number;
  name: string;
  score: number;
  avatar: string;
  badge: string;
  color: string;
  user_id?: number;  // Optional user_id to identify current user
}

export const ResumeathonPage = (): JSX.Element => {
  const [showResumeTester, setShowResumeTester] = useState(false);
  const [hasJoinedGame, setHasJoinedGame] = useState(false);
  const [userName, setUserName] = useState("You");
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  const [leaderboardUsers, setLeaderboardUsers] = useState<LeaderboardUser[]>([]);
  const [atsScore, setAtsScore] = useState<number>(() => {
    const stored = Number(localStorage.getItem('ats_latest_score') || '0');
    return Number.isFinite(stored) ? stored : 0;
  });

  const loadLatestAtsScore = async () => {
    try {
      const res = await fetch('/api/resume-scores', { credentials: 'include' });
      if (!res.ok) return;
      const data = await res.json();
      let latest: number | undefined;
      if (data && data.summary && typeof data.summary.latest_score !== 'undefined') {
        latest = Number(data.summary.latest_score);
      } else if (data && Array.isArray(data.resume_scores) && data.resume_scores.length > 0) {
        latest = Number(data.resume_scores[0].total_score);
      }
      if (Number.isFinite(latest) && (latest as number) > 0) {
        setAtsScore(latest as number);
        localStorage.setItem('ats_latest_score', String(latest));
      }
    } catch (_) {
      // Do not overwrite existing score on failure
    }
  };

  // Function to load leaderboard data from API
  const loadLeaderboardData = async () => {
    try {
      const response = await fetch('/resume-tester/resumeathon-leaderboard', {
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Leaderboard data received:', data);
        
        // Always set leaderboard data, even if empty
        if (data.success !== false) {
          // Sort leaderboard by score (high to low) as a safeguard
          // This ensures correct ordering even if backend ordering has issues
          const sortedLeaderboard = (data.leaderboard || []).sort((a: LeaderboardUser, b: LeaderboardUser) => {
            return b.score - a.score;
          });
          
          // Re-assign ranks after sorting
          const rankedLeaderboard = sortedLeaderboard.map((user, index) => ({
            ...user,
            rank: index + 1
          }));
          
          setLeaderboardUsers(rankedLeaderboard);
          setHasJoinedGame(data.user_joined || false);
          
          // Set current user ID from API response if available
          if (data.current_user_id) {
            setCurrentUserId(data.current_user_id);
          }
        } else {
          console.error('Leaderboard API returned error:', data.error);
          setLeaderboardUsers([]);
          setHasJoinedGame(false);
        }
      } else {
        console.error('Failed to fetch leaderboard:', response.status, response.statusText);
        const errorData = await response.json().catch(() => ({}));
        console.error('Error details:', errorData);
        setLeaderboardUsers([]);
        setHasJoinedGame(false);
      }
    } catch (error) {
      console.error('Error loading leaderboard data:', error);
      setLeaderboardUsers([]);
      setHasJoinedGame(false);
    }
  };

  // Load current user ID
  useEffect(() => {
    const loadCurrentUser = async () => {
      try {
        const res = await fetch('/auth/profile', { credentials: 'include' });
        if (res.ok) {
          const userData = await res.json();
          if (userData && userData.id) {
            setCurrentUserId(userData.id);
            setUserName(userData.full_name || userData.username || 'You');
          }
        }
      } catch (error) {
        console.error('Failed to load current user:', error);
      }
    };
    
    loadCurrentUser();
  }, []);

  // Load user data and check if they've joined the game
  useEffect(() => {
    // Load leaderboard data from API
    loadLeaderboardData();
    // Load latest ATS score
    loadLatestAtsScore();
    
    // Set user name from localStorage as fallback
    const storedUserName = localStorage.getItem('user_name') || 'You';
    setUserName(prev => prev === 'You' ? storedUserName : prev);
  }, []);

  // Function to handle joining the game
  const handleJoinGame = async () => {
    try {
      // Call backend API to join the leaderboard
      const response = await fetch('/resume-tester/join-resumeathon', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for authentication
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        // Update local state
        setHasJoinedGame(true);
        setUserName(data.user.name || 'You');
        
        // Store in localStorage
        localStorage.setItem('resumeathon_joined', 'true');
        localStorage.setItem('user_name', data.user.name || 'You');
        
        // Refresh leaderboard data
        await loadLeaderboardData();
        
        console.log('Successfully joined Resumeathon:', data.message);
      } else {
        console.error('Failed to join Resumeathon:', data.message);
        
        // Show error message to user
        if (data.error === 'NO_RESUME_TEST') {
          alert('You need to test your resume first before joining the leaderboard. Please upload and analyze your resume using the ATS Checker.');
        } else {
          alert(`Failed to join Resumeathon: ${data.message}`);
        }
      }
      
    } catch (error) {
      console.error('Error joining the game:', error);
      alert('Error connecting to server. Please try again.');
    }
  };

  // Show resume tester if activated
  if (showResumeTester) {
    return (
      <ResumeTester 
        onClose={() => setShowResumeTester(false)} 
        onScored={(score) => {
          setAtsScore(score);
          localStorage.setItem('ats_latest_score', String(score));
          // Optionally refresh leaderboard too
          loadLeaderboardData();
        }}
      />
    );
  }

  return (
    <div className="bg-neutral-100 min-h-screen">
      <div className="max-w-6xl mx-auto p-8">
        {/* Header Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4 flex items-center">
            <Trophy className="h-8 w-8 text-yellow-600 mr-3" />
            Resumeathon
          </h1>
          <p className="text-gray-600 text-lg">
            Compete with other users and see how your ATS score ranks on our leaderboard!
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* ATS Score Display */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Zap className="h-5 w-5 text-blue-600" />
                  <span>Your ATS Score</span>
                </CardTitle>
                <p className="text-sm text-gray-600">
                  Your current ATS compatibility score
                </p>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  {/* ATS Score Display */}
                  <div className="mb-6">
                    <div className="text-6xl font-bold text-blue-600 mb-2">
                      {atsScore}
                    </div>
                    <div className="text-2xl font-semibold text-gray-700 mb-1">
                      ATS Score
                    </div>
                    <div className="text-sm text-gray-500">
                      Overall compatibility with Applicant Tracking Systems
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="w-full bg-gray-200 rounded-full h-3 mb-6">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all duration-1000"
                      style={{ width: `${atsScore}%` }}
                    ></div>
                  </div>
                  
                  {/* Action Button */}
                  <Button 
                    className="w-full bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700 text-white font-semibold py-3 px-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300" 
                    onClick={() => setShowResumeTester(true)}
                  >
                    <Zap className="h-5 w-5 mr-2" />
                    Analyze Your Resume
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Resumeathon Leaderboard */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Trophy className="h-5 w-5 text-yellow-600" />
                  <span>Leaderboard</span>
                </CardTitle>
                <p className="text-sm text-gray-600">
                  ATS Score Leaderboard - See how you rank against other users
                </p>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {leaderboardUsers.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <Trophy className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p className="text-lg font-medium">No players yet!</p>
                      <p className="text-sm">Be the first to join the Resumeathon leaderboard</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {leaderboardUsers.map((user) => {
                        const BadgeIcon = user.badge === "Crown" ? Crown : 
                                        user.badge === "Trophy" ? Trophy : 
                                        user.badge === "Medal" ? Medal : Award;
                        
                        // Check if this is the current user
                        const isCurrentUser = currentUserId !== null && user.user_id === currentUserId;
                        
                        // Top 3 get golden background, current user gets blue border
                        const isTopThree = user.rank <= 3;
                        const bgClass = isTopThree 
                          ? "bg-gradient-to-r from-yellow-50 to-orange-50" 
                          : "bg-gray-50";
                        const borderClass = isCurrentUser 
                          ? "border-4 border-blue-500" 
                          : (isTopThree ? "border-2 border-yellow-400" : "border border-gray-200");
                        
                        return (
                          <div 
                            key={user.rank} 
                            className={`flex items-center justify-between p-4 rounded-lg ${bgClass} ${borderClass} transition-all hover:shadow-md`}
                          >
                            <div className="flex items-center space-x-4">
                              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-white border-2 border-gray-300">
                                <span className="text-sm font-bold text-gray-700">#{user.rank}</span>
                              </div>
                              
                              <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
                                  {user.avatar}
                                </div>
                                <div>
                                  <h4 className="font-semibold text-gray-900">{user.name}</h4>
                                  <div className="flex items-center space-x-2">
                                    <BadgeIcon className={`h-4 w-4 ${user.color}`} />
                                    <span className="text-sm text-gray-600">ATS Score</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                            
                            <div className="flex items-center space-x-4">
                              <div className="text-right">
                                <div className="text-2xl font-bold text-gray-900">{user.score}</div>
                                <div className="text-xs text-gray-500">points</div>
                              </div>
                              
                              <div className="w-16 bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-1000"
                                  style={{ width: `${user.score}%` }}
                                />
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                  
                  <div className="mt-6 text-center">
                    <Button 
                      className={`font-semibold py-3 px-8 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 ${
                        hasJoinedGame 
                          ? "bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white" 
                          : "bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white"
                      }`}
                      onClick={hasJoinedGame ? () => setShowResumeTester(true) : handleJoinGame}
                    >
                      <Trophy className="h-5 w-5 mr-2" />
                      {hasJoinedGame ? "Improve Your Score" : "Get into the Game"}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};
