import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Sparkles, MessageSquare, Zap, Shield } from 'lucide-react';

const Login = () => {
  const navigate = useNavigate();

  const handleLogin = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + '/auth/callback';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
      {/* Navigation */}
      <nav className="p-6">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
              <Sparkles size={20} className="text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white">Assistant Melus</h1>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center space-y-8">
          <div className="inline-block">
            <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-2xl">
              <Sparkles size={40} className="text-white" />
            </div>
          </div>
          
          <h1 className="text-6xl font-bold text-white leading-tight">
            Tu Asistente de
            <br />
            <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Inteligencia Artificial
            </span>
          </h1>
          
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Potenciado por los modelos de IA más avanzados. Respuestas inteligentes, conversaciones naturales.
          </p>

          <div className="flex gap-4 justify-center mt-8">
            <Button
              onClick={handleLogin}
              size="lg"
              className="bg-white text-gray-900 hover:bg-gray-100 px-8 py-6 text-lg font-semibold"
            >
              <img 
                src="https://www.google.com/favicon.ico" 
                alt="Google" 
                className="w-5 h-5 mr-2"
              />
              Iniciar con Google
            </Button>
            <Button
              onClick={() => navigate('/pricing')}
              size="lg"
              variant="outline"
              className="border-2 border-white text-white hover:bg-white hover:text-gray-900 px-8 py-6 text-lg font-semibold"
            >
              Ver Precios
            </Button>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mt-32">
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
            <MessageSquare className="w-12 h-12 text-purple-400 mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Conversaciones Inteligentes</h3>
            <p className="text-gray-300">Chatea naturalmente con IA avanzada que entiende contexto y matices.</p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
            <Zap className="w-12 h-12 text-purple-400 mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Respuestas Instantáneas</h3>
            <p className="text-gray-300">Obtiene respuestas rápidas y precisas a cualquier pregunta.</p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
            <Shield className="w-12 h-12 text-purple-400 mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Seguro y Privado</h3>
            <p className="text-gray-300">Tus conversaciones están protegidas y son completamente privadas.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;