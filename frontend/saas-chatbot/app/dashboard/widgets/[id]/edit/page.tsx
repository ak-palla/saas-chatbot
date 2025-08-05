'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { ArrowLeft, Save, Eye, Trash2, Copy, TestTube } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { Header } from '@/components/dashboard/header';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import Link from 'next/link';

interface WidgetConfiguration {
  id: string;
  chatbot_id: string;
  config_name: string;
  template_id?: string;
  custom_css: string;
  theme: string;
  position: string;
  primary_color: string;
  secondary_color: string;
  border_radius: number;
  auto_open: boolean;
  auto_open_delay: number;
  show_avatar: boolean;
  enable_sound: boolean;
  enable_typing_indicator: boolean;
  enable_file_upload: boolean;
  max_width: number;
  max_height: number;
  mobile_full_screen: boolean;
  z_index: number;
  deployment_status: string;
  created_at: string;
  updated_at: string;
}

export default function EditWidgetConfigPage() {
  const router = useRouter();
  const params = useParams();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState<WidgetConfiguration | null>(null);

  useEffect(() => {
    if (params.id) {
      fetchConfiguration(params.id as string);
    }
  }, [params.id]);

  const fetchConfiguration = async (configId: string) => {
    try {
      // First get the config to find the chatbot_id
      const response = await fetch(`/api/widgets/config/${configId}`);
      if (response.ok) {
        const data = await response.json();
        setConfig(data);
      } else {
        throw new Error('Configuration not found');
      }
    } catch (error) {
      console.error('Error fetching configuration:', error);
      toast({
        title: 'Error',
        description: 'Failed to load widget configuration',
        variant: 'destructive',
      });
      router.push('/dashboard/widgets');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!config) return;

    setSaving(true);
    try {
      const response = await fetch(`/api/widgets/${config.chatbot_id}/config/${config.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      if (response.ok) {
        toast({
          title: 'Success',
          description: 'Widget configuration updated successfully',
        });
      } else {
        throw new Error('Failed to update configuration');
      }
    } catch (error) {
      console.error('Error updating configuration:', error);
      toast({
        title: 'Error',
        description: 'Failed to update widget configuration',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!config) return;

    try {
      const response = await fetch(`/api/widgets/${config.chatbot_id}/config/${config.id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        toast({
          title: 'Success',
          description: 'Widget configuration deleted successfully',
        });
        router.push('/dashboard/widgets');
      } else {
        throw new Error('Failed to delete configuration');
      }
    } catch (error) {
      console.error('Error deleting configuration:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete widget configuration',
        variant: 'destructive',
      });
    }
  };

  const handleDuplicate = async () => {
    if (!config) return;

    try {
      const duplicateConfig = {
        ...config,
        config_name: `${config.config_name} (Copy)`,
        deployment_status: 'draft',
      };
      delete (duplicateConfig as any).id;
      delete (duplicateConfig as any).created_at;
      delete (duplicateConfig as any).updated_at;

      const response = await fetch(`/api/widgets/${config.chatbot_id}/config`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(duplicateConfig),
      });

      if (response.ok) {
        toast({
          title: 'Success',
          description: 'Widget configuration duplicated successfully',
        });
        router.push('/dashboard/widgets');
      } else {
        throw new Error('Failed to duplicate configuration');
      }
    } catch (error) {
      console.error('Error duplicating configuration:', error);
      toast({
        title: 'Error',
        description: 'Failed to duplicate widget configuration',
        variant: 'destructive',
      });
    }
  };

  const updateConfig = (key: string, value: any) => {
    if (!config) return;
    setConfig({ ...config, [key]: value });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'default';
      case 'draft': return 'secondary';
      case 'paused': return 'outline';
      case 'archived': return 'destructive';
      default: return 'secondary';
    }
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <Header title="Edit Widget Configuration" description="Modify your widget settings" />
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  if (!config) {
    return (
      <div className="space-y-8">
        <Header title="Configuration Not Found" description="The requested widget configuration could not be found" />
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <h3 className="text-lg font-medium mb-2">Configuration not found</h3>
            <p className="text-muted-foreground mb-4">The widget configuration you're looking for doesn't exist.</p>
            <Link href="/dashboard/widgets">
              <Button>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Widgets
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <Header 
        title={`Edit: ${config.config_name}`}
        description={`Last updated: ${new Date(config.updated_at).toLocaleDateString()}`}
        action={
          <div className="flex items-center space-x-2">
            <Badge variant={getStatusColor(config.deployment_status)}>
              {config.deployment_status}
            </Badge>
            <Link href="/dashboard/widgets">
              <Button variant="outline">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
            </Link>
            <Button onClick={handleDuplicate} variant="outline">
              <Copy className="h-4 w-4 mr-2" />
              Duplicate
            </Button>
            <Link href={`/dashboard/widgets/${config.id}/ab-test`}>
              <Button variant="outline">
                <TestTube className="h-4 w-4 mr-2" />
                A/B Test
              </Button>
            </Link>
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="destructive">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Delete Configuration</AlertDialogTitle>
                  <AlertDialogDescription>
                    Are you sure you want to delete this widget configuration? This action cannot be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
            <Button onClick={handleSave} disabled={saving}>
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Configuration Form */}
        <div className="lg:col-span-2 space-y-6">
          <Tabs defaultValue="general" className="space-y-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="general">General</TabsTrigger>
              <TabsTrigger value="appearance">Appearance</TabsTrigger>
              <TabsTrigger value="behavior">Behavior</TabsTrigger>
              <TabsTrigger value="advanced">Advanced</TabsTrigger>
            </TabsList>

            <TabsContent value="general" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Basic Configuration</CardTitle>
                  <CardDescription>Update the basic properties of your widget</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="config_name">Configuration Name</Label>
                    <Input
                      id="config_name"
                      value={config.config_name}
                      onChange={(e) => updateConfig('config_name', e.target.value)}
                      placeholder="Enter configuration name"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="deployment_status">Status</Label>
                    <Select value={config.deployment_status} onValueChange={(value) => updateConfig('deployment_status', value)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="draft">Draft</SelectItem>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="paused">Paused</SelectItem>
                        <SelectItem value="archived">Archived</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground">
                    <div>
                      <strong>Created:</strong> {new Date(config.created_at).toLocaleString()}
                    </div>
                    <div>
                      <strong>Updated:</strong> {new Date(config.updated_at).toLocaleString()}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="appearance" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Appearance Settings</CardTitle>
                  <CardDescription>Customize the visual appearance of your widget</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="theme">Theme</Label>
                      <Select value={config.theme} onValueChange={(value) => updateConfig('theme', value)}>
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

                    <div className="space-y-2">
                      <Label htmlFor="position">Position</Label>
                      <Select value={config.position} onValueChange={(value) => updateConfig('position', value)}>
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
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="primary_color">Primary Color</Label>
                      <div className="flex items-center space-x-2">
                        <Input
                          id="primary_color"
                          type="color"
                          value={config.primary_color}
                          onChange={(e) => updateConfig('primary_color', e.target.value)}
                          className="w-12 h-10 p-1"
                        />
                        <Input
                          value={config.primary_color}
                          onChange={(e) => updateConfig('primary_color', e.target.value)}
                          placeholder="#3b82f6"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="secondary_color">Secondary Color</Label>
                      <div className="flex items-center space-x-2">
                        <Input
                          id="secondary_color"
                          type="color"
                          value={config.secondary_color}
                          onChange={(e) => updateConfig('secondary_color', e.target.value)}
                          className="w-12 h-10 p-1"
                        />
                        <Input
                          value={config.secondary_color}
                          onChange={(e) => updateConfig('secondary_color', e.target.value)}
                          placeholder="#1f2937"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="border_radius">Border Radius: {config.border_radius}px</Label>
                    <Input
                      id="border_radius"
                      type="range"
                      min="0"
                      max="50"
                      value={config.border_radius}
                      onChange={(e) => updateConfig('border_radius', parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="custom_css">Custom CSS</Label>
                    <Textarea
                      id="custom_css"
                      value={config.custom_css}
                      onChange={(e) => updateConfig('custom_css', e.target.value)}
                      placeholder="/* Add your custom CSS here */"
                      rows={6}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="behavior" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Behavior Settings</CardTitle>
                  <CardDescription>Configure how your widget behaves</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="font-medium">Auto Open</div>
                      <div className="text-sm text-muted-foreground">Automatically open widget on page load</div>
                    </div>
                    <Switch
                      checked={config.auto_open}
                      onCheckedChange={(checked) => updateConfig('auto_open', checked)}
                    />
                  </div>

                  {config.auto_open && (
                    <div className="space-y-2">
                      <Label htmlFor="auto_open_delay">Auto Open Delay (ms)</Label>
                      <Input
                        id="auto_open_delay"
                        type="number"
                        value={config.auto_open_delay}
                        onChange={(e) => updateConfig('auto_open_delay', parseInt(e.target.value))}
                        min="0"
                        max="60000"
                      />
                    </div>
                  )}

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="font-medium">Show Avatar</div>
                      <div className="text-sm text-muted-foreground">Display bot avatar in messages</div>
                    </div>
                    <Switch
                      checked={config.show_avatar}
                      onCheckedChange={(checked) => updateConfig('show_avatar', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="font-medium">Enable Sound</div>
                      <div className="text-sm text-muted-foreground">Play notification sounds</div>
                    </div>
                    <Switch
                      checked={config.enable_sound}
                      onCheckedChange={(checked) => updateConfig('enable_sound', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="font-medium">Typing Indicator</div>
                      <div className="text-sm text-muted-foreground">Show typing indicator when bot is responding</div>
                    </div>
                    <Switch
                      checked={config.enable_typing_indicator}
                      onCheckedChange={(checked) => updateConfig('enable_typing_indicator', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="font-medium">File Upload</div>
                      <div className="text-sm text-muted-foreground">Allow users to upload files</div>
                    </div>
                    <Switch
                      checked={config.enable_file_upload}
                      onCheckedChange={(checked) => updateConfig('enable_file_upload', checked)}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="advanced" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Advanced Settings</CardTitle>
                  <CardDescription>Advanced configuration options</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="max_width">Max Width (px)</Label>
                      <Input
                        id="max_width"
                        type="number"
                        value={config.max_width}
                        onChange={(e) => updateConfig('max_width', parseInt(e.target.value))}
                        min="200"
                        max="800"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="max_height">Max Height (px)</Label>
                      <Input
                        id="max_height"
                        type="number"
                        value={config.max_height}
                        onChange={(e) => updateConfig('max_height', parseInt(e.target.value))}
                        min="300"
                        max="1000"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="z_index">Z-Index</Label>
                    <Input
                      id="z_index"
                      type="number"
                      value={config.z_index}
                      onChange={(e) => updateConfig('z_index', parseInt(e.target.value))}
                      min="1"
                      max="9999999"
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="font-medium">Mobile Full Screen</div>
                      <div className="text-sm text-muted-foreground">Use full screen on mobile devices</div>
                    </div>
                    <Switch
                      checked={config.mobile_full_screen}
                      onCheckedChange={(checked) => updateConfig('mobile_full_screen', checked)}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Preview Panel */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Eye className="h-5 w-5 mr-2" />
                Live Preview
              </CardTitle>
              <CardDescription>See how your widget will look</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-100 rounded-lg p-4 min-h-[300px] relative">
                <div className="text-center text-muted-foreground">
                  <Eye className="h-8 w-8 mx-auto mb-2" />
                  <p>Widget preview will be shown here</p>
                  <p className="text-sm">Theme: {config.theme}</p>
                  <p className="text-sm">Position: {config.position}</p>
                  <div className="flex items-center justify-center mt-2">
                    <div 
                      className="w-4 h-4 rounded-full mr-2"
                      style={{ backgroundColor: config.primary_color }}
                    />
                    <span className="text-sm">{config.primary_color}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Link href={`/dashboard/widgets/${config.id}/analytics`}>
                <Button variant="outline" className="w-full justify-start">
                  <Eye className="h-4 w-4 mr-2" />
                  View Analytics
                </Button>
              </Link>
              <Button 
                variant="outline" 
                className="w-full justify-start"
                onClick={() => {
                  const embedCode = `<script src="${process.env.NEXT_PUBLIC_WIDGET_URL || 'http://localhost:3000/widget/embed.js'}" data-chatbot-id="${config.chatbot_id}" data-config-id="${config.id}"></script>`;
                  navigator.clipboard.writeText(embedCode);
                  toast({
                    title: 'Copied!',
                    description: 'Embed code copied to clipboard',
                  });
                }}
              >
                <Copy className="h-4 w-4 mr-2" />
                Copy Embed Code
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
