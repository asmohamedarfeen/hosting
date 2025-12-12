import React, { useEffect, useState } from "react";
import { useRoute } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface Participant {
  id: number;
  full_name?: string;
  email?: string;
  username?: string;
}

export const WorkshopParticipantsPage = (): JSX.Element => {
  const [, params] = useRoute("/workshop/:id/participants");
  const workshopId = Number(params?.id || 0);
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchParticipants = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await fetch(`/workshops/api/workshops/${workshopId}/participants`, { credentials: 'include' });
        if (!res.ok) {
          const text = await res.text().catch(() => '');
          throw new Error(text || `Failed to fetch participants (status ${res.status})`);
        }
        const data = await res.json();
        setParticipants(Array.isArray(data?.participants) ? data.participants : []);
      } catch (e: any) {
        setError(e?.message || 'Failed to load participants');
      } finally {
        setLoading(false);
      }
    };
    if (workshopId) fetchParticipants();
  }, [workshopId]);

  return (
    <div className="bg-neutral-100 min-h-screen">
      <div className="max-w-4xl mx-auto p-8">
        <Card>
          <CardHeader>
            <CardTitle>Workshop Participants</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8 text-gray-600">Loading...</div>
            ) : error ? (
              <div className="text-center py-8 text-red-600 text-sm">{error}</div>
            ) : participants.length === 0 ? (
              <div className="text-center py-8 text-gray-600 text-sm">No participants yet.</div>
            ) : (
              <div className="space-y-3">
                {participants.map((p) => (
                  <div key={p.id} className="flex items-center justify-between p-3 border rounded-lg bg-white">
                    <div>
                      <div className="font-medium text-gray-900">{p.full_name || p.username || `User #${p.id}`}</div>
                      <div className="text-xs text-gray-500">{p.email || 'Hidden email'}</div>
                    </div>
                    <Badge variant="outline" className="text-xs">Registered</Badge>
                  </div>
                ))}
              </div>
            )}
            <div className="mt-6">
              <Button variant="outline" onClick={() => history.back()}>Back</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default WorkshopParticipantsPage;


