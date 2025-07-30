import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ListFilter, ArrowUpDown } from "lucide-react";

interface ChatbotFiltersProps {
  statusFilter: string;
  onStatusChange: (status: string) => void;
  sortBy: string;
  onSortChange: (sort: string) => void;
}

export function ChatbotFilters({
  statusFilter,
  onStatusChange,
  sortBy,
  onSortChange,
}: ChatbotFiltersProps) {
  return (
    <div className="flex items-center space-x-2">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm">
            <ListFilter className="mr-2 h-4 w-4" />
            Filter
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <DropdownMenuItem
            onClick={() => onStatusChange("all")}
            className={statusFilter === "all" ? "font-bold" : ""}
          >
            All Status
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={() => onStatusChange("active")}
            className={statusFilter === "active" ? "font-bold" : ""}
          >
            Active
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={() => onStatusChange("inactive")}
            className={statusFilter === "inactive" ? "font-bold" : ""}
          >
            Inactive
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={() => onStatusChange("draft")}
            className={statusFilter === "draft" ? "font-bold" : ""}
          >
            Draft
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm">
            <ArrowUpDown className="mr-2 h-4 w-4" />
            Sort
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <DropdownMenuItem
            onClick={() => onSortChange("createdAt")}
            className={sortBy === "createdAt" ? "font-bold" : ""}
          >
            Created Date
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={() => onSortChange("name")}
            className={sortBy === "name" ? "font-bold" : ""}
          >
            Name
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={() => onSortChange("conversations")}
            className={sortBy === "conversations" ? "font-bold" : ""}
          >
            Conversations
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={() => onSortChange("lastActivity")}
            className={sortBy === "lastActivity" ? "font-bold" : ""}
          >
            Last Activity
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}