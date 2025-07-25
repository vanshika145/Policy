import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Bot, Brain, FileSearch, Zap } from 'lucide-react';
import aiRobot from '@/assets/ai-robot.png';
import heroBg from '@/assets/hero-bg.png';
import Spline from '@splinetool/react-spline';

export const Hero = () => {
  const [isProcessing, setIsProcessing] = useState(false);

  const features = [
    { icon: Brain, label: 'AI-Powered Analysis', color: 'text-primary' },
    { icon: FileSearch, label: 'Document Intelligence', color: 'text-accent' },
    { icon: Zap, label: 'Instant Processing', color: 'text-primary-glow' },
    { icon: Bot, label: 'Smart Automation', color: 'text-accent' }
  ];

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `url(${heroBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      />
      
      {/* Floating Particles */}
      <div className="particles">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="particle"
            style={{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 8}s`,
              animationDuration: `${8 + Math.random() * 4}s`
            }}
          />
        ))}
      </div>

      <div className="relative z-10 container mx-auto px-6 pt-20 pb-16">
        <div className="grid lg:grid-cols-2 gap-12 items-center min-h-[80vh]">
          
          {/* Left Content */}
          <div className="space-y-8">
            <div className="space-y-4">
              <Badge variant="outline" className="border-primary/30 text-primary-glow px-4 py-2">
                <Bot className="w-4 h-4 mr-2" />
                AI-Powered Document Intelligence
              </Badge>
              
              <h1 className="text-5xl lg:text-6xl font-bold leading-tight">
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-primary-glow to-accent">
                  Policy Decoder
                </span>
                <br />
                <span className="text-foreground">AI System</span>
              </h1>
              
              <p className="text-xl text-muted-foreground leading-relaxed">
                Advanced LLM-powered system that processes natural language queries 
                and retrieves relevant information from complex policy documents, 
                contracts, and emails with <span className="text-primary-glow">semantic understanding</span>.
              </p>
            </div>

            {/* Feature Grid */}
            <div className="grid grid-cols-2 gap-4">
              {features.map((feature, index) => (
                <Card key={index} className="ai-card p-4 hover:scale-105 transition-transform">
                  <div className="flex items-center space-x-3">
                    <feature.icon className={`w-6 h-6 ${feature.color}`} />
                    <span className="text-sm font-medium">{feature.label}</span>
                  </div>
                </Card>
              ))}
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <Button 
                size="lg" 
                className="btn-ai-primary"
                onClick={() => window.location.href = '/documents'}
              >
                Start Analysis
                <Zap className="w-5 h-5 ml-2" />
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                className="btn-ai-secondary"
              >
                View Demo
                <FileSearch className="w-5 h-5 ml-2" />
              </Button>
            </div>
          </div>

          {/* Right side: Spline 3D Model with floating info cards and glow */}
          <div className="relative flex items-center justify-center bg-[#16213e] rounded-xl shadow-lg h-[64vw] w-[90vw] max-w-[400px] max-h-[400px] mx-auto md:mx-0 md:h-[400px] md:w-[400px]">
            {/* Spline 3D Model */}
            <Spline scene="https://prod.spline.design/JXsLzczqMz5zxmRq/scene.splinecode" className="h-[56vw] w-[80vw] max-w-[350px] max-h-[350px] md:h-[400px] md:w-[400px]" />
            {/* Floating Info Cards */}
            <div className="absolute left-2 top-2 p-2 bg-[#1a2747] rounded-lg shadow-lg text-center w-20 md:-left-8 md:top-12 md:p-4 md:w-24">
              <div className="text-lg md:text-2xl font-bold text-primary-glow">99.2%</div>
              <div className="text-xs md:text-sm text-muted-foreground">Accuracy</div>
            </div>
            <div className="absolute right-2 bottom-4 p-2 bg-[#1a2747] rounded-lg shadow-lg text-center w-24 md:-right-6 md:bottom-20 md:p-4 md:w-28">
              <div className="text-lg md:text-2xl font-bold text-accent">2.3s</div>
              <div className="text-xs md:text-sm text-muted-foreground">Response Time</div>
            </div>
            {/* Glow Effect */}
            <div className="absolute inset-0 bg-gradient-radial from-primary/20 via-transparent to-transparent blur-3xl pointer-events-none" />
          </div>
        </div>
      </div>
    </div>
  );
};