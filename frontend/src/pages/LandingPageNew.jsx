import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Zap, Code2, Layers, Database, Globe, Sparkles, 
  ChevronRight, ChevronDown, Play, Check, Star,
  Cpu, Bot, Rocket, Shield, CreditCard, Users,
  ArrowRight, Menu, X, Github, Mail
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Navigation Component
const Navigation = ({ onGetStarted }) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      isScrolled ? 'bg-gray-900/95 backdrop-blur-md shadow-lg' : 'bg-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">
              Melus<span className="text-cyan-400">AI</span>
            </span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-gray-300 hover:text-white transition-colors">Features</a>
            <a href="#how-it-works" className="text-gray-300 hover:text-white transition-colors">How it Works</a>
            <a href="#pricing" className="text-gray-300 hover:text-white transition-colors">Pricing</a>
            <Link to="/docs" className="text-gray-300 hover:text-white transition-colors">Docs</Link>
          </div>

          {/* CTA Buttons */}
          <div className="hidden md:flex items-center gap-4">
            <Link to="/login" className="text-gray-300 hover:text-white transition-colors">
              Sign In
            </Link>
            <button 
              onClick={onGetStarted}
              className="px-5 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-full font-medium hover:opacity-90 transition-opacity flex items-center gap-2"
            >
              Start Building <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button 
            className="md:hidden text-white"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-gray-900/95 backdrop-blur-md border-t border-gray-800">
            <div className="px-4 py-4 space-y-3">
              <a href="#features" className="block text-gray-300 hover:text-white py-2">Features</a>
              <a href="#how-it-works" className="block text-gray-300 hover:text-white py-2">How it Works</a>
              <a href="#pricing" className="block text-gray-300 hover:text-white py-2">Pricing</a>
              <Link to="/docs" className="block text-gray-300 hover:text-white py-2">Docs</Link>
              <hr className="border-gray-800" />
              <Link to="/login" className="block text-gray-300 hover:text-white py-2">Sign In</Link>
              <button 
                onClick={onGetStarted}
                className="w-full px-5 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-full font-medium"
              >
                Start Building
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

