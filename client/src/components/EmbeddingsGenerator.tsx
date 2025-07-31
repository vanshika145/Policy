import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { apiService, UploadedFile, EmbeddingsResponse } from '@/services/api';
import { 
  Brain, 
  Loader2, 
  CheckCircle, 
  AlertCircle,
  Play,
  Search
} from 'lucide-react';

interface EmbeddingsGeneratorProps {
  file: UploadedFile;
  onEmbeddingsGenerated?: () => void;
}

export const EmbeddingsGenerator: React.FC<EmbeddingsGeneratorProps> = ({ 
  file, 
  onEmbeddingsGenerated 
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [status, setStatus] = useState<'idle' | 'processing' | 'completed' | 'failed'>('idle');
  const [embeddingsResponse, setEmbeddingsResponse] = useState<EmbeddingsResponse | null>(null);
  const { toast } = useToast();

  const handleGenerateEmbeddings = async () => {
    if (isGenerating) return;

    try {
      setIsGenerating(true);
      setStatus('processing');

      // Check if file type is supported
      const supportedTypes = ['pdf', 'docx', 'doc'];
      if (!supportedTypes.includes(file.file_type.toLowerCase())) {
        toast({
          title: "Unsupported File Type",
          description: "Only PDF and Word documents are supported for embeddings generation.",
          variant: "destructive",
        });
        return;
      }

      // Generate embeddings
      const response = await apiService.generateEmbeddings(file.id);
      setEmbeddingsResponse(response);
      
      if (response.success) {
        setStatus('completed');
        toast({
          title: "Embeddings Generation Started",
          description: "Your document is being processed in the background. This may take a few minutes.",
        });
        
        // Poll for status updates
        pollEmbeddingsStatus(file.id);
        
        if (onEmbeddingsGenerated) {
          onEmbeddingsGenerated();
        }
      } else {
        setStatus('failed');
        toast({
          title: "Generation Failed",
          description: response.message || "Failed to start embeddings generation",
          variant: "destructive",
        });
      }

    } catch (error) {
      setStatus('failed');
      console.error('Embeddings generation failed:', error);
      toast({
        title: "Generation Failed",
        description: error instanceof Error ? error.message : "Failed to generate embeddings",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const pollEmbeddingsStatus = async (fileId: number) => {
    const maxAttempts = 30; // 5 minutes with 10-second intervals
    let attempts = 0;

    const poll = async () => {
      try {
        const statusResponse = await apiService.getEmbeddingsStatus(fileId);
        setEmbeddingsResponse(statusResponse);

        if (statusResponse.status === 'completed') {
          setStatus('completed');
          toast({
            title: "Embeddings Generated",
            description: "Your document has been successfully processed and is ready for AI analysis.",
          });
          return;
        } else if (statusResponse.status === 'failed') {
          setStatus('failed');
          toast({
            title: "Generation Failed",
            description: "Failed to generate embeddings for your document.",
            variant: "destructive",
          });
          return;
        }

        // Continue polling
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 10000); // Poll every 10 seconds
        } else {
          setStatus('failed');
          toast({
            title: "Generation Timeout",
            description: "Embeddings generation is taking longer than expected. Please try again later.",
            variant: "destructive",
          });
        }
      } catch (error) {
        console.error('Status polling failed:', error);
        setStatus('failed');
      }
    };

    // Start polling after 10 seconds
    setTimeout(poll, 10000);
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'processing':
        return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Brain className="w-4 h-4" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'processing':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'processing':
        return 'Processing...';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      default:
        return 'Ready to Generate';
    }
  };

  return (
    <Card className="p-4 border-l-4 border-l-primary">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <span className="font-medium">AI Embeddings</span>
          </div>
          
          <Badge className={`${getStatusColor()} text-xs`}>
            {getStatusText()}
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          {status === 'idle' && (
            <Button
              onClick={handleGenerateEmbeddings}
              disabled={isGenerating}
              size="sm"
              className="btn-ai-primary"
            >
              <Play className="w-4 h-4 mr-2" />
              Generate
            </Button>
          )}
          
          {status === 'completed' && (
            <Button
              onClick={() => window.location.href = '/query'}
              size="sm"
              variant="outline"
              className="btn-ai-secondary"
            >
              <Search className="w-4 h-4 mr-2" />
              Query
            </Button>
          )}
        </div>
      </div>

      {status === 'processing' && (
        <div className="mt-3 p-3 bg-blue-50 rounded-lg">
          <div className="flex items-center gap-2 text-sm text-blue-700">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Processing document and generating AI embeddings...</span>
          </div>
          <p className="text-xs text-blue-600 mt-1">
            This may take a few minutes for large documents
          </p>
        </div>
      )}

      {status === 'completed' && (
        <div className="mt-3 p-3 bg-green-50 rounded-lg">
          <div className="flex items-center gap-2 text-sm text-green-700">
            <CheckCircle className="w-4 h-4" />
            <span>Document processed successfully!</span>
          </div>
          <p className="text-xs text-green-600 mt-1">
            Your document is now ready for AI-powered queries
          </p>
        </div>
      )}

      {status === 'failed' && (
        <div className="mt-3 p-3 bg-red-50 rounded-lg">
          <div className="flex items-center gap-2 text-sm text-red-700">
            <AlertCircle className="w-4 h-4" />
            <span>Processing failed</span>
          </div>
          <p className="text-xs text-red-600 mt-1">
            Please try again or contact support if the issue persists
          </p>
        </div>
      )}
    </Card>
  );
};