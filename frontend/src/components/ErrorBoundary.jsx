import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    // Ignorar errores de removeChild causados por extensiones
    if (error?.message?.includes('removeChild') || 
        error?.message?.includes('not a child of this node')) {
      return { hasError: false };
    }
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Ignorar errores de DOM manipulation de extensiones
    if (error?.message?.includes('removeChild') || 
        error?.message?.includes('not a child of this node') ||
        error?.message?.includes('insertBefore')) {
      console.warn('DOM manipulation error ignored (likely browser extension):', error.message);
      return;
    }
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#0a0a12] flex items-center justify-center">
          <div className="text-center text-white">
            <h1 className="text-2xl font-bold mb-4">Algo salió mal</h1>
            <button 
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-purple-500 rounded-lg hover:bg-purple-600"
            >
              Recargar página
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
