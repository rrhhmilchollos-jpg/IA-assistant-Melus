import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Animated falling code background - Matrix style
const CodeBackground = () => {
  const canvasRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*(){}[]<>/\\|~`+-=';
    const fontSize = 14;
    let columns;
    let drops = [];
    
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      columns = Math.floor(canvas.width / fontSize);
      drops = Array(columns).fill(1);
    };
    
    resize();
    window.addEventListener('resize', resize);
    
    const draw = () => {
      // Fade effect
      ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      ctx.fillStyle = 'rgba(100, 100, 120, 0.12)';
      ctx.font = `${fontSize}px monospace`;
      
      for (let i = 0; i < drops.length; i++) {
        const char = chars[Math.floor(Math.random() * chars.length)];
        const x = i * fontSize;
        const y = drops[i] * fontSize;
        
        ctx.fillText(char, x, y);
        
        if (y > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
        }
        drops[i]++;
      }
    };
    
    const interval = setInterval(draw, 45);
    
    return () => {
      clearInterval(interval);
      window.removeEventListener('resize', resize);
    };
  }, []);
  
  return (
    <canvas 
      ref={canvasRef} 
      className="absolute inset-0 pointer-events-none"
      style={{ opacity: 0.6 }}
    />
  );
};

// Animated "e" Logo
const AnimatedLogo = () => {
  return (
    <div className="relative w-20 h-20 mb-8">
      {/* Outer glow pulse */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-cyan-400/30 to-blue-500/30 animate-pulse" />
      
      {/* Inner box */}
      <div className="absolute inset-1 rounded-xl bg-black border border-gray-700/80 flex items-center justify-center overflow-hidden">
        {/* Gradient shimmer */}
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-transparent to-blue-500/5" />
        
        {/* The "e" letter */}
        <span 
          className="text-5xl font-bold text-white relative z-10 select-none"
          style={{
            fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
            textShadow: '0 0 30px rgba(34, 211, 238, 0.4), 0 0 60px rgba(34, 211, 238, 0.2)'
          }}
        >
          e
        </span>
        
        {/* Shine animation overlay */}
        <div 
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full"
          style={{
            animation: 'shine 3s ease-in-out infinite'
          }}
        />
      </div>
    </div>
  );
};

// Right panel showcase carousel
const ShowcaseCarousel = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  
  const slides = [
    {
      metric: "$100M ARR",
      subtext: "in 8 months",
      description: "One of the fastest startups to reach this milestone."
    },
    {
      metric: "500K+",
      subtext: "apps created",
      description: "Join thousands building the future with AI."
    },
    {
      metric: "10x Faster",
      subtext: "development",
      description: "Ship products in minutes, not months."
    }
  ];
  
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 4000);
    return () => clearInterval(timer);
  }, [slides.length]);
  
  return (
    <div className="relative w-full h-full flex flex-col items-center justify-center p-8">
      {/* Background dots pattern */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, rgba(255,255,255,0.3) 1px, transparent 0)`,
          backgroundSize: '24px 24px'
        }}
      />
      
      {/* Content card */}
      <div className="relative bg-black/40 backdrop-blur-sm rounded-2xl border border-white/10 p-8 max-w-sm w-full">
        {/* Window dots */}
        <div className="flex gap-2 mb-6">
          <div className="w-3 h-3 rounded-full bg-red-500/80" />
          <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
          <div className="w-3 h-3 rounded-full bg-green-500/80" />
        </div>
        
        {/* Slide content */}
        {slides.map((slide, index) => (
          <div
            key={index}
            className={`transition-all duration-500 ${
              currentSlide === index 
                ? 'opacity-100 translate-y-0' 
                : 'opacity-0 translate-y-4 absolute'
            }`}
          >
            {currentSlide === index && (
              <div className="text-center">
                <p className="text-gray-400 text-sm mb-2">Melus AI reaches</p>
                <p className="text-5xl font-bold text-white mb-1">
                  {slide.metric}
                </p>
                <p className="text-2xl font-semibold text-cyan-400 mb-4">
                  {slide.subtext}
                </p>
                <p className="text-gray-400 text-sm">
                  {slide.description}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
      
      {/* Carousel indicators */}
      <div className="flex gap-2 mt-8">
        {slides.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentSlide(index)}
            className={`h-2 rounded-full transition-all duration-300 ${
              currentSlide === index 
                ? 'w-8 bg-white' 
                : 'w-2 bg-white/30 hover:bg-white/50'
            }`}
          />
        ))}
      </div>
      
      {/* Emoji celebration */}
      <div className="absolute top-8 right-8 text-4xl animate-bounce">
        🎉
      </div>
    </div>
  );
};

