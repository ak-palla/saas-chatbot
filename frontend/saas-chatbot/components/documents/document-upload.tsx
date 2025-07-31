'use client';

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { 
  Upload, 
  FileText, 
  X, 
  CheckCircle, 
  AlertCircle 
} from "lucide-react";
import { documentService } from "@/lib/api/documents";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useChatbots } from "@/lib/hooks/use-chatbots";
import { cn } from "@/lib/utils";

interface DocumentUploadProps {
  onClose: () => void;
}

interface UploadFile {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  error?: string;
}

export function DocumentUpload({ onClose }: DocumentUploadProps) {
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedChatbotId, setSelectedChatbotId] = useState<string>("");
  const { chatbots, loading: chatbotsLoading } = useChatbots();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      status: 'pending' as const,
      progress: 0,
    }));
    setUploadFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const removeFile = (index: number) => {
    setUploadFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUploadFiles = async () => {
    if (uploadFiles.length === 0 || !selectedChatbotId) return;

    setIsUploading(true);
    
    for (let i = 0; i < uploadFiles.length; i++) {
      const uploadFile = uploadFiles[i];
      
      setUploadFiles(prev => 
        prev.map((file, index) => 
          index === i ? { ...file, status: 'uploading' } : file
        )
      );

      try {
        await documentService.uploadDocument({
          file: uploadFile.file,
          chatbot_id: selectedChatbotId,
        });

        setUploadFiles(prev => 
          prev.map((file, index) => 
            index === i ? { ...file, status: 'success', progress: 100 } : file
          )
        );
      } catch (error) {
        setUploadFiles(prev => 
          prev.map((file, index) => 
            index === i ? { 
              ...file, 
              status: 'error', 
              error: error instanceof Error ? error.message : 'Upload failed' 
            } : file
          )
        );
      }
    }

    setIsUploading(false);
  };

  const getStatusIcon = (status: UploadFile['status']) => {
    switch (status) {
      case 'uploading':
        return <Upload className="h-4 w-4 animate-spin" />;
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  const getStatusBadge = (status: UploadFile['status']) => {
    switch (status) {
      case 'pending':
        return <Badge variant="secondary">Pending</Badge>;
      case 'uploading':
        return <Badge variant="outline">Uploading</Badge>;
      case 'success':
        return <Badge variant="default">Complete</Badge>;
      case 'error':
        return <Badge variant="destructive">Error</Badge>;
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
    <div className="space-y-6">
      <div className="space-y-4">
        <div>
          <label className="text-sm font-medium mb-2 block">Select Chatbot</label>
          <Select value={selectedChatbotId} onValueChange={setSelectedChatbotId}>
            <SelectTrigger>
              <SelectValue placeholder="Choose a chatbot..." />
            </SelectTrigger>
            <SelectContent>
              {chatbotsLoading ? (
                <SelectItem value="loading">Loading...</SelectItem>
              ) : chatbots?.length ? (
                chatbots.map((chatbot) => (
                  <SelectItem key={chatbot.id} value={chatbot.id}>
                    {chatbot.name}
                  </SelectItem>
                ))
              ) : (
                <SelectItem value="none">No chatbots available</SelectItem>
              )}
            </SelectContent>
          </Select>
        </div>

        <Card
          {...getRootProps()}
          className={cn(
            "border-2 border-dashed cursor-pointer transition-colors",
            isDragActive ? "border-blue-400 bg-blue-50" : "hover:border-gray-400",
            !selectedChatbotId && "opacity-50 cursor-not-allowed"
          )}
        >
          <CardContent className="p-6">
            <input {...getInputProps()} disabled={!selectedChatbotId} />
            <div className="text-center space-y-4">
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <div>
                <p className="text-lg font-medium">
                  {isDragActive ? 'Drop files here' : 'Drop files or click to select'}
                </p>
                <p className="text-sm text-muted-foreground">
                  Supports: PDF, TXT, MD, DOCX, PPTX (max 10MB)
                </p>
                {!selectedChatbotId && (
                  <p className="text-sm text-destructive mt-2">
                    Please select a chatbot first
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {uploadFiles.length > 0 && (
        <div className="space-y-4">
          <h3 className="font-medium">Files to upload ({uploadFiles.length})</h3>
          <div className="space-y-2">
            {uploadFiles.map((file, index) => (
              <Card key={index}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div>{getStatusIcon(file.status)}</div>
                      <div>
                        <p className="font-medium">{file.file.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {formatFileSize(file.file.size)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusBadge(file.status)}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(index)}
                        disabled={file.status === 'uploading'}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  
                  {file.status === 'uploading' && (
                    <div className="mt-2">
                      <Progress value={file.progress} className="w-full" />
                    </div>
                  )}
                  
                  {file.status === 'error' && file.error && (
                    <p className="mt-2 text-sm text-destructive">{file.error}</p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      <div className="flex justify-end space-x-2">
        <Button variant="outline" onClick={onClose}>Cancel</Button>
        <Button 
          onClick={handleUploadFiles} 
          disabled={uploadFiles.length === 0 || isUploading}
        >
          {isUploading ? 'Uploading...' : 'Upload All'}
        </Button>
      </div>
    </div>
  );
}


