import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { CheckCircle, Loader2, XCircle, Sparkles, Zap, Crown, ArrowRight } from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const Success = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { checkAuth } = useAuth();
  const [status, setStatus] = useState('checking');
  const [result, setResult] = useState(null);
  const [attempts, setAttempts] = useState(0);

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    const plan = searchParams.get('plan');
    const credits = searchParams.get('credits');
    
    if (sessionId) {
      verifySession(sessionId);
    } else if (plan || credits) {
      // Direct success without session verification
      setStatus('success');
      setResult({
        type: plan ? 'subscription' : 'credits',
        plan: plan,
        credits: credits ? parseInt(credits) : 0
      });
    } else {
      setStatus('error');
    }
  }, [searchParams]);

  const verifySession = async (sessionId, attempt = 0) => {
    const maxAttempts = 5;
    
    if (attempt >= maxAttempts) {
      setStatus('error');
      return;
    }

    try {
      const token = localStorage.getItem('session_token');
      const response = await fetch(`${API_BASE}/api/stripe/verify-session/${sessionId}`, {
        headers: { 'X-Session-Token': token }
      });
      
      const data = await response.json();
      
      if (data.success) {
        setResult(data);
        setStatus('success');
        await checkAuth();
      } else {
        setAttempts(attempt + 1);
        setTimeout(() => verifySession(sessionId, attempt + 1), 2000);
      }
    } catch (error) {
      console.error('Verification failed:', error);
      if (attempt < maxAttempts - 1) {
        setAttempts(attempt + 1);
        setTimeout(() => verifySession(sessionId, attempt + 1), 2000);
      } else {
        setStatus('error');
      }
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        {status === 'checking' && (
          <div className="bg-[#111] border border-[#222] rounded-2xl p-8 text-center">
            <Loader2 className="w-16 h-16 animate-spin text-cyan-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-white mb-2">
              Verifying payment...
            </h2>
            <p className="text-gray-400">
              Please wait while we confirm your payment
            </p>
            {attempts > 0 && (
              <p className="text-sm text-gray-500 mt-4">
                Attempt {attempts + 1} of 5
              </p>
            )}
          </div>
        )}

        {status === 'success' && (
          <div className="bg-[#111] border border-[#222] rounded-2xl p-8 text-center">
            <div className="w-20 h-20 bg-gradient-to-br from-green-500/20 to-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-10 h-10 text-green-400" />
            </div>
            
            <h2 className="text-3xl font-bold text-white mb-2">
              Payment Successful!
            </h2>
            
            {result?.type === 'subscription' ? (
              <div className="mb-6">
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-full mb-4">
                  <Crown className="w-5 h-5 text-cyan-400" />
                  <span className="text-cyan-400 font-medium capitalize">
                    {result.plan} Plan Active
                  </span>
                </div>
                <p className="text-gray-400">
                  {result.unlimited ? 'Unlimited credits unlocked!' : 'Your subscription is now active.'}
                </p>
              </div>
            ) : (
              <div className="mb-6">
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 rounded-full mb-4">
                  <Zap className="w-5 h-5 text-yellow-400" />
                  <span className="text-yellow-400 font-medium">
                    +{result?.added?.toLocaleString() || result?.credits?.toLocaleString() || 0} Credits
                  </span>
                </div>
                <p className="text-gray-400">
                  Credits have been added to your account.
                </p>
              </div>
            )}
            
            <button
              onClick={() => navigate('/builder')}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white rounded-xl font-medium transition-colors"
            >
              Start Building
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {status === 'error' && (
          <div className="bg-[#111] border border-[#222] rounded-2xl p-8 text-center">
            <div className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <XCircle className="w-10 h-10 text-red-400" />
            </div>
            
            <h2 className="text-3xl font-bold text-white mb-2">
              Payment Error
            </h2>
            <p className="text-gray-400 mb-6">
              There was a problem processing your payment. Please try again.
            </p>
            
            <div className="flex gap-3">
              <button
                onClick={() => navigate('/pricing')}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white rounded-xl font-medium transition-colors"
              >
                Try Again
              </button>
              <button
                onClick={() => navigate('/builder')}
                className="flex-1 px-6 py-3 bg-[#222] hover:bg-[#333] text-white rounded-xl font-medium transition-colors"
              >
                Go Back
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Success;