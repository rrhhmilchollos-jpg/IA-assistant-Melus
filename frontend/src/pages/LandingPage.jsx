import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Github, Apple, Mail, ChevronLeft, ChevronRight } from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Matrix-style background characters
const MatrixBackground = () => {
  const [chars, setChars] = useState([]);
  
  useEffect(() => {
    const characters = 'QWERTYUIOPASDFGHJKLZXCVBNM0123456789+-*/<>[]{}()';
    const generateChars = () => {
      const newChars = [];
      for (let i = 0; i < 200; i++) {
        newChars.push({
          char: characters[Math.floor(Math.random() * characters.length)],
          x: Math.random() * 100,
          y: Math.random() * 100,
          opacity: Math.random() * 0.15 + 0.05,
          size: Math.random() * 8 + 10
        });
      }
      setChars(newChars);
    };
    generateChars();
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

// Showcase Carousel
const showcaseItems = [
  {
    title: "$100M ARR",
    subtitle: "One of the fastest startups to reach this milestone.",
    highlight: "Emergent reaches",
    metric: "$100M ARR",
    submetric: "in 8 months",
    description: "Celebrating this milestone with flat 75% off on our standard monthly plan.",
    bgColor: "from-cyan-400 to-blue-400"
  },
  {
    title: "500K+ Apps Built",
    subtitle: "Join thousands of creators building with AI.",
    highlight: "Community milestone",
    metric: "500K+",
    submetric: "apps created",
    description: "From startups to enterprises, everyone builds with Melus.",
    bgColor: "from-purple-400 to-pink-400"
  },
  {
    title: "10x Faster",
    subtitle: "Ship products 10x faster than traditional development.",
    highlight: "Development speed",
    metric: "10x",
    submetric: "faster shipping",
    description: "Go from idea to production in minutes, not months.",
    bgColor: "from-green-400 to-teal-400"
  }
];

const LandingPage = () => {
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const [currentSlide, setCurrentSlide] = useState(0);
  const [showEmailForm, setShowEmailForm] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [authLoading, setAuthLoading] = useState(false);
  const [error, setError] = useState('');

  // Redirect if already logged in
  useEffect(() => {
    if (!loading && user) {
      navigate('/home');
    }
  }, [user, loading, navigate]);

  // Auto-rotate carousel
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % showcaseItems.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleGoogleAuth = () => {
    window.location.href = `${API_BASE}/api/auth/google`;
  };

  const handleGitHubAuth = () => {
    window.location.href = `${API_BASE}/api/github/auth`;
  };

  const handleEmailAuth = async (e) => {
    e.preventDefault();
    setAuthLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name: email.split('@')[0] })
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('session_token', data.session_token);
        window.location.href = '/home';
      } else {
        setError(data.detail || 'Error de autenticación');
      }
    } catch (err) {
      setError('Error de conexión');
    } finally {
      setAuthLoading(false);
    }
  };

  const currentShowcase = showcaseItems[currentSlide];

  return (
    <div className="min-h-screen bg-[#fafafa] flex">
      {/* Left Side - Auth */}
      <div className="flex-1 relative flex flex-col items-center justify-center px-8">
        <MatrixBackground />
        
        {/* Logo */}
        <div className="absolute top-6 left-6 z-10">
          <span className="text-xl font-semibold text-gray-800 tracking-tight">
            melus
          </span>
        </div>

        {/* Main Content */}
        <div className="relative z-10 w-full max-w-md">
          {/* Animated Logo */}
          <div className="flex justify-center mb-8">
            <div className="w-20 h-20 relative">
              <div className="absolute inset-0 bg-gradient-to-br from-gray-200 to-gray-300 rounded-2xl transform rotate-12 animate-pulse" />
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-4xl font-bold text-gray-600">e</span>
              </div>
            </div>
          </div>

          {/* Title */}
          <h1 className="text-center mb-2">
            <span className="text-3xl font-semibold text-gray-800 block">
              Build Full-Stack
            </span>
            <span className="text-3xl font-semibold bg-gradient-to-r from-cyan-500 to-blue-500 bg-clip-text text-transparent">
              Web & Mobile Apps in minutes
            </span>
          </h1>

          {/* Auth Buttons */}
          <div className="mt-10 space-y-3">
            {!showEmailForm ? (
              <>
                {/* Google Button */}
                <button
                  onClick={handleGoogleAuth}
                  className="w-full flex items-center justify-center gap-3 px-6 py-3.5 bg-gray-900 hover:bg-gray-800 text-white rounded-full font-medium transition-colors"
                  data-testid="google-auth-btn"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Continue with Google
                </button>

                {/* Social Buttons Row */}
                <div className="flex gap-3">
                  <button
                    onClick={handleGitHubAuth}
                    className="flex-1 flex items-center justify-center gap-2 px-6 py-3.5 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-full font-medium transition-colors border border-gray-200"
                    data-testid="github-auth-btn"
                  >
                    <Github className="w-5 h-5" />
                  </button>
                  <button
                    className="flex-1 flex items-center justify-center gap-2 px-6 py-3.5 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-full font-medium transition-colors border border-gray-200 opacity-50 cursor-not-allowed"
                    disabled
                  >
                    <Apple className="w-5 h-5" />
                  </button>
                  <button
                    className="flex-1 flex items-center justify-center gap-2 px-6 py-3.5 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-full font-medium transition-colors border border-gray-200 opacity-50 cursor-not-allowed"
                    disabled
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                    </svg>
                  </button>
                </div>

                {/* Divider */}
                <div className="flex items-center gap-4 py-2">
                  <div className="flex-1 border-t border-dashed border-gray-300" />
                  <span className="text-sm text-gray-400">OR</span>
                  <div className="flex-1 border-t border-dashed border-gray-300" />
                </div>

                {/* Email Button */}
                <button
                  onClick={() => setShowEmailForm(true)}
                  className="w-full flex items-center justify-center gap-3 px-6 py-3.5 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-full font-medium transition-colors border border-gray-200"
                  data-testid="email-auth-btn"
                >
                  <Mail className="w-5 h-5" />
                  Continue with Email
                </button>
              </>
            ) : (
              /* Email Form */
              <form onSubmit={handleEmailAuth} className="space-y-4">
                <button
                  type="button"
                  onClick={() => setShowEmailForm(false)}
                  className="text-sm text-gray-500 hover:text-gray-700 mb-2"
                >
                  ← Back
                </button>
                
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email"
                  className="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl focus:border-gray-500 focus:ring-0 outline-none"
                  required
                />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                  className="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl focus:border-gray-500 focus:ring-0 outline-none"
                  required
                />
                
                {error && (
                  <p className="text-red-500 text-sm text-center">{error}</p>
                )}
                
                <button
                  type="submit"
                  disabled={authLoading}
                  className="w-full px-6 py-3.5 bg-gray-900 hover:bg-gray-800 disabled:opacity-50 text-white rounded-full font-medium transition-colors"
                >
                  {authLoading ? 'Loading...' : (isLogin ? 'Sign In' : 'Create Account')}
                </button>
                
                <p className="text-center text-sm text-gray-500">
                  {isLogin ? "Don't have an account? " : "Already have an account? "}
                  <button
                    type="button"
                    onClick={() => setIsLogin(!isLogin)}
                    className="text-gray-800 font-medium hover:underline"
                  >
                    {isLogin ? 'Sign Up' : 'Sign In'}
                  </button>
                </p>
              </form>
            )}
          </div>

          {/* Terms */}
          <p className="text-center text-xs text-gray-400 mt-6">
            By continuing, you agree to our{' '}
            <a href="/terms" className="text-gray-600 hover:underline">Terms of Service</a>
            {' '}and{' '}
            <a href="/privacy" className="text-gray-600 hover:underline">Privacy Policy</a>.
          </p>
        </div>
      </div>

      {/* Right Side - Showcase */}
      <div className="hidden lg:flex flex-1 relative overflow-hidden">
        <div className={`absolute inset-0 bg-gradient-to-br ${currentShowcase.bgColor} transition-all duration-1000`} />
        
        {/* Badge */}
        <div className="absolute top-6 right-6 z-20">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-white/20 backdrop-blur-sm rounded-full text-white text-sm">
            <span className="w-5 h-5 bg-orange-500 rounded flex items-center justify-center text-xs font-bold">Y</span>
            Combinator S24
          </div>
        </div>

        {/* Content */}
        <div className="relative z-10 flex flex-col items-center justify-center w-full p-12">
          <h2 className="text-5xl font-bold text-white mb-2">
            {currentShowcase.title} 🎉
          </h2>
          <p className="text-white/80 text-lg mb-8">
            {currentShowcase.subtitle}
          </p>

          {/* Mockup Card */}
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-3 h-3 rounded-full bg-red-400" />
              <div className="w-3 h-3 rounded-full bg-yellow-400" />
              <div className="w-3 h-3 rounded-full bg-green-400" />
            </div>
            
            <div className="text-center py-8">
              <p className="text-gray-500 text-sm mb-2">{currentShowcase.highlight}</p>
              <p className="text-5xl font-bold bg-gradient-to-r from-cyan-500 to-blue-500 bg-clip-text text-transparent">
                {currentShowcase.metric}
              </p>
              <p className="text-2xl font-semibold text-gray-800 mt-1">
                {currentShowcase.submetric}
              </p>
              <p className="text-gray-500 text-sm mt-4">
                {currentShowcase.description}
              </p>
            </div>
          </div>

          {/* Carousel Controls */}
          <div className="flex items-center gap-4 mt-8">
            <button
              onClick={() => setCurrentSlide((prev) => (prev - 1 + showcaseItems.length) % showcaseItems.length)}
              className="p-2 rounded-full bg-white/20 hover:bg-white/30 text-white transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            
            <div className="flex gap-2">
              {showcaseItems.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setCurrentSlide(i)}
                  className={`h-2 rounded-full transition-all ${
                    i === currentSlide ? 'w-8 bg-white' : 'w-2 bg-white/40'
                  }`}
                />
              ))}
            </div>
            
            <button
              onClick={() => setCurrentSlide((prev) => (prev + 1) % showcaseItems.length)}
              className="p-2 rounded-full bg-white/20 hover:bg-white/30 text-white transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
