import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { creditsAPI } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { CheckCircle, Loader2, XCircle } from 'lucide-react';

const Success = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { updateCredits, checkAuth } = useAuth();
  const [status, setStatus] = useState('checking'); // checking, success, error
  const [creditsAdded, setCreditsAdded] = useState(0);
  const [attempts, setAttempts] = useState(0);

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    
    if (!sessionId) {
      setStatus('error');
      return;
    }

    checkPaymentStatus(sessionId);
  }, [searchParams]);

  const checkPaymentStatus = async (sessionId, attempt = 0) => {
    const maxAttempts = 5;
    
    if (attempt >= maxAttempts) {
      setStatus('error');
      return;
    }

    try {
      const response = await creditsAPI.getCheckoutStatus(sessionId);
      
      if (response.payment_status === 'paid') {
        setCreditsAdded(response.credits_added);
        setStatus('success');
        // Refresh user data
        await checkAuth();
      } else if (response.status === 'expired') {
        setStatus('error');
      } else {
        // Keep polling
        setAttempts(attempt + 1);
        setTimeout(() => checkPaymentStatus(sessionId, attempt + 1), 2000);
      }
    } catch (error) {
      console.error('Payment status check failed:', error);
      if (attempt < maxAttempts - 1) {
        setAttempts(attempt + 1);
        setTimeout(() => checkPaymentStatus(sessionId, attempt + 1), 2000);
      } else {
        setStatus('error');
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        {status === 'checking' && (
          <div className="bg-white rounded-2xl p-8 shadow-xl text-center">
            <Loader2 className="w-16 h-16 animate-spin text-purple-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Verificando pago...
            </h2>
            <p className="text-gray-600">
              Por favor espera mientras confirmamos tu pago
            </p>
            {attempts > 0 && (
              <p className="text-sm text-gray-500 mt-4">
                Intento {attempts + 1} de 5
              </p>
            )}
          </div>
        )}

        {status === 'success' && (
          <div className="bg-white rounded-2xl p-8 shadow-xl text-center">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-12 h-12 text-green-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              ¡Pago Exitoso!
            </h2>
            <p className="text-gray-600 mb-6">
              Se han agregado {creditsAdded.toLocaleString()} créditos a tu cuenta
            </p>
            <Button
              onClick={() => navigate('/dashboard')}
              className="w-full bg-purple-600 hover:bg-purple-700"
              size="lg"
            >
              Ir al Chat
            </Button>
          </div>
        )}

        {status === 'error' && (
          <div className="bg-white rounded-2xl p-8 shadow-xl text-center">
            <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <XCircle className="w-12 h-12 text-red-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Error en el Pago
            </h2>
            <p className="text-gray-600 mb-6">
              Hubo un problema al procesar tu pago. Por favor intenta nuevamente.
            </p>
            <div className="flex gap-3">
              <Button
                onClick={() => navigate('/pricing')}
                className="flex-1 bg-purple-600 hover:bg-purple-700"
              >
                Reintentar
              </Button>
              <Button
                onClick={() => navigate('/dashboard')}
                variant="outline"
                className="flex-1"
              >
                Volver
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Success;