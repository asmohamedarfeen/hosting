import React, { useState } from "react";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { Bell, Mail, Smartphone, Lock, Trash2 } from "lucide-react";

export const SettingsPage = (): JSX.Element => {
  const [location, setLocation] = useLocation();
  
  const [notifications, setNotifications] = useState({
    emailJobAlerts: true,
    emailApplicationUpdates: true,
    pushJobAlerts: false,
    pushApplicationUpdates: true,
    weeklyDigest: true,
    promotionalEmails: false
  });

  const [accountSettings, setAccountSettings] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: ""
  });


  const handleNotificationChange = (key: string, value: boolean) => {
    setNotifications(prev => ({ ...prev, [key]: value }));
  };

  const handlePasswordChange = (field: string, value: string) => {
    setAccountSettings(prev => ({ ...prev, [field]: value }));
  };

  const handleSaveNotifications = () => {
    // Save notifications settings
    console.log("Saving notifications:", notifications);
  };

  const handleChangePassword = (e: React.FormEvent) => {
    e.preventDefault();
    // Change password logic
    console.log("Changing password");
    setAccountSettings({
      currentPassword: "",
      newPassword: "",
      confirmPassword: ""
    });
  };

  const handleDeleteAccount = () => {
    // Delete account logic
    if (confirm("Are you sure you want to delete your account? This action cannot be undone.")) {
      console.log("Deleting account");
    }
  };

  return (
    <div className="bg-neutral-100 min-h-screen">
      {/* Header */}

      <div className="max-w-4xl mx-auto p-8">
        <div className="space-y-8">
          {/* Notification Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="font-h5 text-[#673ab7] flex items-center gap-2">
                <Bell className="w-5 h-5" />
                Notification Preferences
              </CardTitle>
              <p className="font-caption text-[#000000b2]">
                Choose how you want to receive updates about jobs and applications.
              </p>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Email Notifications */}
              <div>
                <h3 className="font-body font-semibold text-[#673ab7] mb-4 flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  Email Notifications
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="font-caption font-semibold">Job Alerts</Label>
                      <p className="font-caption text-[#000000b2] text-sm">
                        Get notified when new jobs match your preferences
                      </p>
                    </div>
                    <Switch
                      checked={notifications.emailJobAlerts}
                      onCheckedChange={(checked) => handleNotificationChange("emailJobAlerts", checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="font-caption font-semibold">Application Updates</Label>
                      <p className="font-caption text-[#000000b2] text-sm">
                        Updates on your job applications status
                      </p>
                    </div>
                    <Switch
                      checked={notifications.emailApplicationUpdates}
                      onCheckedChange={(checked) => handleNotificationChange("emailApplicationUpdates", checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="font-caption font-semibold">Weekly Digest</Label>
                      <p className="font-caption text-[#000000b2] text-sm">
                        Weekly summary of new opportunities
                      </p>
                    </div>
                    <Switch
                      checked={notifications.weeklyDigest}
                      onCheckedChange={(checked) => handleNotificationChange("weeklyDigest", checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="font-caption font-semibold">Promotional Emails</Label>
                      <p className="font-caption text-[#000000b2] text-sm">
                        Special offers and feature updates
                      </p>
                    </div>
                    <Switch
                      checked={notifications.promotionalEmails}
                      onCheckedChange={(checked) => handleNotificationChange("promotionalEmails", checked)}
                    />
                  </div>
                </div>
              </div>

              <Separator />

              {/* Push Notifications */}
              <div>
                <h3 className="font-body font-semibold text-[#673ab7] mb-4 flex items-center gap-2">
                  <Smartphone className="w-4 h-4" />
                  Push Notifications
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="font-caption font-semibold">Job Alerts</Label>
                      <p className="font-caption text-[#000000b2] text-sm">
                        Instant notifications for matching jobs
                      </p>
                    </div>
                    <Switch
                      checked={notifications.pushJobAlerts}
                      onCheckedChange={(checked) => handleNotificationChange("pushJobAlerts", checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="font-caption font-semibold">Application Updates</Label>
                      <p className="font-caption text-[#000000b2] text-sm">
                        Real-time updates on application status
                      </p>
                    </div>
                    <Switch
                      checked={notifications.pushApplicationUpdates}
                      onCheckedChange={(checked) => handleNotificationChange("pushApplicationUpdates", checked)}
                    />
                  </div>
                </div>
              </div>

              <div className="pt-4">
                <Button
                  onClick={handleSaveNotifications}
                  className="bg-[#673ab7] hover:bg-[#673ab7]/90 text-white"
                >
                  Save Notification Settings
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Security Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="font-h5 text-[#673ab7] flex items-center gap-2">
                <Lock className="w-5 h-5" />
                Security & Password
              </CardTitle>
              <p className="font-caption text-[#000000b2]">
                Keep your account secure by updating your password regularly.
              </p>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleChangePassword} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="currentPassword" className="font-caption">Current Password</Label>
                  <Input
                    id="currentPassword"
                    type="password"
                    value={accountSettings.currentPassword}
                    onChange={(e) => handlePasswordChange("currentPassword", e.target.value)}
                    className="border-[#673ab733] focus:border-[#673ab7]"
                    placeholder="Enter current password"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="newPassword" className="font-caption">New Password</Label>
                  <Input
                    id="newPassword"
                    type="password"
                    value={accountSettings.newPassword}
                    onChange={(e) => handlePasswordChange("newPassword", e.target.value)}
                    className="border-[#673ab733] focus:border-[#673ab7]"
                    placeholder="Enter new password"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirmPassword" className="font-caption">Confirm New Password</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    value={accountSettings.confirmPassword}
                    onChange={(e) => handlePasswordChange("confirmPassword", e.target.value)}
                    className="border-[#673ab733] focus:border-[#673ab7]"
                    placeholder="Confirm new password"
                  />
                </div>

                <Button
                  type="submit"
                  className="bg-[#673ab7] hover:bg-[#673ab7]/90 text-white"
                >
                  Change Password
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Account Management */}
          <Card>
            <CardHeader>
              <CardTitle className="font-h5 text-[#673ab7] flex items-center gap-2">
                <Trash2 className="w-5 h-5" />
                Account Management
              </CardTitle>
              <p className="font-caption text-[#000000b2]">
                Manage your account settings and data.
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <Button
                  variant="outline"
                  onClick={() => setLocation("/profile")}
                  className="border-[#673ab7] text-[#673ab7]"
                >
                  Update Profile Information
                </Button>

                <Button
                  variant="outline"
                  className="border-[#673ab7] text-[#673ab7]"
                >
                  Download My Data
                </Button>
              </div>

              <Separator />

              <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                <h4 className="font-body font-semibold text-red-800 mb-2">Danger Zone</h4>
                <p className="font-caption text-red-700 mb-4">
                  Once you delete your account, there is no going back. Please be certain.
                </p>
                <Button
                  onClick={handleDeleteAccount}
                  variant="destructive"
                  className="bg-red-600 hover:bg-red-700"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete Account
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};