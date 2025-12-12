import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Calendar, MapPin, Users, Music, Palette, Coffee, Trophy, Star, Clock, Heart } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

export const CulturalEventsPage = (): JSX.Element => {
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [rsvpStatus, setRsvpStatus] = useState<{[key: number]: boolean}>({});
  const [isHr, setIsHr] = useState(false);
  const [userFullName, setUserFullName] = useState<string>("");
  const [newEvent, setNewEvent] = useState({
    title: "",
    description: "",
    date: "",
    time: "",
    location: "",
    category: "festival"
  });
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch('/auth/profile', { credentials: 'include' });
        if (!res.ok) return;
        const user = await res.json();
        const type = (user?.user_type || user?.role || "").toString().toLowerCase();
        const hr = Boolean(
          user?.is_hr === true ||
          type === 'hr' ||
          type === 'human_resources' ||
          type === 'hr_user' ||
          type === 'domain' ||
          type === 'recruiter'
        );
        setIsHr(hr);
        const fullName: string = user?.full_name || user?.fullName || "";
        setUserFullName(fullName.trim());
      } catch {}
    })();
  }, []);

  const events = [
    {
      id: 1,
      title: "Tech Talk: Future of AI",
      description: "Join our expert panel discussing the latest trends in artificial intelligence and machine learning.",
      date: "2024-01-28",
      time: "6:00 PM - 8:00 PM",
      location: "Main Auditorium, Tech Park",
      category: "tech-talk",
      organizer: "GrowIQ Tech Team",
      attendees: 85,
      maxAttendees: 150,
      image: "/figmaAssets/tech-talk.jpg",
      tags: ["AI", "Machine Learning", "Technology", "Panel Discussion"],
      isUpcoming: true,
      isFeatured: true
    },
    {
      id: 2,
      title: "Annual Cultural Fest",
      description: "Celebrate diversity with music, dance, food, and cultural performances from around the world.",
      date: "2024-02-15",
      time: "4:00 PM - 10:00 PM",
      location: "Central Plaza, GrowIQ Campus",
      category: "festival",
      organizer: "Cultural Committee",
      attendees: 245,
      maxAttendees: 300,
      image: "/figmaAssets/cultural-fest.jpg",
      tags: ["Music", "Dance", "Food", "Cultural", "Celebration"],
      isUpcoming: true,
      isFeatured: true
    },
    {
      id: 3,
      title: "Coffee & Code Networking",
      description: "Informal networking session with industry professionals over coffee and light snacks.",
      date: "2024-01-25",
      time: "10:00 AM - 12:00 PM",
      location: "Cafe Lounge, Building A",
      category: "networking",
      organizer: "Professional Development",
      attendees: 32,
      maxAttendees: 50,
      image: "/figmaAssets/coffee-networking.jpg",
      tags: ["Networking", "Coffee", "Professional", "Casual"],
      isUpcoming: true,
      isFeatured: false
    },
    {
      id: 4,
      title: "Innovation Hackathon",
      description: "24-hour hackathon to solve real-world problems with innovative technology solutions.",
      date: "2024-02-10",
      time: "9:00 AM - 9:00 AM (Next Day)",
      location: "Innovation Lab, Tech Center",
      category: "competition",
      organizer: "Innovation Team",
      attendees: 76,
      maxAttendees: 100,
      image: "/figmaAssets/hackathon.jpg",
      tags: ["Hackathon", "Innovation", "Competition", "24hrs"],
      isUpcoming: true,
      isFeatured: false
    },
    {
      id: 5,
      title: "Art & Design Workshop",
      description: "Learn digital art techniques and UI/UX design principles in this hands-on workshop.",
      date: "2024-01-30",
      time: "2:00 PM - 5:00 PM",
      location: "Design Studio, Creative Wing",
      category: "workshop",
      organizer: "Design Team",
      attendees: 28,
      maxAttendees: 40,
      image: "/figmaAssets/art-workshop.jpg",
      tags: ["Art", "Design", "Workshop", "Creative", "UI/UX"],
      isUpcoming: true,
      isFeatured: false
    },
    {
      id: 6,
      title: "Music Evening",
      description: "Acoustic performances by talented employees featuring various genres and instruments.",
      date: "2024-02-05",
      time: "7:00 PM - 9:00 PM",
      location: "Outdoor Amphitheater",
      category: "entertainment",
      organizer: "Music Club",
      attendees: 67,
      maxAttendees: 120,
      image: "/figmaAssets/music-evening.jpg",
      tags: ["Music", "Acoustic", "Performance", "Entertainment"],
      isUpcoming: true,
      isFeatured: false
    }
  ];

  const categories = [
    { id: "all", label: "All Events", count: events.length, icon: Calendar },
    { id: "tech-talk", label: "Tech Talks", count: events.filter(e => e.category === "tech-talk").length, icon: Trophy },
    { id: "festival", label: "Festivals", count: events.filter(e => e.category === "festival").length, icon: Star },
    { id: "networking", label: "Networking", count: events.filter(e => e.category === "networking").length, icon: Coffee },
    { id: "competition", label: "Competitions", count: events.filter(e => e.category === "competition").length, icon: Trophy },
    { id: "workshop", label: "Workshops", count: events.filter(e => e.category === "workshop").length, icon: Palette },
    { id: "entertainment", label: "Entertainment", count: events.filter(e => e.category === "entertainment").length, icon: Music }
  ];

  const filteredEvents = selectedCategory === "all" 
    ? events 
    : events.filter(e => e.category === selectedCategory);

  const handleRSVP = (eventId: number) => {
    setRsvpStatus(prev => ({ ...prev, [eventId]: !prev[eventId] }));
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      "tech-talk": "bg-blue-100 text-blue-800",
      "festival": "bg-purple-100 text-purple-800",
      "networking": "bg-green-100 text-green-800",
      "competition": "bg-red-100 text-red-800",
      "workshop": "bg-yellow-100 text-yellow-800",
      "entertainment": "bg-pink-100 text-pink-800"
    };
    return colors[category as keyof typeof colors] || "bg-gray-100 text-gray-800";
  };

  return (
    <div className="bg-neutral-100 min-h-screen">
      
      <div className="max-w-6xl mx-auto p-8">
        {/* Header Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Cultural Events & Community</h1>
          <p className="text-gray-600 text-lg">
            Connect, learn, and celebrate with our vibrant community through exciting events and activities.
          </p>
          {isHr && (
            <div className="mt-4">
              <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-purple-600 hover:bg-purple-700 text-white">
                    Add Cultural Event (HR only)
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-xl">
                  <DialogHeader>
                    <DialogTitle>Post Cultural Event</DialogTitle>
                  </DialogHeader>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
                    <input
                      className="border rounded px-3 py-2 text-sm"
                      placeholder="Title"
                      value={newEvent.title}
                      onChange={(e) => setNewEvent({ ...newEvent, title: e.target.value })}
                    />
                    <input
                      className="border rounded px-3 py-2 text-sm"
                      placeholder="Date (YYYY-MM-DD)"
                      value={newEvent.date}
                      onChange={(e) => setNewEvent({ ...newEvent, date: e.target.value })}
                    />
                    <input
                      className="border rounded px-3 py-2 text-sm"
                      placeholder="Time (e.g., 6:00 PM - 8:00 PM)"
                      value={newEvent.time}
                      onChange={(e) => setNewEvent({ ...newEvent, time: e.target.value })}
                    />
                    <input
                      className="border rounded px-3 py-2 text-sm"
                      placeholder="Location"
                      value={newEvent.location}
                      onChange={(e) => setNewEvent({ ...newEvent, location: e.target.value })}
                    />
                    <select
                      className="border rounded px-3 py-2 text-sm"
                      value={newEvent.category}
                      onChange={(e) => setNewEvent({ ...newEvent, category: e.target.value })}
                    >
                      <option value="tech-talk">Tech Talks</option>
                      <option value="festival">Festivals</option>
                      <option value="networking">Networking</option>
                      <option value="competition">Competitions</option>
                      <option value="workshop">Workshops</option>
                      <option value="entertainment">Entertainment</option>
                    </select>
                    <textarea
                      className="border rounded px-3 py-2 text-sm md:col-span-2"
                      rows={3}
                      placeholder="Description"
                      value={newEvent.description}
                      onChange={(e) => setNewEvent({ ...newEvent, description: e.target.value })}
                    />
                  </div>
                  <div className="mt-3 flex justify-end gap-2">
                    <Button variant="outline" onClick={() => setIsCreateOpen(false)}>Cancel</Button>
                    <Button
                      onClick={async () => {
                        if (!newEvent.title || !newEvent.date) return;
                        try {
                          const res = await fetch('/api/cultural-events', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            credentials: 'include',
                            body: JSON.stringify(newEvent)
                          });
                          const data = await res.json().catch(() => ({}));
                          if (!res.ok || !data?.success) {
                            throw new Error(data?.detail || data?.message || 'Failed to create event');
                          }
                          setIsCreateOpen(false);
                          // Optionally refresh events list if backed by API
                          alert('Event created successfully');
                        } catch (e: any) {
                          alert(e?.message || 'Failed to create event');
                        }
                      }}
                      className="bg-purple-600 hover:bg-purple-700 text-white"
                    >
                      Submit Event
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          )}
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Calendar className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="text-2xl font-bold">{events.length}</p>
                  <p className="text-sm text-gray-600">Upcoming Events</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-green-600" />
                <div>
                  <p className="text-2xl font-bold">{events.reduce((sum, e) => sum + e.attendees, 0)}</p>
                  <p className="text-sm text-gray-600">Total Attendees</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Star className="h-5 w-5 text-yellow-600" />
                <div>
                  <p className="text-2xl font-bold">{events.filter(e => e.isFeatured).length}</p>
                  <p className="text-sm text-gray-600">Featured Events</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Heart className="h-5 w-5 text-red-600" />
                <div>
                  <p className="text-2xl font-bold">{Object.values(rsvpStatus).filter(Boolean).length}</p>
                  <p className="text-sm text-gray-600">Your RSVPs</p>
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
                <category.icon className="h-4 w-4" />
                <span>{category.label}</span>
                <Badge variant="secondary" className="ml-1">
                  {category.count}
                </Badge>
              </Button>
            ))}
          </div>
        </div>

        {/* Featured Events */}
        {selectedCategory === "all" && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Featured Events</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {events.filter(event => event.isFeatured).map((event) => (
                <Card key={event.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-0">
                    <div className="aspect-video bg-gradient-to-r from-purple-400 to-blue-500 rounded-t-lg flex items-center justify-center">
                      <div className="text-white text-center">
                        <Music className="h-12 w-12 mx-auto mb-2" />
                        <p className="text-sm opacity-90">Event Image</p>
                      </div>
                    </div>
                    
                    <div className="p-6">
                      <div className="flex justify-between items-start mb-3">
                        <h3 className="text-xl font-bold">{event.title}</h3>
                        <Badge className={getCategoryColor(event.category)}>
                          Featured
                        </Badge>
                      </div>
                      
                      <p className="text-gray-600 mb-4">{event.description}</p>
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center text-sm text-gray-600">
                          <Calendar className="h-4 w-4 mr-2" />
                          {event.date} at {event.time}
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                          <MapPin className="h-4 w-4 mr-2" />
                          {event.location}
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                          <Users className="h-4 w-4 mr-2" />
                          {event.attendees}/{event.maxAttendees} attending
                        </div>
                      </div>
                      
                      <div className="flex gap-2">
                        <Button 
                          className="flex-1" 
                          variant={rsvpStatus[event.id] ? "secondary" : "default"}
                          onClick={() => handleRSVP(event.id)}
                        >
                          {rsvpStatus[event.id] ? "✓ RSVP Confirmed" : "RSVP Now"}
                        </Button>
                        {isHr && userFullName && event.organizer === userFullName && (
                          <Button
                            variant="outline"
                            className="flex-1"
                            onClick={() => (window.location.href = `/cultural-events/${event.id}/participants`)}
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
          </div>
        )}

        {/* All Events */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            {selectedCategory === "all" ? "All Events" : categories.find(c => c.id === selectedCategory)?.label}
          </h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {filteredEvents.map((event) => (
              <Card key={event.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg">{event.title}</CardTitle>
                    {event.isFeatured && (
                      <Badge className="bg-yellow-100 text-yellow-800">
                        <Star className="h-3 w-3 mr-1" />
                        Featured
                      </Badge>
                    )}
                  </div>
                  
                  <Badge className={getCategoryColor(event.category)}>
                    {event.category.replace("-", " ")}
                  </Badge>
                </CardHeader>

                <CardContent>
                  <p className="text-gray-600 mb-4 text-sm">{event.description}</p>
                  
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center text-sm text-gray-600">
                      <Calendar className="h-3 w-3 mr-2" />
                      {event.date}
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Clock className="h-3 w-3 mr-2" />
                      {event.time}
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <MapPin className="h-3 w-3 mr-2" />
                      {event.location}
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Users className="h-3 w-3 mr-2" />
                      {event.attendees}/{event.maxAttendees} attending
                    </div>
                  </div>
                  
                  <div className="flex flex-wrap gap-1 mb-4">
                    {event.tags.slice(0, 3).map((tag, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                  
                  <Button 
                    className="w-full" 
                    size="sm"
                    variant={rsvpStatus[event.id] ? "secondary" : "default"}
                    onClick={() => handleRSVP(event.id)}
                  >
                    {rsvpStatus[event.id] ? "✓ RSVP Confirmed" : "RSVP Now"}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredEvents.length === 0 && (
            <div className="text-center py-12">
              <Calendar className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No events found</h3>
              <p className="text-gray-600">Try selecting a different category to see available events.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};