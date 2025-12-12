import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Users, 
  BookOpen, 
  Briefcase, 
  MessageSquare, 
  Settings, 
  BarChart3, 
  Shield, 
  Trash2, 
  Edit, 
  Eye,
  Plus,
  Search,
  Filter,
  Download
} from "lucide-react";

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  user_type: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login: string;
}

interface Workshop {
  id: number;
  title: string;
  instructor: string;
  category: string;
  level: string;
  status: string;
  approval_status: string;
  created_at: string;
  created_by: number;
  rejection_reason?: string;
}

interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  status: string;
  created_at: string;
}

export const AdminDashboard = (): JSX.Element => {
  const [users, setUsers] = useState<User[]>([]);
  const [workshops, setWorkshops] = useState<Workshop[]>([]);
  const [pendingWorkshops, setPendingWorkshops] = useState<Workshop[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedUserType, setSelectedUserType] = useState("all");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [rejectionReason, setRejectionReason] = useState("");
  const [showRejectionDialog, setShowRejectionDialog] = useState(false);
  const [selectedWorkshopId, setSelectedWorkshopId] = useState<number | null>(null);

  // Fetch all data
  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchUsers(),
        fetchWorkshops(),
        fetchPendingWorkshops(),
        fetchJobs()
      ]);
    } catch (error) {
      console.error('Error fetching admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await fetch('/api/users', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || []);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const fetchWorkshops = async () => {
    try {
      const response = await fetch('/admin/api/workshops', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setWorkshops(data.workshops || []);
      }
    } catch (error) {
      console.error('Error fetching workshops:', error);
    }
  };

  const fetchPendingWorkshops = async () => {
    try {
      const response = await fetch('/admin/api/workshops/pending', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setPendingWorkshops(data.workshops || []);
      }
    } catch (error) {
      console.error('Error fetching pending workshops:', error);
    }
  };

  const fetchJobs = async () => {
    try {
      const response = await fetch('/api/jobs', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setJobs(data.jobs || []);
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const handleUserAction = async (userId: number, action: string) => {
    try {
      const response = await fetch(`/api/users/${userId}/${action}`, {
        method: 'POST',
        credentials: 'include'
      });
      
      if (response.ok) {
        alert(`User ${action} successful`);
        fetchUsers();
      } else {
        alert(`Failed to ${action} user`);
      }
    } catch (error) {
      console.error(`Error ${action} user:`, error);
      alert(`Error ${action} user`);
    }
  };

  const handleWorkshopAction = async (workshopId: number, action: string) => {
    try {
      const response = await fetch(`/workshops/api/workshops/${workshopId}`, {
        method: action === 'delete' ? 'DELETE' : 'PUT',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: action === 'delete' ? undefined : JSON.stringify({ status: action })
      });
      
      if (response.ok) {
        alert(`Workshop ${action} successful`);
        fetchWorkshops();
      } else {
        alert(`Failed to ${action} workshop`);
      }
    } catch (error) {
      console.error(`Error ${action} workshop:`, error);
      alert(`Error ${action} workshop`);
    }
  };

  const handleApproveWorkshop = async (workshopId: number) => {
    try {
      const response = await fetch(`/admin/api/workshops/${workshopId}/approve`, {
        method: 'POST',
        credentials: 'include'
      });
      
      if (response.ok) {
        alert('Workshop approved successfully');
        fetchWorkshops();
        fetchPendingWorkshops();
      } else {
        alert('Failed to approve workshop');
      }
    } catch (error) {
      console.error('Error approving workshop:', error);
      alert('Error approving workshop');
    }
  };

  const handleRejectWorkshop = async (workshopId: number) => {
    if (!rejectionReason.trim()) {
      alert('Please provide a reason for rejection');
      return;
    }

    try {
      const response = await fetch(`/admin/api/workshops/${workshopId}/reject`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ rejection_reason: rejectionReason })
      });
      
      if (response.ok) {
        alert('Workshop rejected successfully');
        setShowRejectionDialog(false);
        setRejectionReason('');
        setSelectedWorkshopId(null);
        fetchWorkshops();
        fetchPendingWorkshops();
      } else {
        alert('Failed to reject workshop');
      }
    } catch (error) {
      console.error('Error rejecting workshop:', error);
      alert('Error rejecting workshop');
    }
  };

  const openRejectionDialog = (workshopId: number) => {
    setSelectedWorkshopId(workshopId);
    setShowRejectionDialog(true);
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.full_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedUserType === "all" || user.user_type === selectedUserType;
    const matchesStatus = selectedStatus === "all" || 
                         (selectedStatus === "active" && user.is_active) ||
                         (selectedStatus === "inactive" && !user.is_active);
    
    return matchesSearch && matchesType && matchesStatus;
  });

  const getStats = () => {
    const totalUsers = users.length;
    const activeUsers = users.filter(u => u.is_active).length;
    const verifiedUsers = users.filter(u => u.is_verified).length;
    const adminUsers = users.filter(u => u.user_type === 'admin').length;
    const totalWorkshops = workshops.length;
    const publishedWorkshops = workshops.filter(w => w.status === 'published').length;
    const pendingWorkshops = pendingWorkshops.length;
    const totalJobs = jobs.length;

    return {
      totalUsers,
      activeUsers,
      verifiedUsers,
      adminUsers,
      totalWorkshops,
      publishedWorkshops,
      pendingWorkshops,
      totalJobs
    };
  };

  const stats = getStats();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-gray-600 mt-2">Manage your Glow-IQ platform</p>
            </div>
            <div className="flex items-center space-x-4">
              <Button
                onClick={() => window.location.href = '/admin-desk'}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <BookOpen className="h-4 w-4 mr-2" />
                Workshop Desk
              </Button>
              <Badge className="bg-red-100 text-red-800">
                <Shield className="h-3 w-3 mr-1" />
                Admin Access
              </Badge>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Users className="h-8 w-8 text-blue-600" />
                <div>
                  <p className="text-2xl font-bold">{stats.totalUsers}</p>
                  <p className="text-sm text-gray-600">Total Users</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <BookOpen className="h-8 w-8 text-green-600" />
                <div>
                  <p className="text-2xl font-bold">{stats.totalWorkshops}</p>
                  <p className="text-sm text-gray-600">Workshops</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Shield className="h-8 w-8 text-yellow-600" />
                <div>
                  <p className="text-2xl font-bold">{stats.pendingWorkshops}</p>
                  <p className="text-sm text-gray-600">Pending Approval</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Briefcase className="h-8 w-8 text-purple-600" />
                <div>
                  <p className="text-2xl font-bold">{stats.totalJobs}</p>
                  <p className="text-sm text-gray-600">Job Postings</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <BarChart3 className="h-8 w-8 text-orange-600" />
                <div>
                  <p className="text-2xl font-bold">{stats.activeUsers}</p>
                  <p className="text-sm text-gray-600">Active Users</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="users" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="users">Users</TabsTrigger>
            <TabsTrigger value="pending">Pending</TabsTrigger>
            <TabsTrigger value="workshops">Workshops</TabsTrigger>
            <TabsTrigger value="jobs">Jobs</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          {/* Users Tab */}
          <TabsContent value="users" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>User Management</CardTitle>
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <Search className="h-4 w-4 text-gray-400" />
                      <Input
                        placeholder="Search users..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-64"
                      />
                    </div>
                    <Select value={selectedUserType} onValueChange={setSelectedUserType}>
                      <SelectTrigger className="w-32">
                        <SelectValue placeholder="Type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Types</SelectItem>
                        <SelectItem value="normal">Normal</SelectItem>
                        <SelectItem value="admin">Admin</SelectItem>
                        <SelectItem value="premium">Premium</SelectItem>
                      </SelectContent>
                    </Select>
                    <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                      <SelectTrigger className="w-32">
                        <SelectValue placeholder="Status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Status</SelectItem>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="inactive">Inactive</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {filteredUsers.map((user) => (
                    <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                          <Users className="h-5 w-5 text-gray-600" />
                        </div>
                        <div>
                          <h3 className="font-medium">{user.full_name}</h3>
                          <p className="text-sm text-gray-600">{user.email}</p>
                          <div className="flex items-center space-x-2 mt-1">
                            <Badge variant={user.user_type === 'admin' ? 'default' : 'secondary'}>
                              {user.user_type}
                            </Badge>
                            <Badge variant={user.is_active ? 'default' : 'destructive'}>
                              {user.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                            {user.is_verified && (
                              <Badge variant="outline" className="text-green-600">
                                Verified
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleUserAction(user.id, 'toggle_active')}
                        >
                          {user.is_active ? 'Deactivate' : 'Activate'}
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleUserAction(user.id, 'delete')}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Pending Workshops Tab */}
          <TabsContent value="pending" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Pending Workshop Approvals</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {pendingWorkshops.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <Shield className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                      <p>No pending workshops for approval</p>
                    </div>
                  ) : (
                    pendingWorkshops.map((workshop) => (
                      <div key={workshop.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex-1">
                          <h3 className="font-medium text-lg">{workshop.title}</h3>
                          <p className="text-sm text-gray-600">by {workshop.instructor}</p>
                          <div className="flex items-center space-x-2 mt-2">
                            <Badge variant="outline">{workshop.category}</Badge>
                            <Badge variant="outline">{workshop.level}</Badge>
                            <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                              Pending Approval
                            </Badge>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            Created: {new Date(workshop.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button
                            onClick={() => handleApproveWorkshop(workshop.id)}
                            className="bg-green-600 hover:bg-green-700"
                            size="sm"
                          >
                            Approve
                          </Button>
                          <Button
                            onClick={() => openRejectionDialog(workshop.id)}
                            variant="destructive"
                            size="sm"
                          >
                            Reject
                          </Button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Workshops Tab */}
          <TabsContent value="workshops" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Workshop Management</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {workshops.map((workshop) => (
                    <div key={workshop.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <h3 className="font-medium">{workshop.title}</h3>
                        <p className="text-sm text-gray-600">by {workshop.instructor}</p>
                        <div className="flex items-center space-x-2 mt-1">
                          <Badge variant="outline">{workshop.category}</Badge>
                          <Badge variant="outline">{workshop.level}</Badge>
                          <Badge variant={workshop.status === 'published' ? 'default' : 'secondary'}>
                            {workshop.status}
                          </Badge>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleWorkshopAction(workshop.id, 'published')}
                        >
                          Publish
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleWorkshopAction(workshop.id, 'draft')}
                        >
                          Draft
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleWorkshopAction(workshop.id, 'delete')}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Jobs Tab */}
          <TabsContent value="jobs" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Job Management</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {jobs.map((job) => (
                    <div key={job.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <h3 className="font-medium">{job.title}</h3>
                        <p className="text-sm text-gray-600">{job.company} • {job.location}</p>
                        <Badge variant="outline" className="mt-1">{job.status}</Badge>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>System Settings</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div>
                    <Label htmlFor="site-name">Site Name</Label>
                    <Input id="site-name" defaultValue="Glow-IQ" />
                  </div>
                  <div>
                    <Label htmlFor="site-description">Site Description</Label>
                    <Textarea 
                      id="site-description" 
                      defaultValue="Professional development platform for career growth"
                      rows={3}
                    />
                  </div>
                  <div>
                    <Label htmlFor="maintenance-mode">Maintenance Mode</Label>
                    <Select defaultValue="off">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="off">Off</SelectItem>
                        <SelectItem value="on">On</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button>Save Settings</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Rejection Dialog */}
        <Dialog open={showRejectionDialog} onOpenChange={setShowRejectionDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Reject Workshop</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="rejection-reason">Reason for Rejection</Label>
                <Textarea
                  id="rejection-reason"
                  placeholder="Please provide a reason for rejecting this workshop..."
                  value={rejectionReason}
                  onChange={(e) => setRejectionReason(e.target.value)}
                  rows={4}
                />
              </div>
              <div className="flex justify-end space-x-2">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowRejectionDialog(false);
                    setRejectionReason('');
                    setSelectedWorkshopId(null);
                  }}
                >
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => selectedWorkshopId && handleRejectWorkshop(selectedWorkshopId)}
                  disabled={!rejectionReason.trim()}
                >
                  Reject Workshop
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};