// Hero Section
const HeroSection = ({ onGetStarted }) => {
  const [prompt, setPrompt] = useState('');
  
  const examplePrompts = [
    "Build a SaaS dashboard with user analytics",
    "Create an e-commerce store with Stripe payments",
    "Design a community forum with real-time chat",
    "Build a project management tool like Trello"
  ];

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gray-950 pt-16">
      {/* Background Effects */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=%2260%22 height=%2260%22 viewBox=%220 0 60 60%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cg fill=%22none%22 fill-rule=%22evenodd%22%3E%3Cg fill=%22%239C92AC%22 fill-opacity=%220.05%22%3E%3Cpath d=%22M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-30" />
      </div>

      <div className="relative z-10 max-w-5xl mx-auto px-4 text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-full text-sm text-gray-300 mb-8">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <span>AI-Powered Development Platform</span>
          <span className="px-2 py-0.5 bg-cyan-500/20 text-cyan-400 rounded-full text-xs font-medium">NEW</span>
        </div>

        {/* Main Headline */}
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
          Build Full-Stack Apps
          <br />
          <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 bg-clip-text text-transparent">
            in Minutes, Not Months
          </span>
        </h1>

        <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
          Describe your idea in natural language. Our multi-agent AI system builds complete 
          web and mobile applications with frontend, backend, database, and deployment.
        </p>

        {/* Prompt Input */}
        <div className="max-w-2xl mx-auto mb-8">
          <div className="relative bg-gray-900/80 backdrop-blur-sm border border-gray-700 rounded-2xl p-2 focus-within:border-cyan-500/50 transition-colors">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe your app idea... e.g., 'Build a task management app with teams and real-time updates'"
              className="w-full bg-transparent text-white placeholder-gray-500 px-4 py-3 resize-none focus:outline-none text-lg"
              rows={2}
            />
            <div className="flex items-center justify-between px-2">
              <div className="flex items-center gap-2 text-gray-500 text-sm">
                <Cpu className="w-4 h-4" />
                <span>Powered by GPT-4o</span>
              </div>
              <button 
                onClick={onGetStarted}
                className="px-6 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-xl font-medium hover:opacity-90 transition-opacity flex items-center gap-2"
              >
                <Play className="w-4 h-4" /> Start Building
              </button>
            </div>
          </div>
        </div>

        {/* Example Prompts */}
        <div className="flex flex-wrap justify-center gap-2 mb-12">
          {examplePrompts.map((example, i) => (
            <button
              key={i}
              onClick={() => setPrompt(example)}
              className="px-4 py-2 bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 rounded-full text-sm text-gray-400 hover:text-white transition-colors"
            >
              {example}
            </button>
          ))}
        </div>

        {/* Stats */}
        <div className="flex flex-wrap justify-center gap-8 md:gap-16">
          {[
            { value: '50K+', label: 'Apps Built' },
            { value: '10x', label: 'Faster Development' },
            { value: '99%', label: 'Uptime' },
            { value: '4.9', label: 'User Rating', icon: Star }
          ].map((stat, i) => (
            <div key={i} className="text-center">
              <div className="text-3xl font-bold text-white flex items-center justify-center gap-1">
                {stat.value}
                {stat.icon && <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />}
              </div>
              <div className="text-gray-500 text-sm">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
        <ChevronDown className="w-6 h-6 text-gray-500" />
      </div>
    </section>
  );
};

// Features Section
const FeaturesSection = () => {
  const features = [
    {
      icon: Bot,
      title: 'Multi-Agent AI System',
      description: '6 specialized AI agents work together: Planner, Researcher, Developer, QA, Optimizer, and Cost Controller.',
      color: 'cyan'
    },
    {
      icon: Code2,
      title: 'Full-Stack Generation',
      description: 'Complete frontend (React/Vue), backend (FastAPI/Node), database schemas, and API integrations.',
      color: 'blue'
    },
    {
      icon: Layers,
      title: 'Live Preview & Iteration',
      description: 'See your app as it builds. Iterate with natural language commands to refine the output.',
      color: 'purple'
    },
    {
      icon: Database,
      title: 'Database & APIs',
      description: 'Automatic database design, migrations, and connections to external APIs like Stripe, Auth, etc.',
      color: 'green'
    },
    {
      icon: Rocket,
      title: 'One-Click Deploy',
      description: 'Deploy instantly to cloud hosting with SSL, CDN, and auto-scaling included.',
      color: 'orange'
    },
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'Built-in security best practices, rate limiting, and data protection compliance.',
      color: 'red'
    }
  ];

  const colorClasses = {
    cyan: 'from-cyan-500/20 to-cyan-500/5 border-cyan-500/20 text-cyan-400',
    blue: 'from-blue-500/20 to-blue-500/5 border-blue-500/20 text-blue-400',
    purple: 'from-purple-500/20 to-purple-500/5 border-purple-500/20 text-purple-400',
    green: 'from-green-500/20 to-green-500/5 border-green-500/20 text-green-400',
    orange: 'from-orange-500/20 to-orange-500/5 border-orange-500/20 text-orange-400',
    red: 'from-red-500/20 to-red-500/5 border-red-500/20 text-red-400'
  };

  return (
    <section id="features" className="py-24 bg-gray-950">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            Everything You Need to Build
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            From idea to production in minutes. Our AI handles the complexity so you can focus on what matters.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, i) => (
            <div 
              key={i}
              className={`p-6 rounded-2xl bg-gradient-to-b ${colorClasses[feature.color]} border backdrop-blur-sm hover:scale-105 transition-transform duration-300`}
            >
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colorClasses[feature.color]} flex items-center justify-center mb-4`}>
                <feature.icon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-gray-400">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// How It Works Section
const HowItWorksSection = () => {
  const steps = [
    {
      number: '01',
      title: 'Describe Your Idea',
      description: 'Tell our AI what you want to build in plain English. Be as detailed or brief as you like.',
      visual: 'prompt'
    },
    {
      number: '02',
      title: 'AI Plans & Builds',
      description: 'Our multi-agent system analyzes requirements, designs architecture, and generates code.',
      visual: 'agents'
    },
    {
      number: '03',
      title: 'Review & Iterate',
      description: 'Preview your app in real-time. Request changes and refinements through conversation.',
      visual: 'preview'
    },
    {
      number: '04',
      title: 'Deploy & Scale',
      description: 'One click to deploy. Your app goes live with hosting, SSL, and scaling handled.',
      visual: 'deploy'
    }
  ];

  return (
    <section id="how-it-works" className="py-24 bg-gray-900">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            How It Works
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            From concept to production in four simple steps
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, i) => (
            <div key={i} className="relative">
              {i < steps.length - 1 && (
                <div className="hidden lg:block absolute top-8 left-full w-full h-0.5 bg-gradient-to-r from-cyan-500/50 to-transparent" />
              )}
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 text-white text-2xl font-bold mb-4">
                  {step.number}
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">{step.title}</h3>
                <p className="text-gray-400">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Pricing Section
const PricingSection = ({ onGetStarted }) => {
  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: 'forever',
      description: 'Perfect for trying out MelusAI',
      credits: '1,000',
      features: [
        '1,000 credits/month',
        'Basic AI models',
        'Community support',
        'Export to GitHub',
        '3 active projects'
      ],
      cta: 'Get Started',
      highlighted: false
    },
    {
      name: 'Pro',
      price: '$29',
      period: '/month',
      description: 'For serious builders and teams',
      credits: '50,000',
      features: [
        '50,000 credits/month',
        'GPT-4o & advanced models',
        'Priority support',
        'Unlimited projects',
        'Custom deployments',
        'API access'
      ],
      cta: 'Start Pro Trial',
      highlighted: true
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      description: 'For organizations at scale',
      credits: 'Unlimited',
      features: [
        'Unlimited credits',
        'Custom AI models',
        'Dedicated support',
        'White-label option',
        'SLA guarantee',
        'On-premise deployment'
      ],
      cta: 'Contact Sales',
      highlighted: false
    }
  ];

  return (
    <section id="pricing" className="py-24 bg-gray-950">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Start free, scale as you grow. No hidden fees.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {plans.map((plan, i) => (
            <div 
              key={i}
              className={`relative p-8 rounded-2xl border ${
                plan.highlighted 
                  ? 'bg-gradient-to-b from-cyan-500/10 to-blue-600/10 border-cyan-500/50' 
                  : 'bg-gray-900/50 border-gray-800'
              }`}
            >
              {plan.highlighted && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full text-sm font-medium text-white">
                  Most Popular
                </div>
              )}
              
              <div className="text-center mb-6">
                <h3 className="text-xl font-semibold text-white mb-2">{plan.name}</h3>
                <div className="flex items-baseline justify-center gap-1">
                  <span className="text-4xl font-bold text-white">{plan.price}</span>
                  <span className="text-gray-400">{plan.period}</span>
                </div>
                <p className="text-gray-400 text-sm mt-2">{plan.description}</p>
              </div>

              <div className="mb-6 p-4 bg-gray-800/50 rounded-xl text-center">
                <span className="text-2xl font-bold text-cyan-400">{plan.credits}</span>
                <span className="text-gray-400 text-sm block">credits/month</span>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, j) => (
                  <li key={j} className="flex items-center gap-3 text-gray-300">
                    <Check className="w-5 h-5 text-cyan-400 flex-shrink-0" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <button 
                onClick={onGetStarted}
                className={`w-full py-3 rounded-xl font-medium transition-colors ${
                  plan.highlighted
                    ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white hover:opacity-90'
                    : 'bg-gray-800 text-white hover:bg-gray-700'
                }`}
              >
                {plan.cta}
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// FAQ Section
const FAQSection = () => {
  const [openIndex, setOpenIndex] = useState(null);
  
  const faqs = [
    {
      question: 'What can I build with MelusAI?',
      answer: 'You can build virtually any web or mobile application: SaaS platforms, e-commerce stores, dashboards, community sites, APIs, and more. Our AI handles frontend, backend, database, and integrations.'
    },
    {
      question: 'Do I need coding experience?',
      answer: 'No coding experience required! Simply describe what you want in plain language. However, developers can also use MelusAI to accelerate their workflow and get more complex projects done faster.'
    },
    {
      question: 'How do credits work?',
      answer: 'Credits are consumed based on the complexity of operations. Simple tasks use fewer credits, while complex AI operations use more. You can see credit usage in real-time in your dashboard.'
    },
    {
      question: 'Can I export my code?',
      answer: 'Yes! You own 100% of the code generated. Export to GitHub, download as a ZIP, or deploy directly to your own infrastructure.'
    },
    {
      question: 'What AI models do you use?',
      answer: 'We use a multi-model approach including GPT-4o for complex reasoning, with automatic fallbacks and cost optimization. Enterprise users can also bring their own models.'
    },
    {
      question: 'Is my data secure?',
      answer: 'Absolutely. We follow industry best practices including encryption at rest and in transit, SOC 2 compliance, and we never train on your data without explicit consent.'
    }
  ];

  return (
    <section className="py-24 bg-gray-900">
      <div className="max-w-3xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-xl text-gray-400">
            Everything you need to know about MelusAI
          </p>
        </div>

        <div className="space-y-4">
          {faqs.map((faq, i) => (
            <div 
              key={i}
              className="border border-gray-800 rounded-xl overflow-hidden"
            >
              <button
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                className="w-full px-6 py-4 flex items-center justify-between text-left bg-gray-900/50 hover:bg-gray-800/50 transition-colors"
              >
                <span className="text-lg font-medium text-white">{faq.question}</span>
                <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${openIndex === i ? 'rotate-180' : ''}`} />
              </button>
              {openIndex === i && (
                <div className="px-6 py-4 bg-gray-800/30 text-gray-400">
                  {faq.answer}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// CTA Section
const CTASection = ({ onGetStarted }) => {
  return (
    <section className="py-24 bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
      <div className="max-w-4xl mx-auto px-4 text-center">
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
          Ready to Build Your Next
          <br />
          <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            Big Idea?
          </span>
        </h2>
        <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
          Join thousands of builders who are shipping products faster with MelusAI.
          Start for free, no credit card required.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button 
            onClick={onGetStarted}
            className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-full font-medium text-lg hover:opacity-90 transition-opacity flex items-center gap-2"
          >
            Start Building for Free <ArrowRight className="w-5 h-5" />
          </button>
          <Link 
            to="/docs"
            className="px-8 py-4 bg-gray-800 hover:bg-gray-700 text-white rounded-full font-medium text-lg transition-colors"
          >
            Read Documentation
          </Link>
        </div>
      </div>
    </section>
  );
};

// Footer
const Footer = () => {
  const links = {
    Product: ['Features', 'Pricing', 'Integrations', 'Changelog', 'Roadmap'],
    Resources: ['Documentation', 'Tutorials', 'Blog', 'Case Studies', 'API Reference'],
    Company: ['About', 'Careers', 'Press', 'Contact', 'Partners'],
    Legal: ['Privacy Policy', 'Terms of Service', 'Cookie Policy', 'Security']
  };

  return (
    <footer className="bg-gray-950 border-t border-gray-800">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid md:grid-cols-2 lg:grid-cols-6 gap-8 mb-12">
          {/* Brand */}
          <div className="lg:col-span-2">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white">
                Melus<span className="text-cyan-400">AI</span>
              </span>
            </Link>
            <p className="text-gray-400 mb-4">
              Build full-stack applications in minutes with AI. 
              From idea to production, faster than ever.
            </p>
            <div className="flex gap-4">
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <Github className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Links */}
          {Object.entries(links).map(([category, items]) => (
            <div key={category}>
              <h4 className="font-semibold text-white mb-4">{category}</h4>
              <ul className="space-y-2">
                {items.map((item) => (
                  <li key={item}>
                    <a href="#" className="text-gray-400 hover:text-white transition-colors">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom */}
        <div className="flex flex-col md:flex-row items-center justify-between pt-8 border-t border-gray-800">
          <p className="text-gray-500 text-sm">
            © 2024 MelusAI. All rights reserved.
          </p>
          <div className="flex items-center gap-4 mt-4 md:mt-0">
            <span className="flex items-center gap-2 text-gray-500 text-sm">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              All systems operational
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};

// Main Landing Page Component
const LandingPageNew = () => {
  const navigate = useNavigate();
  const { user, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && user) {
      navigate('/home');
    }
  }, [user, isLoading, navigate]);

  const handleGetStarted = () => {
    navigate('/login');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950">
      <Navigation onGetStarted={handleGetStarted} />
      <HeroSection onGetStarted={handleGetStarted} />
      <FeaturesSection />
      <HowItWorksSection />
      <PricingSection onGetStarted={handleGetStarted} />
      <FAQSection />
      <CTASection onGetStarted={handleGetStarted} />
      <Footer />
    </div>
  );
};

export default LandingPageNew;
