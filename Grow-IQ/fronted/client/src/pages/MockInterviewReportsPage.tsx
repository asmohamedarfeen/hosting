import React, { useEffect, useState } from "react";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  ArrowLeft, 
  Calendar, 
  Clock, 
  Target, 
  TrendingUp, 
  CheckCircle, 
  AlertTriangle,
  Lightbulb,
  BarChart3,
  FileText
} from "lucide-react";

interface InterviewReport {
  id: number;
  session_uuid: string;
  job_role: string;
  job_desc: string;
  score_overall: number;
  score_accuracy: number;
  score_clarity: number;
  score_relevance: number;
  score_confidence: number;
  feedback_summary: string;
  strengths: string[];
  areas_for_improvement: string[];
  suggestions: string[];
  detailed_analysis: Record<string, string>;
  keywords: string[];
  ended_at: string;
  interview_duration_minutes: number;
  questions_answered: number;
}

export const MockInterviewReportsPage = (): JSX.Element => {
  const [location, setLocation] = useLocation();
  const [reports, setReports] = useState<InterviewReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedReport, setSelectedReport] = useState<InterviewReport | null>(null);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const response = await fetch('/mock-interview/sessions', {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch reports');
      }
      
      const data = await response.json();
      setReports(data.sessions || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBadgeColor = (score: number) => {
    if (score >= 80) return 'bg-green-100 text-green-800';
    if (score >= 60) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your interview reports...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center">
        <Card className="max-w-md w-full text-center">
          <CardContent className="pt-6">
            <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Error Loading Reports</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={fetchReports} className="mr-2">
              Try Again
            </Button>
            <Button variant="outline" onClick={() => setLocation('/mock-interview')}>
              Back to Mock Interview
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (selectedReport) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
        <div className="max-w-6xl mx-auto px-4 py-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                onClick={() => setSelectedReport(null)}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Reports
              </Button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Interview Report</h1>
                <p className="text-gray-600">{selectedReport.job_role} • {formatDate(selectedReport.ended_at)}</p>
              </div>
            </div>
            <Badge className={getScoreBadgeColor(selectedReport.score_overall)}>
              Overall Score: {selectedReport.score_overall}/100
            </Badge>
          </div>

          {/* Report Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Overall Feedback */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Overall Feedback
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 leading-relaxed">{selectedReport.feedback_summary}</p>
                </CardContent>
              </Card>

              {/* Strengths */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-green-700">
                    <CheckCircle className="w-5 h-5" />
                    Strengths
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {selectedReport.strengths.map((strength, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">{strength}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Areas for Improvement */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-orange-700">
                    <AlertTriangle className="w-5 h-5" />
                    Areas for Improvement
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {selectedReport.areas_for_improvement.map((area, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <AlertTriangle className="w-4 h-4 text-orange-600 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">{area}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Detailed Analysis */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5" />
                    Detailed Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {Object.entries(selectedReport.detailed_analysis).map(([key, value]) => (
                      <div key={key} className="p-4 bg-gray-50 rounded-lg">
                        <h4 className="font-semibold text-gray-900 mb-2 capitalize">
                          {key.replace('_', ' ')}
                        </h4>
                        <p className="text-gray-700">{value}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Suggestions */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Lightbulb className="w-5 h-5" />
                    Actionable Suggestions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ol className="space-y-2">
                    {selectedReport.suggestions.map((suggestion, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <span className="bg-purple-100 text-purple-800 rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium flex-shrink-0">
                          {index + 1}
                        </span>
                        <span className="text-gray-700">{suggestion}</span>
                      </li>
                    ))}
                  </ol>
                </CardContent>
              </Card>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Scores */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    Detailed Scores
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Overall</span>
                    <span className={`font-semibold ${getScoreColor(selectedReport.score_overall)}`}>
                      {selectedReport.score_overall}/100
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Accuracy</span>
                    <span className={`font-semibold ${getScoreColor(selectedReport.score_accuracy)}`}>
                      {selectedReport.score_accuracy}/100
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Clarity</span>
                    <span className={`font-semibold ${getScoreColor(selectedReport.score_clarity)}`}>
                      {selectedReport.score_clarity}/100
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Relevance</span>
                    <span className={`font-semibold ${getScoreColor(selectedReport.score_relevance)}`}>
                      {selectedReport.score_relevance}/100
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Confidence</span>
                    <span className={`font-semibold ${getScoreColor(selectedReport.score_confidence)}`}>
                      {selectedReport.score_confidence}/100
                    </span>
                  </div>
                </CardContent>
              </Card>

              {/* Interview Details */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5" />
                    Interview Details
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Calendar className="w-4 h-4" />
                    <span>{formatDate(selectedReport.ended_at)}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Clock className="w-4 h-4" />
                    <span>{selectedReport.interview_duration_minutes} minutes</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Target className="w-4 h-4" />
                    <span>{selectedReport.questions_answered} questions answered</span>
                  </div>
                </CardContent>
              </Card>

              {/* Keywords */}
              <Card>
                <CardHeader>
                  <CardTitle>Key Topics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {selectedReport.keywords.map((keyword, index) => (
                      <Badge key={index} variant="secondary">
                        {keyword}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Interview Reports</h1>
            <p className="text-gray-600">View detailed AI-generated reports from your mock interviews</p>
          </div>
          <Button
            variant="outline"
            onClick={() => setLocation('/mock-interview')}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Mock Interview
          </Button>
        </div>

        {/* Reports List */}
        {reports.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No Reports Yet</h3>
              <p className="text-gray-600 mb-6">
                Complete a mock interview to see your detailed AI-generated report here.
              </p>
              <Button onClick={() => setLocation('/mock-interview')}>
                Start Your First Interview
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {reports.map((report) => (
              <Card 
                key={report.id} 
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => setSelectedReport(report)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{report.job_role}</CardTitle>
                      <p className="text-sm text-gray-600 mt-1">
                        {formatDate(report.ended_at)}
                      </p>
                    </div>
                    <Badge className={getScoreBadgeColor(report.score_overall)}>
                      {report.score_overall}/100
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Clock className="w-4 h-4" />
                      <span>{report.interview_duration_minutes} minutes</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Target className="w-4 h-4" />
                      <span>{report.questions_answered} questions</span>
                    </div>
                    <p className="text-sm text-gray-700 line-clamp-2">
                      {report.feedback_summary}
                    </p>
                    <div className="flex flex-wrap gap-1 mt-3">
                      {report.keywords.slice(0, 3).map((keyword, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {keyword}
                        </Badge>
                      ))}
                      {report.keywords.length > 3 && (
                        <Badge variant="secondary" className="text-xs">
                          +{report.keywords.length - 3} more
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
