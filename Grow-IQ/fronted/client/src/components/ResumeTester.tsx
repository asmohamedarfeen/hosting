import React, { useState, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

interface ResumeScore {
  total_score: number;
  content_quality: { score: number; explanation: string; total_score: number };
  skills_match: { score: number; explanation: string; total_score: number };
  experience_achievements: { score: number; explanation: string; total_score: number };
  format_structure: { score: number; explanation: string; total_score: number };
  education_certifications: { score: number; explanation: string; total_score: number };
  analysis_duration_ms?: number;
  timestamp?: string;
}

interface ResumeTesterProps {
  onClose?: () => void;
  onScored?: (score: number) => void;
}

export const ResumeTester: React.FC<ResumeTesterProps> = ({ onClose, onScored }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<ResumeScore | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processFile = async (file: File) => {
    if (file.type !== 'application/pdf') {
      setError('Only PDF files are supported.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('File size exceeds 10MB limit.');
      return;
    }

    setIsUploading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/upload-resume', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        let errorMessage = `HTTP error! status: ${response.status}`;
        
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          // If it's not JSON, use the text as is
          errorMessage = errorText || errorMessage;
        }
        
        throw new Error(errorMessage);
      }

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      // Check if the result has the expected structure
      if (!data.total_score && !data.content_quality) {
        throw new Error('Invalid response format from server. Please try again.');
      }

      setResult(data);
      // Notify parent about the new score so ATS Checker updates immediately
      if (typeof data.total_score === 'number' && onScored) {
        onScored(data.total_score);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while processing your resume.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    await processFile(file);
  };

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      await processFile(files[0]);
    }
  };

  const getCategoryColor = (category: string): string => {
    const colors: { [key: string]: string } = {
      'content_quality': '#ff6b6b', // Content Quality - Red
      'skills_match': '#4ecdc4', // Skills Match - Teal
      'experience_achievements': '#45b7d1', // Experience - Blue
      'format_structure': '#f9ca24', // Format - Yellow
      'education_certifications': '#6c5ce7'  // Education - Purple
    };
    return colors[category] || '#6c5ce7';
  };

  const getCategoryLabel = (category: string): string => {
    const labels: { [key: string]: string } = {
      'content_quality': 'Content Quality',
      'skills_match': 'Skills Match',
      'experience_achievements': 'Experience & Achievements',
      'format_structure': 'Format & Structure',
      'education_certifications': 'Education & Certifications'
    };
    return labels[category] || category;
  };

  const getScoreMessage = (score: number): string => {
    if (score >= 90) return "🏆 Excellent! Your resume is highly optimized for ATS systems.";
    if (score >= 80) return "🥇 Very Good! Your resume is well-optimized for ATS screening.";
    if (score >= 70) return "🥈 Good! Your resume meets most ATS requirements.";
    if (score >= 60) return "🥉 Fair! Consider implementing suggested improvements.";
    return "📝 Needs Improvement! Review and implement the recommendations above.";
  };

  const renderScoreChart = (score: number, maxScore: number, label: string, explanation: string, index: number) => {
    const percentage = Math.round((score / maxScore) * 100);
    const circumference = 2 * Math.PI * 50;
    const strokeDashoffset = circumference * (1 - percentage / 100);
    
    // Get color based on label
    const categoryKey = Object.keys(result || {}).find(key => 
      key !== 'total_score' && key !== 'analysis_duration_ms' && key !== 'timestamp' && key !== 'metadata' &&
      getCategoryLabel(key) === label
    ) || '';
    const color = getCategoryColor(categoryKey);

    return (
      <Card key={index} className="p-6 text-center hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
        <CardContent className="p-0">
          <h4 className="text-lg font-semibold mb-4 text-gray-800">{label}</h4>
          <div className="relative w-32 h-32 mx-auto mb-4">
            <svg width="128" height="128" viewBox="0 0 128 128" className="transform -rotate-90">
              {/* Background circle */}
              <circle
                cx="64"
                cy="64"
                r="50"
                fill="none"
                stroke="#e9ecef"
                strokeWidth="8"
              />
              {/* Progress arc */}
              <circle
                cx="64"
                cy="64"
                r="50"
                fill="none"
                stroke={color}
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                className="transition-all duration-1500 ease-out"
                style={{
                  strokeDashoffset: strokeDashoffset,
                }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <div className="text-2xl font-bold text-blue-600">{score}</div>
              <div className="text-sm text-gray-500">/ {maxScore}</div>
            </div>
          </div>
          <div className="text-sm text-gray-600 mb-3 leading-relaxed">{explanation}</div>
          <Badge 
            variant="secondary" 
            className="text-xs"
            style={{ backgroundColor: `${color}20`, color: color }}
          >
            {percentage}% Complete
          </Badge>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card className="shadow-lg">
        <CardHeader className="text-center pb-4">
          <div className="flex items-center justify-between">
            {onClose && (
              <Button variant="ghost" onClick={onClose} className="text-gray-500 hover:text-gray-700">
                ← Back
              </Button>
            )}
            <CardTitle className="text-2xl font-bold text-gray-800 flex items-center gap-2">
              <FileText className="h-6 w-6 text-blue-600" />
              ATS Resume Scorer
            </CardTitle>
            <div className="w-20"></div> {/* Spacer for centering */}
          </div>
          <p className="text-gray-600 mt-2">
            Upload your resume to get an AI-powered ATS compatibility score and detailed feedback.
          </p>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Upload Section with Drag and Drop */}
          <div
            onDragEnter={handleDragEnter}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 ${
              isDragging
                ? 'border-blue-500 bg-blue-50 scale-105'
                : 'border-blue-300 hover:border-blue-400 bg-white'
            }`}
          >
            <Upload className={`h-12 w-12 mx-auto mb-4 transition-colors ${
              isDragging ? 'text-blue-600' : 'text-blue-500'
            }`} />
            <Label 
              htmlFor="resume-file" 
              className="text-lg font-medium text-gray-700 cursor-pointer block mb-2"
            >
              {isDragging ? 'Drop your PDF resume here' : 'Choose PDF Resume or Drag & Drop'}
            </Label>
            <Input
              id="resume-file"
              type="file"
              accept="application/pdf"
              onChange={handleFileUpload}
              ref={fileInputRef}
              className="hidden"
            />
            <p className="text-sm text-gray-500 mt-2">
              Only PDF files are supported. Maximum file size: 10MB
            </p>
            {isDragging && (
              <p className="text-sm text-blue-600 font-medium mt-2 animate-pulse">
                Release to upload
              </p>
            )}
          </div>

          {/* Loading State */}
          {isUploading && (
            <div className="text-center py-12">
              <div className="relative">
                <Loader2 className="h-16 w-16 text-blue-500 animate-spin mx-auto mb-4" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-8 h-8 bg-blue-100 rounded-full animate-ping"></div>
                </div>
              </div>
              <h3 className="text-xl font-semibold text-blue-600 mb-2">Processing Your Resume...</h3>
              <p className="text-gray-600 mb-4">We're analyzing your document using AI</p>
              <div className="flex justify-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="text-center py-8">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-red-600 mb-2">Error Processing Resume</h3>
              <p className="text-gray-600">{error}</p>
              <Button 
                onClick={() => {
                  setError(null);
                  if (fileInputRef.current) fileInputRef.current.value = '';
                }}
                className="mt-4"
              >
                Try Again
              </Button>
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="space-y-6">
              {/* Overall Score */}
              <div className="text-center py-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl text-white">
                <h2 className="text-2xl font-bold mb-2">🎯 Resume Analysis Results</h2>
                <div className="text-6xl font-bold mb-2">{result.total_score}/100</div>
                <p className="text-lg opacity-90">{getScoreMessage(result.total_score)}</p>
                {result.analysis_duration_ms && (
                  <p className="text-sm opacity-75 mt-2">
                    Analysis completed in {(result.analysis_duration_ms / 1000).toFixed(1)}s
                  </p>
                )}
              </div>

              {/* Category Scores */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {Object.entries(result).filter(([key, value]) => 
                  key !== 'total_score' && key !== 'analysis_duration_ms' && key !== 'timestamp' && key !== 'metadata'
                ).map(([category, data], index) => {
                  if (typeof data === 'object' && data !== null && 'score' in data) {
                    return renderScoreChart(
                      data.score,
                      data.total_score,
                      getCategoryLabel(category),
                      data.explanation,
                      index
                    );
                  }
                  return null;
                })}
              </div>

              {/* Detailed Analysis */}
              <Card className="bg-gray-50">
                <CardHeader>
                  <CardTitle className="text-xl text-gray-800 flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    Detailed Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {Object.entries(result).filter(([key, value]) => 
                      key !== 'total_score' && key !== 'analysis_duration_ms' && key !== 'timestamp' && key !== 'metadata'
                    ).map(([category, data], index) => {
                      if (typeof data === 'object' && data !== null && 'score' in data) {
                        return (
                          <li key={index} className="flex items-start gap-3">
                            <div 
                              className="w-3 h-3 rounded-full mt-2 flex-shrink-0"
                              style={{ backgroundColor: getCategoryColor(category) }}
                            ></div>
                            <div>
                              <strong className="text-blue-600">{getCategoryLabel(category)}:</strong>
                              <span className="text-gray-700 ml-2">{data.explanation}</span>
                            </div>
                          </li>
                        );
                      }
                      return null;
                    })}
                  </ul>
                </CardContent>
              </Card>

              {/* Action Buttons */}
              <div className="flex justify-center gap-4">
                <Button 
                  onClick={() => {
                    setResult(null);
                    setError(null);
                    if (fileInputRef.current) fileInputRef.current.value = '';
                  }}
                  variant="outline"
                  className="bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-200"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Try Another Resume
                </Button>
                {onClose && (
                  <Button onClick={onClose}>
                    Close
                  </Button>
                )}
              </div>
            </div>
          )}

        </CardContent>
      </Card>
    </div>
  );
};
