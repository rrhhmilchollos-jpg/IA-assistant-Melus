import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Check,
  X,
  Zap,
  Sparkles,
  Crown,
  Rocket,
  ChevronLeft,
  Loader2,
  CreditCard,
  Shield,
  Users,
  Clock,
  Code,
  Bot,
  Star
} from 'lucide-react';
import { Toaster, toast } from '../components/ui/sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Pricing Plans
const PLANS = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    period: 'forever',
    description: 'Perfect for trying out Melus AI',
    credits: 50,
    creditsLabel: '50 credits/month',
    icon: Sparkles,
    color: 'from-gray-500 to-gray-600',
    features: [
      { text: '50 credits per month', included: true },
      { text: 'GPT-4o model', included: true },
      { text: 'Basic code generation', included: true },
      { text: '3 projects', included: true },
      { text: 'Community support', included: true },
      { text: 'Premium models', included: false },
      { text: 'Unlimited projects', included: false },
      { text: 'Priority support', included: false },
      { text: 'Advanced agents (E2)', included: false },
    ],
    cta: 'Get Started',
    popular: false
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 20,
    period: 'month',
    description: 'For developers who need more power',
    credits: 'unlimited',
    creditsLabel: 'Unlimited credits',
    icon: Rocket,
    color: 'from-cyan-500 to-blue-600',
    features: [
      { text: 'Unlimited credits', included: true },
      { text: 'All AI models (GPT-5.2, Claude 4.5, etc)', included: true },
      { text: 'Advanced code generation', included: true },
      { text: 'Unlimited projects', included: true },
      { text: 'Priority support', included: true },
      { text: 'All agent modes (E1, E1.5, E2)', included: true },
      { text: 'GitHub integration', included: true },
      { text: 'Custom deployments', included: true },
      { text: 'Team collaboration', included: false },
    ],
    cta: 'Upgrade to Pro',
    popular: true
  },
  {
    id: 'team',
    name: 'Team',
    price: 50,
    period: 'month',
    description: 'For teams building together',
    credits: 'unlimited',
    creditsLabel: 'Unlimited credits',
    icon: Crown,
    color: 'from-purple-500 to-pink-600',
    features: [
      { text: 'Everything in Pro', included: true },
      { text: 'Up to 5 team members', included: true },
      { text: 'Shared projects', included: true },
      { text: 'Admin dashboard', included: true },
      { text: 'API access', included: true },
      { text: 'Custom integrations', included: true },
      { text: 'Dedicated support', included: true },
      { text: 'SLA guarantee', included: true },
      { text: 'On-premise deployment', included: false },
    ],
    cta: 'Contact Sales',
    popular: false
  }
];

// Credit Packs for one-time purchase
const CREDIT_PACKS = [
  { credits: 100, price: 5, popular: false },
  { credits: 500, price: 20, popular: true },
  { credits: 1000, price: 35, popular: false },
  { credits: 5000, price: 150, popular: false },
];

