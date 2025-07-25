import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, 
  FileSearch, 
  Zap, 
  Shield, 
  Target, 
  BarChart3,
  MessageSquare,
  Database,
  CheckCircle
} from 'lucide-react';

export const Features = () => {
  const mainFeatures = [
    {
      icon: Brain,
      title: 'LLM-Powered Analysis',
      description: 'Advanced language models process natural language queries with semantic understanding, not just keyword matching.',
      color: 'text-primary',
      benefits: ['Semantic Understanding', 'Context Awareness', 'Multilingual Support']
    },
    {
      icon: FileSearch,
      title: 'Smart Document Retrieval',
      description: 'Intelligent search through policy documents, contracts, and emails to find relevant clauses and information.',
      color: 'text-accent',
      benefits: ['PDF Processing', 'Word Documents', 'Email Analysis']
    },
    {
      icon: Target,
      title: 'Precise Decision Making',
      description: 'Evaluate retrieved information to determine accurate decisions like approval status or payout amounts.',
      color: 'text-primary-glow',
      benefits: ['Rule-based Logic', 'Confidence Scoring', 'Audit Trail']
    },
    {
      icon: Zap,
      title: 'Real-time Processing',
      description: 'Get instant responses with structured JSON output including decisions, amounts, and detailed justifications.',
      color: 'text-accent',
      benefits: ['Sub-3s Response', 'Structured Output', 'API Ready']
    }
  ];

  const capabilities = [
    {
      icon: MessageSquare,
      title: 'Natural Language Input',
      description: 'Process vague, incomplete, or plain English queries effectively'
    },
    {
      icon: Database,
      title: 'Multi-format Support',
      description: 'Handle PDFs, Word files, emails, and unstructured documents'
    },
    {
      icon: Shield,
      title: 'Explainable AI',
      description: 'Reference exact clauses and provide transparent reasoning'
    },
    {
      icon: BarChart3,
      title: 'Confidence Scoring',
      description: 'Quantify decision confidence with accuracy metrics'
    }
  ];

  const useCases = [
    {
      domain: 'Insurance',
      examples: ['Claim Processing', 'Policy Validation', 'Risk Assessment'],
      color: 'border-blue-500/30 text-blue-400'
    },
    {
      domain: 'Legal',
      examples: ['Contract Analysis', 'Compliance Checking', 'Case Research'],
      color: 'border-purple-500/30 text-purple-400'
    },
    {
      domain: 'HR',
      examples: ['Policy Queries', 'Benefits Analysis', 'Compliance Audits'],
      color: 'border-green-500/30 text-green-400'
    },
    {
      domain: 'Finance',
      examples: ['Loan Processing', 'Credit Analysis', 'Regulatory Compliance'],
      color: 'border-yellow-500/30 text-yellow-400'
    }
  ];

  return (
    <section className="py-20 px-6">
      <div className="container mx-auto">
        
        {/* Main Features */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-accent to-primary-glow">
              Intelligent Document Processing
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Advanced AI capabilities designed for complex document analysis and decision-making processes
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8 mb-20">
          {mainFeatures.map((feature, index) => (
            <Card key={index} className="ai-card-glow p-6 element-3d">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-background/50 rounded-lg flex items-center justify-center">
                    <feature.icon className={`w-6 h-6 ${feature.color}`} />
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground mb-4">{feature.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {feature.benefits.map((benefit, idx) => (
                      <Badge key={idx} variant="outline" className="text-xs border-border/50">
                        <CheckCircle className="w-3 h-3 mr-1 text-green-400" />
                        {benefit}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Core Capabilities */}
        <div className="mb-20">
          <h3 className="text-3xl font-bold text-center mb-12">Core Capabilities</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {capabilities.map((capability, index) => (
              <Card key={index} className="ai-card p-6 text-center hover:scale-105 transition-transform">
                <capability.icon className="w-8 h-8 text-primary mx-auto mb-4" />
                <h4 className="font-semibold mb-2">{capability.title}</h4>
                <p className="text-sm text-muted-foreground">{capability.description}</p>
              </Card>
            ))}
          </div>
        </div>

        {/* Use Cases */}
        <div className="mb-20">
          <h3 className="text-3xl font-bold text-center mb-12">Industry Applications</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {useCases.map((useCase, index) => (
              <Card key={index} className={`ai-card p-6 border ${useCase.color}`}>
                <h4 className={`font-semibold mb-4 ${useCase.color.split(' ')[1]}`}>
                  {useCase.domain}
                </h4>
                <div className="space-y-2">
                  {useCase.examples.map((example, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-sm">
                      <div className="w-1 h-1 bg-current rounded-full" />
                      <span className="text-muted-foreground">{example}</span>
                    </div>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Sample Query Flow */}
        <Card className="ai-card-glow p-8">
          <h3 className="text-2xl font-bold text-center mb-8">Sample Query Processing Flow</h3>
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <MessageSquare className="w-8 h-8 text-primary" />
              </div>
              <h4 className="font-semibold mb-2">Input Query</h4>
              <p className="text-sm text-muted-foreground mb-4">
                "46M, knee surgery, Pune, 3-month policy"
              </p>
              <Badge variant="outline" className="text-xs">Natural Language</Badge>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Brain className="w-8 h-8 text-accent" />
              </div>
              <h4 className="font-semibold mb-2">AI Processing</h4>
              <p className="text-sm text-muted-foreground mb-4">
                Parse entities, search documents, evaluate rules
              </p>
              <Badge variant="outline" className="text-xs">Semantic Analysis</Badge>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-primary-glow/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-green-400" />
              </div>
              <h4 className="font-semibold mb-2">Structured Output</h4>
              <p className="text-sm text-muted-foreground mb-4">
                Decision: Approved, Amount: ₹85,000
              </p>
              <Badge variant="outline" className="text-xs">JSON Response</Badge>
            </div>
          </div>
        </Card>
      </div>
    </section>
  );
};