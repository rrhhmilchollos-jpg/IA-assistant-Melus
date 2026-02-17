import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { creditsAPI } from '../api/client';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
import { Check, ArrowLeft, Zap, Loader2 } from 'lucide-react';
import { toast } from '../hooks/use-toast';

const Pricing = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState({});

  useEffect(() => {
    loadPackages();
  }, []);

  const loadPackages = async () => {
    try {
      const pkgs = await creditsAPI.getPackages();
      setPackages(pkgs);
    } catch (error) {
      console.error('Failed to load packages:', error);
    }
  };

  const handlePurchase = async (packageId) => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    setLoading({ ...loading, [packageId]: true });
    
    try {
      const response = await creditsAPI.createCheckout(packageId);
      // Redirect to Stripe checkout
      window.location.href = response.checkout_url;
    } catch (error) {
      console.error('Failed to create checkout:', error);
      toast({
        title: "Error",
        description: "No se pudo iniciar el proceso de pago",
        variant: "destructive"
      });
      setLoading({ ...loading, [packageId]: false });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Navigation */}
      <nav className="bg-white border-b p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Button
            variant="ghost"
            onClick={() => navigate(isAuthenticated ? '/dashboard' : '/login')}
          >
            <ArrowLeft size={20} className="mr-2" />
            {isAuthenticated ? 'Volver al Chat' : 'Volver'}
          </Button>
          
          {user && (
            <div className="flex items-center gap-2 bg-purple-50 px-4 py-2 rounded-lg">
              <Zap size={18} className="text-purple-600" />
              <span className="font-semibold text-purple-900">
                {user.credits.toLocaleString()} créditos
              </span>
            </div>
          )}
        </div>
      </nav>

      {/* Pricing Section */}
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Elige tu Plan de Créditos
          </h1>
          <p className="text-xl text-gray-600">
            Compra créditos y úsalos cuando lo necesites. Sin suscripciones.
          </p>
        </div>

        <div className="grid md:grid-cols-4 gap-6">
          {packages.map((pkg) => (
            <Card
              key={pkg.package_id}
              className={`relative ${
                pkg.popular
                  ? 'border-2 border-purple-500 shadow-xl scale-105'
                  : 'border border-gray-200'
              }`}
            >
              {pkg.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-purple-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                    Popular
                  </span>
                </div>
              )}
              
              <CardHeader>
                <CardTitle className="text-2xl">{pkg.name}</CardTitle>
                <CardDescription>
                  <div className="mt-4">
                    <span className="text-4xl font-bold text-gray-900">
                      ${pkg.price}
                    </span>
                    <span className="text-gray-600 ml-2">USD</span>
                  </div>
                </CardDescription>
              </CardHeader>
              
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Check size={18} className="text-green-600" />
                    <span className="text-gray-700">
                      {pkg.credits.toLocaleString()} créditos
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check size={18} className="text-green-600" />
                    <span className="text-gray-700">
                      ~{Math.floor(pkg.credits / 1500)} mensajes
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check size={18} className="text-green-600" />
                    <span className="text-gray-700">Sin expiración</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check size={18} className="text-green-600" />
                    <span className="text-gray-700">Uso flexible</span>
                  </div>
                </div>
              </CardContent>
              
              <CardFooter>
                <Button
                  className={`w-full ${
                    pkg.popular
                      ? 'bg-purple-600 hover:bg-purple-700'
                      : 'bg-gray-900 hover:bg-gray-800'
                  }`}
                  onClick={() => handlePurchase(pkg.package_id)}
                  disabled={loading[pkg.package_id]}
                >
                  {loading[pkg.package_id] ? (
                    <>
                      <Loader2 size={18} className="mr-2 animate-spin" />
                      Procesando...
                    </>
                  ) : (
                    'Comprar Ahora'
                  )}
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>

        {/* Info Section */}
        <div className="mt-16 bg-white rounded-2xl p-8 shadow-sm">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            ¿Cómo funcionan los créditos?
          </h3>
          <div className="grid md:grid-cols-3 gap-6 text-gray-700">
            <div>
              <h4 className="font-semibold mb-2">1 crédito = 1 token</h4>
              <p className="text-sm">Los créditos se consumen según el uso real de la IA.</p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Sin expiración</h4>
              <p className="text-sm">Tus créditos nunca expiran, úsalos cuando quieras.</p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Pago seguro</h4>
              <p className="text-sm">Procesado por Stripe, el método de pago más seguro.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Pricing;