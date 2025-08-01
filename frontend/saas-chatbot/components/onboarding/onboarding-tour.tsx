'use client';

import { useState, useEffect } from 'react';
import { X, ArrowRight, ArrowLeft, CheckCircle, Bot, Settings, BarChart3, Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  icon: React.ElementType;
  target?: string;
  action?: {
    text: string;
    href?: string;
    onClick?: () => void;
  };
}

const onboardingSteps: OnboardingStep[] = [
  {
    id: 'welcome',
    title: 'Welcome to ChatBot SaaS! 🎉',
    description: 'Let\'s get you started with creating your first AI chatbot. This quick tour will show you everything you need to know.',
    icon: Bot,
  },
  {
    id: 'create-chatbot',
    title: 'Create Your First Chatbot',
    description: 'Start by creating a chatbot with our easy 3-step process. You can customize everything from personality to appearance.',
    icon: Bot,
    action: {
      text: 'Create Chatbot',
      href: '/dashboard/chatbots/new',
    },
  },
  {
    id: 'upload-docs',
    title: 'Add Knowledge Base',
    description: 'Upload documents to give your chatbot specific knowledge about your business, products, or services.',
    icon: Upload,
    action: {
      text: 'Upload Documents',
      href: '/dashboard/documents',
    },
  },
  {
    id: 'customize',
    title: 'Customize Appearance',
    description: 'Make your chatbot match your brand with custom colors, positioning, and messaging.',
    icon: Settings,
  },
  {
    id: 'analytics',
    title: 'Track Performance',
    description: 'Monitor conversations, user engagement, and chatbot effectiveness with detailed analytics.',
    icon: BarChart3,
    action: {
      text: 'View Analytics',
      href: '/dashboard/analytics',
    },
  },
];

interface OnboardingTourProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
}

export function OnboardingTour({ isOpen, onClose, onComplete }: OnboardingTourProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      setCurrentStep(0);
      setIsCompleted(false);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const step = onboardingSteps[currentStep];
  const isLastStep = currentStep === onboardingSteps.length - 1;
  const isFirstStep = currentStep === 0;

  const handleNext = () => {
    if (isLastStep) {
      setIsCompleted(true);
      setTimeout(() => {
        onComplete();
      }, 1000);
    } else {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleSkip = () => {
    onClose();
  };

  const handleActionClick = () => {
    if (step.action?.href) {
      window.location.href = step.action.href;
    } else if (step.action?.onClick) {
      step.action.onClick();
    }
    onComplete();
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl mx-auto relative">
        <CardHeader className="text-center pb-4">
          <div className="flex items-center justify-between mb-4">
            <Badge variant="outline" className="bg-blue-50 dark:bg-blue-950/30 text-blue-700 dark:text-blue-300">
              Step {currentStep + 1} of {onboardingSteps.length}
            </Badge>
            <Button variant="ghost" size="sm" onClick={handleSkip}>
              <X className="w-4 h-4" />
            </Button>
          </div>
          
          {isCompleted ? (
            <div className="space-y-4">
              <div className="w-20 h-20 mx-auto bg-gradient-to-br from-green-500 to-green-600 rounded-full flex items-center justify-center">
                <CheckCircle className="h-10 w-10 text-white" />
              </div>
              <CardTitle className="text-2xl text-green-600">You're All Set! 🚀</CardTitle>
              <p className="text-muted-foreground">
                You've completed the onboarding tour. Ready to build amazing chatbots!
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="w-16 h-16 mx-auto bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center">
                <step.icon className="h-8 w-8 text-white" />
              </div>
              <CardTitle className="text-2xl">{step.title}</CardTitle>
              <p className="text-muted-foreground text-lg leading-relaxed">
                {step.description}
              </p>
            </div>
          )}
        </CardHeader>

        {!isCompleted && (
          <CardContent>
            {/* Progress Bar */}
            <div className="mb-6">
              <div className="flex items-center justify-between text-sm text-muted-foreground mb-2">
                <span>Progress</span>
                <span>{Math.round(((currentStep + 1) / onboardingSteps.length) * 100)}%</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${((currentStep + 1) / onboardingSteps.length) * 100}%` }}
                />
              </div>
            </div>

            {/* Navigation */}
            <div className="flex items-center justify-between">
              <div>
                {!isFirstStep && (
                  <Button variant="outline" onClick={handlePrevious}>
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Previous
                  </Button>
                )}
              </div>
              
              <div className="flex gap-3">
                {step.action && (
                  <Button variant="outline" onClick={handleActionClick}>
                    {step.action.text}
                  </Button>
                )}
                <Button onClick={handleNext} className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  {isLastStep ? 'Complete Tour' : 'Next'}
                  {!isLastStep && <ArrowRight className="w-4 h-4 ml-2" />}
                </Button>
              </div>
            </div>
          </CardContent>
        )}
      </Card>
    </div>
  );
}