import React, { useState, useEffect, useRef } from "react";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { UserAvatar } from "@/components/UserAvatar";
import { usePageTransition } from "@/contexts/TransitionContext";
import { mainAppService, MainUser, Connection } from "@/services/mainAppService";

const MAIN_API_BASE = 'http://localhost:8000';
import { 
  ArrowLeft, 
  Send, 
  Users, 
  MessageCircle, 
  UserPlus, 
  Check, 
  X,
  Search,
  MoreVertical,
  Phone,
  Video,
  Settings,
  RefreshCw
} from "lucide-react";

export const MessagingPage = (): JSX.Element => {
  const [location, setLocation] = useLocation();
  const { navigateWithBubbles } = usePageTransition();
  
  // Get user ID from URL parameters
  const urlParams = new URLSearchParams(location.split('?')[1] || '');
  const targetUserId = urlParams.get('user');
  
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState<MainUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Users and connections
  const [users, setUsers] = useState<MainUser[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  
  // Messaging state
  const [selectedUser, setSelectedUser] = useState<MainUser | null>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [isSending, setIsSending] = useState(false);
  
  // WebSocket - disabled for now
  // const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);
  
  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Check authentication on mount
  useEffect(() => {
    checkAuthentication();
  }, []);

  // Auto scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load data when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      loadInitialData();
    }
  }, [isAuthenticated]);

  // Handle user selection
  const handleUserSelect = async (user: MainUser) => {
    setSelectedUser(user);
    try {
      const chatData = await mainAppService.getChatHistory(user.id);
      setMessages(chatData.messages);
    } catch (error) {
      console.error('Failed to load chat history:', error);
      setMessages([]);
    }
  };

  // Auto-select user from URL parameter
  useEffect(() => {
    if (targetUserId && users.length > 0) {
      const user = users.find(u => u.id === parseInt(targetUserId));
      if (user) {
        handleUserSelect(user);
      }
    }
  }, [targetUserId, users]);

  // Refresh messages periodically when a user is selected
  useEffect(() => {
    if (!selectedUser || !isAuthenticated) return;

    const refreshMessages = async () => {
      try {
        const chatData = await mainAppService.getChatHistory(selectedUser.id);
        setMessages(chatData.messages);
      } catch (error) {
        console.error('Failed to refresh messages:', error);
      }
    };

    // Refresh messages every 5 seconds
    const interval = setInterval(refreshMessages, 5000);

    return () => clearInterval(interval);
  }, [selectedUser, isAuthenticated]);

  // WebSocket connection - disabled for now, using main app database
  // useEffect(() => {
  //   if (currentUser && isAuthenticated) {
  //     const ws = messageService.createWebSocketConnection(
  //       currentUser.id,
  //       handleWebSocketMessage
  //     );
  //     setWsConnection(ws);

  //     return () => {
  //       ws.close();
  //     };
  //   }
  // }, [currentUser, isAuthenticated]);

  const checkAuthentication = async () => {
    try {
      const user = await mainAppService.getCurrentUser();
      if (user && user.id) {
      setCurrentUser(user);
      setIsAuthenticated(true);
      } else {
        console.error('Invalid user data received');
        setIsAuthenticated(false);
      }
    } catch (error: any) {
      console.error('Authentication check failed:', error);
      // Check if it's a 401 (unauthorized) or network error
      if (error?.message?.includes('401') || error?.message?.includes('Not authenticated')) {
      setIsAuthenticated(false);
      } else {
        // For other errors, still allow access but show warning
        console.warn('Authentication check had issues, but allowing access:', error);
        // Try to set a minimal user object to allow access
        setIsAuthenticated(true);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const loadInitialData = async () => {
    try {
      const [usersData, connectionsData] = await Promise.all([
        mainAppService.getUsers(),
        mainAppService.getConnections()
      ]);
      
      setUsers(usersData.users || []);
      setConnections([...(connectionsData.sent_connections || []), ...(connectionsData.received_connections || [])]);
    } catch (error) {
      console.error('Failed to load initial data:', error);
      // Set empty arrays on error to prevent blank page
      setUsers([]);
      setConnections([]);
    }
  };

  // WebSocket message handler - disabled for now
  // const handleWebSocketMessage = (message: any) => {
  //   if (message.type === 'message' && selectedUser) {
  //     setMessages(prev => [...prev, message]);
  //   }
  // };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedUser || isSending || newMessage.length > 1000) return;

    // Check if user is authenticated
    if (!isAuthenticated || !currentUser) {
      alert('Please log in to send messages.');
      return;
    }

    const messageContent = newMessage.trim();
    setNewMessage("");
    setIsSending(true);
    
    try {
      const message = await mainAppService.sendMessage(selectedUser.id, messageContent);
      setMessages(prev => [...prev, message]);
    } catch (error) {
      console.error('Failed to send message:', error);
      // Restore the message if sending failed
      setNewMessage(messageContent);
      
      // Provide more specific error messages
      if (error instanceof Error) {
        if (error.message.includes('401') || error.message.includes('Not authenticated')) {
          alert('Please log in to send messages. Redirecting to login...');
          navigateWithBubbles('/login');
        } else if (error.message.includes('403')) {
          alert('You can only message your connections. Please connect with this user first.');
        } else {
          alert(`Failed to send message: ${error.message}`);
        }
      } else {
        alert('Failed to send message. Please try again.');
      }
    } finally {
      setIsSending(false);
    }
  };

  const handleConnectionRequest = async (userId: number) => {
    try {
      await mainAppService.sendConnectionRequest(userId);
      await loadInitialData(); // Refresh connections
    } catch (error) {
      console.error('Failed to send connection request:', error);
    }
  };

  const handleAcceptConnection = async (connectionId: number) => {
    try {
      await mainAppService.acceptConnection(connectionId);
      await loadInitialData(); // Refresh connections
    } catch (error) {
      console.error('Failed to accept connection:', error);
    }
  };

  const handleRejectConnection = async (connectionId: number) => {
    try {
      await mainAppService.rejectConnection(connectionId);
      await loadInitialData(); // Refresh connections
    } catch (error) {
      console.error('Failed to reject connection:', error);
    }
  };

  const filteredUsers = users.filter(user => 
    user.id !== currentUser?.id &&
    (user.name || user.full_name || user.username || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  const connectedUsers = connections
    .filter(conn => conn.status === 'accepted')
    .map(conn => conn.user_id === currentUser?.id ? conn.connected_user : conn.user);

  // Connection requests should only be shown on the Connections page
  const pendingRequests: Connection[] = [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading messaging system...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-center">Authentication Required</CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-gray-600 mb-4">Please log in to access the messaging system.</p>
            <Button onClick={() => navigateWithBubbles("/login")} className="w-full">
              Go to Login
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-1/3 border-r bg-white flex flex-col">
        {/* Header */}
        <div className="p-4 border-b">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Messages</h2>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigateWithBubbles("/network")}
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>
          </div>
          
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Search people..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Pending Requests intentionally hidden in MessagingPage */}

        {/* Connected Users */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-4">
            <h3 className="font-medium text-sm text-gray-700 mb-2">Connected</h3>
            {connectedUsers.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <MessageCircle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium mb-2">No connections yet</p>
                <p className="text-sm">Connect with people in the Network section to start messaging.</p>
                <Button 
                  onClick={() => navigateWithBubbles("/network")} 
                  className="mt-4"
                  variant="outline"
                  size="sm"
                >
                  Go to Network
                </Button>
              </div>
            ) : (
              connectedUsers.map((user) => (
                <div
                  key={user.id}
                  className={`flex items-center space-x-3 p-3 rounded-lg cursor-pointer hover:bg-gray-50 ${
                    selectedUser?.id === user.id ? 'bg-blue-50 border border-blue-200' : ''
                  }`}
                  onClick={() => handleUserSelect(user)}
                >
                  <UserAvatar 
                    user={user} 
                    size="sm"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{user.name || user.full_name || user.username || 'Unknown User'}</p>
                    <p className="text-xs text-gray-500 truncate">{user.email}</p>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* All Users */}
          <div className="p-4 border-t">
            <h3 className="font-medium text-sm text-gray-700 mb-2">Find People</h3>
            {filteredUsers.map((user) => {
              const isConnected = connectedUsers.some(conn => conn.id === user.id);
              const hasPendingRequest = connections.some(conn => 
                (conn.user_id === currentUser?.id && conn.connected_user_id === user.id && conn.status === 'pending') ||
                (conn.connected_user_id === currentUser?.id && conn.user_id === user.id && conn.status === 'pending')
              );

              return (
                <div
                  key={user.id}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50"
                >
                  <div className="flex items-center space-x-3">
                    <UserAvatar 
                      user={user} 
                      size="sm"
                    />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{user.name || user.full_name || user.username || 'Unknown User'}</p>
                      <p className="text-xs text-gray-500">{user.email}</p>
                    </div>
                  </div>
                  {!isConnected && !hasPendingRequest && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleConnectionRequest(user.id)}
                    >
                      <UserPlus className="w-3 h-3" />
                    </Button>
                  )}
                  {hasPendingRequest && (
                    <Badge variant="secondary">Pending</Badge>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {selectedUser ? (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b bg-white flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <UserAvatar 
                  user={selectedUser} 
                  size="sm"
                />
                <div>
                  <h3 className="font-medium">{selectedUser.name || selectedUser.username}</h3>
                  <p className="text-sm text-gray-500">
                    {selectedUser.email} • {messages.length} messages
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={async () => {
                    try {
                      const chatData = await mainAppService.getChatHistory(selectedUser.id);
                      setMessages(chatData.messages);
                    } catch (error) {
                      console.error('Failed to refresh messages:', error);
                    }
                  }}
                  title="Refresh messages"
                >
                  <RefreshCw className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="sm" title="Call">
                  <Phone className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="sm" title="Video call">
                  <Video className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="sm" title="More options">
                  <MoreVertical className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {/* Messages */}
            <div 
              ref={messagesContainerRef}
              className="flex-1 overflow-y-auto p-4 space-y-4"
            >
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <MessageCircle className="w-16 h-16 mb-4 text-gray-300" />
                  <h3 className="text-lg font-medium mb-2">No messages yet</h3>
                  <p className="text-sm text-center">
                    Start a conversation with {selectedUser.name} by sending your first message below.
                  </p>
                </div>
              ) : (
                messages.map((message, index) => {
                  const isCurrentUser = message.sender_id === currentUser?.id;
                  const showSenderName = index === 0 || messages[index - 1].sender_id !== message.sender_id;
                  
                  return (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${isCurrentUser ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`flex gap-3 max-w-[80%] ${
                        isCurrentUser ? 'flex-row-reverse' : 'flex-row'
                      }`}>
                        {/* Profile Photo */}
                        <div className="flex-shrink-0">
                          <UserAvatar 
                            user={isCurrentUser ? currentUser : message.sender} 
                            size="sm"
                          />
                        </div>
                        
                        {/* Message Content */}
                        <div className="flex flex-col">
                          {showSenderName && !isCurrentUser && (
                            <p className="text-xs text-gray-500 mb-1">
                              {message.sender?.name || message.sender?.username || 'Unknown User'}
                            </p>
                          )}
                          <div
                            className={`px-4 py-2 rounded-lg ${
                              isCurrentUser
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-200 text-gray-900'
                            }`}
                          >
                            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                            <div className={`flex items-center justify-between mt-1 ${
                              isCurrentUser ? 'text-blue-100' : 'text-gray-500'
                            }`}>
                              <p className="text-xs">
                                {new Date(message.created_at).toLocaleTimeString()}
                              </p>
                              {isCurrentUser && (
                                <div className="flex items-center space-x-1">
                                  {message.is_read ? (
                                    <Check className="w-3 h-3" />
                                  ) : (
                                    <div className="w-3 h-3 rounded-full bg-blue-300" />
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <div className="p-4 border-t bg-white">
              {!isAuthenticated ? (
                <div className="text-center py-4">
                  <p className="text-sm text-gray-500 mb-2">Please log in to send messages</p>
                  <Button 
                    onClick={() => navigateWithBubbles('/login')}
                    size="sm"
                    variant="outline"
                  >
                    Go to Login
                  </Button>
                </div>
              ) : (
                <>
                  <div className="flex space-x-2">
                    <div className="flex-1 relative">
                      <Textarea
                        placeholder={`Message ${selectedUser.name}...`}
                        value={newMessage}
                        onChange={(e) => {
                          if (e.target.value.length <= 1000) {
                            setNewMessage(e.target.value);
                          }
                        }}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSendMessage();
                          }
                        }}
                        className={`flex-1 min-h-[40px] max-h-32 pr-12 resize-none ${
                          newMessage.length > 900 ? 'border-orange-300' : ''
                        }`}
                        disabled={isSending}
                      />
                      {newMessage.trim() && (
                        <div className={`absolute right-2 top-2 text-xs ${
                          newMessage.length > 900 ? 'text-orange-500' : 'text-gray-400'
                        }`}>
                          {newMessage.length}/1000
                        </div>
                      )}
                    </div>
                    <Button
                      onClick={handleSendMessage}
                      disabled={!newMessage.trim() || isSending}
                      className="px-4 h-10"
                      size="sm"
                    >
                      {isSending ? (
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <Send className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                  <div className="mt-2 text-xs text-gray-500">
                    Press Enter to send, Shift+Enter for new line
                  </div>
                </>
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Select a conversation</h3>
              <p className="text-gray-500 mb-4">Choose someone to start messaging</p>
              {!isAuthenticated && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 max-w-md">
                  <p className="text-sm text-yellow-800 mb-2">
                    You need to be logged in to send messages.
                  </p>
                  <Button 
                    onClick={() => navigateWithBubbles('/login')}
                    size="sm"
                    className="bg-yellow-600 hover:bg-yellow-700"
                  >
                    Go to Login
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
