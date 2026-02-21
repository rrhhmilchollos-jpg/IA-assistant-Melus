import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Mail, ChevronLeft, ChevronRight } from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Matrix-style background with scattered characters
const CodeBackground = () => {
  const [chars, setChars] = useState([]);
  
  useEffect(() => {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*/<>[]{}()&@#$%';
    const newChars = [];
    for (let i = 0; i < 150; i++) {
      newChars.push({
        char: characters[Math.floor(Math.random() * characters.length)],
        x: Math.random() * 100,
        y: Math.random() * 100,
        opacity: Math.random() * 0.12 + 0.03,
        size: Math.random() * 10 + 12
      });
    }
    setChars(newChars);
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none select-none">
      {chars.map((c, i) => (
        <span
          key={i}
          className="absolute font-mono text-gray-400"
          style={{
            left: `${c.x}%`,
            top: `${c.y}%`,
            opacity: c.opacity,
            fontSize: `${c.size}px`
          }}
        >
          {c.char}
        </span>
      ))}
    </div>
  );
};

// Showcase slides data
const showcaseSlides = [
  {
    title: "$100M ARR",
    emoji: "🎉",
    subtitle: "One of the fastest startups to reach this milestone.",
    highlight: "Celebrating this milestone with",
    promo: "flat 75% off on our standard monthly plan.",
    bgGradient: "from-cyan-400 via-sky-300 to-blue-400"
  },
  {
    title: "500K+ Apps",
    emoji: "🚀",
    subtitle: "Built by developers around the world.",
    highlight: "Join the community building",
    promo: "the future of software development.",
    bgGradient: "from-purple-400 via-pink-300 to-rose-400"
  },
  {
    title: "10x Faster",
    emoji: "⚡",
    subtitle: "Ship products in minutes, not months.",
    highlight: "AI-powered development",
    promo: "that actually works.",
    bgGradient: "from-emerald-400 via-teal-300 to-cyan-400"
  }
];

const LandingPage = () => {
  const navigate = useNavigate();
  const { user, isLoading } = useAuth();
  const [currentSlide, setCurrentSlide] = useState(0);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showEmailForm, setShowEmailForm] = useState(false);
  const [isLogin, setIsLogin] = useState(true);
  const [authLoading, setAuthLoading] = useState(false);
  const [error, setError] = useState('');

  // Redirect authenticated users
  useEffect(() => {
    if (!isLoading && user) {
      navigate('/home');
    }
  }, [user, isLoading, navigate]);

  // Auto-rotate carousel
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % showcaseSlides.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  // Handle Google login
  const handleGoogleAuth = () => {
    window.location.href = `${API_BASE}/api/auth/google`;
  };

  // Handle Facebook login
  const handleFacebookAuth = () => {
    window.location.href = `${API_BASE}/api/auth/facebook`;
  };

  // Handle GitHub login (disabled for now)
  const handleGitHubAuth = () => {
    window.location.href = `${API_BASE}/api/github/auth`;
  };

  // Handle email auth
  const handleEmailAuth = async (e) => {
    e.preventDefault();
    setAuthLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          email, 
          password, 
          name: email.split('@')[0] 
        })
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('session_token', data.session_token);
        window.location.href = '/home';
      } else {
        setError(data.detail || 'Authentication error');
      }
    } catch (err) {
      setError('Connection error. Please try again.');
    } finally {
      setAuthLoading(false);
    }
  };

  const currentShowcase = showcaseSlides[currentSlide];

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f8f9fa] flex">
      {/* Left side - Auth */}
      <div className="flex-1 relative flex flex-col items-center justify-center px-8">
        <CodeBackground />
        
        {/* Logo - Top left */}
        <div className="absolute top-6 left-8 z-10">
          <span className="text-xl font-light tracking-tight text-gray-800">
            melus<span className="font-normal">AI</span>
          </span>
        </div>

        {/* Main Content */}
        <div className="relative z-10 w-full max-w-md">
          {/* Logo Icon */}
          <div className="flex justify-center mb-6">
            <div className="w-12 h-12 relative">
              <svg viewBox="0 0 48 48" fill="none" className="w-full h-full">
                <rect x="8" y="8" width="32" height="32" rx="8" fill="#e5e7eb" stroke="#d1d5db" strokeWidth="1"/>
                <path d="M18 20 L24 16 L30 20 L30 28 L24 32 L18 28 Z" fill="#9ca3af"/>
                <circle cx="24" cy="24" r="4" fill="#6b7280"/>
              </svg>
            </div>
          </div>

          {/* Title */}
          <h1 className="text-center mb-8">
            <span className="text-3xl font-medium text-gray-800 block mb-1">
              Build Full-Stack
            </span>
            <span className="text-3xl font-medium bg-gradient-to-r from-cyan-500 to-blue-500 bg-clip-text text-transparent">
              Web & Mobile Apps in minutes
            </span>
          </h1>

          {/* Auth Buttons */}
          <div className="space-y-3">
            {!showEmailForm ? (
              <>
                {/* Google Button - Dark */}
                <button
                  onClick={handleGoogleAuth}
                  disabled={authLoading}
                  className="w-full flex items-center justify-center gap-3 px-6 py-3.5 bg-gray-900 hover:bg-gray-800 text-white rounded-full font-medium transition-colors disabled:opacity-50"
                  data-testid="google-login-btn"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Continue with Google
                </button>

                {/* Social Buttons Row - Light gray */}
                <div className="flex gap-2">
                  <button
                    onClick={handleGitHubAuth}
                    disabled={authLoading}
                    className="flex-1 flex items-center justify-center gap-2 px-6 py-3.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full font-medium transition-colors disabled:opacity-50"
                    data-testid="github-login-btn"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd"/>
                    </svg>
                  </button>
                  
                  <button
                    disabled
                    className="flex-1 flex items-center justify-center gap-2 px-6 py-3.5 bg-gray-100 text-gray-400 rounded-full font-medium cursor-not-allowed"
                    title="Coming soon"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
                    </svg>
                  </button>
                  
                  <button
                    onClick={handleFacebookAuth}
                    disabled={authLoading}
                    className="flex-1 flex items-center justify-center gap-2 px-6 py-3.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full font-medium transition-colors disabled:opacity-50"
                    data-testid="facebook-login-btn"
                  >
                    <svg className="w-5 h-5" fill="#1877F2" viewBox="0 0 24 24">
                      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                    </svg>
                  </button>
                </div>

                {/* Divider - Dashed */}
                <div className="flex items-center gap-4 py-3">
                  <div className="flex-1 border-t border-dashed border-gray-300" />
                  <span className="text-sm text-gray-400">OR</span>
                  <div className="flex-1 border-t border-dashed border-gray-300" />
                </div>

                {/* Email Button - Light gray with icon */}
                <button
                  onClick={() => setShowEmailForm(true)}
                  className="w-full flex items-center justify-center gap-3 px-6 py-3.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full font-medium transition-colors"
                  data-testid="email-toggle-btn"
                >
                  <Mail size={20} className="text-gray-500" />
                  Continue with Email
                </button>
              </>
            ) : (
              /* Email Form */
              <form onSubmit={handleEmailAuth} className="space-y-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowEmailForm(false);
                    setError('');
                  }}
                  className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 transition-colors mb-2"
                >
                  <ChevronLeft size={16} />
                  Back
                </button>
                
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email"
                  className="w-full px-4 py-3.5 bg-white border border-gray-200 rounded-full text-gray-800 placeholder-gray-400 focus:outline-none focus:border-gray-400 transition-colors"
                  data-testid="email-input"
                  required
                  autoFocus
                />
                
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                  className="w-full px-4 py-3.5 bg-white border border-gray-200 rounded-full text-gray-800 placeholder-gray-400 focus:outline-none focus:border-gray-400 transition-colors"
                  data-testid="password-input"
                  required
                />
                
                {error && (
                  <p className="text-red-500 text-sm text-center py-1">{error}</p>
                )}
                
                <button
                  type="submit"
                  disabled={authLoading}
                  className="w-full px-6 py-3.5 bg-gray-900 hover:bg-gray-800 text-white rounded-full font-medium transition-colors disabled:opacity-50"
                  data-testid="email-submit-btn"
                >
                  {authLoading ? (
                    <span className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Loading...
                    </span>
                  ) : (
                    isLogin ? 'Sign In' : 'Create Account'
                  )}
                </button>
                
                <p className="text-center text-gray-500 text-sm">
                  {isLogin ? "Don't have an account? " : "Already have an account? "}
                  <button
                    type="button"
                    onClick={() => {
                      setIsLogin(!isLogin);
                      setError('');
                    }}
                    className="text-gray-700 hover:text-gray-900 font-medium"
                  >
                    {isLogin ? 'Sign Up' : 'Sign In'}
                  </button>
                </p>
              </form>
            )}
          </div>

          {/* Terms and Privacy */}
          <p className="text-center text-gray-400 text-xs mt-6">
            By continuing, you agree to our{' '}
            <a href="/terms" className="text-gray-500 hover:text-gray-700 underline">
              Terms of Service
            </a>{' '}
            and{' '}
            <a href="/privacy" className="text-gray-500 hover:text-gray-700 underline">
              Privacy Policy
            </a>.
          </p>
        </div>
      </div>
      
      {/* Right side - Showcase with gradient */}
      <div className={`hidden lg:flex flex-1 relative bg-gradient-to-br ${currentShowcase.bgGradient} overflow-hidden`}>
        {/* Y Combinator badge - Top right */}
        <div className="absolute top-4 right-4 z-20">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-white/90 backdrop-blur-sm rounded-full shadow-sm">
            <div className="w-5 h-5 bg-orange-500 rounded flex items-center justify-center">
              <span className="text-white text-xs font-bold">Y</span>
            </div>
            <span className="text-gray-700 text-sm font-medium">Combinator S24</span>
          </div>
        </div>
        
        {/* Content */}
        <div className="relative z-10 flex flex-col items-center justify-center w-full p-12">
          {/* Top title */}
          <div className="text-center mb-8">
            <h2 className="text-4xl font-bold text-white mb-2">
              {currentShowcase.title} {currentShowcase.emoji}
            </h2>
            <p className="text-white/80 text-lg">
              {currentShowcase.subtitle}
            </p>
          </div>
          
          {/* Mockup Card - Laptop style */}
          <div className="relative w-full max-w-lg">
            {/* Laptop frame */}
            <div className="bg-gray-900 rounded-t-xl p-2">
              {/* Browser buttons */}
              <div className="flex items-center gap-1.5 px-2 mb-2">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <div className="flex-1 mx-4">
                  <div className="h-5 bg-gray-700 rounded-full" />
                </div>
              </div>
              
              {/* Screen content */}
              <div className="bg-white rounded-lg p-8 text-center">
                <p className="text-gray-500 text-sm mb-2">Melus AI reaches</p>
                <p className="text-5xl font-bold bg-gradient-to-r from-cyan-500 to-blue-500 bg-clip-text text-transparent mb-1">
                  {currentShowcase.title}
                </p>
                <p className="text-xl font-semibold text-cyan-500 mb-4">
                  in 8 months
                </p>
                <p className="text-gray-500 text-sm">
                  {currentShowcase.highlight}
                </p>
                <p className="text-cyan-500 text-sm font-medium">
                  {currentShowcase.promo}
                </p>
              </div>
            </div>
            
            {/* Laptop base */}
            <div className="h-4 bg-gray-300 rounded-b-lg mx-8" />
            <div className="h-1 bg-gray-400 rounded-b mx-16" />
          </div>

          {/* Carousel Controls */}
          <div className="flex items-center gap-4 mt-8">
            <button
              onClick={() => setCurrentSlide((prev) => (prev - 1 + showcaseSlides.length) % showcaseSlides.length)}
              className="p-2 rounded-full bg-white/20 hover:bg-white/30 text-white transition-colors"
            >
              <ChevronLeft size={20} />
            </button>
            
            <div className="flex gap-2">
              {showcaseSlides.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setCurrentSlide(i)}
                  className={`h-2 rounded-full transition-all ${
                    i === currentSlide ? 'w-8 bg-white' : 'w-2 bg-white/40 hover:bg-white/60'
                  }`}
                />
              ))}
            </div>
            
            <button
              onClick={() => setCurrentSlide((prev) => (prev + 1) % showcaseSlides.length)}
              className="p-2 rounded-full bg-white/20 hover:bg-white/30 text-white transition-colors"
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
