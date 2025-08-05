'use client';

import { useState, useEffect } from 'react';
import { ArrowLeft, Download, Eye, Star, Filter, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { Header } from '@/components/dashboard/header';
import Link from 'next/link';

interface WidgetTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  css_template: string;
  config_template: Record<string, any>;
  preview_image_url?: string;
  is_premium: boolean;
  is_active: boolean;
  downloads_count: number;
  rating: number;
  created_at: string;
}

const categories = [
  { value: 'all', label: 'All Categories' },
  { value: 'corporate', label: 'Corporate' },
  { value: 'startup', label: 'Startup' },
  { value: 'ecommerce', label: 'E-commerce' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'education', label: 'Education' },
  { value: 'creative', label: 'Creative' },
  { value: 'minimal', label: 'Minimal' },
];

export default function WidgetTemplatesPage() {
  const [templates, setTemplates] = useState<WidgetTemplate[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<WidgetTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showPremiumOnly, setShowPremiumOnly] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchTemplates();
  }, []);

  useEffect(() => {
    filterTemplates();
  }, [templates, searchQuery, selectedCategory, showPremiumOnly]);

  const fetchTemplates = async () => {
    try {
      const response = await fetch('/api/widgets/templates');
      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
      toast({
        title: 'Error',
        description: 'Failed to load templates',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const filterTemplates = () => {
    let filtered = templates.filter(template => template.is_active);

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(template =>
        template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(template => template.category === selectedCategory);
    }

    // Premium filter
    if (showPremiumOnly) {
      filtered = filtered.filter(template => template.is_premium);
    }

    setFilteredTemplates(filtered);
  };

  const handleUseTemplate = async (template: WidgetTemplate) => {
    try {
      // Increment download count
      await fetch(`/api/widgets/templates/${template.id}/download`, {
        method: 'POST',
      });

      // Navigate to new widget page with template pre-selected
      const params = new URLSearchParams({
        template: template.id,
      });
      window.location.href = `/dashboard/widgets/new?${params.toString()}`;
    } catch (error) {
      console.error('Error using template:', error);
      toast({
        title: 'Error',
        description: 'Failed to use template',
        variant: 'destructive',
      });
    }
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${
          i < Math.floor(rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`}
      />
    ));
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <Header title="Widget Templates" description="Browse and use pre-built widget templates" />
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <Header 
        title="Widget Templates" 
        description="Browse and use pre-built widget templates to quickly customize your chatbot"
        action={
          <Link href="/dashboard/widgets">
            <Button variant="outline">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Widgets
            </Button>
          </Link>
        }
      />

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="h-5 w-5 mr-2" />
            Filter Templates
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Search templates..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {categories.map((category) => (
                  <SelectItem key={category.value} value={category.value}>
                    {category.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button
              variant={showPremiumOnly ? "default" : "outline"}
              onClick={() => setShowPremiumOnly(!showPremiumOnly)}
              className="w-full md:w-auto"
            >
              <Star className="h-4 w-4 mr-2" />
              Premium Only
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTemplates.map((template) => (
          <Card key={template.id} className="overflow-hidden hover:shadow-lg transition-shadow">
            <div className="aspect-video bg-gradient-to-br from-blue-50 to-indigo-100 relative">
              {template.preview_image_url ? (
                <img
                  src={template.preview_image_url}
                  alt={template.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <Eye className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">Preview</p>
                  </div>
                </div>
              )}
              {template.is_premium && (
                <Badge className="absolute top-2 right-2 bg-yellow-500">
                  <Star className="h-3 w-3 mr-1" />
                  Premium
                </Badge>
              )}
            </div>
            
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-lg">{template.name}</CardTitle>
                  <CardDescription className="mt-1">{template.description}</CardDescription>
                </div>
                <Badge variant="outline" className="ml-2">
                  {template.category}
                </Badge>
              </div>
            </CardHeader>
            
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <div className="flex items-center space-x-1">
                  {renderStars(template.rating)}
                  <span className="ml-1">({template.rating.toFixed(1)})</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Download className="h-4 w-4" />
                  <span>{template.downloads_count}</span>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Button 
                  className="flex-1"
                  onClick={() => handleUseTemplate(template)}
                >
                  Use Template
                </Button>
                <Button variant="outline" size="icon">
                  <Eye className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredTemplates.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Search className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No templates found</h3>
            <p className="text-muted-foreground mb-4">
              Try adjusting your search criteria or browse all categories.
            </p>
            <Button 
              variant="outline" 
              onClick={() => {
                setSearchQuery('');
                setSelectedCategory('all');
                setShowPremiumOnly(false);
              }}
            >
              Clear Filters
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Template Stats */}
      <Card>
        <CardHeader>
          <CardTitle>Template Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-primary">{templates.length}</div>
              <div className="text-sm text-muted-foreground">Total Templates</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-primary">
                {templates.filter(t => t.is_premium).length}
              </div>
              <div className="text-sm text-muted-foreground">Premium Templates</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-primary">
                {categories.length - 1}
              </div>
              <div className="text-sm text-muted-foreground">Categories</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-primary">
                {templates.reduce((sum, t) => sum + t.downloads_count, 0)}
              </div>
              <div className="text-sm text-muted-foreground">Total Downloads</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
