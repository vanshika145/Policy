import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
import { 
  Send, 
  Brain, 
  CheckCircle, 
  XCircle, 
  FileText, 
  Clock,
  DollarSign,
  MapPin,
  User,
  Calendar
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue
} from '@/components/ui/select';
import { useNavigate } from 'react-router-dom';

interface QueryResult {
  decision: 'approved' | 'rejected' | 'pending';
  amount?: number;
  justification: string;
  clauses: string[];
  confidence: number;
  processingTime: number;
  parsedQuery: {
    age?: number;
    procedure?: string;
    location?: string;
    policyDuration?: string;
    gender?: string;
  };
}

export const QueryInterface = () => {
  const [query, setQuery] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<QueryResult | null>(null);
  const { toast } = useToast();
  const [inputMode, setInputMode] = useState<'plain' | 'form'>('plain');
  // Structured form state
  const [form, setForm] = useState({
    age: '',
    gender: '',
    location: '',
    query: '',
    policyName: '',
    policyDuration: ''
  });

  const sampleQueries = [
    "46-year-old male, knee surgery in Pune, 3-month-old insurance policy",
    "Female, 32, dental treatment, Mumbai, 1-year policy",
    "Emergency surgery, 28M, Bangalore, 6-month policy, cardiac procedure"
  ];

  const navigate = useNavigate();

  const processQuery = async () => {
    if (!query.trim()) {
      toast({
        title: "Error",
        description: "Please enter a query to process",
        variant: "destructive"
      });
      return;
    }

    setIsProcessing(true);
    setProgress(0);
    setResult(null);

    // Simulate AI processing with realistic progress
    const steps = [
      { step: 'Parsing query...', progress: 20 },
      { step: 'Analyzing documents...', progress: 45 },
      { step: 'Semantic matching...', progress: 70 },
      { step: 'Evaluating clauses...', progress: 90 },
      { step: 'Generating response...', progress: 100 }
    ];

    for (const { step, progress: stepProgress } of steps) {
      await new Promise(resolve => setTimeout(resolve, 800));
      setProgress(stepProgress);
    }

    // Mock AI response based on query
    const mockResult: QueryResult = {
      decision: query.includes('knee surgery') ? 'approved' : 
                query.includes('dental') ? 'rejected' : 'pending',
      amount: query.includes('knee surgery') ? 85000 : undefined,
      justification: query.includes('knee surgery') 
        ? "Knee surgery is covered under the orthopedic procedures section of your policy. The procedure is approved as it meets all eligibility criteria."
        : query.includes('dental')
        ? "Dental treatments are excluded from your current policy tier. Consider upgrading to comprehensive coverage."
        : "Additional documentation required for final decision.",
      clauses: [
        "Section 4.2.1 - Orthopedic Procedures Coverage",
        "Section 2.1 - Policy Eligibility Criteria",
        "Section 7.3 - Geographical Coverage Areas"
      ],
      confidence: 94.7,
      processingTime: 2.3,
      parsedQuery: {
        age: query.includes('46') ? 46 : query.includes('32') ? 32 : query.includes('28') ? 28 : undefined,
        procedure: query.includes('knee surgery') ? 'Knee Surgery' : 
                  query.includes('dental') ? 'Dental Treatment' : 
                  query.includes('cardiac') ? 'Cardiac Procedure' : 'Unknown',
        location: query.includes('Pune') ? 'Pune' : 
                 query.includes('Mumbai') ? 'Mumbai' : 
                 query.includes('Bangalore') ? 'Bangalore' : 'Unknown',
        policyDuration: query.includes('3-month') ? '3 months' : 
                       query.includes('1-year') ? '1 year' : 
                       query.includes('6-month') ? '6 months' : 'Unknown',
        gender: query.includes('male') || query.includes('M') ? 'Male' : 
               query.includes('Female') ? 'Female' : 'Unknown'
      }
    };

    setResult(mockResult);
    setIsProcessing(false);

    toast({
      title: "Analysis Complete",
      description: `Query processed in ${mockResult.processingTime}s with ${mockResult.confidence}% confidence`,
    });

    // Navigate to results page after analysis
    navigate('/results');
  };

  const getDecisionIcon = (decision: string) => {
    switch (decision) {
      case 'approved': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'rejected': return <XCircle className="w-5 h-5 text-red-400" />;
      default: return <Clock className="w-5 h-5 text-yellow-400" />;
    }
  };

  const getDecisionColor = (decision: string) => {
    switch (decision) {
      case 'approved': return 'text-green-400 border-green-400/30';
      case 'rejected': return 'text-red-400 border-red-400/30';
      default: return 'text-yellow-400 border-yellow-400/30';
    }
  };

  return (
    <section className="py-20 px-6">
      <div className="container mx-auto max-w-4xl">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
              Natural Language Query Interface
            </span>
          </h2>
          <p className="text-xl text-muted-foreground">
            Enter your query in plain English or use the structured form to let our AI decode the relevant policy information
          </p>
        </div>
        {/* Toggle Tabs */}
        <div className="flex justify-center mb-8 gap-2">
          <button
            className={`px-6 py-2 rounded-l-lg font-semibold transition-colors ${inputMode === 'plain' ? 'bg-primary-glow text-white shadow-lg' : 'bg-background text-primary border border-primary'}`}
            onClick={() => setInputMode('plain')}
          >
            Plain Text
          </button>
          <button
            className={`px-6 py-2 rounded-r-lg font-semibold transition-colors ${inputMode === 'form' ? 'bg-primary-glow text-white shadow-lg' : 'bg-background text-primary border border-primary'}`}
            onClick={() => setInputMode('form')}
          >
            Form Fields
          </button>
        </div>
        {/* Conditional Rendering */}
        {inputMode === 'plain' ? (
          <Card className="ai-card-glow p-6 mb-8">
            <div className="space-y-4">
              <label className="text-sm font-medium flex items-center gap-2">
                <Brain className="w-4 h-4 text-primary" />
                Enter your query
              </label>
              <Textarea
                placeholder="e.g., 46-year-old male, knee surgery in Pune, 3-month-old insurance policy"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="min-h-[100px] bg-background/50 border-border/50 resize-none"
              />
              {/* Sample Queries */}
              <div className="flex flex-wrap gap-2">
                <span className="text-sm text-muted-foreground">Try these:</span>
                {sampleQueries.map((sample, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    className="text-xs h-auto py-1 px-2 btn-ai-secondary"
                    onClick={() => setQuery(sample)}
                  >
                    {sample.substring(0, 30)}...
                  </Button>
                ))}
              </div>
              {/* Process Button */}
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <FileText className="w-4 h-4" />
                  AI will analyze policy documents and provide structured response
                </div>
                <Button 
                  onClick={processQuery}
                  disabled={isProcessing}
                  className="btn-ai-primary"
                >
                  {isProcessing ? 'Processing...' : 'Analyze Query'}
                  <Send className="w-4 h-4 ml-2" />
                </Button>
              </div>
              {/* Progress Bar */}
              {isProcessing && (
                <div className="space-y-2">
                  <Progress value={progress} className="h-2" />
                  <div className="text-sm text-muted-foreground text-center">
                    Processing your query with AI semantic understanding...
                  </div>
                </div>
              )}
            </div>
          </Card>
        ) : (
          <Card className="ai-card-glow p-6 mb-8">
            <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <User className="w-5 h-5 text-primary" />
              Structured Query Form
            </h3>
            <form className="grid grid-cols-1 md:grid-cols-2 gap-6" onSubmit={e => { e.preventDefault(); /* handle form submit here */ }}>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Age</label>
                <Input
                  type="number"
                  placeholder="Enter age"
                  value={form.age}
                  onChange={e => setForm(f => ({ ...f, age: e.target.value }))}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Gender</label>
                <Select value={form.gender} onValueChange={val => setForm(f => ({ ...f, gender: val }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select gender" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="male">Male</SelectItem>
                    <SelectItem value="female">Female</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-slate-300 mb-2">Location</label>
                <Input
                  type="text"
                  placeholder="Enter city"
                  value={form.location}
                  onChange={e => setForm(f => ({ ...f, location: e.target.value }))}
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-slate-300 mb-2">Query</label>
                <Textarea
                  placeholder="Describe the condition or treatment"
                  value={form.query}
                  onChange={e => setForm(f => ({ ...f, query: e.target.value }))}
                  className="min-h-[80px]"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Policy Name</label>
                <Select value={form.policyName} onValueChange={val => setForm(f => ({ ...f, policyName: val }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select policy" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Basic Plan">Basic Plan</SelectItem>
                    <SelectItem value="Premium Plus">Premium Plus</SelectItem>
                    <SelectItem value="HealthFlex">HealthFlex</SelectItem>
                    <SelectItem value="Global Shield">Global Shield</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Policy Duration</label>
                <Select value={form.policyDuration} onValueChange={val => setForm(f => ({ ...f, policyDuration: val }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select duration" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="<1 month">Less than 1 month</SelectItem>
                    <SelectItem value="1-3 months">1–3 months</SelectItem>
                    <SelectItem value=">6 months">More than 6 months</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="md:col-span-2 flex justify-end">
                <Button type="submit" className="btn-ai-primary px-8 py-2 mt-2">Analyze Query</Button>
              </div>
            </form>
          </Card>
        )}
        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* (All result sections removed as requested) */}
          </div>
        )}
      </div>
    </section>
  );
};