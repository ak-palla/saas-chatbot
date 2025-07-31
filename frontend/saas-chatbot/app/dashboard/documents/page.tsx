'use client';

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DocumentsTable } from "@/components/documents/documents-table";
import { DocumentUpload } from "@/components/documents/document-upload";
import { Plus, Upload } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useChatbots } from "@/lib/hooks/use-chatbots";
import { Header } from "@/components/dashboard/header";

export default function DocumentsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [selectedChatbot, setSelectedChatbot] = useState("all");
  const { chatbots } = useChatbots();

  return (
    <div className="space-y-8">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <Header 
          title="Documents" 
          description="Manage your knowledge base documents for chatbot training"
        />
        <Button onClick={() => setShowUploadDialog(true)} className="self-start lg:self-auto">
          <Upload className="mr-2 h-4 w-4" />
          Upload Document
        </Button>
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <div className="flex-1">
          <Input
            placeholder="Search documents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full max-w-sm"
          />
        </div>
        <Select value={selectedChatbot} onValueChange={setSelectedChatbot}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Filter by chatbot" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Chatbots</SelectItem>
            {chatbots?.map((chatbot) => (
              <SelectItem key={chatbot.id} value={chatbot.id}>
                {chatbot.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <DocumentsTable searchTerm={searchTerm} chatbotId={selectedChatbot} />

      <Dialog open={showUploadDialog} onOpenChange={setShowUploadDialog}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Upload Documents</DialogTitle>
          </DialogHeader>
          <DocumentUpload onClose={() => setShowUploadDialog(false)} />
        </DialogContent>
      </Dialog>
    </div>
  );
}