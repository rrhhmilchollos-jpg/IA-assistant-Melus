import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Check, Zap, Star, ArrowRight, CreditCard, Loader2 } from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const PricingPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(null);
  const [billingConfig, setBillingConfig] = useState(null);
  const [currentCredits, setCurrentCredits] = useState(1000);
  const token = localStorage.getItem('session_token');

  useEffect(() => {
    fetchBillingConfig();
    if (token) fetchCredits();
  }, [token]);

  const fetchBillingConfig = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/billing/config`);
      const data = await res.json();
      setBillingConfig(data);
    } catch (err) {
      console.error('Error fetching billing config:', err);
    }
  };

  const fetchCredits = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/billing/credits`, {
        headers: { 'X-Session-Token': token }
      });
      const data = await res.json();
      setCurrentCredits(data.credits);
    } catch (err) {
      console.error('Error fetching credits:', err);
    }
  };

  const handleSubscribe = async (planId) => {
    if (!user) {
      navigate('/login');
      return;
    }

    if (planId === 'free') {
      navigate('/home');
      return;
    }

    setLoading(planId);
    try {
      const res = await fetch(`${API_BASE}/api/billing/checkout/subscription`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({
          plan_id: planId,
          success_url: window.location.origin,
          cancel_url: window.location.origin + '/pricing'
        })
      });

      const data = await res.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (err) {
      console.error('Checkout error:', err);
    } finally {
      setLoading(null);
    }
  };

  const handleBuyCredits = async (packageId) => {
    if (!user) {
      navigate('/login');
      return;
    }

    setLoading(packageId);
    try {
      const res = await fetch(`${API_BASE}/api/billing/checkout/credits`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({
          credit_package_id: packageId,
          success_url: window.location.origin,
          cancel_url: window.location.origin + '/pricing'
        })
      });

      const data = await res.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (err) {
      console.error('Checkout error:', err);
    } finally {
      setLoading(null);
    }
  };

  const plans = [
    {
      id: 'free',
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
      id: 'pro',
      name: 'Pro',
      price: '$29',
      period: '/month',
      description: 'For serious builders',
      credits: '50,000',
      features: [
        '50,000 credits/month',
        'GPT-4o & advanced models',
        'Priority support',
        'Unlimited projects',
        'Custom deployments',
        'API access'
      ],
      cta: 'Upgrade to Pro',
      highlighted: true
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: '$99',
      period: '/month',
      description: 'For teams and agencies',
      credits: 'Unlimited',
      features: [
        'Unlimited credits',
        'Custom AI models',
        'Dedicated support',
        'White-label option',
        'SLA guarantee',
        'On-premise option'
      ],
      cta: 'Contact Sales',
      highlighted: false
    }
  ];

  const creditPackages = [
    { id: 'credits_5k', credits: 5000, price: 5, name: '5K Credits' },
    { id: 'credits_25k', credits: 25000, price: 20, name: '25K Credits', popular: true },
    { id: 'credits_100k', credits: 100000, price: 75, name: '100K Credits' }
  ];

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <button onClick={() => navigate('/')} className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <span className="text-xl font-bold">
              Melus<span className="text-cyan-400">AI</span>
            </span>
          </button>

          {user && (
            <div className="flex items-center gap-4">
              <div className="px-3 py-1.5 bg-gray-800 rounded-lg text-sm">
                <span className="text-gray-400">Credits:</span>
                <span className="text-cyan-400 font-bold ml-2">{currentCredits.toLocaleString()}</span>
              </div>
              <button 
                onClick={() => navigate('/home')}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg"
              >
                Dashboard
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Plans Section */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Simple, Transparent
              <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent"> Pricing</span>
            </h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Start free, scale as you grow. No hidden fees.
            </p>
          </div>

          {/* Plans Grid */}
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto mb-20">
            {plans.map((plan) => (
              <div 
                key={plan.id}
                className={`relative p-8 rounded-2xl border ${
                  plan.highlighted 
                    ? 'bg-gradient-to-b from-cyan-500/10 to-blue-600/10 border-cyan-500/50' 
                    : 'bg-gray-900/50 border-gray-800'
                }`}
              >
                {plan.highlighted && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full text-sm font-medium flex items-center gap-1">
                    <Star className="w-4 h-4" /> Most Popular
                  </div>
                )}
                
                <div className="text-center mb-6">
                  <h3 className="text-xl font-semibold mb-2">{plan.name}</h3>
                  <div className="flex items-baseline justify-center gap-1">
                    <span className="text-4xl font-bold">{plan.price}</span>
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
                  onClick={() => handleSubscribe(plan.id)}
                  disabled={loading === plan.id}
                  className={`w-full py-3 rounded-xl font-medium transition-all flex items-center justify-center gap-2 ${
                    plan.highlighted
                      ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white hover:opacity-90'
                      : 'bg-gray-800 text-white hover:bg-gray-700'
                  }`}
                >
                  {loading === plan.id ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      {plan.cta}
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            ))}
          </div>

          {/* Credit Packages */}
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">Need More Credits?</h2>
              <p className="text-gray-400">Buy credit packages anytime, no subscription required</p>
            </div>

            <div className="grid md:grid-cols-3 gap-4">
              {creditPackages.map((pkg) => (
                <div 
                  key={pkg.id}
                  className={`p-6 rounded-xl border ${
                    pkg.popular 
                      ? 'bg-cyan-500/10 border-cyan-500/50' 
                      : 'bg-gray-900/50 border-gray-800'
                  }`}
                >
                  {pkg.popular && (
                    <span className="text-xs font-medium text-cyan-400 mb-2 block">BEST VALUE</span>
                  )}
                  <h3 className="text-lg font-semibold mb-1">{pkg.name}</h3>
                  <div className="flex items-baseline gap-1 mb-4">
                    <span className="text-2xl font-bold">${pkg.price}</span>
                    <span className="text-gray-400 text-sm">one-time</span>
                  </div>
                  <button
                    onClick={() => handleBuyCredits(pkg.id)}
                    disabled={loading === pkg.id}
                    className="w-full py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                  >
                    {loading === pkg.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <CreditCard className="w-4 h-4" />
                        Buy Now
                      </>
                    )}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-16 px-4 bg-gray-900/50">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-8">Frequently Asked Questions</h2>
          
          <div className="space-y-4">
            {[
              {
                q: "How do credits work?",
                a: "Credits are consumed when you generate code, run AI operations, or deploy projects. Simple operations use fewer credits, while complex AI tasks use more."
              },
              {
                q: "Can I upgrade or downgrade anytime?",
                a: "Yes! You can change your plan at any time. When upgrading, you'll get immediate access to new features. When downgrading, changes apply at the end of your billing period."
              },
              {
                q: "What happens when I run out of credits?",
                a: "You can purchase additional credit packages anytime, or upgrade your plan for more monthly credits."
              },
              {
                q: "Do credits roll over?",
                a: "Monthly subscription credits reset each billing cycle. Purchased credit packages never expire."
              }
            ].map((faq, i) => (
              <div key={i} className="p-4 bg-gray-800/50 rounded-xl">
                <h3 className="font-semibold mb-2">{faq.q}</h3>
                <p className="text-gray-400 text-sm">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default PricingPage;
