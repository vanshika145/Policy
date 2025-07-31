import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Download, FileText, FileCheck2, FileClock, Brain, User, Calendar, ShieldCheck, XCircle, CheckCircle } from 'lucide-react';
import { Header } from './Header';
import { apiService } from '@/services/api';

const dummyQuery = {
  mode: 'plain', // or 'form'
  plain: 'Does my policy cover flight delays?',
  form: {
    age: 45,
    gender: 'Female',
    condition: 'Heart surgery',
    location: 'Mumbai',
    policyName: 'Premium Plus',
    policyDuration: '2 Months',
  },
};

const dummyResult = {
  decision: 'rejected',
  amount: null,
  justification: 'Flight delay coverage only applicable after 7 days of policy activation. Current policy is 3 days old.',
  clauses: [
    { id: '5.2', title: '' },
    { id: '8.1(b)', title: '' },
  ],
};

export default function ResultsPage() {
  const [userFiles, setUserFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    loadUserFiles();
  }, []);

  const loadUserFiles = async () => {
    try {
      const files = await apiService.getUserFiles();
      setUserFiles(files);
      if (files.length > 0) {
        setSelectedFile(files[0]);
      }
    } catch (error) {
      console.error('Failed to load user files:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getFileType = (fileType) => {
    switch (fileType.toLowerCase()) {
      case 'pdf': return 'PDF Document';
      case 'docx': return 'Word Document';
      case 'doc': return 'Word Document';
      case 'eml': return 'Email Document';
      default: return fileType.toUpperCase();
    }
  };
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#181a2a] to-[#10111a] text-slate-100">
      <Header />
      <main className="container mx-auto px-4 py-12 max-w-5xl flex flex-col gap-8">
        {/* Title and Query Summary */}
        <div className="mb-2">
          <h1 className="text-2xl md:text-3xl font-bold mb-2">Here's What We Found in Your Policy</h1>
        </div>

        {userFiles.length === 0 ? (
          <Card className="rounded-2xl p-8 shadow-md bg-gradient-to-br from-[#1e1f2f] to-[#15161f] ai-card-glow">
            <div className="text-center">
              <FileText className="w-16 h-16 text-slate-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No Documents Found</h3>
              <p className="text-slate-300 mb-4">
                You haven't uploaded any documents yet. Upload some documents to see analysis results.
              </p>
              <Button 
                className="btn-ai-primary"
                onClick={() => window.location.href = '/documents'}
              >
                Upload Documents
              </Button>
            </div>
          </Card>
        ) : (
          <>
            {/* Your Query Card */}
            <Card className="rounded-2xl p-6 shadow-md bg-gradient-to-br from-[#1e1f2f] to-[#15161f] ai-card-glow mb-2">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Brain className="w-5 h-5 text-primary-glow" />
            Your Query
          </h2>
          {dummyQuery.mode === 'plain' ? (
            <div className="text-base text-slate-200 italic">{dummyQuery.plain}</div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-base">
              <div><span className="font-medium">Age:</span> {dummyQuery.form.age}</div>
              <div><span className="font-medium">Gender:</span> {dummyQuery.form.gender}</div>
              <div className="sm:col-span-2"><span className="font-medium">Condition:</span> {dummyQuery.form.condition}</div>
              <div><span className="font-medium">Location:</span> {dummyQuery.form.location}</div>
              <div><span className="font-medium">Policy Name:</span> {dummyQuery.form.policyName}</div>
              <div><span className="font-medium">Policy Duration:</span> {dummyQuery.form.policyDuration}</div>
            </div>
          )}
        </Card>
        {/* Main Content: 2 columns on desktop, stacked on mobile */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Left: AI Analysis Result */}
          <Card className="rounded-2xl p-6 shadow-md bg-gradient-to-br from-[#1e1f2f] to-[#15161f] ai-card-glow md:col-span-2 flex flex-col gap-4">
            <h2 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-accent" />
              AI Analysis Result
            </h2>
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <span className="font-medium">Decision:</span>
                {dummyResult.decision === 'approved' ? (
                  <Badge className="bg-green-600/80 text-white px-3 py-1 flex items-center gap-1"><CheckCircle className="w-4 h-4" /> Approved</Badge>
                ) : (
                  <Badge className="bg-red-600/80 text-white px-3 py-1 flex items-center gap-1"><XCircle className="w-4 h-4" /> Rejected</Badge>
                )}
              </div>
              <div className="flex items-center gap-2">
                <span className="font-medium">Amount:</span>
                <span className="text-accent font-bold">{dummyResult.amount ? ` ₹${dummyResult.amount.toLocaleString()}` : '—'}</span>
              </div>
            </div>
            <div>
              <span className="font-medium">Justification:</span>
              <div className="mt-2 bg-background/40 rounded-lg p-3 text-slate-200 italic border-l-4 border-primary-glow">
                {dummyResult.justification}
              </div>
            </div>
            <div>
              <span className="font-medium">Matched Clauses:</span>
              <div className="flex flex-wrap gap-2 mt-2">
                {dummyResult.clauses.map(clause => (
                  <span key={clause.id} className="bg-slate-800/70 text-slate-100 px-3 py-1 rounded-full text-xs border border-primary-glow/30">
                    Clause {clause.id}
                  </span>
                ))}
              </div>
            </div>
          </Card>
          {/* Right: Document Info */}
          <Card className="rounded-2xl p-6 shadow-md bg-gradient-to-br from-[#1e1f2f] to-[#15161f] ai-card-glow flex flex-col gap-4 h-fit">
            <h2 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary-glow" />
              Document Info
            </h2>
            <div className="flex flex-col gap-2 text-base">
              {selectedFile ? (
                <>
                  <div className="flex items-center gap-2"><span className="font-medium">File Name:</span> {selectedFile.filename}</div>
                  <div className="flex items-center gap-2"><span className="font-medium">Type:</span> {getFileType(selectedFile.file_type)}</div>
                  <div className="flex items-center gap-2"><span className="font-medium">Uploaded:</span> {formatDate(selectedFile.upload_time)}</div>
                </>
              ) : (
                <div className="text-slate-400">No document selected</div>
              )}
            </div>
            <div className="flex gap-2 mt-2">
              <Button variant="outline" className="w-full btn-ai-secondary">Re-upload</Button>
              <Button variant="destructive" className="w-full">Delete</Button>
            </div>
          </Card>
        </div>
        {/* Ask Another Question */}
        <Card className="rounded-2xl p-6 shadow-md bg-gradient-to-br from-[#1e1f2f] to-[#15161f] ai-card-glow flex flex-col gap-4 mt-2">
          <h2 className="text-lg font-semibold mb-2 flex items-center gap-2">
            <User className="w-5 h-5 text-accent" />
            Ask Another Question
          </h2>
          <form className="flex flex-col sm:flex-row gap-4">
            <Input
              type="text"
              placeholder="Ask another question..."
              className="flex-1 bg-background/70 border border-primary-glow"
            />
            <Button type="submit" className="btn-ai-primary px-6 py-2">Ask</Button>
          </form>
          <div className="flex items-center gap-2 mt-2">
            <Download className="w-4 h-4 text-primary-glow" />
            <span className="text-xs text-muted-foreground">Download Full JSON Result</span>
          </div>
        </Card>
          </>
        )}
      </main>
    </div>
  );
} 