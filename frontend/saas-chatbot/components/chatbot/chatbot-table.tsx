'use client';

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
  SortingState,
} from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { MoreHorizontal, ExternalLink, Copy, Trash2 } from "lucide-react";

interface Chatbot {
  id: string;
  name: string;
  status: "active" | "inactive" | "draft";
  model: string;
  conversations: number;
  documents: number;
  createdAt: string;
  lastActivity: string;
}

const mockChatbots: Chatbot[] = [
  {
    id: "1",
    name: "Customer Support Bot",
    status: "active",
    model: "GPT-4",
    conversations: 342,
    documents: 15,
    createdAt: "2024-01-15",
    lastActivity: "2 hours ago",
  },
  {
    id: "2",
    name: "Sales Assistant",
    status: "active",
    model: "GPT-3.5",
    conversations: 156,
    documents: 8,
    createdAt: "2024-01-10",
    lastActivity: "5 hours ago",
  },
  {
    id: "3",
    name: "FAQ Bot",
    status: "inactive",
    model: "GPT-3.5",
    conversations: 89,
    documents: 5,
    createdAt: "2024-01-05",
    lastActivity: "1 day ago",
  },
  {
    id: "4",
    name: "Product Guide",
    status: "draft",
    model: "GPT-4",
    conversations: 0,
    documents: 3,
    createdAt: "2024-01-20",
    lastActivity: "Never",
  },
];

interface ChatbotTableProps {
  searchTerm: string;
  statusFilter: string;
  sortBy: string;
}

export function ChatbotTable({ searchTerm, statusFilter, sortBy }: ChatbotTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [rowSelection, setRowSelection] = useState({});

  const columns: ColumnDef<Chatbot>[] = [
    {
      id: "select",
      header: ({ table }) => (
        <Checkbox
          checked={table.getIsAllPageRowsSelected()}
          onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
          aria-label="Select all"
        />
      ),
      cell: ({ row }) => (
        <Checkbox
          checked={row.getIsSelected()}
          onCheckedChange={(value) => row.toggleSelected(!!value)}
          aria-label="Select row"
        />
      ),
      enableSorting: false,
      enableHiding: false,
    },
    {
      accessorKey: "name",
      header: "Name",
      cell: ({ row }) => {
        const chatbot = row.original;
        return (
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600" />
            <div>
              <div className="font-medium">{chatbot.name}</div>
              <div className="text-sm text-muted-foreground">{chatbot.model}</div>
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => {
        const status = row.getValue("status") as string;
        return (
          <Badge
            variant={
              status === "active"
                ? "default"
                : status === "inactive"
                ? "secondary"
                : "outline"
            }
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </Badge>
        );
      },
    },
    {
      accessorKey: "conversations",
      header: "Conversations",
    },
    {
      accessorKey: "documents",
      header: "Documents",
    },
    {
      accessorKey: "lastActivity",
      header: "Last Activity",
    },
    {
      id: "actions",
      cell: ({ row }) => {
        const chatbot = row.original;
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                onClick={() => navigator.clipboard.writeText(chatbot.id)}
              >
                <ExternalLink className="mr-2 h-4 w-4" />
                View Details
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => navigator.clipboard.writeText(chatbot.id)}
              >
                <Copy className="mr-2 h-4 w-4" />
                Duplicate
              </DropdownMenuItem>
              <DropdownMenuItem className="text-destructive">
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];

  const table = useReactTable({
    data: mockChatbots,
    columns,
    state: {
      sorting,
      rowSelection,
      globalFilter: searchTerm,
    },
    onSortingChange: setSorting,
    onRowSelectionChange: setRowSelection,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <TableHead key={header.id}>
                  {header.isPlaceholder
                    ? null
                    : flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                data-state={row.getIsSelected() && "selected"}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length} className="h-24 text-center">
                No chatbots found.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}