// Plan Card Component
const PlanCard = ({ plan, currentPlan, onSelect, isLoading }) => {
  const Icon = plan.icon;
  const isCurrentPlan = currentPlan === plan.id;

  return (
    <div
      className={`relative rounded-2xl p-6 transition-all ${
        plan.popular
          ? 'bg-gradient-to-b from-[#1a1a1a] to-[#111] border-2 border-cyan-500/50 shadow-xl shadow-cyan-500/10'
          : 'bg-[#111] border border-[#222]'
      }`}
    >
      {plan.popular && (
        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
          <div className="px-4 py-1 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full text-xs font-medium text-white">
            Most Popular
          </div>
        </div>
      )}

      <div className="flex items-center gap-3 mb-4">
        <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${plan.color} flex items-center justify-center`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">{plan.name}</h3>
          <p className="text-xs text-gray-500">{plan.description}</p>
        </div>
      </div>

      <div className="mb-6">
        <div className="flex items-baseline gap-1">
          <span className="text-4xl font-bold text-white">
            {plan.price === 0 ? 'Free' : `$${plan.price}`}
          </span>
          {plan.price > 0 && (
            <span className="text-gray-500 text-sm">/{plan.period}</span>
          )}
        </div>
        <p className="text-sm text-cyan-400 mt-1">{plan.creditsLabel}</p>
      </div>

      <ul className="space-y-3 mb-6">
        {plan.features.map((feature, i) => (
          <li key={i} className="flex items-center gap-2 text-sm">
            {feature.included ? (
              <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
            ) : (
              <X className="w-4 h-4 text-gray-600 flex-shrink-0" />
            )}
            <span className={feature.included ? 'text-gray-300' : 'text-gray-600'}>
              {feature.text}
            </span>
          </li>
        ))}
      </ul>

      <button
        onClick={() => onSelect(plan.id)}
        disabled={isLoading || isCurrentPlan}
        className={`w-full py-3 rounded-xl font-medium transition-all ${
          isCurrentPlan
            ? 'bg-[#222] text-gray-500 cursor-not-allowed'
            : plan.popular
            ? 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white'
            : 'bg-[#222] hover:bg-[#333] text-white'
        }`}
      >
        {isLoading ? (
          <Loader2 className="w-5 h-5 animate-spin mx-auto" />
        ) : isCurrentPlan ? (
          'Current Plan'
        ) : (
          plan.cta
        )}
      </button>
    </div>
  );
};

// Credit Pack Card
const CreditPackCard = ({ pack, onPurchase, isLoading }) => {
  return (
    <div
      className={`relative rounded-xl p-4 transition-all ${
        pack.popular
          ? 'bg-gradient-to-b from-[#1a1a1a] to-[#111] border-2 border-amber-500/50'
          : 'bg-[#111] border border-[#222]'
      }`}
    >
      {pack.popular && (
        <div className="absolute -top-2 right-3">
          <div className="px-2 py-0.5 bg-amber-500 rounded text-[10px] font-medium text-black">
            Best Value
          </div>
        </div>
      )}

      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Zap className="w-5 h-5 text-yellow-400" />
          <span className="text-lg font-bold text-white">{pack.credits}</span>
          <span className="text-sm text-gray-500">credits</span>
        </div>
        <span className="text-xl font-bold text-white">${pack.price}</span>
      </div>

      <p className="text-xs text-gray-500 mb-3">
        ${(pack.price / pack.credits * 100).toFixed(1)}¢ per credit
      </p>

      <button
        onClick={() => onPurchase(pack)}
        disabled={isLoading}
        className="w-full py-2 bg-[#222] hover:bg-[#333] text-white rounded-lg text-sm font-medium transition-colors"
      >
        {isLoading ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Buy Now'}
      </button>
    </div>
  );
};

// Main Pricing Page
const PricingPageNew = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('plans'); // 'plans' | 'credits'

  const currentPlan = user?.subscription || 'free';

  const handleSelectPlan = async (planId) => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    if (planId === 'free') {
      toast.info('You are already on the Free plan');
      return;
    }

    if (planId === 'team') {
      toast.info('Contact us for Team plan at team@melus.ai');
      return;
    }

    setIsLoading(true);
    const token = localStorage.getItem('session_token');

    try {
      const response = await fetch(`${API_BASE}/api/stripe/create-checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({
          plan: planId,
          success_url: `${window.location.origin}/success?plan=${planId}`,
          cancel_url: `${window.location.origin}/pricing`
        })
      });

      const data = await response.json();

      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        throw new Error(data.error || 'Failed to create checkout');
      }
    } catch (error) {
      console.error('Checkout error:', error);
      toast.error('Failed to start checkout. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePurchaseCredits = async (pack) => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    setIsLoading(true);
    const token = localStorage.getItem('session_token');

    try {
      const response = await fetch(`${API_BASE}/api/stripe/create-checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({
          credits: pack.credits,
          price: pack.price,
          success_url: `${window.location.origin}/success?credits=${pack.credits}`,
          cancel_url: `${window.location.origin}/pricing`
        })
      });

      const data = await response.json();

      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        throw new Error(data.error || 'Failed to create checkout');
      }
    } catch (error) {
      console.error('Credit purchase error:', error);
      toast.error('Failed to start checkout. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      <Toaster />

      {/* Header */}
      <header className="sticky top-0 z-50 bg-[#0a0a0a]/80 backdrop-blur-md border-b border-[#222]">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate(-1)}
              className="p-2 hover:bg-[#222] rounded-lg transition-colors"
            >
              <ChevronLeft className="w-5 h-5 text-gray-400" />
            </button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <span className="text-lg font-semibold text-white">Melus AI</span>
            </div>
          </div>

          {isAuthenticated ? (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-[#1a1a1a] rounded-lg">
                <Zap className="w-4 h-4 text-yellow-400" />
                <span className="text-sm text-white">{user?.credits || 0} credits</span>
              </div>
              <button
                onClick={() => navigate('/builder')}
                className="px-4 py-2 bg-[#222] hover:bg-[#333] text-white rounded-lg text-sm font-medium transition-colors"
              >
                Go to Builder
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/login')}
                className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
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
          )}
        </div>
      </header>

      {/* Hero */}
      <section className="py-16 px-4 text-center">
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
          Simple, transparent pricing
        </h1>
        <p className="text-lg text-gray-400 max-w-2xl mx-auto">
          Choose the plan that's right for you. Start free and upgrade when you need more power.
        </p>
      </section>

      {/* Tab Selector */}
      <div className="max-w-6xl mx-auto px-4 mb-8">
        <div className="flex items-center justify-center gap-2 p-1 bg-[#111] rounded-xl w-fit mx-auto">
          <button
            onClick={() => setActiveTab('plans')}
            className={`px-6 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'plans'
                ? 'bg-[#222] text-white'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            Subscription Plans
          </button>
          <button
            onClick={() => setActiveTab('credits')}
            className={`px-6 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'credits'
                ? 'bg-[#222] text-white'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            Buy Credits
          </button>
        </div>
      </div>

      {/* Plans Grid */}
      {activeTab === 'plans' && (
        <section className="max-w-6xl mx-auto px-4 pb-16">
          <div className="grid md:grid-cols-3 gap-6">
            {PLANS.map(plan => (
              <PlanCard
                key={plan.id}
                plan={plan}
                currentPlan={currentPlan}
                onSelect={handleSelectPlan}
                isLoading={isLoading}
              />
            ))}
          </div>
        </section>
      )}

      {/* Credits Grid */}
      {activeTab === 'credits' && (
        <section className="max-w-4xl mx-auto px-4 pb-16">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-white mb-2">Buy Credits</h2>
            <p className="text-gray-400">One-time purchase. Credits never expire.</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {CREDIT_PACKS.map((pack, i) => (
              <CreditPackCard
                key={i}
                pack={pack}
                onPurchase={handlePurchaseCredits}
                isLoading={isLoading}
              />
            ))}
          </div>
        </section>
      )}

      {/* Features Section */}
      <section className="max-w-6xl mx-auto px-4 py-16 border-t border-[#222]">
        <h2 className="text-2xl font-bold text-white text-center mb-12">
          Why developers choose Melus AI
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              icon: Bot,
              title: 'Multiple AI Models',
              description: 'Access GPT-5.2, Claude 4.5, Gemini 3, and more. Choose the best model for your task.'
            },
            {
              icon: Code,
              title: 'Production-Ready Code',
              description: 'Generate clean, well-structured code that follows best practices and modern standards.'
            },
            {
              icon: Rocket,
              title: 'Instant Deployment',
              description: 'Deploy your projects with one click. GitHub integration and custom domains included.'
            },
            {
              icon: Shield,
              title: 'Secure & Private',
              description: 'Your code and data are encrypted and never shared. Enterprise-grade security.'
            },
            {
              icon: Clock,
              title: '24/7 Availability',
              description: 'Build anytime, anywhere. Our AI agents are always ready to help you code.'
            },
            {
              icon: Users,
              title: 'Team Collaboration',
              description: 'Work together on projects. Share, review, and deploy as a team.'
            }
          ].map((feature, i) => {
            const Icon = feature.icon;
            return (
              <div key={i} className="p-6 bg-[#111] border border-[#222] rounded-xl">
                <div className="w-10 h-10 rounded-lg bg-[#1a1a1a] flex items-center justify-center mb-4">
                  <Icon className="w-5 h-5 text-cyan-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-sm text-gray-400">{feature.description}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* FAQ Section */}
      <section className="max-w-3xl mx-auto px-4 py-16 border-t border-[#222]">
        <h2 className="text-2xl font-bold text-white text-center mb-12">
          Frequently Asked Questions
        </h2>
        <div className="space-y-6">
          {[
            {
              q: 'What are credits?',
              a: 'Credits are used each time you generate code or make AI requests. Different operations cost different amounts of credits.'
            },
            {
              q: 'Can I change my plan anytime?',
              a: 'Yes! You can upgrade, downgrade, or cancel your subscription at any time. Changes take effect immediately.'
            },
            {
              q: 'What happens if I run out of credits?',
              a: 'Free users can wait for their monthly refresh or purchase credit packs. Pro users have unlimited credits.'
            },
            {
              q: 'Is there a refund policy?',
              a: 'We offer a 14-day money-back guarantee on all subscriptions. Credit pack purchases are final.'
            }
          ].map((faq, i) => (
            <div key={i} className="p-6 bg-[#111] border border-[#222] rounded-xl">
              <h3 className="text-lg font-semibold text-white mb-2">{faq.q}</h3>
              <p className="text-gray-400">{faq.a}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer CTA */}
      <section className="py-16 px-4 border-t border-[#222]">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to start building?
          </h2>
          <p className="text-gray-400 mb-8">
            Join thousands of developers building amazing apps with Melus AI.
          </p>
          <button
            onClick={() => navigate(isAuthenticated ? '/builder' : '/register')}
            className="px-8 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white rounded-xl font-medium transition-colors"
          >
            {isAuthenticated ? 'Go to Builder' : 'Get Started Free'}
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-[#222]">
        <div className="max-w-6xl mx-auto flex items-center justify-between text-sm text-gray-500">
          <span>© 2024 Melus AI. All rights reserved.</span>
          <div className="flex items-center gap-6">
            <a href="#" className="hover:text-white transition-colors">Privacy</a>
            <a href="#" className="hover:text-white transition-colors">Terms</a>
            <a href="#" className="hover:text-white transition-colors">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default PricingPageNew;
