/**
 * Message Service - Handles all messaging API calls
 * Connects to the message system backend at localhost:9000
 * Integrated with main database authentication
 */

// Use relative URLs for same-domain requests, or environment variables for different domains
const MESSAGE_API_BASE = import.meta.env.VITE_MESSAGE_API_BASE_URL || '/api/v1';
const MAIN_API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export interface User {
  id: number;
  name: string;
  email: string;
  bio?: string;
  created_at: string;
  is_active: boolean;
}

export interface Message {
  id: number;
  sender_id: number;
  receiver_id: number;
  content: string;
  timestamp: string;
  is_read: boolean;
  sender: User;
  receiver: User;
}

export interface Connection {
  id: number;
  sender_id: number;
  receiver_id: number;
  status: string;
  created_at: string;
  updated_at: string;
  sender: User;
  receiver: User;
}

export interface MessageCreate {
  receiver_id: number;
  content: string;
}

export interface ConnectionCreate {
  receiver_id: number;
}

class MessageService {
  private token: string | null = null;
  private mainSessionToken: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  setMainSessionToken(sessionToken: string) {
    this.mainSessionToken = sessionToken;
  }

  // Get main database session token from cookies
  private async getMainSessionToken(): Promise<string | null> {
    try {
      const response = await fetch(`${MAIN_API_BASE}/auth/profile`, {
        credentials: 'include',
        method: 'GET'
      });
      
      if (response.ok) {
        // Extract session token from cookies
        const cookies = document.cookie.split(';');
        const sessionCookie = cookies.find(cookie => 
          cookie.trim().startsWith('session_token=')
        );
        
        if (sessionCookie) {
          return sessionCookie.split('=')[1];
        }
      }
    } catch (error) {
      console.error('Error getting main session token:', error);
    }
    return null;
  }

  private getHeaders() {
    return {
      'Content-Type': 'application/json',
      ...(this.token && { 'Authorization': `Bearer ${this.token}` })
    };
  }

  // Authentication
  async login(email: string, password: string) {
    // Try messaging database authentication directly
    const response = await fetch(`${MESSAGE_API_BASE}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  // Auto-login using main app session
  async autoLogin() {
    const response = await fetch(`${MESSAGE_API_BASE}/users/auto-login`, {
      method: 'POST',
      credentials: 'include' // Include cookies for session token
    });

    if (!response.ok) {
      throw new Error('Auto-login failed');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  async register(name: string, email: string, password: string, bio?: string) {
    const response = await fetch(`${MESSAGE_API_BASE}/users/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password, bio })
    });

    if (!response.ok) {
      throw new Error('Registration failed');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  async getCurrentUser() {
    const response = await fetch(`${MESSAGE_API_BASE}/users/me`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get current user');
    }

    return response.json();
  }

  // Users
  async getUsers(skip = 0, limit = 100) {
    const response = await fetch(`${MESSAGE_API_BASE}/users/?skip=${skip}&limit=${limit}`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get users');
    }

    return response.json();
  }

  async getUserById(userId: number) {
    const response = await fetch(`${MESSAGE_API_BASE}/users/${userId}`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get user');
    }

    return response.json();
  }

  // Connections
  async getConnections() {
    const response = await fetch(`${MESSAGE_API_BASE}/connections/`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get connections');
    }

    return response.json();
  }

  async sendConnectionRequest(receiverId: number) {
    const response = await fetch(`${MESSAGE_API_BASE}/connections/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ receiver_id: receiverId })
    });

    if (!response.ok) {
      throw new Error('Failed to send connection request');
    }

    return response.json();
  }

  async acceptConnection(connectionId: number) {
    const response = await fetch(`${MESSAGE_API_BASE}/connections/${connectionId}/accept`, {
      method: 'PUT',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to accept connection');
    }

    return response.json();
  }

  async rejectConnection(connectionId: number) {
    const response = await fetch(`${MESSAGE_API_BASE}/connections/${connectionId}/reject`, {
      method: 'PUT',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to reject connection');
    }

    return response.json();
  }

  // Messages
  async sendMessage(receiverId: number, content: string) {
    const response = await fetch(`${MESSAGE_API_BASE}/messages/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ receiver_id: receiverId, content })
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    return response.json();
  }

  async getChatHistory(otherUserId: number, limit = 50, offset = 0) {
    const response = await fetch(`${MESSAGE_API_BASE}/messages/chat/${otherUserId}?limit=${limit}&offset=${offset}`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get chat history');
    }

    return response.json();
  }

  async markMessageAsRead(messageId: number) {
    const response = await fetch(`${MESSAGE_API_BASE}/messages/${messageId}/read`, {
      method: 'PUT',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to mark message as read');
    }

    return response.json();
  }

  // WebSocket connection
  createWebSocketConnection(userId: number, onMessage: (message: any) => void) {
    // Use wss:// for HTTPS, ws:// for HTTP, or environment variable
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = import.meta.env.VITE_WS_BASE_URL || `${wsProtocol}//${window.location.host}`;
    const ws = new WebSocket(`${wsHost}/api/v1/messages/ws/${userId}`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        onMessage(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return ws;
  }
}

export const messageService = new MessageService();
