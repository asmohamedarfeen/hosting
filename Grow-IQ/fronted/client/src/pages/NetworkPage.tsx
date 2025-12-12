import React, { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { usePageTransition } from "@/contexts/TransitionContext";
import { mainAppService, MainUser, Connection, ConnectionRequest } from "@/services/mainAppService";

// Use environment variable or empty string for relative URLs
const MAIN_API_BASE = import.meta.env.VITE_API_BASE_URL || '';
import { 
  ArrowLeft, 
  Users, 
  MessageCircle, 
  UserPlus, 
  Check, 
  X,
  Search,
  Mail,
  Phone,
  MapPin,
  Briefcase,
  Calendar,
  Globe,
  Linkedin,
  Twitter,
  Github,
  RefreshCw
} from "lucide-react";

export const NetworkPage = (): JSX.Element => {
  const [location, setLocation] = useLocation();
  const { navigateWithBubbles } = usePageTransition();
  
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState<MainUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Network data
  const [users, setUsers] = useState<MainUser[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [requests, setRequests] = useState<ConnectionRequest[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState<'all' | 'connections' | 'requests'>('all');
  const [successMessage, setSuccessMessage] = useState<string>("");

  // Stats
  const [stats, setStats] = useState({
    totalConnections: 0,
    pendingRequests: 0,
    sentRequests: 0
  });

  // Check authentication on mount
  useEffect(() => {
    console.log('NetworkPage mounted, checking authentication...');
    checkAuthentication();
  }, []);

  // Debug effect to log state changes
  useEffect(() => {
    console.log('NetworkPage state changed:', {
      isAuthenticated,
      isLoading,
      currentUser: currentUser?.id,
      connections: connections.length,
      users: users.length,
      activeTab
    });
  }, [isAuthenticated, isLoading, currentUser, connections.length, users.length, activeTab]);

  // Load data when authenticated
  useEffect(() => {
    console.log('Authentication state changed:', { isAuthenticated, isLoading });
    if (isAuthenticated) {
      loadNetworkData();
    }
  }, [isAuthenticated]);

  const checkAuthentication = async () => {
    try {
      // Check if user is logged into main app
      const mainUser = await mainAppService.getCurrentUser();
      setCurrentUser(mainUser);
      setIsAuthenticated(true);
      console.log('Main app user authenticated:', mainUser.name || mainUser.full_name, 'ID:', mainUser.id);
    } catch (error) {
      console.log('User not authenticated, showing public network view:', error);
      setIsAuthenticated(false);
      // Still load users even if not authenticated
      loadNetworkData();
    } finally {
      setIsLoading(false);
    }
  };

  const loadNetworkData = async () => {
    try {
      setIsLoading(true);
      console.log('Loading network data...');
      
      // Try to get users first (this should work even without auth)
      const usersData = await mainAppService.getUsers(0, 100);
      console.log('Users loaded:', usersData.users.length, usersData);
      setUsers(usersData.users);
      
      // Try to get connections (this might fail if not authenticated)
      try {
        const connectionsData = await mainAppService.getConnections();
        console.log('Connections data loaded:', connectionsData);
        const allConnections = [...connectionsData.sent_connections, ...connectionsData.received_connections];
        console.log('All connections:', allConnections);
        console.log('Sent connections:', connectionsData.sent_connections);
        console.log('Received connections:', connectionsData.received_connections);
        setConnections(allConnections);
        setRequests(connectionsData.requests);
        
        // Calculate stats
        const acceptedConnections = connectionsData.sent_connections.filter((c: Connection) => c.status === 'accepted').length +
                                   connectionsData.received_connections.filter((c: Connection) => c.status === 'accepted').length;
        const pendingReceived = connectionsData.requests.length; // Pending requests from others
        const pendingSent = connectionsData.sent_connections.filter((c: Connection) => c.status === 'pending').length;
        
        setStats({
          totalConnections: acceptedConnections,
          pendingRequests: pendingReceived,
          sentRequests: pendingSent
        });
      } catch (connError) {
        console.log('Connections not available (user not authenticated):', connError);
        setConnections([]);
        setRequests([]);
        setStats({
          totalConnections: 0,
          pendingRequests: 0,
          sentRequests: 0
        });
      }
    } catch (error) {
      console.error('Failed to load network data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConnectionRequest = async (userId: number) => {
    try {
      const status = getConnectionStatus(userId);
      if (status !== 'none') {
        setSuccessMessage(status === 'accepted' ? 'You are already connected.' : 'A request already exists.');
        // Navigate to where the person will appear
        if (status === 'accepted') {
          setActiveTab('connections');
        } else {
          setActiveTab('requests');
        }
        await loadNetworkData();
        setTimeout(() => setSuccessMessage(''), 3000);
        return;
      }

      await mainAppService.sendConnectionRequest(userId);
      setActiveTab('requests');
      await loadNetworkData(); // Refresh data
      
      // Show success message
      setSuccessMessage('Connection request sent successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (error: any) {
      console.error('Failed to send connection request:', error);
      
      // Show error message
      const msg = error?.message?.toString()?.toLowerCase() || '';
      if (msg.includes('already') || msg.includes('pending')) {
        setSuccessMessage('A request already exists or you are connected.');
        // Try to route to appropriate tab even if backend reported it
        const status = getConnectionStatus(userId);
        if (status === 'accepted') {
          setActiveTab('connections');
        } else {
          setActiveTab('requests');
        }
        await loadNetworkData();
      } else if (msg.includes('401')) {
        setSuccessMessage('Please log in to connect.');
      } else {
        setSuccessMessage('Failed to send connection request.');
      }
      setTimeout(() => setSuccessMessage(''), 5000);
    }
  };

  const handleAcceptConnection = async (userId: number) => {
    try {
      // Find the request for this user
      const request = requests.find(req => req.sender.id === userId);
      if (request) {
        console.log('Accepting connection request:', request);
        await mainAppService.acceptConnection(request.id);
        console.log('Connection accepted, refreshing data...');
        
        // Find the user object for the accepted connection
        const connectedUser = users.find(u => u.id === userId);
        if (!connectedUser) {
          console.error('User not found for connection:', userId);
          return;
        }
        
        // Immediately update the UI optimistically
        const newConnection: Connection = {
          id: request.id,
          user_id: currentUser?.id || 0,
          connected_user_id: userId,
          status: 'accepted',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          user: currentUser!,
          connected_user: connectedUser
        };
        
        // Add the new connection to the connections array
        setConnections(prev => [...prev, newConnection]);
        
        // Remove the request from the requests array
        setRequests(prev => prev.filter(req => req.id !== request.id));
        
        // Update stats
        setStats(prev => ({
          ...prev,
          totalConnections: prev.totalConnections + 1,
          pendingRequests: prev.pendingRequests - 1
        }));
        
        // Then refresh data to ensure consistency
        await loadNetworkData();
        console.log('Data refreshed after accepting connection');
        
        // Switch to connections tab to show the new connection
        setActiveTab('connections');
        
        // Show success message
        setSuccessMessage('Connection accepted! User added to your connections.');
        setTimeout(() => setSuccessMessage(''), 3000);
      } else {
        console.error('No request found for user:', userId);
      }
    } catch (error) {
      console.error('Failed to accept connection:', error);
    }
  };

  const handleRejectConnection = async (userId: number) => {
    try {
      // Find the request for this user
      const request = requests.find(req => req.sender.id === userId);
      if (request) {
        await mainAppService.rejectConnection(request.id);
        await loadNetworkData(); // Refresh data
      }
    } catch (error) {
      console.error('Failed to reject connection:', error);
    }
  };

  const handleStartMessage = (user: MainUser) => {
    // Navigate to messaging page with user ID as parameter
    navigateWithBubbles(`/messaging?user=${user.id}`);
  };

  const filteredUsers = users.filter(user => {
    if (user.id === currentUser?.id) return false;
    
    const matchesSearch = (user.name || user.full_name || user.username || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchQuery.toLowerCase());
    
    if (activeTab === 'connections') {
      const isConnected = connections.some(conn => 
        conn.status === 'accepted' && 
        ((conn.user_id === currentUser?.id && conn.connected_user_id === user.id) ||
         (conn.connected_user_id === currentUser?.id && conn.user_id === user.id))
      );
      console.log(`User ${user.name} (${user.id}) - isConnected: ${isConnected}`, {
        connections: connections.length,
        currentUser: currentUser?.id,
        connectionCheck: connections.map(c => ({
          id: c.id,
          user_id: c.user_id,
          connected_user_id: c.connected_user_id,
          status: c.status
        }))
      });
      return matchesSearch && isConnected;
    }
    
    if (activeTab === 'requests') {
      // Show users who have sent requests to the current user
      const hasPendingRequest = requests.some(req => req.sender.id === user.id);
      return matchesSearch && hasPendingRequest;
    }
    
    return matchesSearch;
  });

  console.log('NetworkPage render:', { 
    users: users.length, 
    filteredUsers: filteredUsers.length, 
    isAuthenticated, 
    isLoading,
    searchQuery,
    activeTab 
  });

  const getConnectionStatus = (userId: number) => {
    // Check if there's an accepted connection first
    const acceptedConnection = connections.find(conn => 
      ((conn.user_id === currentUser?.id && conn.connected_user_id === userId) ||
       (conn.connected_user_id === currentUser?.id && conn.user_id === userId)) &&
      conn.status === 'accepted'
    );
    if (acceptedConnection) return 'accepted';
    
    // Check if there's a pending request from this user
    const hasRequestFromUser = requests.some(req => req.sender.id === userId);
    if (hasRequestFromUser) return 'pending_received';
    
    // Check if current user has sent a request to this user
    const hasSentRequest = connections.some(conn => 
      conn.user_id === currentUser?.id && conn.connected_user_id === userId && conn.status === 'pending'
    );
    if (hasSentRequest) return 'pending_sent';
    
    return 'none';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading network...</p>
        </div>
      </div>
    );
  }

  // Show a banner if not authenticated but still show the network
  const showAuthBanner = !isAuthenticated && !isLoading;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Authentication Banner */}
      {showAuthBanner && (
        <div className="bg-blue-50 border-b border-blue-200 px-4 py-3">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Users className="h-5 w-5 text-blue-400" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-blue-800">
                  You're viewing the public network. <Button variant="link" className="p-0 h-auto text-blue-600 underline" onClick={() => navigateWithBubbles("/login")}>Login</Button> to connect with others.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Success/Error Message */}
      {successMessage && (
        <div className={`border rounded-lg p-4 flex items-center mx-4 mt-4 ${
          successMessage.includes('Failed') 
            ? 'bg-red-50 border-red-200' 
            : 'bg-green-50 border-green-200'
        }`}>
          {successMessage.includes('Failed') ? (
            <X className="w-5 h-5 text-red-600 mr-2" />
          ) : (
            <Check className="w-5 h-5 text-green-600 mr-2" />
          )}
          <span className={`font-medium ${
            successMessage.includes('Failed') 
              ? 'text-red-800' 
              : 'text-green-800'
          }`}>{successMessage}</span>
        </div>
      )}
      
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center space-x-6">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigateWithBubbles("/home")}
                className="hover:bg-gray-100 p-2"
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">My Network</h1>
                <p className="text-sm text-gray-500 mt-1">
                  Connect with professionals and grow your network
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {currentUser && (
                <div className="flex items-center space-x-3">
                  <Avatar className="w-10 h-10">
                    <AvatarImage 
                      src={currentUser.profile_pic ? `${MAIN_API_BASE}${currentUser.profile_pic}` : undefined}
                      alt={currentUser.name || currentUser.full_name || currentUser.username || 'User'}
                    />
                    <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold">
                      {(currentUser.name || currentUser.full_name || currentUser.username || 'U')[0].toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="hidden sm:block">
                    <p className="text-sm font-medium text-gray-900">{currentUser.name || currentUser.full_name || currentUser.username}</p>
                    <p className="text-xs text-gray-500">{currentUser.email}</p>
                  </div>
                </div>
              )}
              <div className="flex space-x-2">
                <Button
                  onClick={loadNetworkData}
                  variant="outline"
                  size="sm"
                  disabled={isLoading}
                  className="hover:bg-gray-50"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
                <Button
                  onClick={() => navigateWithBubbles("/messaging")}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2"
                >
                  <MessageCircle className="w-4 h-4 mr-2" />
                  Messages
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Total Connections</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.totalConnections}</p>
                  <p className="text-xs text-green-600 mt-1">+2 this week</p>
                </div>
                <div className="p-3 bg-blue-100 rounded-full">
                  <Users className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1 flex items-center">
                    Pending Requests
                    {stats.pendingRequests > 0 && (
                      <span className="ml-2 w-2 h-2 bg-red-500 rounded-full"></span>
                    )}
                  </p>
                  <p className="text-3xl font-bold text-gray-900">{stats.pendingRequests}</p>
                  <p className="text-xs text-yellow-600 mt-1">Awaiting response</p>
                </div>
                <div className="p-3 bg-yellow-100 rounded-full">
                  <UserPlus className="w-6 h-6 text-yellow-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Sent Requests</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.sentRequests}</p>
                  <p className="text-xs text-blue-600 mt-1">Waiting for approval</p>
                </div>
                <div className="p-3 bg-green-100 rounded-full">
                  <Check className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Network Growth</p>
                  <p className="text-3xl font-bold text-gray-900">+{stats.totalConnections + stats.pendingRequests}</p>
                  <p className="text-xs text-purple-600 mt-1">This month</p>
                </div>
                <div className="p-3 bg-purple-100 rounded-full">
                  <Globe className="w-6 h-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search and Filters */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Search people by name or email..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <div className="flex space-x-2">
                <Button
                  variant={activeTab === 'all' ? 'default' : 'outline'}
                  onClick={() => setActiveTab('all')}
                >
                  All People
                </Button>
                <Button
                  variant={activeTab === 'connections' ? 'default' : 'outline'}
                  onClick={() => {
                    console.log('Connections tab clicked, current state:', {
                      connections: connections.length,
                      currentUser: currentUser?.id,
                      isAuthenticated
                    });
                    setActiveTab('connections');
                  }}
                >
                  Connections
                </Button>
                <Button
                  variant={activeTab === 'requests' ? 'default' : 'outline'}
                  onClick={() => setActiveTab('requests')}
                  className="relative"
                >
                  Requests
                  {requests.length > 0 && (
                    <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center">
                      <span className="text-xs text-white font-bold">{requests.length}</span>
                    </span>
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* User List */}
        {isLoading ? (
          <div className="space-y-4">
            {[...Array(6)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 bg-gray-200 rounded-full"></div>
                    <div className="flex-1">
                      <div className="h-4 bg-gray-200 rounded w-32 mb-2"></div>
                      <div className="h-3 bg-gray-200 rounded w-48 mb-2"></div>
                      <div className="h-3 bg-gray-200 rounded w-24"></div>
                    </div>
                    <div className="h-8 bg-gray-200 rounded w-24"></div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredUsers.length === 0 ? (
          <div className="text-center py-12">
            <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No users found</h3>
            <p className="text-gray-500">
              {searchQuery ? 'Try adjusting your search terms.' : 'No users available at the moment.'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredUsers.map((user) => {
            const connectionStatus = getConnectionStatus(user.id);
            const isConnected = connectionStatus === 'accepted';
            const isPendingReceived = connectionStatus === 'pending_received';
            const isPendingSent = connectionStatus === 'pending_sent';
            const isSentByMe = connections.find(conn => 
              conn.user_id === currentUser?.id && conn.connected_user_id === user.id && conn.status === 'pending'
            );
            
            // Get the request details if this is a pending request
            const requestDetails = requests.find(req => req.sender.id === user.id);

            // If we're on All People, hide users who are already connected
            // But show users with pending requests so they can see the status
            if (activeTab === 'all' && isConnected) {
              return null;
            }

            return (
              <Card key={user.id} className="hover:shadow-md transition-all duration-200">
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    {/* Avatar */}
                      <Avatar className="w-16 h-16 border-2 border-gray-200">
                        <AvatarImage 
                          src={user.profile_pic ? `${MAIN_API_BASE}${user.profile_pic}` : undefined}
                          alt={user.name || user.full_name || user.username || 'User'}
                        />
                        <AvatarFallback className="text-xl font-semibold bg-gradient-to-br from-blue-500 to-purple-600 text-white">
                          {(user.name || user.full_name || user.username || 'U')[0].toUpperCase()}
                        </AvatarFallback>
                      </Avatar>

                    {/* User Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <h3 className="font-bold text-gray-900 text-lg truncate">
                            {user.name || user.full_name || user.username}
                          </h3>
                          <p className="text-sm text-gray-500 truncate">{user.email}</p>
                          <div className="flex items-center space-x-4 mt-1">
                      {user.title && (
                              <p className="text-sm text-gray-600 truncate">{user.title}</p>
                      )}
                      {user.company && (
                              <p className="text-sm text-gray-500 truncate">at {user.company}</p>
                      )}
                          </div>
                      {isPendingReceived && requestDetails?.message && (
                        <div className="mt-2 p-2 bg-blue-50 rounded-lg border border-blue-200">
                          <p className="text-sm text-blue-800 italic">"{requestDetails.message}"</p>
                        </div>
                      )}
                          <div className="flex items-center text-xs text-gray-400 mt-1">
                        <Calendar className="w-3 h-3 mr-1" />
                        Joined {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'Recently'}
                      </div>
                    </div>

                        {/* Status Badge */}
                        <div className="flex-shrink-0 ml-4">
                      {isConnected && (
                        <Badge variant="default" className="bg-green-100 text-green-800 border-green-200">
                          <Check className="w-3 h-3 mr-1" />
                          Connected
                        </Badge>
                      )}
                      {isPendingReceived && (
                        <Badge variant="secondary" className="bg-blue-100 text-blue-800 border-blue-200">
                          <UserPlus className="w-3 h-3 mr-1" />
                          Request Received
                        </Badge>
                      )}
                      {isPendingSent && (
                        <Badge variant="secondary" className="bg-yellow-100 text-yellow-800 border-yellow-200">
                          <UserPlus className="w-3 h-3 mr-1" />
                          Request Sent
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* Bio Section */}
                  {user.bio && (
                        <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                          <p className="text-sm text-gray-700 line-clamp-2">{user.bio}</p>
                    </div>
                  )}

                  {/* Action Buttons */}
                      <div className="flex items-center justify-between mt-4">
                    <div className="flex space-x-2">
                      {isConnected ? (
                        <Button
                          size="sm"
                          onClick={() => handleStartMessage(user)}
                          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium"
                        >
                          <MessageCircle className="w-4 h-4 mr-2" />
                          Message
                        </Button>
                      ) : isPendingReceived ? (
                        <div className="flex space-x-2">
                          <Button
                            size="sm"
                            onClick={() => handleAcceptConnection(user.id)}
                            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium"
                          >
                            <Check className="w-4 h-4 mr-1" />
                            Accept
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleRejectConnection(user.id)}
                            className="border-red-300 text-red-600 hover:bg-red-50"
                          >
                            <X className="w-4 h-4 mr-1" />
                            Decline
                          </Button>
                        </div>
                      ) : !isPendingSent ? (
                        <Button
                          size="sm"
                          onClick={() => isAuthenticated ? handleConnectionRequest(user.id) : navigateWithBubbles("/login")}
                          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium"
                        >
                          <UserPlus className="w-4 h-4 mr-2" />
                          {isAuthenticated ? 'Connect' : 'Login to Connect'}
                        </Button>
                      ) : (
                        <Button
                          size="sm"
                          variant="outline"
                          disabled
                          className="px-4 py-2 rounded-lg bg-yellow-50 border-yellow-300 text-yellow-700"
                        >
                          <UserPlus className="w-4 h-4 mr-2" />
                          Request Sent
                        </Button>
                      )}
                    </div>
                    
                    {/* Quick Actions */}
                    <div className="flex space-x-1">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        className="hover:bg-gray-100 p-2"
                        title="Send Email"
                      >
                        <Mail className="w-4 h-4 text-gray-500" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        className="hover:bg-gray-100 p-2"
                        title="View Profile"
                      >
                        <Globe className="w-4 h-4 text-gray-500" />
                      </Button>
                    </div>
                  </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
          </div>
        )}

        {filteredUsers.length === 0 && (
          <Card>
            <CardContent className="p-12 text-center">
              <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No people found</h3>
              <p className="text-gray-500">
                {searchQuery ? 'Try adjusting your search terms' : 'No connections to display'}
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};
