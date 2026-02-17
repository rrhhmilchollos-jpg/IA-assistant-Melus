import React, { useState, useEffect } from 'react';
import { Github, ExternalLink, Check, X, Loader2, Upload, FolderGit2, Lock, Globe } from 'lucide-react';
import { Button } from './ui/button';
import { githubAPI } from '../api/client';
import { toast } from '../hooks/use-toast';

const GitHubIntegration = ({ projectId = null, conversationId = null, onPushSuccess }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pushing, setPushing] = useState(false);
  const [repos, setRepos] = useState([]);
  const [showRepoModal, setShowRepoModal] = useState(false);
  const [repoName, setRepoName] = useState('');
  const [isPrivate, setIsPrivate] = useState(false);
  const [createNew, setCreateNew] = useState(true);
  const [selectedRepo, setSelectedRepo] = useState('');

  useEffect(() => {
    checkGitHubStatus();
  }, []);

  const checkGitHubStatus = async () => {
    setLoading(true);
    try {
      const result = await githubAPI.getStatus();
      setStatus(result);
      if (result.connected) {
        loadRepos();
      }
    } catch (error) {
      console.error('Failed to check GitHub status:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRepos = async () => {
    try {
      const result = await githubAPI.listRepos();
      setRepos(result.repositories || []);
    } catch (error) {
      console.error('Failed to load repos:', error);
    }
  };

  const handleConnect = async () => {
    try {
      const result = await githubAPI.login();
      if (result.auth_url) {
        window.location.href = result.auth_url;
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "No se pudo conectar con GitHub",
        variant: "destructive"
      });
    }
  };

  const handleDisconnect = async () => {
    try {
      await githubAPI.disconnect();
      setStatus({ connected: false });
      toast({
        title: "GitHub desconectado",
        description: "Tu cuenta de GitHub ha sido desconectada"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "No se pudo desconectar GitHub",
        variant: "destructive"
      });
    }
  };

  const handlePush = async () => {
    setPushing(true);
    try {
      let result;
      const finalRepoName = createNew ? repoName : selectedRepo;
      
      if (projectId) {
        result = await githubAPI.pushProject(projectId, finalRepoName, createNew, isPrivate);
      } else if (conversationId) {
        result = await githubAPI.pushConversation(conversationId, finalRepoName, isPrivate);
      } else {
        throw new Error("No project or conversation specified");
      }

      toast({
        title: "¡Subido a GitHub!",
        description: `${result.files_pushed} archivos subidos a ${result.repo_name}`
      });

      setShowRepoModal(false);
      if (onPushSuccess) onPushSuccess(result);
      
      // Open repo in new tab
      if (result.repo_url) {
        window.open(result.repo_url, '_blank');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "No se pudo subir a GitHub",
        variant: "destructive"
      });
    } finally {
      setPushing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-gray-400">
        <Loader2 className="w-4 h-4 animate-spin" />
        <span className="text-sm">Verificando GitHub...</span>
      </div>
    );
  }

  return (
    <div className="space-y-4" data-testid="github-integration">
      {/* Connection Status */}
      <div className="flex items-center justify-between p-4 bg-[#1a1a2e] rounded-lg border border-purple-500/20">
        <div className="flex items-center gap-3">
          <Github className="w-6 h-6 text-white" />
          <div>
            <p className="font-medium text-white">GitHub</p>
            {status?.connected ? (
              <p className="text-sm text-green-400 flex items-center gap-1">
                <Check className="w-3 h-3" />
                Conectado como @{status.username}
              </p>
            ) : (
              <p className="text-sm text-gray-400">No conectado</p>
            )}
          </div>
        </div>
        
        {status?.connected ? (
          <div className="flex items-center gap-2">
            <Button
              onClick={() => setShowRepoModal(true)}
              disabled={!projectId && !conversationId}
              className="bg-purple-500 hover:bg-purple-600 text-white"
              data-testid="push-to-github-btn"
            >
              <Upload className="w-4 h-4 mr-2" />
              Subir a GitHub
            </Button>
            <Button
              variant="ghost"
              onClick={handleDisconnect}
              className="text-red-400 hover:text-red-300 hover:bg-red-500/20"
            >
              Desconectar
            </Button>
          </div>
        ) : (
          <Button
            onClick={handleConnect}
            className="bg-gray-700 hover:bg-gray-600 text-white"
            data-testid="connect-github-btn"
          >
            <Github className="w-4 h-4 mr-2" />
            Conectar GitHub
          </Button>
        )}
      </div>

      {/* Push Modal */}
      {showRepoModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50" onClick={() => setShowRepoModal(false)}>
          <div 
            className="bg-[#1a1a2e] rounded-xl p-6 w-full max-w-md border border-purple-500/30"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <FolderGit2 className="w-5 h-5 text-purple-400" />
                Subir a GitHub
              </h3>
              <button onClick={() => setShowRepoModal(false)} className="text-gray-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              {/* Create new vs existing */}
              <div className="flex gap-4">
                <button
                  onClick={() => setCreateNew(true)}
                  className={`flex-1 p-3 rounded-lg border transition-colors ${
                    createNew 
                      ? 'border-purple-500 bg-purple-500/20 text-purple-400' 
                      : 'border-gray-700 text-gray-400 hover:border-gray-600'
                  }`}
                >
                  Crear nuevo repo
                </button>
                <button
                  onClick={() => setCreateNew(false)}
                  disabled={repos.length === 0}
                  className={`flex-1 p-3 rounded-lg border transition-colors ${
                    !createNew 
                      ? 'border-purple-500 bg-purple-500/20 text-purple-400' 
                      : 'border-gray-700 text-gray-400 hover:border-gray-600'
                  } ${repos.length === 0 ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  Repo existente
                </button>
              </div>

              {createNew ? (
                <>
                  {/* Repo name */}
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Nombre del repositorio</label>
                    <input
                      type="text"
                      value={repoName}
                      onChange={(e) => setRepoName(e.target.value)}
                      placeholder="mi-proyecto"
                      className="w-full bg-[#0d0d1a] border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-purple-500 outline-none"
                      data-testid="repo-name-input"
                    />
                  </div>

                  {/* Privacy */}
                  <div className="flex items-center gap-4">
                    <button
                      onClick={() => setIsPrivate(false)}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${
                        !isPrivate 
                          ? 'border-green-500 bg-green-500/20 text-green-400' 
                          : 'border-gray-700 text-gray-400'
                      }`}
                    >
                      <Globe className="w-4 h-4" />
                      Público
                    </button>
                    <button
                      onClick={() => setIsPrivate(true)}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${
                        isPrivate 
                          ? 'border-yellow-500 bg-yellow-500/20 text-yellow-400' 
                          : 'border-gray-700 text-gray-400'
                      }`}
                    >
                      <Lock className="w-4 h-4" />
                      Privado
                    </button>
                  </div>
                </>
              ) : (
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Seleccionar repositorio</label>
                  <select
                    value={selectedRepo}
                    onChange={(e) => setSelectedRepo(e.target.value)}
                    className="w-full bg-[#0d0d1a] border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-purple-500 outline-none"
                  >
                    <option value="">Selecciona un repositorio</option>
                    {repos.map(repo => (
                      <option key={repo.name} value={repo.name}>
                        {repo.name} {repo.private ? '🔒' : '🌐'}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Cost info */}
              <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                <p className="text-sm text-yellow-400">
                  Costo: {projectId ? '100' : '50'} créditos
                </p>
              </div>

              {/* Push button */}
              <Button
                onClick={handlePush}
                disabled={pushing || (createNew ? !repoName.trim() : !selectedRepo)}
                className="w-full bg-purple-500 hover:bg-purple-600 text-white"
                data-testid="confirm-push-btn"
              >
                {pushing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Subiendo...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    Subir a GitHub
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GitHubIntegration;
