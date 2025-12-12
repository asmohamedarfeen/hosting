import React, { useState } from "react";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { NavigationHeader } from "@/components/ui/navigation-header";
import { Eye, EyeOff } from "lucide-react";

export const LoginPage = (): JSX.Element => {
  const [location, setLocation] = useLocation();
  const [showPassword, setShowPassword] = useState(false);
  const [isLogin, setIsLogin] = useState(true);
  
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    firstName: "",
    lastName: "",
    confirmPassword: ""
  });


  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, this would handle authentication
    if (isLogin) {
      // Login logic
      setLocation("/dashboard");
    } else {
      // Signup logic
      setLocation("/dashboard");
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setFormData({
      email: "",
      password: "",
      firstName: "",
      lastName: "",
      confirmPassword: ""
    });
  };

  return (
    <div className="bg-neutral-100 min-h-screen">
      {/* Header */}
      <NavigationHeader title={isLogin ? "Welcome Back" : "Create Account"} />

      <div className="flex items-center justify-center min-h-[calc(100vh-82px)] p-8">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="font-h5 text-[#673ab7] text-2xl">
              {isLogin ? "Welcome Back" : "Create Account"}
            </CardTitle>
            <p className="font-caption text-[#000000b2]">
              {isLogin 
                ? "Sign in to your account to continue" 
                : "Join GrowIQ to find your dream job"
              }
            </p>
          </CardHeader>
          
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {!isLogin && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="firstName" className="font-caption">First Name</Label>
                    <Input
                      id="firstName"
                      required
                      value={formData.firstName}
                      onChange={(e) => handleInputChange("firstName", e.target.value)}
                      className="border-[#673ab733] focus:border-[#673ab7]"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastName" className="font-caption">Last Name</Label>
                    <Input
                      id="lastName"
                      required
                      value={formData.lastName}
                      onChange={(e) => handleInputChange("lastName", e.target.value)}
                      className="border-[#673ab733] focus:border-[#673ab7]"
                    />
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="email" className="font-caption">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => handleInputChange("email", e.target.value)}
                  className="border-[#673ab733] focus:border-[#673ab7]"
                  placeholder="Enter your email"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="font-caption">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    required
                    value={formData.password}
                    onChange={(e) => handleInputChange("password", e.target.value)}
                    className="border-[#673ab733] focus:border-[#673ab7] pr-10"
                    placeholder="Enter your password"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-[#673ab7]" />
                    ) : (
                      <Eye className="h-4 w-4 text-[#673ab7]" />
                    )}
                  </Button>
                </div>
              </div>

              {!isLogin && (
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword" className="font-caption">Confirm Password</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    required
                    value={formData.confirmPassword}
                    onChange={(e) => handleInputChange("confirmPassword", e.target.value)}
                    className="border-[#673ab733] focus:border-[#673ab7]"
                    placeholder="Confirm your password"
                  />
                </div>
              )}

              {isLogin && (
                <div className="flex justify-end">
                  <Button
                    type="button"
                    variant="link"
                    className="text-[#673ab7] p-0 h-auto font-caption"
                  >
                    Forgot Password?
                  </Button>
                </div>
              )}

              <Button
                type="submit"
                className="w-full bg-[#673ab7] hover:bg-[#673ab7]/90 text-white py-3"
              >
                {isLogin ? "Sign In" : "Create Account"}
              </Button>
            </form>

            <div className="mt-6">
              <Separator className="my-4" />
              
              <div className="text-center">
                <p className="font-caption text-[#000000b2]">
                  {isLogin ? "Don't have an account?" : "Already have an account?"}
                  {" "}
                  <Button
                    type="button"
                    variant="link"
                    onClick={toggleMode}
                    className="text-[#673ab7] p-0 h-auto font-caption underline"
                  >
                    {isLogin ? "Sign up" : "Sign in"}
                  </Button>
                </p>
              </div>
            </div>

            {!isLogin && (
              <div className="mt-4 text-center">
                <p className="font-caption text-[#000000b2] text-xs">
                  By creating an account, you agree to our{" "}
                  <Button
                    type="button"
                    variant="link"
                    className="text-[#673ab7] p-0 h-auto font-caption text-xs underline"
                  >
                    Terms of Service
                  </Button>
                  {" "}and{" "}
                  <Button
                    type="button"
                    variant="link"
                    className="text-[#673ab7] p-0 h-auto font-caption text-xs underline"
                  >
                    Privacy Policy
                  </Button>
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};