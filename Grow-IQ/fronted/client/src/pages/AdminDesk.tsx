import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Shield, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Eye, 
  MessageSquare,
  Calendar,
  Users,
  DollarSign,
  MapPin,
  Globe,
  BookOpen,
  Star,
  AlertCircle
} from "lucide-react";

interface Workshop {
  id: number;
  title: string;
  description: string;
  instructor: string;
  instructor_email: string;
  instructor_bio: string;
  category: string;
  level: string;
  duration_hours: number;
  max_participants: number;
  price: number;
  currency: string;
  start_date: string;
  end_date: string;
  location: string;
  is_online: boolean;
  meeting_link?: string;
  materials: string[];
  prerequisites: string[];
  learning_objectives: string[];
  status: string;
  approval_status: string;
  approved_by?: number;
  approved_at?: string;
  rejection_reason?: string;
  created_by: number;
  created_at: string;
  updated_at: string;
  creator?: {
    id: number;
    username: string;
    full_name: string;
    email: string;
  };
}

export const AdminDesk = (): JSX.Element => {
  const [workshops, setWorkshops] = useState<Workshop[]>([]);
  const [pendingWorkshops, setPendingWorkshops] = useState<Workshop[]>([]);
  const [approvedWorkshops, setApprovedWorkshops] = useState<Workshop[]>([]);
  const [rejectedWorkshops, setRejectedWorkshops] = useState<Workshop[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedWorkshop, setSelectedWorkshop] = useState<Workshop | null>(null);
  const [showDetailsDialog, setShowDetailsDialog] = useState(false);
  const [showRejectionDialog, setShowRejectionDialog] = useState(false);
  const [rejectionReason, setRejectionReason] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  // Fetch all workshop data
  useEffect(() => {
    fetchWorkshopData();
  }, []);

  const fetchWorkshopData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchAllWorkshops(),
        fetchPendingWorkshops(),
        fetchApprovedWorkshops(),
        fetchRejectedWorkshops()
      ]);
    } catch (error) {
      console.error('Error fetching workshop data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAllWorkshops = async () => {
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

  const fetchApprovedWorkshops = async () => {
    try {
      const response = await fetch('/admin/api/workshops?approval_status=approved', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setApprovedWorkshops(data.workshops || []);
      }
    } catch (error) {
      console.error('Error fetching approved workshops:', error);
    }
  };

  const fetchRejectedWorkshops = async () => {
    try {
      const response = await fetch('/admin/api/workshops?approval_status=rejected', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setRejectedWorkshops(data.workshops || []);
      }
    } catch (error) {
      console.error('Error fetching rejected workshops:', error);
    }
  };

  const handleApproveWorkshop = async (workshopId: number) => {
    try {
      setIsProcessing(true);
      const response = await fetch(`/admin/api/workshops/${workshopId}/approve`, {
        method: 'POST',
        credentials: 'include'
      });
      
      if (response.ok) {
        alert('Workshop approved successfully!');
        fetchWorkshopData();
        setShowDetailsDialog(false);
        setSelectedWorkshop(null);
      } else {
        alert('Failed to approve workshop');
      }
    } catch (error) {
      console.error('Error approving workshop:', error);
      alert('Error approving workshop');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRejectWorkshop = async (workshopId: number) => {
    if (!rejectionReason.trim()) {
      alert('Please provide a reason for rejection');
      return;
    }

    try {
      setIsProcessing(true);
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
        fetchWorkshopData();
        setShowDetailsDialog(false);
        setSelectedWorkshop(null);
      } else {
        alert('Failed to reject workshop');
      }
    } catch (error) {
      console.error('Error rejecting workshop:', error);
      alert('Error rejecting workshop');
    } finally {
      setIsProcessing(false);
    }
  };

  const openDetailsDialog = (workshop: Workshop) => {
    setSelectedWorkshop(workshop);
    setShowDetailsDialog(true);
  };

  const openRejectionDialog = (workshop: Workshop) => {
    setSelectedWorkshop(workshop);
    setShowRejectionDialog(true);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatPrice = (price: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(price);
  };

  const getStatusBadge = (status: string, approvalStatus: string) => {
    if (approvalStatus === 'pending') {
      return <Badge className="bg-yellow-100 text-yellow-800"><Clock className="h-3 w-3 mr-1" />Pending</Badge>;
    } else if (approvalStatus === 'approved') {
      return <Badge className="bg-green-100 text-green-800"><CheckCircle className="h-3 w-3 mr-1" />Approved</Badge>;
    } else if (approvalStatus === 'rejected') {
      return <Badge className="bg-red-100 text-red-800"><XCircle className="h-3 w-3 mr-1" />Rejected</Badge>;
    }
    return <Badge variant="secondary">{status}</Badge>;
  };

  const getLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading admin desk...</p>
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
              <h1 className="text-3xl font-bold text-gray-900">Admin Desk</h1>
              <p className="text-gray-600 mt-2">Manage workshop applications and approvals</p>
            </div>
            <div className="flex items-center space-x-2">
              <Badge className="bg-red-100 text-red-800">
                <Shield className="h-3 w-3 mr-1" />
                Admin Access
              </Badge>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Clock className="h-8 w-8 text-yellow-600" />
                <div>
                  <p className="text-2xl font-bold">{pendingWorkshops.length}</p>
                  <p className="text-sm text-gray-600">Pending Review</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-8 w-8 text-green-600" />
                <div>
                  <p className="text-2xl font-bold">{approvedWorkshops.length}</p>
                  <p className="text-sm text-gray-600">Approved</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <XCircle className="h-8 w-8 text-red-600" />
                <div>
                  <p className="text-2xl font-bold">{rejectedWorkshops.length}</p>
                  <p className="text-sm text-gray-600">Rejected</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <BookOpen className="h-8 w-8 text-blue-600" />
                <div>
                  <p className="text-2xl font-bold">{workshops.length}</p>
                  <p className="text-sm text-gray-600">Total Workshops</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="pending" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="pending">Pending Review</TabsTrigger>
            <TabsTrigger value="approved">Approved</TabsTrigger>
            <TabsTrigger value="rejected">Rejected</TabsTrigger>
            <TabsTrigger value="all">All Workshops</TabsTrigger>
          </TabsList>

          {/* Pending Workshops Tab */}
          <TabsContent value="pending" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="h-5 w-5 text-yellow-600" />
                  <span>Pending Workshop Approvals</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {pendingWorkshops.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <Clock className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                      <p>No pending workshops for review</p>
                    </div>
                  ) : (
                    pendingWorkshops.map((workshop) => (
                      <div key={workshop.id} className="border rounded-lg p-6 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <h3 className="text-lg font-semibold">{workshop.title}</h3>
                              {getStatusBadge(workshop.status, workshop.approval_status)}
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                              <div className="space-y-2">
                                <p className="text-sm text-gray-600">
                                  <strong>Instructor:</strong> {workshop.instructor}
                                </p>
                                <p className="text-sm text-gray-600">
                                  <strong>Category:</strong> {workshop.category}
                                </p>
                                <p className="text-sm text-gray-600">
                                  <strong>Level:</strong> 
                                  <Badge className={`ml-2 ${getLevelColor(workshop.level)}`}>
                                    {workshop.level}
                                  </Badge>
                                </p>
                                <p className="text-sm text-gray-600">
                                  <strong>Duration:</strong> {workshop.duration_hours} hours
                                </p>
                              </div>
                              
                              <div className="space-y-2">
                                <p className="text-sm text-gray-600">
                                  <strong>Date:</strong> {formatDate(workshop.start_date)}
                                </p>
                                <p className="text-sm text-gray-600">
                                  <strong>Location:</strong> {workshop.is_online ? 'Online' : workshop.location}
                                </p>
                                <p className="text-sm text-gray-600">
                                  <strong>Price:</strong> {formatPrice(workshop.price, workshop.currency)}
                                </p>
                                <p className="text-sm text-gray-600">
                                  <strong>Max Participants:</strong> {workshop.max_participants}
                                </p>
                              </div>
                            </div>
                            
                            <p className="text-sm text-gray-700 mb-4 line-clamp-2">
                              {workshop.description}
                            </p>
                            
                            <div className="flex items-center space-x-2 text-xs text-gray-500">
                              <Calendar className="h-3 w-3" />
                              <span>Created: {formatDate(workshop.created_at)}</span>
                              <span>•</span>
                              <Users className="h-3 w-3" />
                              <span>By: {workshop.creator?.full_name || 'Unknown'}</span>
                            </div>
                          </div>
                          
                          <div className="flex flex-col space-y-2 ml-4">
                            <Button
                              onClick={() => openDetailsDialog(workshop)}
                              variant="outline"
                              size="sm"
                            >
                              <Eye className="h-4 w-4 mr-1" />
                              Review
                            </Button>
                            <Button
                              onClick={() => handleApproveWorkshop(workshop.id)}
                              className="bg-green-600 hover:bg-green-700"
                              size="sm"
                              disabled={isProcessing}
                            >
                              <CheckCircle className="h-4 w-4 mr-1" />
                              Approve
                            </Button>
                            <Button
                              onClick={() => openRejectionDialog(workshop)}
                              variant="destructive"
                              size="sm"
                              disabled={isProcessing}
                            >
                              <XCircle className="h-4 w-4 mr-1" />
                              Reject
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Approved Workshops Tab */}
          <TabsContent value="approved" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span>Approved Workshops</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {approvedWorkshops.map((workshop) => (
                    <div key={workshop.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="font-semibold">{workshop.title}</h3>
                            {getStatusBadge(workshop.status, workshop.approval_status)}
                          </div>
                          <p className="text-sm text-gray-600">by {workshop.instructor}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            Approved: {workshop.approved_at ? formatDate(workshop.approved_at) : 'Unknown'}
                          </p>
                        </div>
                        <Button
                          onClick={() => openDetailsDialog(workshop)}
                          variant="outline"
                          size="sm"
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          View Details
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Rejected Workshops Tab */}
          <TabsContent value="rejected" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <XCircle className="h-5 w-5 text-red-600" />
                  <span>Rejected Workshops</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {rejectedWorkshops.map((workshop) => (
                    <div key={workshop.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="font-semibold">{workshop.title}</h3>
                            {getStatusBadge(workshop.status, workshop.approval_status)}
                          </div>
                          <p className="text-sm text-gray-600">by {workshop.instructor}</p>
                          {workshop.rejection_reason && (
                            <p className="text-xs text-red-600 mt-1">
                              <strong>Reason:</strong> {workshop.rejection_reason}
                            </p>
                          )}
                        </div>
                        <Button
                          onClick={() => openDetailsDialog(workshop)}
                          variant="outline"
                          size="sm"
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          View Details
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* All Workshops Tab */}
          <TabsContent value="all" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BookOpen className="h-5 w-5 text-blue-600" />
                  <span>All Workshops</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {workshops.map((workshop) => (
                    <div key={workshop.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="font-semibold">{workshop.title}</h3>
                            {getStatusBadge(workshop.status, workshop.approval_status)}
                          </div>
                          <p className="text-sm text-gray-600">by {workshop.instructor}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            Created: {formatDate(workshop.created_at)}
                          </p>
                        </div>
                        <Button
                          onClick={() => openDetailsDialog(workshop)}
                          variant="outline"
                          size="sm"
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          View Details
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Workshop Details Dialog */}
        <Dialog open={showDetailsDialog} onOpenChange={setShowDetailsDialog}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center space-x-2">
                <BookOpen className="h-5 w-5" />
                <span>Workshop Details</span>
              </DialogTitle>
            </DialogHeader>
            
            {selectedWorkshop && (
              <div className="space-y-6">
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-2xl font-bold">{selectedWorkshop.title}</h2>
                    <p className="text-gray-600">by {selectedWorkshop.instructor}</p>
                    <div className="flex items-center space-x-2 mt-2">
                      {getStatusBadge(selectedWorkshop.status, selectedWorkshop.approval_status)}
                      <Badge className={getLevelColor(selectedWorkshop.level)}>
                        {selectedWorkshop.level}
                      </Badge>
                    </div>
                  </div>
                  <div className="text-right text-sm text-gray-500">
                    <p>Created: {formatDate(selectedWorkshop.created_at)}</p>
                    {selectedWorkshop.approved_at && (
                      <p>Approved: {formatDate(selectedWorkshop.approved_at)}</p>
                    )}
                  </div>
                </div>

                {/* Description */}
                <div>
                  <h3 className="font-semibold mb-2">Description</h3>
                  <p className="text-gray-700">{selectedWorkshop.description}</p>
                </div>

                {/* Instructor Info */}
                <div>
                  <h3 className="font-semibold mb-2">Instructor Information</h3>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p><strong>Name:</strong> {selectedWorkshop.instructor}</p>
                    <p><strong>Email:</strong> {selectedWorkshop.instructor_email}</p>
                    <p><strong>Bio:</strong> {selectedWorkshop.instructor_bio}</p>
                  </div>
                </div>

                {/* Workshop Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-semibold mb-2">Workshop Details</h3>
                    <div className="space-y-2">
                      <p><strong>Category:</strong> {selectedWorkshop.category}</p>
                      <p><strong>Duration:</strong> {selectedWorkshop.duration_hours} hours</p>
                      <p><strong>Max Participants:</strong> {selectedWorkshop.max_participants}</p>
                      <p><strong>Price:</strong> {formatPrice(selectedWorkshop.price, selectedWorkshop.currency)}</p>
                      <p><strong>Location:</strong> {selectedWorkshop.is_online ? 'Online' : selectedWorkshop.location}</p>
                      {selectedWorkshop.is_online && selectedWorkshop.meeting_link && (
                        <p><strong>Meeting Link:</strong> {selectedWorkshop.meeting_link}</p>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-2">Schedule</h3>
                    <div className="space-y-2">
                      <p><strong>Start Date:</strong> {formatDate(selectedWorkshop.start_date)}</p>
                      <p><strong>End Date:</strong> {formatDate(selectedWorkshop.end_date)}</p>
                    </div>
                  </div>
                </div>

                {/* Materials, Prerequisites, Objectives */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {selectedWorkshop.materials && selectedWorkshop.materials.length > 0 && (
                    <div>
                      <h3 className="font-semibold mb-2">Required Materials</h3>
                      <ul className="list-disc list-inside text-sm text-gray-700">
                        {selectedWorkshop.materials.map((material, index) => (
                          <li key={index}>{material}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {selectedWorkshop.prerequisites && selectedWorkshop.prerequisites.length > 0 && (
                    <div>
                      <h3 className="font-semibold mb-2">Prerequisites</h3>
                      <ul className="list-disc list-inside text-sm text-gray-700">
                        {selectedWorkshop.prerequisites.map((prereq, index) => (
                          <li key={index}>{prereq}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {selectedWorkshop.learning_objectives && selectedWorkshop.learning_objectives.length > 0 && (
                    <div>
                      <h3 className="font-semibold mb-2">Learning Objectives</h3>
                      <ul className="list-disc list-inside text-sm text-gray-700">
                        {selectedWorkshop.learning_objectives.map((objective, index) => (
                          <li key={index}>{objective}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Rejection Reason */}
                {selectedWorkshop.rejection_reason && (
                  <div>
                    <h3 className="font-semibold mb-2 text-red-600">Rejection Reason</h3>
                    <div className="bg-red-50 p-4 rounded-lg">
                      <p className="text-red-700">{selectedWorkshop.rejection_reason}</p>
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                {selectedWorkshop.approval_status === 'pending' && (
                  <div className="flex justify-end space-x-2 pt-4 border-t">
                    <Button
                      onClick={() => handleApproveWorkshop(selectedWorkshop.id)}
                      className="bg-green-600 hover:bg-green-700"
                      disabled={isProcessing}
                    >
                      <CheckCircle className="h-4 w-4 mr-1" />
                      Approve Workshop
                    </Button>
                    <Button
                      onClick={() => openRejectionDialog(selectedWorkshop)}
                      variant="destructive"
                      disabled={isProcessing}
                    >
                      <XCircle className="h-4 w-4 mr-1" />
                      Reject Workshop
                    </Button>
                  </div>
                )}
              </div>
            )}
          </DialogContent>
        </Dialog>

        {/* Rejection Dialog */}
        <Dialog open={showRejectionDialog} onOpenChange={setShowRejectionDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <span>Reject Workshop</span>
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="rejection-reason">Reason for Rejection</Label>
                <Textarea
                  id="rejection-reason"
                  placeholder="Please provide a clear reason for rejecting this workshop..."
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
                  }}
                >
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => selectedWorkshop && handleRejectWorkshop(selectedWorkshop.id)}
                  disabled={!rejectionReason.trim() || isProcessing}
                >
                  <XCircle className="h-4 w-4 mr-1" />
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
