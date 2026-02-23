import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  Play,
  Code,
  Zap,
  Shield,
  Clock,
  Users,
  Check,
  ChevronRight,
  Bot,
  Sparkles,
  Rocket,
  Github,
  Twitter,
  Linkedin,
  Star,
  MessageSquare,
  Eye,
  Terminal,
  Layers,
  Globe,
  Lock
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Feature Card
const FeatureCard = ({ icon: Icon, title, description }) => (
  <div className="p-6 bg-[#111] border border-[#222] rounded-2xl hover:border-[#333] transition-colors group">
    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
      <Icon className="w-6 h-6 text-cyan-400" />
    </div>
    <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
    <p className="text-sm text-gray-400 leading-relaxed">{description}</p>
  </div>
);

// Testimonial Card
const TestimonialCard = ({ quote, author, role, avatar }) => (
  <div className="p-6 bg-[#111] border border-[#222] rounded-2xl">
    <div className="flex items-center gap-1 mb-4">
      {[...Array(5)].map((_, i) => (
        <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
      ))}
    </div>
    <p className="text-gray-300 mb-4 italic">"{quote}"</p>
    <div className="flex items-center gap-3">
      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white font-bold">
        {avatar}
      </div>
      <div>
        <div className="text-sm font-medium text-white">{author}</div>
        <div className="text-xs text-gray-500">{role}</div>
      </div>
    </div>
  </div>
);

// Code Preview Animation
const CodePreview = () => {
  const [currentLine, setCurrentLine] = useState(0);
  const lines = [
    { text: 'const App = () => {', color: 'text-blue-400' },
    { text: '  const [tasks, setTasks] = useState([]);', color: 'text-purple-400' },
    { text: '', color: '' },
    { text: '  const addTask = (task) => {', color: 'text-yellow-400' },
    { text: '    setTasks([...tasks, task]);', color: 'text-green-400' },
    { text: '  };', color: 'text-yellow-400' },
    { text: '', color: '' },
    { text: '  return (', color: 'text-blue-400' },
    { text: '    <TaskList tasks={tasks} />', color: 'text-cyan-400' },
    { text: '  );', color: 'text-blue-400' },
    { text: '};', color: 'text-blue-400' },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentLine(prev => (prev + 1) % (lines.length + 3));
    }, 500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-[#0a0a0a] rounded-xl border border-[#222] overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-2 bg-[#111] border-b border-[#222]">
        <div className="w-3 h-3 rounded-full bg-red-500" />
        <div className="w-3 h-3 rounded-full bg-yellow-500" />
        <div className="w-3 h-3 rounded-full bg-green-500" />
        <span className="ml-2 text-xs text-gray-500">App.jsx</span>
      </div>
      <div className="p-4 font-mono text-sm">
        {lines.map((line, i) => (
          <div
            key={i}
            className={`${line.color} transition-opacity duration-300 ${
              i <= currentLine ? 'opacity-100' : 'opacity-0'
            }`}
          >
            {line.text || '\u00A0'}
          </div>
        ))}
        <div className={`h-4 w-2 bg-cyan-400 animate-pulse ${currentLine > lines.length ? 'opacity-100' : 'opacity-0'}`} />
      </div>
    </div>
  );
};

