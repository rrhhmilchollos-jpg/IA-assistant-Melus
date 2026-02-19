import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { creditsAPI } from '../api/client';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Check, ArrowLeft, Zap, Loader2, Copy, CheckCircle } from 'lucide-react';
import { toast } from '../hooks/use-toast';

const Pricing = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState({});
  const [customAmount, setCustomAmount] = useState('');
  const [promoCode, setPromoCode] = useState('');
  const [promoCopied, setPromoCopied] = useState(false);

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
      const response = await creditsAPI.createCheckout(packageId, null, promoCode);
      window.location.href = response.checkout_url;
    } catch (error) {
      console.error('Failed to create checkout:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "No se pudo iniciar el proceso de pago",
        variant: "destructive"
      });
      setLoading({ ...loading, [packageId]: false });
    }
  };

  const handleCustomPurchase = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    const amount = parseFloat(customAmount);
    if (!amount || amount < 1) {
      toast({
        title: "Error",
        description: "El monto mínimo es 1€",
        variant: "destructive"
      });
      return;
    }

    setLoading({ ...loading, custom: true });
    
    try {
      const response = await creditsAPI.createCheckout(null, amount, promoCode);
      window.location.href = response.checkout_url;
    } catch (error) {
      console.error('Failed to create checkout:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "No se pudo iniciar el proceso de pago",
        variant: "destructive"
      });
      setLoading({ ...loading, custom: false });
    }
  };

  const copyPromoCode = () => {
    navigator.clipboard.writeText('VALENTINE20');
    setPromoCopied(true);
    setTimeout(() => setPromoCopied(false), 2000);
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
            Volver
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
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Comprar más créditos
          </h1>
          <p className="text-xl text-gray-600 mb-6">
            Obtén 5 créditos por solo 1€! Obtén nuestro mejor paquete con 20% DE DESCUENTO o ingresa un monto personalizado.
          </p>

          {/* Promo Banner */}
          <div className="inline-block bg-gradient-to-r from-pink-500 to-purple-600 rounded-2xl p-1 mb-8">
            <div className="bg-white rounded-xl px-8 py-4">
              <div className="flex items-center gap-4">
                <div className="text-left">
                  <div className="text-sm font-semibold text-gray-600">20% Off</div>
                  <div className="text-xs text-gray-500">en compras superiores a 100€</div>
                </div>
                <div className="flex items-center gap-2 bg-gray-100 px-4 py-2 rounded-lg">
                  <code className="font-mono font-bold text-purple-600">VALENTINE20</code>
                  <button
                    onClick={copyPromoCode}
                    className="hover:bg-gray-200 p-1 rounded transition-colors"
                  >
                    {promoCopied ? (
                      <CheckCircle size={16} className="text-green-600" />
                    ) : (
                      <Copy size={16} className="text-gray-600" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Credit Packages */}
        <div className="grid md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
          {packages.map((pkg) => (
            <Card
              key={pkg.package_id}
              className={`relative ${
                pkg.popular
                  ? 'border-2 border-purple-500 shadow-xl'
                  : 'border border-gray-200'
              }`}
            >
              {pkg.popular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <span className="bg-purple-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
                    Popular
                  </span>
                </div>
              )}
              
              <CardHeader className="pb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-100 to-pink-100 rounded-xl flex items-center justify-center mb-3">
                  <Zap className="text-purple-600" size={24} />
                </div>
                {pkg.bonus > 0 ? (
                  <>
                    <div className="text-gray-400 line-through text-sm">
                      {pkg.base_credits.toLocaleString()} créditos
                    </div>
                    <CardTitle className="text-xl text-purple-600">
                      {pkg.credits.toLocaleString()} créditos
                    </CardTitle>
                  </>
                ) : (
                  <CardTitle className="text-xl">
                    {pkg.credits.toLocaleString()} créditos
                  </CardTitle>
                )}
                <CardDescription>
                  <div className="mt-2">
                    <span className="text-3xl font-bold text-gray-900">
                      {pkg.price}€
                    </span>
                  </div>
                </CardDescription>
              </CardHeader>
              
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
                    'Comprar ahora'
                  )}
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>

        {/* Custom Amount Section */}
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle className="text-center">Ingresar monto personalizado</CardTitle>
            <CardDescription className="text-center">
              $1 = 5 créditos
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Monto en USD
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                    $
                  </span>
                  <Input
                    type="number"
                    min="1"
                    step="1"
                    placeholder="Ingresa el monto"
                    value={customAmount}
                    onChange={(e) => setCustomAmount(e.target.value)}
                    className="pl-8"
                  />
                </div>
                {customAmount && parseFloat(customAmount) >= 1 && (
                  <p className="text-sm text-gray-600 mt-2">
                    Recibirás {(parseFloat(customAmount) * 5).toLocaleString()} créditos
                  </p>
                )}
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Código promocional (opcional)
                </label>
                <Input
                  type="text"
                  placeholder="VALENTINE20"
                  value={promoCode}
                  onChange={(e) => setPromoCode(e.target.value.toUpperCase())}
                />
              </div>
            </div>
          </CardContent>
          <CardFooter>
            <Button
              className="w-full bg-purple-600 hover:bg-purple-700"
              onClick={handleCustomPurchase}
              disabled={loading.custom || !customAmount || parseFloat(customAmount) < 1}
            >
              {loading.custom ? (
                <>
                  <Loader2 size={18} className="mr-2 animate-spin" />
                  Procesando...
                </>
              ) : (
                'Comprar'
              )}
            </Button>
          </CardFooter>
        </Card>

        {/* Info Section */}
        <div className="mt-16 bg-white rounded-2xl p-8 shadow-sm">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            ¿Cómo funcionan los créditos?
          </h3>
          <div className="grid md:grid-cols-3 gap-6 text-gray-700">
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Check className="text-purple-600" />
              </div>
              <h4 className="font-semibold mb-2">1 crédito = 1 token de IA</h4>
              <p className="text-sm">Los créditos se consumen según el uso real de la IA.</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Check className="text-purple-600" />
              </div>
              <h4 className="font-semibold mb-2">Sin expiración</h4>
              <p className="text-sm">Tus créditos nunca expiran, úsalos cuando quieras.</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Check className="text-purple-600" />
              </div>
              <h4 className="font-semibold mb-2">Pago seguro con Stripe</h4>
              <p className="text-sm">Procesado por Stripe, el método de pago más seguro del mundo.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Pricing;
