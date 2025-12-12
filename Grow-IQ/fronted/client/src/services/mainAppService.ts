/**
 * Main App Service - Handles authentication and data from the main application
 * Bypasses messaging system and uses main app directly
 */

// Use relative URL for same-domain requests, or environment variable for different domains
const MAIN_API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export interface MainUser {
  id: number;
  username?: string;
  name: string; // API returns 'name' field
  email: string;
  full_name?: string;
  title?: string;
  company?: string;
  location?: string;
  bio?: string;
  profile_image?: string;
  profile_pic?: string;
  user_type?: string;
  domain?: string;
  is_verified?: boolean;
  is_active?: boolean;
  last_login?: string;
  created_at?: string;
  updated_at?: string;
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
  profile_visibility?: string;
  show_email?: boolean;
  show_phone?: boolean;
}

export interface Connection {
  id: number;
  user_id: number;
  connected_user_id: number;
  status: 'pending' | 'accepted' | 'rejected';
  created_at: string;
  updated_at: string;
  user: MainUser;
  connected_user: MainUser;
}

export interface ConnectionRequest {
  id: number;
  sender: MainUser;
  message?: string;
  created_at: string;
}

export interface ConnectionResponse {
  connections: Connection[];
  sent_connections: Connection[];
  received_connections: Connection[];
  requests: ConnectionRequest[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

class MainAppService {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  getToken(): string | null {
    return this.token;
  }

  private getHeaders() {
    return {
      'Content-Type': 'application/json',
      ...(this.token && { 'Authorization': `Bearer ${this.token}` })
    };
  }

  // Authentication
  async getCurrentUser(): Promise<MainUser> {
    const response = await fetch(`${MAIN_API_BASE}/auth/profile`, {
      credentials: 'include'
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => '');
      if (response.status === 401 || response.status === 403) {
        throw new Error(`401: Not authenticated - ${errorText || 'Please log in'}`);
    }
      throw new Error(`Failed to get user: ${response.status} ${errorText}`);
    }

    const userData = await response.json();
    if (!userData || !userData.id) {
      throw new Error('Invalid user data received');
    }

    // Normalize user data - ensure 'name' field exists (frontend expects it)
    return {
      ...userData,
      name: userData.name || userData.full_name || userData.username || 'User'
    };
  }

  // Get all users from main database
  async getUsers(skip = 0, limit = 100): Promise<{ users: MainUser[] }> {
    const response = await fetch(`${MAIN_API_BASE}/api/v1/users?offset=${skip}&limit=${limit}`, {
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error('Failed to get users');
    }

    return response.json();
  }

  // Get connections from main database
  async getConnections(): Promise<{ sent_connections: Connection[], received_connections: Connection[], requests: ConnectionRequest[] }> {
    try {
      const [connectionsResponse, requestsResponse, currentUserResponse] = await Promise.all([
        fetch(`${MAIN_API_BASE}/connections/api/connections`, {
          credentials: 'include'
        }),
        fetch(`${MAIN_API_BASE}/connections/api/pending-requests`, {
          credentials: 'include'
        }),
        fetch(`${MAIN_API_BASE}/auth/profile`, {
          credentials: 'include'
        })
      ]);

      if (!connectionsResponse.ok) {
        throw new Error('Failed to get connections');
      }

      const connectionsData = await connectionsResponse.json();
      const requestsData = requestsResponse.ok ? await requestsResponse.json() : { requests: [] };
      const currentUser = currentUserResponse.ok ? await currentUserResponse.json() : null;

      // Convert the API response to our expected format
      const sent_connections: Connection[] = [];
      const received_connections: Connection[] = [];
      
      // Process connections (these are accepted connections)
      if (connectionsData.connections && currentUser) {
        connectionsData.connections.forEach((conn: any) => {
          // The API returns connections where conn.user is the connected user
          const connection: Connection = {
            id: conn.id,
            user_id: currentUser.id, // Current user ID
            connected_user_id: conn.user.id, // Connected user's ID
            status: 'accepted',
            created_at: conn.connected_since || new Date().toISOString(),
            updated_at: conn.connected_since || new Date().toISOString(),
            user: currentUser, // Current user
            connected_user: conn.user // The connected user from API response
          };
          received_connections.push(connection);
        });
      }

      return {
        sent_connections,
        received_connections,
        requests: requestsData.requests || []
      };
    } catch (error) {
      console.error('Error fetching connections:', error);
      return {
        sent_connections: [],
        received_connections: [],
        requests: []
      };
    }
  }

  // Send connection request (use main API to align with auth/session)
  async sendConnectionRequest(userId: number): Promise<void> {
    const response = await fetch(`${MAIN_API_BASE}/connections/api/request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ receiver_id: userId })
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({} as any));
      throw new Error(err?.detail || err?.message || 'Failed to send connection request');
    }
  }

  // Accept connection request
  async acceptConnection(requestId: number): Promise<void> {
    const response = await fetch(`${MAIN_API_BASE}/connections/api/respond-request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      credentials: 'include',
      body: `request_id=${requestId}&response=accept`
    });

    if (!response.ok) {
      throw new Error('Failed to accept connection');
    }
  }

  // Reject connection request
  async rejectConnection(requestId: number): Promise<void> {
    const response = await fetch(`${MAIN_API_BASE}/connections/api/respond-request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      credentials: 'include',
      body: `request_id=${requestId}&response=decline`
    });

    if (!response.ok) {
      throw new Error('Failed to reject connection');
    }
  }

  // Messaging methods
  async sendMessage(receiverId: number, content: string): Promise<any> {
    const response = await fetch(`${MAIN_API_BASE}/api/messages/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        receiver_id: receiverId,
        content: content
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.message || `HTTP ${response.status}`;
      
      if (response.status === 401) {
        throw new Error('401: Authentication required');
      } else if (response.status === 403) {
        throw new Error('403: You can only message your connections');
      } else if (response.status === 404) {
        throw new Error('404: User not found');
      } else {
        throw new Error(`${response.status}: ${errorMessage}`);
      }
    }

    return response.json();
  }

  async getChatHistory(userId: number): Promise<{ messages: any[] }> {
    const response = await fetch(`${MAIN_API_BASE}/api/messages/chat/${userId}`, {
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error(`Failed to get chat history: ${response.status}`);
    }

    const messages = await response.json();
    return { messages };
  }


  async getConversations(): Promise<any[]> {
    const response = await fetch(`${MAIN_API_BASE}/api/messages/conversations`, {
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error(`Failed to get conversations: ${response.status}`);
    }

    return response.json();
  }

  async markMessageRead(messageId: number): Promise<void> {
    const response = await fetch(`${MAIN_API_BASE}/api/messages/${messageId}/read`, {
      method: 'PUT',
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error(`Failed to mark message as read: ${response.status}`);
    }
  }

  async getUnreadCount(): Promise<{ unread_count: number }> {
    const response = await fetch(`${MAIN_API_BASE}/api/messages/unread-count`, {
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error(`Failed to get unread count: ${response.status}`);
    }

    return response.json();
  }
}

export const mainAppService = new MainAppService();