// Main Landing Page
const LandingPageEmergent = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0a0a0a]/80 backdrop-blur-md border-b border-[#222]">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span className="text-xl font-semibold">Melus AI</span>
          </div>

          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm text-gray-400 hover:text-white transition-colors">Features</a>
            <a href="#how-it-works" className="text-sm text-gray-400 hover:text-white transition-colors">How it works</a>
            <button onClick={() => navigate('/pricing')} className="text-sm text-gray-400 hover:text-white transition-colors">Pricing</button>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/login')}
              className="px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors"
            >
              Sign In
            </button>
            <button
              onClick={() => navigate('/register')}
              className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
            >
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left - Text Content */}
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-[#111] border border-[#222] rounded-full text-sm text-gray-400 mb-6">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                Powered by GPT-5.2, Claude 4.5, Gemini 3
              </div>

              <h1 className="text-5xl md:text-6xl font-bold leading-tight mb-6">
                Build software
                <br />
                <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                  with AI agents
                </span>
              </h1>

              <p className="text-lg text-gray-400 mb-8 max-w-lg">
                Describe what you want to build and watch AI agents create production-ready
                applications in minutes. No coding required.
              </p>

              <div className="flex items-center gap-4 mb-8">
                <button
                  onClick={() => navigate('/register')}
                  className="group flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white rounded-xl font-medium transition-all"
                >
                  Start Building Free
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>
                <button className="flex items-center gap-2 px-6 py-3 bg-[#111] hover:bg-[#1a1a1a] border border-[#222] text-white rounded-xl font-medium transition-colors">
                  <Play className="w-4 h-4" />
                  Watch Demo
                </button>
              </div>

              <div className="flex items-center gap-6 text-sm text-gray-500">
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-400" />
                  Free to start
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-400" />
                  No credit card
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-400" />
                  50 free credits
                </div>
              </div>
            </div>

            {/* Right - Code Preview */}
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 blur-3xl" />
              <div className="relative">
                <CodePreview />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 px-4 border-y border-[#222]">
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
          {[
            { value: '10K+', label: 'Developers' },
            { value: '50K+', label: 'Projects Built' },
            { value: '99.9%', label: 'Uptime' },
            { value: '4.9/5', label: 'Rating' },
          ].map((stat, i) => (
            <div key={i} className="text-center">
              <div className="text-3xl font-bold text-white mb-1">{stat.value}</div>
              <div className="text-sm text-gray-500">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Everything you need to build</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Powerful features that help you go from idea to production in minutes, not months.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              icon={Bot}
              title="Multiple AI Models"
              description="Choose from GPT-5.2, Claude 4.5, Gemini 3, and more. Each optimized for different tasks."
            />
            <FeatureCard
              icon={Code}
              title="Full-Stack Generation"
              description="Generate complete applications with frontend, backend, and database in a single prompt."
            />
            <FeatureCard
              icon={Eye}
              title="Live Preview"
              description="See your app come to life in real-time. Test and iterate without leaving the builder."
            />
            <FeatureCard
              icon={Terminal}
              title="Real-Time Logs"
              description="Watch AI agents work with detailed terminal output. Understand every step of the process."
            />
            <FeatureCard
              icon={Rocket}
              title="One-Click Deploy"
              description="Deploy to production with a single click. GitHub integration and custom domains included."
            />
            <FeatureCard
              icon={Lock}
              title="Secure & Private"
              description="Your code is encrypted and never shared. Enterprise-grade security for peace of mind."
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 px-4 bg-[#0d0d0d]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">How it works</h2>
            <p className="text-gray-400">Three simple steps to your next app</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: '01',
                title: 'Describe',
                description: 'Tell us what you want to build in plain language. Be as detailed or simple as you like.',
                icon: MessageSquare
              },
              {
                step: '02',
                title: 'Generate',
                description: 'Our AI agents analyze your request, plan the architecture, and write production-ready code.',
                icon: Layers
              },
              {
                step: '03',
                title: 'Deploy',
                description: 'Preview your app, make adjustments, and deploy to production with one click.',
                icon: Globe
              }
            ].map((item, i) => {
              const Icon = item.icon;
              return (
                <div key={i} className="relative">
                  {i < 2 && (
                    <div className="hidden md:block absolute top-8 left-full w-full h-0.5 bg-gradient-to-r from-[#222] to-transparent z-0" />
                  )}
                  <div className="relative z-10 p-6 bg-[#111] border border-[#222] rounded-2xl">
                    <div className="text-4xl font-bold text-cyan-500/30 mb-4">{item.step}</div>
                    <div className="w-12 h-12 rounded-xl bg-[#1a1a1a] flex items-center justify-center mb-4">
                      <Icon className="w-6 h-6 text-cyan-400" />
                    </div>
                    <h3 className="text-xl font-semibold text-white mb-2">{item.title}</h3>
                    <p className="text-sm text-gray-400">{item.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Loved by developers</h2>
            <p className="text-gray-400">See what our users are saying</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <TestimonialCard
              quote="Built my entire SaaS MVP in a weekend. Melus AI is absolutely incredible for rapid prototyping."
              author="Sarah Chen"
              role="Startup Founder"
              avatar="S"
            />
            <TestimonialCard
              quote="The code quality is surprisingly good. It follows best practices and is actually maintainable."
              author="Marcus Williams"
              role="Senior Developer"
              avatar="M"
            />
            <TestimonialCard
              quote="Finally, an AI tool that understands what I want. The multi-model support is a game changer."
              author="Alex Rivera"
              role="Freelance Developer"
              avatar="A"
            />
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="p-12 bg-gradient-to-b from-[#111] to-[#0d0d0d] border border-[#222] rounded-3xl">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to build something amazing?
            </h2>
            <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
              Join thousands of developers using Melus AI to ship faster.
              Start with 50 free credits, no credit card required.
            </p>
            <button
              onClick={() => navigate('/register')}
              className="group inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white rounded-xl font-medium transition-all"
            >
              Start Building Now
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 border-t border-[#222]">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
                <span className="text-lg font-semibold">Melus AI</span>
              </div>
              <p className="text-sm text-gray-500">
                Build software with AI agents. Fast, reliable, and production-ready.
              </p>
            </div>

            <div>
              <h4 className="text-sm font-medium text-white mb-4">Product</h4>
              <ul className="space-y-2">
                <li><a href="#features" className="text-sm text-gray-500 hover:text-white transition-colors">Features</a></li>
                <li><a href="#" className="text-sm text-gray-500 hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="text-sm text-gray-500 hover:text-white transition-colors">Changelog</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-medium text-white mb-4">Resources</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-sm text-gray-500 hover:text-white transition-colors">Documentation</a></li>
                <li><a href="#" className="text-sm text-gray-500 hover:text-white transition-colors">API Reference</a></li>
                <li><a href="#" className="text-sm text-gray-500 hover:text-white transition-colors">Blog</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-medium text-white mb-4">Company</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-sm text-gray-500 hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="text-sm text-gray-500 hover:text-white transition-colors">Privacy</a></li>
                <li><a href="#" className="text-sm text-gray-500 hover:text-white transition-colors">Terms</a></li>
              </ul>
            </div>
          </div>

          <div className="pt-8 border-t border-[#222] flex items-center justify-between">
            <p className="text-sm text-gray-500">© 2024 Melus AI. All rights reserved.</p>
            <div className="flex items-center gap-4">
              <a href="#" className="text-gray-500 hover:text-white transition-colors">
                <Github className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-500 hover:text-white transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-500 hover:text-white transition-colors">
                <Linkedin className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPageEmergent;
