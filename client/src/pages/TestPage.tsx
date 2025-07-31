import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { apiService } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

const TestPage = () => {
  const [healthStatus, setHealthStatus] = useState<string>('');
  const [files, setFiles] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const testHealthCheck = async () => {
    try {
      setIsLoading(true);
      const response = await apiService.healthCheck();
      setHealthStatus(`✅ API is healthy: ${response.message}`);
      toast({
        title: "API Test Successful",
        description: "Backend is running and accessible",
      });
    } catch (error) {
      setHealthStatus(`❌ API Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      toast({
        title: "API Test Failed",
        description: error instanceof Error ? error.message : "Failed to connect to backend",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const testGetFiles = async () => {
    try {
      setIsLoading(true);
      const userFiles = await apiService.getUserFiles();
      setFiles(userFiles);
      toast({
        title: "Files Loaded",
        description: `Found ${userFiles.length} uploaded files`,
      });
    } catch (error) {
      toast({
        title: "Failed to Load Files",
        description: error instanceof Error ? error.message : "Authentication or API error",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setIsLoading(true);
      const response = await apiService.uploadFile(file);
      toast({
        title: "Upload Successful",
        description: `${file.name} uploaded successfully`,
      });
      // Refresh files list
      await testGetFiles();
    } catch (error) {
      toast({
        title: "Upload Failed",
        description: error instanceof Error ? error.message : "Failed to upload file",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="container mx-auto max-w-4xl">
        <h1 className="text-3xl font-bold text-white mb-8">API Test Page</h1>
        
        <div className="grid gap-6">
          {/* Health Check */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Backend Health Check</h2>
            <Button 
              onClick={testHealthCheck} 
              disabled={isLoading}
              className="mb-4"
            >
              Test API Connection
            </Button>
            {healthStatus && (
              <div className="p-4 bg-slate-800 rounded-lg">
                <pre className="text-white">{healthStatus}</pre>
              </div>
            )}
          </Card>

          {/* File Upload Test */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-white mb-4">File Upload Test</h2>
            <div className="mb-4">
              <input
                type="file"
                accept=".pdf,.doc,.docx,.eml"
                onChange={handleFileUpload}
                disabled={isLoading}
                className="block w-full text-sm text-slate-300
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-primary file:text-white
                  hover:file:bg-primary/80"
              />
            </div>
            <Button 
              onClick={testGetFiles} 
              disabled={isLoading}
              variant="outline"
            >
              Load User Files
            </Button>
          </Card>

          {/* Files List */}
          {files.length > 0 && (
            <Card className="p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Uploaded Files ({files.length})</h2>
              <div className="space-y-2">
                {files.map((file) => (
                  <div key={file.id} className="p-3 bg-slate-800 rounded-lg">
                    <div className="text-white font-medium">{file.filename}</div>
                    <div className="text-slate-400 text-sm">
                      Type: {file.file_type} | Uploaded: {new Date(file.upload_time).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default TestPage; 