const LandingPage = () => {
  const navigate = useNavigate();
  const { user, isLoading } = useAuth();
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

  // Handle Google login
  const handleGoogleAuth = () => {
    window.location.href = `${API_BASE}/api/auth/google`;
  };

  // Handle GitHub login
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

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden flex">
      {/* Animated code background */}
      <CodeBackground />
      
      {/* Left side - Auth section */}
      <div className="flex-1 relative z-10 flex flex-col items-center justify-center px-8 py-12">
        <div className="w-full max-w-md">
          {/* Y Combinator Badge */}
          <div className="flex justify-center mb-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-orange-500/10 border border-orange-500/40 rounded-full">
              <div className="w-5 h-5 bg-orange-500 rounded flex items-center justify-center">
                <span className="text-white text-xs font-bold">Y</span>
              </div>
              <span className="text-orange-400 text-sm font-medium">Combinator S24</span>
            </div>
          </div>
          
          {/* Animated Logo */}
          <div className="flex justify-center">
            <AnimatedLogo />
          </div>
          
          {/* Title */}
          <h1 className="text-center mb-2">
            <span className="text-4xl md:text-5xl font-bold text-white block">
              Build Full-Stack
            </span>
          </h1>
          <h2 className="text-center mb-10">
            <span className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              Web & Mobile Apps in minutes
            </span>
          </h2>
          
          {/* Auth buttons */}
          <div className="space-y-4">
            {!showEmailForm ? (
              <>
                {/* Continue with Google - Main CTA */}
                <button
                  onClick={handleGoogleAuth}
                  disabled={authLoading}
                  className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-gray-900 hover:bg-gray-800 border border-gray-700 text-white font-medium rounded-xl transition-all disabled:opacity-50"
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
                
                {/* Social login row */}
                <div className="flex gap-3">
                  {/* GitHub */}
                  <button
                    onClick={handleGitHubAuth}
                    disabled={authLoading}
                    className="flex-1 flex items-center justify-center px-4 py-3.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl transition-all disabled:opacity-50"
                    data-testid="github-login-btn"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd"/>
                    </svg>
                  </button>
                  
                  {/* Apple - disabled */}
                  <button
                    disabled
                    className="flex-1 flex items-center justify-center px-4 py-3.5 bg-gray-800/50 border border-gray-700/50 rounded-xl opacity-40 cursor-not-allowed"
                    title="Coming soon"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
                    </svg>
                  </button>
                  
                  {/* Facebook - disabled */}
                  <button
                    disabled
                    className="flex-1 flex items-center justify-center px-4 py-3.5 bg-gray-800/50 border border-gray-700/50 rounded-xl opacity-40 cursor-not-allowed"
                    title="Coming soon"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                    </svg>
                  </button>
                </div>
                
                {/* Divider */}
                <div className="flex items-center gap-4 py-2">
                  <div className="flex-1 h-px bg-gray-800" />
                  <span className="text-gray-500 text-sm">OR</span>
                  <div className="flex-1 h-px bg-gray-800" />
                </div>
                
                {/* Continue with Email */}
                <button
                  onClick={() => setShowEmailForm(true)}
                  className="w-full px-6 py-4 bg-transparent hover:bg-gray-900 border border-gray-700 text-white font-medium rounded-xl transition-all"
                  data-testid="email-toggle-btn"
                >
                  Continue with Email
                </button>
              </>
            ) : (
              /* Email Form */
              <form onSubmit={handleEmailAuth} className="space-y-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowEmailForm(false);
                    setError('');
                  }}
                  className="flex items-center gap-1 text-sm text-gray-400 hover:text-white transition-colors mb-4"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Back
                </button>
                
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email address"
                  className="w-full px-4 py-4 bg-gray-900 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 transition-colors"
                  data-testid="email-input"
                  required
                  autoFocus
                />
                
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                  className="w-full px-4 py-4 bg-gray-900 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 transition-colors"
                  data-testid="password-input"
                  required
                />
                
                {error && (
                  <p className="text-red-400 text-sm text-center py-2">{error}</p>
                )}
                
                <button
                  type="submit"
                  disabled={authLoading}
                  className="w-full px-6 py-4 bg-white hover:bg-gray-100 text-black font-medium rounded-xl transition-all disabled:opacity-50"
                  data-testid="email-submit-btn"
                >
                  {authLoading ? (
                    <span className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                      Loading...
                    </span>
                  ) : (
                    isLogin ? 'Sign In' : 'Create Account'
                  )}
                </button>
                
                <p className="text-center text-gray-400 text-sm">
                  {isLogin ? "Don't have an account? " : "Already have an account? "}
                  <button
                    type="button"
                    onClick={() => {
                      setIsLogin(!isLogin);
                      setError('');
                    }}
                    className="text-cyan-400 hover:text-cyan-300 font-medium"
                  >
                    {isLogin ? 'Sign Up' : 'Sign In'}
                  </button>
                </p>
              </form>
            )}
          </div>
          
          {/* Terms and Privacy */}
          <p className="text-center text-gray-600 text-sm mt-8">
            By continuing, you agree to our{' '}
            <a href="/terms" className="text-gray-400 hover:text-white underline">
              Terms of Service
            </a>{' '}
            and{' '}
            <a href="/privacy" className="text-gray-400 hover:text-white underline">
              Privacy Policy
            </a>
          </p>
        </div>
      </div>
      
      {/* Right side - Showcase panel (cyan/turquoise) */}
      <div className="hidden lg:flex flex-1 relative bg-gradient-to-br from-cyan-500 via-teal-500 to-emerald-500">
        <ShowcaseCarousel />
      </div>
      
      {/* Global styles for animations */}
      <style>{`
        @keyframes shine {
          0% { transform: translateX(-100%); }
          50%, 100% { transform: translateX(200%); }
        }
      `}</style>
    </div>
  );
};

export default LandingPage;
