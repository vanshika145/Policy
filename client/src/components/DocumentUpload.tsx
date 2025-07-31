import { useState, useCallback, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { apiService, UploadedFile } from '@/services/api';
import { EmbeddingsGenerator } from './EmbeddingsGenerator';
import { 
  Upload, 
  File, 
  FileText, 
  Mail, 
  CheckCircle, 
  AlertCircle,
  X,
  Brain
} from 'lucide-react';

interface FileWithStatus extends UploadedFile {
  status: 'processing' | 'completed' | 'error';
  extractedText?: string;
  entities?: string[];
}

export const DocumentUpload = () => {
  const [files, setFiles] = useState<FileWithStatus[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  // Load existing files on component mount
  useEffect(() => {
    loadUserFiles();
  }, []);

  const loadUserFiles = async () => {
    try {
      const userFiles = await apiService.getUserFiles();
      const filesWithStatus: FileWithStatus[] = userFiles.map(file => ({
        ...file,
        status: 'completed' as const,
        extractedText: `Successfully uploaded ${file.filename}`,
        entities: ['Document', 'Policy', 'Analysis Ready']
      }));
      setFiles(filesWithStatus);
    } catch (error) {
      console.error('Failed to load user files:', error);
      // Don't show error toast for initial load
    }
  };

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    processFiles(droppedFiles);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      processFiles(selectedFiles);
    }
  };

  const processFiles = async (fileList: File[]) => {
    setIsLoading(true);
    
    for (const file of fileList) {
      try {
        setUploadProgress(0);
        
        // Create a temporary file entry
        const tempFile: FileWithStatus = {
          id: Date.now(),
          filename: file.name,
          file_type: file.type,
          upload_time: new Date().toISOString(),
          file_path: '',
          user_id: 0,
          status: 'processing'
        };

        setFiles(prev => [...prev, tempFile]);

        // Simulate upload progress
        for (let progress = 0; progress <= 90; progress += 10) {
          await new Promise(resolve => setTimeout(resolve, 100));
          setUploadProgress(progress);
        }

        // Upload to backend
        const response = await apiService.uploadFile(file);
        
        setUploadProgress(100);

        // Update file with real data from backend
        setFiles(prev => prev.map(f => 
          f.id === tempFile.id 
            ? {
                ...response.file,
                status: 'completed' as const,
                extractedText: `Successfully uploaded ${response.file.filename}`,
                entities: ['Document', 'Policy', 'Analysis Ready']
              }
            : f
        ));

        toast({
          title: "Upload Successful",
          description: `${file.name} has been uploaded successfully`,
        });

      } catch (error) {
        console.error('Upload failed:', error);
        
        // Update file status to error
        setFiles(prev => prev.map(f => 
          f.filename === file.name 
            ? { ...f, status: 'error' as const }
            : f
        ));

        toast({
          title: "Upload Failed",
          description: error instanceof Error ? error.message : "Failed to upload file",
          variant: "destructive",
        });
      }
    }

    setIsLoading(false);
    setUploadProgress(0);
  };

  const removeFile = (fileId: number) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const getFileIcon = (fileType: string) => {
    if (fileType.includes('pdf')) return <File className="w-5 h-5 text-red-400" />;
    if (fileType.includes('word') || fileType.includes('doc')) return <FileText className="w-5 h-5 text-blue-400" />;
    if (fileType.includes('email') || fileType.includes('eml')) return <Mail className="w-5 h-5 text-green-400" />;
    return <FileText className="w-5 h-5 text-gray-400" />;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'error': return <AlertCircle className="w-4 h-4 text-red-400" />;
      default: return <Brain className="w-4 h-4 text-primary animate-ai-pulse" />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <section className="py-20 px-6 bg-background/30">
      <div className="container mx-auto max-w-4xl">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-primary">
              Document Intelligence Hub
            </span>
          </h2>
          <p className="text-xl text-muted-foreground">
            Upload policy documents, contracts, and emails for AI-powered analysis
          </p>
        </div>

        {/* Upload Area */}
        <Card 
          className={`ai-card-glow p-8 mb-8 transition-all duration-300 ${
            isDragOver ? 'border-primary/60 bg-primary/5' : ''
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
                <Upload className="w-8 h-8 text-primary" />
              </div>
            </div>
            
            <div>
              <h3 className="text-xl font-semibold mb-2">Upload Documents</h3>
              <p className="text-muted-foreground mb-4">
                Drag & drop your files here, or click to browse
              </p>
              
              <div className="flex flex-wrap justify-center gap-2 mb-4">
                {[
                  { icon: <File className="w-4 h-4" />, label: 'PDF', color: 'text-red-400' },
                  { icon: <FileText className="w-4 h-4" />, label: 'Word', color: 'text-blue-400' },
                  { icon: <Mail className="w-4 h-4" />, label: 'Email', color: 'text-green-400' }
                ].map((format, index) => (
                  <Badge key={index} variant="outline" className="border-border/50">
                    <span className={format.color}>{format.icon}</span>
                    <span className="ml-1">{format.label}</span>
                  </Badge>
                ))}
              </div>
            </div>

            <div className="flex justify-center">
              <Button className="btn-ai-primary relative">
                <input
                  type="file"
                  multiple
                  accept=".pdf,.doc,.docx,.txt,.eml"
                  onChange={handleFileSelect}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                Select Files
                <Upload className="w-4 h-4 ml-2" />
              </Button>
            </div>

            {uploadProgress > 0 && uploadProgress < 100 && (
              <div className="space-y-2">
                <Progress value={uploadProgress} className="h-2" />
                <p className="text-sm text-muted-foreground">
                  Uploading and processing... {uploadProgress}%
                </p>
              </div>
            )}
          </div>
        </Card>

        {/* Uploaded Files */}
        {files.length > 0 && (
          <Card className="ai-card p-6">
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Brain className="w-5 h-5 text-primary" />
              Processed Documents ({files.length})
            </h3>
            
            <div className="space-y-4">
              {files.map((file) => (
                <div key={file.id} className="ai-card p-4 hover:bg-background/20 transition-colors">
                  <div className="flex items-start justify-between">
                                            <div className="flex items-start gap-3 flex-1">
                      {getFileIcon(file.file_type)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium truncate">{file.filename}</h4>
                          {getStatusIcon(file.status)}
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground mb-2">
                          <span>{file.file_type.toUpperCase()}</span>
                          <Badge variant="outline" className="text-xs">
                            {file.status}
                          </Badge>
                        </div>
                        
                        {file.extractedText && (
                          <p className="text-sm text-muted-foreground mb-2">
                            {file.extractedText}
                          </p>
                        )}
                        
                        {file.entities && (
                          <div className="flex flex-wrap gap-1">
                            {file.entities.map((entity, index) => (
                              <Badge key={index} variant="secondary" className="text-xs">
                                {entity}
                              </Badge>
                            ))}
                          </div>
                        )}
                        
                        {/* Embeddings Generator */}
                        {file.status === 'completed' && (
                          <div className="mt-3">
                            <EmbeddingsGenerator 
                              file={file}
                              onEmbeddingsGenerated={() => {
                                // Refresh files or update status
                                loadUserFiles();
                              }}
                            />
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(file.id)}
                      className="text-muted-foreground hover:text-destructive"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
            
            {files.some(f => f.status === 'completed') && (
              <div className="mt-6 p-4 bg-primary/10 rounded-lg border border-primary/20">
                <div className="flex items-center gap-2 text-primary mb-2">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-medium">Documents Ready for Analysis</span>
                </div>
                <p className="text-sm text-muted-foreground mb-4">
                  Your documents have been processed and are now available for AI-powered query analysis. 
                  Click below to proceed to the query interface.
                </p>
                <Button 
                  className="btn-ai-primary w-full"
                  onClick={() => window.location.href = '/query'}
                >
                  Proceed to Query Interface
                  <Brain className="w-4 h-4 ml-2" />
                </Button>
              </div>
            )}
          </Card>
        )}
      </div>
    </section>
  );
};