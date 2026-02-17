import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import AgentConsole from '../components/AgentConsole';
import { ArrowLeft } from 'lucide-react';

const GeneratorPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleProjectCreated = (project) => {
    console.log('Project created:', project);
  };

  return (
    <div className="min-h-screen bg-[#0d0d1a]" data-testid="generator-page">
      {/* Simple Header */}
      <header className="bg-[#1a1a2e] border-b border-purple-500/20 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              Volver
            </button>
            <h1 className="text-xl font-bold text-white">Generador de Apps</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-sm">
              {user?.credits || 0} créditos
            </span>
            {user?.is_admin && (
              <button
                onClick={() => navigate('/admin')}
                className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded text-sm"
              >
                Admin
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Agent Console */}
      <AgentConsole onProjectCreated={handleProjectCreated} />
    </div>
  );
};

export default GeneratorPage;
