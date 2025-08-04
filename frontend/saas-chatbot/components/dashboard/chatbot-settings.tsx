'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Settings, Bot, Palette, Save, AlertTriangle, FileText, Upload, X, CheckCircle, AlertCircle } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { apiService } from '@/lib/api';
import { documentService } from '@/lib/api/documents';
import { useDropzone } from 'react-dropzone';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';

interface ChatbotSettingsProps {
  chatbot: any;
}

interface UploadFile {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  error?: string;
}

export function ChatbotSettings({ chatbot }: ChatbotSettingsProps) {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [documents, setDocuments] = useState<any[]>([]);
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(false);
  
  const [settings, setSettings] = useState({
    name: chatbot?.name || '',
    description: chatbot?.description || '',
    system_prompt: chatbot?.system_prompt || '',
    model: chatbot?.model || 'llama-3.1-8b-instant',
    is_active: chatbot?.is_active ?? true,
    appearance_config: {
      theme: chatbot?.appearance_config?.theme || 'light',
      primaryColor: chatbot?.appearance_config?.primaryColor || '#3b82f6',
      position: chatbot?.appearance_config?.position || 'bottom-right',
      greetingMessage: chatbot?.appearance_config?.greetingMessage || 'Hello! How can I help you today?',
      botName: chatbot?.appearance_config?.botName || 'Assistant',
      showAvatar: chatbot?.appearance_config?.showAvatar ?? true,
      ...chatbot?.appearance_config
    },
    behavior_config: {
      enableVoice: chatbot?.behavior_config?.enableVoice ?? false,
      enableTypingIndicator: chatbot?.behavior_config?.enableTypingIndicator ?? true,
      enableEmoji: chatbot?.behavior_config?.enableEmoji ?? true,
      maxTokens: chatbot?.behavior_config?.maxTokens || 1000,
      temperature: chatbot?.behavior_config?.temperature || 0.7,
      ...chatbot?.behavior_config
    }
  });

  const loadDocuments = async () => {
    if (!chatbot?.id) return;
    
    console.log('📚 RAG DEBUG: Loading documents for chatbot:', chatbot.id);
    setIsLoadingDocuments(true);
    try {
      const docs = await documentService.getDocuments(chatbot.id);
      console.log('✅ RAG DEBUG: Documents loaded successfully:', {
        count: docs?.length || 0,
        documents: docs?.map(d => ({ 
          id: d.id, 
          filename: d.filename, 
          processed: d.processed, 
          fileType: d.file_type 
        })) || []
      });
      setDocuments(docs);
    } catch (error) {
      console.error('💥 RAG DEBUG: Failed to load documents:', error);
      toast({
        title: "Error",
        description: "Failed to load documents",
        variant: "destructive",
      });
    } finally {
      setIsLoadingDocuments(false);
    }
  };

  const handleSave = async () => {
    setIsLoading(true);
    try {
      console.log('💾 VOICE DEBUG: ==================== SAVING SETTINGS ====================');
      console.log('💾 VOICE DEBUG: Saving chatbot settings...');
      console.log('💾 VOICE DEBUG: Current settings state:', JSON.stringify(settings, null, 2));
      console.log('💾 VOICE DEBUG: Voice settings specifically:', {
        enableVoice: settings.behavior_config.enableVoice,
        behaviorConfigExists: !!settings.behavior_config,
        fullBehaviorConfig: settings.behavior_config
      });
      
      // Update chatbot settings via API
      const updateData = {
        name: settings.name,
        description: settings.description,
        system_prompt: settings.system_prompt,
        model: settings.model,
        is_active: settings.is_active,
        appearance_config: settings.appearance_config,
        behavior_config: settings.behavior_config
      };

      console.log('💾 VOICE DEBUG: Update data being sent to backend:', JSON.stringify(updateData, null, 2));
      console.log('💾 VOICE DEBUG: behavior_config in update data:', updateData.behavior_config);
      console.log('💾 VOICE DEBUG: enableVoice in update data:', updateData.behavior_config?.enableVoice);

      console.log('📡 VOICE DEBUG: Sending update request to backend...');
      console.log('🔄 EMBEDDING: Starting save with automatic embedding generation...');
      
      const response = await apiService.updateChatbot(chatbot.id, updateData);
      console.log('✅ VOICE DEBUG: Settings saved successfully');
      console.log('✅ VOICE DEBUG: Backend response:', response);
      
      // Handle embedding stats from response
      const embeddingStats = response.embedding_stats;
      console.log('📊 EMBEDDING: Processing results:', embeddingStats);
      
      if (embeddingStats) {
        if (embeddingStats.success) {
          const { processed_count, total_embeddings, message, already_processed } = embeddingStats;
          
          if (processed_count > 0) {
            // New documents were processed
            toast({
              title: "Settings Updated with Document Processing",
              description: `${message || `Processed ${processed_count} documents and generated ${total_embeddings} embeddings`}`,
            });
          } else if (already_processed && already_processed > 0) {
            // No new documents, but existing ones found
            toast({
              title: "Settings Updated",
              description: `Settings saved. ${embeddingStats.message || `${already_processed} documents already processed`}`,
            });
          } else {
            // No documents found
            toast({
              title: "Settings Updated",
              description: "Settings saved successfully. No documents found to process.",
            });
          }
        } else {
          // Embedding processing failed
          toast({
            title: "Settings Updated (Embedding Warning)",
            description: `Settings saved, but document processing failed: ${embeddingStats.error}`,
            variant: "destructive",
          });
        }
      } else {
        // No embedding stats (shouldn't happen with new implementation)
        toast({
          title: "Settings Updated",
          description: "Your chatbot settings have been saved successfully.",
        });
      }
      
      // Refresh documents list to show updated processing status
      if (embeddingStats && embeddingStats.processed_count > 0) {
        console.log('🔄 EMBEDDING: Refreshing documents list...');
        try {
          await loadDocuments();
        } catch (refreshError) {
          console.error('⚠️ EMBEDDING: Failed to refresh documents:', refreshError);
        }
      }
      
    } catch (error) {
      console.error('💥 RAG DEBUG: Settings save error:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to update settings. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const onDrop = (acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      status: 'pending' as const,
      progress: 0,
    }));
    setUploadFiles(prev => [...prev, ...newFiles]);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const removeFile = (index: number) => {
    setUploadFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUploadFiles = async () => {
    if (uploadFiles.length === 0 || !chatbot?.id) return;

    console.log('🚀 RAG DEBUG: Starting file upload process', {
      fileCount: uploadFiles.length,
      chatbotId: chatbot.id,
      files: uploadFiles.map(f => ({ name: f.file.name, size: f.file.size, type: f.file.type }))
    });

    setIsUploading(true);
    
    for (let i = 0; i < uploadFiles.length; i++) {
      const uploadFile = uploadFiles[i];
      
      console.log(`📁 RAG DEBUG: Processing file ${i + 1}/${uploadFiles.length}: ${uploadFile.file.name}`);
      
      setUploadFiles(prev => 
        prev.map((file, index) => 
          index === i ? { ...file, status: 'uploading' } : file
        )
      );

      try {
        console.log(`⬆️ RAG DEBUG: Uploading ${uploadFile.file.name} to backend...`);
        
        const result = await documentService.uploadDocument({
          file: uploadFile.file,
          chatbot_id: chatbot.id,
        });

        console.log(`✅ RAG DEBUG: Upload successful for ${uploadFile.file.name}`, result);

        setUploadFiles(prev => 
          prev.map((file, index) => 
            index === i ? { ...file, status: 'success', progress: 100 } : file
          )
        );
        
        console.log(`🔄 RAG DEBUG: Reloading documents list after successful upload...`);
        // Reload documents after successful upload
        await loadDocuments();
        console.log(`✅ RAG DEBUG: Documents list reloaded`);
      } catch (error) {
        console.error(`💥 RAG DEBUG: Upload failed for ${uploadFile.file.name}:`, error);
        
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

    console.log('🎉 RAG DEBUG: File upload process completed');
    
    // Trigger embedding generation for all uploaded documents
    if (uploadFiles.some(file => file.status === 'success') && chatbot?.id) {
      console.log('🧠 RAG DEBUG: Triggering embedding generation for uploaded documents...');
      try {
        const processingResult = await documentService.processDocuments(chatbot.id);
        console.log('✅ RAG DEBUG: Embedding generation completed:', processingResult);
        
        if (processingResult.success && processingResult.processed_count > 0) {
          toast({
            title: "Documents Processed",
            description: `Successfully processed ${processingResult.processed_count} documents with ${processingResult.total_embeddings} embeddings generated.`,
          });
        }
        
        // Reload documents to show updated processing status
        await loadDocuments();
      } catch (error) {
        console.error('💥 RAG DEBUG: Embedding generation failed:', error);
        toast({
          title: "Processing Warning",
          description: "Documents uploaded but embedding generation failed. You can retry later.",
          variant: "destructive",
        });
      }
    }
    
    setIsUploading(false);
    
    // Clear successful uploads after delay
    setTimeout(() => {
      setUploadFiles(prev => prev.filter(file => file.status !== 'success'));
    }, 3000);
  };

  const handleDeleteDocument = async (documentId: string) => {
    try {
      await documentService.deleteDocument(documentId);
      toast({
        title: "Document Deleted",
        description: "Document has been removed successfully.",
      });
      await loadDocuments();
    } catch (error) {
      console.error('❌ Failed to delete document:', error);
      toast({
        title: "Error",
        description: "Failed to delete document",
        variant: "destructive",
      });
    }
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

  // Load documents when component mounts or chatbot changes
  useState(() => {
    if (chatbot?.id) {
      loadDocuments();
    }
  });

  return (
    <div className="space-y-6">
      <Tabs defaultValue="general" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="general" className="flex items-center gap-2">
            <Bot className="h-4 w-4" />
            General
          </TabsTrigger>
          <TabsTrigger value="behavior" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Behavior
          </TabsTrigger>
          <TabsTrigger value="appearance" className="flex items-center gap-2">
            <Palette className="h-4 w-4" />
            Appearance
          </TabsTrigger>
          <TabsTrigger value="documents" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Documents
          </TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>General Settings</CardTitle>
              <CardDescription>
                Configure your chatbot's basic information and behavior.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Chatbot Name</Label>
                <Input
                  id="name"
                  value={settings.name}
                  onChange={(e) => setSettings({ ...settings, name: e.target.value })}
                  placeholder="My Chatbot"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={settings.description}
                  onChange={(e) => setSettings({ ...settings, description: e.target.value })}
                  placeholder="Describe what your chatbot does..."
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="system_prompt">System Prompt</Label>
                <Textarea
                  id="system_prompt"
                  value={settings.system_prompt}
                  onChange={(e) => setSettings({ ...settings, system_prompt: e.target.value })}
                  placeholder="You are a helpful assistant..."
                  rows={4}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="model">AI Model</Label>
                <Select
                  value={settings.model}
                  onValueChange={(value) => setSettings({ ...settings, model: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="llama-3.1-70b-versatile">Llama 3.1 70B (Versatile)</SelectItem>
                    <SelectItem value="llama-3.1-8b-instant">Llama 3.1 8B (Instant)</SelectItem>
                    <SelectItem value="llama3-8b-8192">Llama 3 8B</SelectItem>
                    <SelectItem value="llama3-70b-8192">Llama 3 70B</SelectItem>
                    <SelectItem value="gemma2-9b-it">Gemma 2 9B</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="space-y-1">
                  <div className="font-medium">Active Status</div>
                  <div className="text-sm text-muted-foreground">
                    Make chatbot available to users
                  </div>
                </div>
                <Switch
                  checked={settings.is_active}
                  onCheckedChange={(checked) => setSettings({ ...settings, is_active: checked })}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="behavior" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Behavior Configuration</CardTitle>
              <CardDescription>
                Configure how your chatbot responds and interacts with users.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="space-y-1">
                  <div className="font-medium">Voice Chat</div>
                  <div className="text-sm text-muted-foreground">
                    Enable speech-to-text and text-to-speech
                  </div>
                </div>
                <Switch
                  checked={settings.behavior_config.enableVoice}
                  onCheckedChange={(checked) => 
                    setSettings({
                      ...settings,
                      behavior_config: { ...settings.behavior_config, enableVoice: checked }
                    })
                  }
                />
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="space-y-1">
                  <div className="font-medium">Typing Indicator</div>
                  <div className="text-sm text-muted-foreground">
                    Show typing animation when bot is responding
                  </div>
                </div>
                <Switch
                  checked={settings.behavior_config.enableTypingIndicator}
                  onCheckedChange={(checked) => 
                    setSettings({
                      ...settings,
                      behavior_config: { ...settings.behavior_config, enableTypingIndicator: checked }
                    })
                  }
                />
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="space-y-1">
                  <div className="font-medium">Emoji Support</div>
                  <div className="text-sm text-muted-foreground">
                    Allow emojis in responses
                  </div>
                </div>
                <Switch
                  checked={settings.behavior_config.enableEmoji}
                  onCheckedChange={(checked) => 
                    setSettings({
                      ...settings,
                      behavior_config: { ...settings.behavior_config, enableEmoji: checked }
                    })
                  }
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="maxTokens">Max Tokens</Label>
                  <Input
                    id="maxTokens"
                    type="number"
                    value={settings.behavior_config.maxTokens}
                    onChange={(e) => 
                      setSettings({
                        ...settings,
                        behavior_config: { ...settings.behavior_config, maxTokens: parseInt(e.target.value) }
                      })
                    }
                    min="100"
                    max="4000"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="temperature">Temperature</Label>
                  <Input
                    id="temperature"
                    type="number"
                    step="0.1"
                    value={settings.behavior_config.temperature}
                    onChange={(e) => 
                      setSettings({
                        ...settings,
                        behavior_config: { ...settings.behavior_config, temperature: parseFloat(e.target.value) }
                      })
                    }
                    min="0"
                    max="2"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="appearance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Appearance Settings</CardTitle>
              <CardDescription>
                Customize how your chatbot looks and feels.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="botName">Bot Name</Label>
                  <Input
                    id="botName"
                    value={settings.appearance_config.botName}
                    onChange={(e) => 
                      setSettings({
                        ...settings,
                        appearance_config: { ...settings.appearance_config, botName: e.target.value }
                      })
                    }
                    placeholder="Assistant"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="theme">Theme</Label>
                  <Select
                    value={settings.appearance_config.theme}
                    onValueChange={(value) => 
                      setSettings({
                        ...settings,
                        appearance_config: { ...settings.appearance_config, theme: value }
                      })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">Light</SelectItem>
                      <SelectItem value="dark">Dark</SelectItem>
                      <SelectItem value="auto">Auto</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="greetingMessage">Greeting Message</Label>
                <Input
                  id="greetingMessage"
                  value={settings.appearance_config.greetingMessage}
                  onChange={(e) => 
                    setSettings({
                      ...settings,
                      appearance_config: { ...settings.appearance_config, greetingMessage: e.target.value }
                    })
                  }
                  placeholder="Hello! How can I help you today?"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="primaryColor">Primary Color</Label>
                <div className="flex items-center space-x-2">
                  <Input
                    id="primaryColor"
                    type="color"
                    value={settings.appearance_config.primaryColor}
                    onChange={(e) => 
                      setSettings({
                        ...settings,
                        appearance_config: { ...settings.appearance_config, primaryColor: e.target.value }
                      })
                    }
                    className="w-16 h-10"
                  />
                  <Input
                    value={settings.appearance_config.primaryColor}
                    onChange={(e) => 
                      setSettings({
                        ...settings,
                        appearance_config: { ...settings.appearance_config, primaryColor: e.target.value }
                      })
                    }
                    className="font-mono"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="position">Widget Position</Label>
                <Select
                  value={settings.appearance_config.position}
                  onValueChange={(value) => 
                    setSettings({
                      ...settings,
                      appearance_config: { ...settings.appearance_config, position: value }
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="bottom-right">Bottom Right</SelectItem>
                    <SelectItem value="bottom-left">Bottom Left</SelectItem>
                    <SelectItem value="top-right">Top Right</SelectItem>
                    <SelectItem value="top-left">Top Left</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="space-y-1">
                  <div className="font-medium">Show Avatar</div>
                  <div className="text-sm text-muted-foreground">
                    Display chatbot avatar in conversations
                  </div>
                </div>
                <Switch
                  checked={settings.appearance_config.showAvatar}
                  onCheckedChange={(checked) => 
                    setSettings({
                      ...settings,
                      appearance_config: { ...settings.appearance_config, showAvatar: checked }
                    })
                  }
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="documents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Document Management</CardTitle>
              <CardDescription>
                Upload and manage documents for your chatbot's knowledge base.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Upload Area */}
              <div>
                <Label className="text-sm font-medium mb-2 block">Upload Documents</Label>
                <div
                  {...getRootProps()}
                  className="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer hover:border-gray-400 transition-colors"
                >
                  <input {...getInputProps()} />
                  <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <div>
                    <p className="text-lg font-medium">
                      {isDragActive ? 'Drop files here' : 'Drop files or click to select'}
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">
                      Supports: PDF, TXT, MD, DOCX (max 10MB)
                    </p>
                  </div>
                </div>
              </div>

              {/* Upload Queue */}
              {uploadFiles.length > 0 && (
                <div className="space-y-3">
                  <h4 className="font-medium">Upload Queue ({uploadFiles.length})</h4>
                  <div className="space-y-2">
                    {uploadFiles.map((file, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div>{getStatusIcon(file.status)}</div>
                          <div>
                            <p className="font-medium text-sm">{file.file.name}</p>
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
                    ))}
                  </div>
                  <Button 
                    onClick={handleUploadFiles}
                    disabled={uploadFiles.length === 0 || isUploading}
                    className="w-full"
                  >
                    {isUploading ? 'Uploading...' : `Upload ${uploadFiles.length} file${uploadFiles.length > 1 ? 's' : ''}`}
                  </Button>
                </div>
              )}

              {/* Existing Documents */}
              <div className="space-y-3">
                <h4 className="font-medium">Uploaded Documents</h4>
                {isLoadingDocuments ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
                    <p className="text-sm text-muted-foreground mt-2">Loading documents...</p>
                  </div>
                ) : documents.length > 0 ? (
                  <div className="space-y-2">
                    {documents.map((doc) => (
                      <div key={doc.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <FileText className="h-5 w-5 text-gray-500" />
                          <div>
                            <p className="font-medium text-sm">{doc.filename}</p>
                            <div className="flex items-center space-x-3 text-xs text-muted-foreground">
                              <span>{doc.file_type?.toUpperCase()}</span>
                              <span>{formatFileSize(doc.file_size || 0)}</span>
                              <span>
                                {doc.processed ? (
                                  <Badge variant="secondary" className="text-green-600 bg-green-50">
                                    ✓ Embeddings Ready
                                  </Badge>
                                ) : (
                                  <Badge variant="outline" className="text-yellow-600">
                                    ⏳ Pending Processing
                                  </Badge>
                                )}
                              </span>
                            </div>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteDocument(doc.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 border rounded-lg">
                    <FileText className="mx-auto h-12 w-12 text-gray-400 mb-3" />
                    <p className="text-sm text-muted-foreground">No documents uploaded yet</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Upload documents to build your chatbot's knowledge base
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

      </Tabs>

      <div className="flex justify-end space-x-2 pt-4 border-t">
        <Button variant="outline" disabled={isLoading}>
          Cancel
        </Button>
        <Button onClick={handleSave} disabled={isLoading} className="flex items-center gap-2">
          <Save className="h-4 w-4" />
          {isLoading ? 'Saving & Processing Embeddings...' : 'Save Changes'}
        </Button>
        
        {/* Embedding Processing Status */}
        {isLoading && (
          <div className="mt-2 text-xs text-muted-foreground">
            <p>💡 Generating vector embeddings for uploaded documents...</p>
            <p>This ensures your RAG system has the latest content.</p>
          </div>
        )}
      </div>
    </div>
  );
}