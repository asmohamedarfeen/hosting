import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Calendar, Clock, Users, BookOpen, Video, Award, Plus, MapPin, DollarSign, User } from "lucide-react";
import { useLocation } from "wouter";

interface Workshop {
  id: number;
  title: string;
  description: string;
  instructor: string;
  instructor_email?: string;
  instructor_bio?: string;
  category: string;
  level: string;
  duration_hours: number;
  max_participants?: number;
  price: number;
  currency: string;
  start_date: string;
  end_date: string;
  location?: string;
  is_online: boolean;
  meeting_link?: string;
  materials: string[];
  prerequisites: string[];
  learning_objectives: string[];
  status: string;
  created_by: number;
  created_at: string;
  updated_at: string;
  creator?: {
    id: number;
    username: string;
    full_name: string;
  };
}

interface WorkshopFormData {
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
  meeting_link: string;
  materials: string[];
  prerequisites: string[];
  learning_objectives: string[];
}

export const WorkshopPage = (): JSX.Element => {
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [workshops, setWorkshops] = useState<Workshop[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [isHr, setIsHr] = useState(false);
  const [formData, setFormData] = useState<WorkshopFormData>({
    title: "",
    description: "",
    instructor: "",
    instructor_email: "",
    instructor_bio: "",
    category: "",
    level: "",
    duration_hours: 1,
    max_participants: 0,
    price: 0,
    currency: "USD",
    start_date: "",
    end_date: "",
    location: "",
    is_online: false,
    meeting_link: "",
    materials: [],
    prerequisites: [],
    learning_objectives: []
  });
  const [, setLocation] = useLocation();

  // Fetch workshops from API
  useEffect(() => {
    fetchWorkshops();
    checkAuthentication();
  }, []);

  const checkAuthentication = async () => {
    try {
      const response = await fetch('/auth/profile', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setIsAuthenticated(true);
        const type = (userData?.user_type || userData?.role || "").toString().toLowerCase();
        const hr = Boolean(
          userData?.is_hr === true ||
          type === 'hr' || type === 'human_resources' || type === 'hr_user' || type === 'domain' || type === 'recruiter'
        );
        setIsHr(hr);
      } else {
        setIsAuthenticated(false);
        setUser(null);
      }
    } catch (error) {
      console.error('Error checking authentication:', error);
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  const fetchWorkshops = async () => {
    try {
      setLoading(true);
      const response = await fetch('/workshops/api/workshops?status=published', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setWorkshops(data.workshops || []);
      } else {
        console.error('Failed to fetch workshops');
      }
    } catch (error) {
      console.error('Error fetching workshops:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWorkshop = async () => {
    // Check authentication first
    if (!isAuthenticated) {
      alert('Please log in to create a workshop.');
      setLocation('/login');
      return;
    }

    try {
      setIsCreating(true);
      
      // Convert arrays to JSON strings for backend
      const workshopData = {
        ...formData,
        materials: formData.materials.length > 0 ? formData.materials : [],
        prerequisites: formData.prerequisites.length > 0 ? formData.prerequisites : [],
        learning_objectives: formData.learning_objectives.length > 0 ? formData.learning_objectives : [],
        status: 'draft'
      };

      const response = await fetch('/workshops/api/workshops', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(workshopData)
      });

      if (response.ok) {
        const newWorkshop = await response.json();
        setWorkshops(prev => [newWorkshop, ...prev]);
        setIsCreateDialogOpen(false);
        resetForm();
        alert('Workshop submitted for admin approval! You will be notified once it\'s approved.');
      } else {
        let errorMessage = 'Unknown error';
        try {
          const error = await response.json();
          errorMessage = error.detail || error.message || 'Unknown error';
        } catch (e) {
          // If response is not JSON, check status code
          if (response.status === 401) {
            errorMessage = 'Please log in to create a workshop.';
          } else if (response.status === 403) {
            errorMessage = 'You do not have permission to create workshops.';
          } else if (response.status === 400) {
            errorMessage = 'Invalid workshop data. Please check all required fields.';
          } else if (response.status === 500) {
            errorMessage = 'Server error. Please try again later.';
          } else {
            errorMessage = `Request failed with status ${response.status}`;
          }
        }
        alert(`Failed to create workshop: ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error creating workshop:', error);
      alert('Failed to create workshop. Please try again.');
    } finally {
      setIsCreating(false);
    }
  };

  const resetForm = () => {
    setFormData({
      title: "",
      description: "",
      instructor: "",
      instructor_email: "",
      instructor_bio: "",
      category: "",
      level: "",
      duration_hours: 1,
      max_participants: 0,
      price: 0,
      currency: "USD",
      start_date: "",
      end_date: "",
      location: "",
      is_online: false,
      meeting_link: "",
      materials: [],
      prerequisites: [],
      learning_objectives: []
    });
  };

  const handleRegister = async (workshopId: number) => {
    try {
      const response = await fetch('/workshops/api/registrations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ workshop_id: workshopId })
      });

      if (response.ok) {
        alert('Successfully registered for the workshop!');
        // Refresh workshops to update participant count
        fetchWorkshops();
        setRegistrations((prev) => ({ ...prev, [workshopId]: true }));
      } else {
        const error = await response.json();
        alert(`Registration failed: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error registering for workshop:', error);
      alert('Failed to register. Please try again.');
    }
  };

  const categories = [
    { id: "all", label: "All Workshops", count: workshops.length },
    { id: "technical", label: "Technical", count: workshops.filter(w => w.category === "technical").length },
    { id: "career", label: "Career", count: workshops.filter(w => w.category === "career").length },
    { id: "soft-skills", label: "Soft Skills", count: workshops.filter(w => w.category === "soft-skills").length }
  ];

  const [registrations, setRegistrations] = useState<Record<number, boolean>>({});

  const filteredWorkshops = selectedCategory === "all" 
    ? workshops 
    : workshops.filter(w => w.category === selectedCategory);

  const getLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case "beginner": return "bg-green-100 text-green-800";
      case "intermediate": return "bg-yellow-100 text-yellow-800";
      case "advanced": return "bg-red-100 text-red-800";
      case "expert": return "bg-purple-100 text-purple-800";
      default: return "bg-blue-100 text-blue-800";
    }
  };

  const formatPrice = (price: number, currency: string) => {
    if (price === 0) return "Free";
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(price / 100);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  // Load user's registrations to mark registered workshops
  useEffect(() => {
    const loadMyRegistrations = async () => {
      try {
        const res = await fetch('/workshops/api/registrations', { credentials: 'include' });
        if (!res.ok) return;
        const data = await res.json();
        if (Array.isArray(data)) {
          const map: Record<number, boolean> = {};
          for (const r of data) {
            if (r?.workshop_id && (r.status === 'registered' || r.status === 'completed')) {
              map[r.workshop_id] = true;
            }
          }
          setRegistrations(map);
        }
      } catch {}
    };
    loadMyRegistrations();
  }, []);

  if (loading) {
    return (
      <div className="bg-neutral-100 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading workshops...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-neutral-100 min-h-screen">
      <div className="max-w-6xl mx-auto p-8">
        {/* Header Section */}
        <div className="mb-8 flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Professional Development Workshops</h1>
            <p className="text-gray-600 text-lg">
              Enhance your skills with expert-led workshops designed to accelerate your career growth.
            </p>
          </div>
          
          {/* Add Workshop Button */}
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button 
                className="bg-blue-600 hover:bg-blue-700 text-white"
                onClick={() => {
                  if (!isAuthenticated) {
                    alert('Please log in to create a workshop.');
                    setLocation('/login');
                    return;
                  }
                }}
              >
                <Plus className="h-4 w-4 mr-2" />
                {isAuthenticated ? 'Add New Workshop' : 'Login to Create Workshop'}
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Create New Workshop</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="title">Workshop Title *</Label>
                    <Input
                      id="title"
                      value={formData.title}
                      onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                      placeholder="Enter workshop title"
                    />
                  </div>
                  <div>
                    <Label htmlFor="instructor">Instructor Name *</Label>
                    <Input
                      id="instructor"
                      value={formData.instructor}
                      onChange={(e) => setFormData(prev => ({ ...prev, instructor: e.target.value }))}
                      placeholder="Enter instructor name"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="description">Description *</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Enter workshop description"
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="category">Category *</Label>
                    <Select value={formData.category} onValueChange={(value) => setFormData(prev => ({ ...prev, category: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="technical">Technical</SelectItem>
                        <SelectItem value="soft-skills">Soft Skills</SelectItem>
                        <SelectItem value="career">Career</SelectItem>
                        <SelectItem value="leadership">Leadership</SelectItem>
                        <SelectItem value="communication">Communication</SelectItem>
                        <SelectItem value="project-management">Project Management</SelectItem>
                        <SelectItem value="data-science">Data Science</SelectItem>
                        <SelectItem value="web-development">Web Development</SelectItem>
                        <SelectItem value="mobile-development">Mobile Development</SelectItem>
                        <SelectItem value="devops">DevOps</SelectItem>
                        <SelectItem value="cybersecurity">Cybersecurity</SelectItem>
                        <SelectItem value="design">Design</SelectItem>
                        <SelectItem value="marketing">Marketing</SelectItem>
                        <SelectItem value="sales">Sales</SelectItem>
                        <SelectItem value="finance">Finance</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="level">Level *</Label>
                    <Select value={formData.level} onValueChange={(value) => setFormData(prev => ({ ...prev, level: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select level" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="beginner">Beginner</SelectItem>
                        <SelectItem value="intermediate">Intermediate</SelectItem>
                        <SelectItem value="advanced">Advanced</SelectItem>
                        <SelectItem value="expert">Expert</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="duration">Duration (hours) *</Label>
                    <Input
                      id="duration"
                      type="number"
                      min="1"
                      value={formData.duration_hours}
                      onChange={(e) => setFormData(prev => ({ ...prev, duration_hours: parseInt(e.target.value) || 1 }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="max_participants">Max Participants</Label>
                    <Input
                      id="max_participants"
                      type="number"
                      min="0"
                      value={formData.max_participants}
                      onChange={(e) => setFormData(prev => ({ ...prev, max_participants: parseInt(e.target.value) || 0 }))}
                      placeholder="0 = unlimited"
                    />
                  </div>
                  <div>
                    <Label htmlFor="price">Price (cents) *</Label>
                    <Input
                      id="price"
                      type="number"
                      min="0"
                      value={formData.price}
                      onChange={(e) => setFormData(prev => ({ ...prev, price: parseInt(e.target.value) || 0 }))}
                      placeholder="0 = free"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="start_date">Start Date & Time *</Label>
                    <Input
                      id="start_date"
                      type="datetime-local"
                      value={formData.start_date}
                      onChange={(e) => setFormData(prev => ({ ...prev, start_date: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="end_date">End Date & Time *</Label>
                    <Input
                      id="end_date"
                      type="datetime-local"
                      value={formData.end_date}
                      onChange={(e) => setFormData(prev => ({ ...prev, end_date: e.target.value }))}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="location">Location</Label>
                    <Input
                      id="location"
                      value={formData.location}
                      onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
                      placeholder="Physical location or 'Online'"
                    />
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="is_online"
                      checked={formData.is_online}
                      onChange={(e) => setFormData(prev => ({ ...prev, is_online: e.target.checked }))}
                      className="rounded"
                    />
                    <Label htmlFor="is_online">Online Workshop</Label>
                  </div>
                </div>

                {formData.is_online && (
                  <div>
                    <Label htmlFor="meeting_link">Meeting Link</Label>
                    <Input
                      id="meeting_link"
                      value={formData.meeting_link}
                      onChange={(e) => setFormData(prev => ({ ...prev, meeting_link: e.target.value }))}
                      placeholder="https://meet.google.com/..."
                    />
                  </div>
                )}

                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button 
                    onClick={handleCreateWorkshop} 
                    disabled={isCreating || !formData.title || !formData.description || !formData.instructor || !formData.category || !formData.level}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    {isCreating ? "Creating..." : "Create Workshop"}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <BookOpen className="h-5 w-5 text-purple-600" />
                <div>
                  <p className="text-2xl font-bold">{workshops.length}</p>
                  <p className="text-sm text-gray-600">Total Workshops</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Video className="h-5 w-5 text-green-600" />
                <div>
                  <p className="text-2xl font-bold">{workshops.filter(w => w.status === 'published').length}</p>
                  <p className="text-sm text-gray-600">Live Sessions</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="text-2xl font-bold">{workshops.reduce((sum, w) => sum + (w.max_participants || 0), 0)}</p>
                  <p className="text-sm text-gray-600">Participants</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Award className="h-5 w-5 text-yellow-600" />
                <div>
                  <p className="text-2xl font-bold">95%</p>
                  <p className="text-sm text-gray-600">Satisfaction Rate</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Category Filter */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <Button
                key={category.id}
                variant={selectedCategory === category.id ? "default" : "outline"}
                onClick={() => setSelectedCategory(category.id)}
                className="flex items-center space-x-2"
              >
                <span>{category.label}</span>
                <Badge variant="secondary" className="ml-2">
                  {category.count}
                </Badge>
              </Button>
            ))}
          </div>
        </div>

        {/* Workshop Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredWorkshops.map((workshop) => (
            <Card key={workshop.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <CardTitle className="text-xl mb-2">{workshop.title}</CardTitle>
                    <p className="text-gray-600 mb-3 line-clamp-2">{workshop.description}</p>
                  </div>
                  <div className="flex flex-col items-end space-y-2">
                    <Badge className={getLevelColor(workshop.level)}>
                      {workshop.level.charAt(0).toUpperCase() + workshop.level.slice(1)}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {formatPrice(workshop.price, workshop.currency)}
                    </Badge>
                  </div>
                </div>
                
                <div className="flex flex-wrap gap-2">
                  <Badge variant="outline">
                    {workshop.category.replace("-", " ").charAt(0).toUpperCase() + workshop.category.replace("-", " ").slice(1)}
                  </Badge>
                  {workshop.is_online && (
                    <Badge className="bg-blue-100 text-blue-800">
                      Online
                    </Badge>
                  )}
                </div>
              </CardHeader>

              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center text-sm text-gray-600">
                    <Calendar className="h-4 w-4 mr-2" />
                    {formatDate(workshop.start_date)} at {formatTime(workshop.start_date)}
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-600">
                    <Clock className="h-4 w-4 mr-2" />
                    Duration: {workshop.duration_hours} hour{workshop.duration_hours !== 1 ? 's' : ''}
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-600">
                    <User className="h-4 w-4 mr-2" />
                    Instructor: {workshop.instructor}
                  </div>
                  
                  {workshop.location && (
                    <div className="flex items-center text-sm text-gray-600">
                      <MapPin className="h-4 w-4 mr-2" />
                      {workshop.location}
                    </div>
                  )}
                  
                  {workshop.max_participants && (
                    <div className="flex items-center text-sm text-gray-600">
                      <Users className="h-4 w-4 mr-2" />
                      Max {workshop.max_participants} participants
                    </div>
                  )}
                  
                  <div className="pt-4">
                    {registrations[workshop.id] ? (
                      <Button className="w-full" disabled>
                        Applied
                      </Button>
                    ) : (
                      <Button 
                        className="w-full" 
                        onClick={() => handleRegister(workshop.id)}
                        disabled={workshop.status !== 'published'}
                      >
                        {workshop.status === 'published' ? 'Apply' : 'Coming Soon'}
                      </Button>
                    )}
                    {isAuthenticated && isHr && (user && (user.id || user.user_id) === workshop.created_by) && (
                      <Button 
                        variant="outline"
                        className="w-full mt-2"
                        onClick={() => setLocation(`/workshop/${workshop.id}/participants`)}
                      >
                        List Participants
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredWorkshops.length === 0 && (
          <div className="text-center py-12">
            <BookOpen className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No workshops found</h3>
            <p className="text-gray-600">Try selecting a different category to see available workshops.</p>
          </div>
        )}
      </div>
    </div>
  );
};