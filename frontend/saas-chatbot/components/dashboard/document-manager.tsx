'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { FileText, Upload, Trash2, Download, Search, Filter } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

interface DocumentManagerProps {
  chatbot: any;
}

export function DocumentManager({ chatbot }: DocumentManagerProps) {
  const { toast } = useToast();
  const [isUploading, setIsUploading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Mock documents data - in real app, this would come from API
  const [documents] = useState([
    {
      id: '1',
      name: 'Product Catalog 2024.pdf',
      type: 'pdf',
      size: '2.4 MB',
      status: 'processed',
      uploadedAt: '2024-01-15T10:30:00Z',
      pages: 45,
    },
    {
      id: '2',
      name: 'FAQ Document.docx',
      type: 'docx',
      size: '856 KB',
      status: 'processed',
      uploadedAt: '2024-01-14T15:22:00Z',
      pages: 12,
    },
    {
      id: '3',
      name: 'Terms of Service.txt',
      type: 'txt',
      size: '12 KB',
      status: 'processing',
      uploadedAt: '2024-01-16T09:15:00Z',
      pages: 3,
    },
    {
      id: '4',
      name: 'User Manual.pdf',
      type: 'pdf',
      size: '3.2 MB',
      status: 'failed',
      uploadedAt: '2024-01-13T14:45:00Z',
      pages: 67,
    },
  ]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    try {
      // In a real app, this would upload to the API
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate upload
      
      toast({
        title: "File Uploaded",
        description: `Successfully uploaded ${files[0].name}`,
      });
    } catch (error) {
      toast({
        title: "Upload Failed",
        description: "Failed to upload file. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
      // Reset the input
      event.target.value = '';
    }
  };

  const handleDelete = async (documentId: string, documentName: string) => {
    try {
      // In a real app, this would call the API to delete the document
      await new Promise(resolve => setTimeout(resolve, 500));
      
      toast({
        title: "Document Deleted",
        description: `${documentName} has been deleted successfully.`,
      });
    } catch (error) {
      toast({
        title: "Delete Failed",
        description: "Failed to delete document. Please try again.",
        variant: "destructive",
      });
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'processed':
        return <Badge variant="default" className="bg-green-100 text-green-800 hover:bg-green-100">Processed</Badge>;
      case 'processing':
        return <Badge variant="default" className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">Processing</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  const getFileIcon = (type: string) => {
    return <FileText className="h-4 w-4" />;
  };

  const formatFileSize = (size: string) => {
    return size;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const filteredDocuments = documents.filter(doc =>
    doc.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload Documents
          </CardTitle>
          <CardDescription>
            Upload documents to train your chatbot. Supported formats: PDF, DOCX, TXT, HTML, Markdown
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6 text-center">
            <Upload className="mx-auto h-12 w-12 text-muted-foreground/50 mb-4" />
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                Drag and drop files here, or click to select
              </p>
              <input
                type="file"
                multiple
                accept=".pdf,.docx,.txt,.html,.md"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
                disabled={isUploading}
              />
              <Button
                variant="outline"
                onClick={() => document.getElementById('file-upload')?.click()}
                disabled={isUploading}
                className="mt-2"
              >
                {isUploading ? 'Uploading...' : 'Select Files'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Document Library
          </CardTitle>
          <CardDescription>
            Manage your uploaded documents and their processing status
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search documents..."
                className="pl-8"
              />
            </div>
            <Button variant="outline" size="sm">
              <Filter className="h-4 w-4 mr-2" />
              Filter
            </Button>
          </div>

          <div className="space-y-2">
            {filteredDocuments.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                {searchTerm ? 'No documents match your search.' : 'No documents uploaded yet.'}
              </div>
            ) : (
              filteredDocuments.map((document) => (
                <div
                  key={document.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    {getFileIcon(document.type)}
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">{document.name}</span>
                        {getStatusBadge(document.status)}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {formatFileSize(document.size)} • {document.pages} pages • Uploaded {formatDate(document.uploadedAt)}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm">
                      <Download className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(document.id, document.name)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>

          {filteredDocuments.length > 0 && (
            <div className="mt-4 pt-4 border-t text-sm text-muted-foreground">
              Total: {filteredDocuments.length} documents
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}