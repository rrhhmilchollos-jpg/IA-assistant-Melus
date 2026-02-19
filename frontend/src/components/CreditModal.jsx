import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { creditsAPI } from '../api/client';
import { Button } from '../components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../components/ui/collapsible';
import { Coins, Copy, CheckCircle, ChevronDown, X } from 'lucide-react';
import { toast } from '../hooks/use-toast';

const CreditModal = ({ isOpen, onClose }) => {
  const { user } = useAuth();
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState({});
  const [customAmount, setCustomAmount] = useState('');
  const [promoCode, setPromoCode] = useState('');
  const [promoCopied, setPromoCopied] = useState(false);
  const [isInfoOpen, setIsInfoOpen] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadPackages();
    }
  }, [isOpen]);

  const loadPackages = async () => {
    try {
      const pkgs = await creditsAPI.getPackages();
      setPackages(pkgs);
    } catch (error) {
      console.error('Failed to load packages:', error);
    }
  };

  const handlePurchase = async (packageId) => {
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

  const isPremium = (packageId) => {
    return packageId === 'package_3000' || packageId === 'package_6000';
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-5xl bg-gray-900/95 backdrop-blur-xl border-gray-700 text-white max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-3 mb-4">
            <Coins className="w-8 h-8 text-yellow-500" />
            <DialogTitle className="text-2xl text-white">Comprar más créditos</DialogTitle>
          </div>
        </DialogHeader>

        {/* Promo Banner */}
        <div className="bg-gradient-to-r from-orange-500 to-orange-400 rounded-lg p-4 flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="text-white font-semibold">🎁 20% Off</span>
            <span className="text-white/90 text-sm">en compras superiores a 100€</span>
          </div>
          <div className="flex items-center gap-2 bg-white/20 px-4 py-2 rounded-lg">
            <code className="font-mono font-bold text-white">VALENTINE20</code>
            <button
              onClick={copyPromoCode}
              className="hover:bg-white/20 p-1 rounded transition-colors"
            >
              {promoCopied ? (
                <CheckCircle size={18} className="text-white" />
              ) : (
                <Copy size={18} className="text-white" />
              )}
            </button>
          </div>
        </div>

        {/* Description */}
        <p className="text-gray-300 text-center mb-6">
          Obtén <span className="text-green-400 font-semibold">5 créditos</span> por solo{' '}
          <span className="text-green-400 font-semibold">1€</span>! Obtén nuestro mejor paquete con{' '}
          <span className="text-orange-400 font-semibold">20% DE DESCUENTO</span> o ingresa un monto personalizado.
        </p>

        {/* Credit Packages */}
        <div className="grid grid-cols-5 gap-3 mb-6">
          {packages.map((pkg) => {
            const premium = isPremium(pkg.package_id);
            return (
              <div
                key={pkg.package_id}
                className={`rounded-xl p-4 text-center ${
                  premium 
                    ? 'bg-gradient-to-br from-yellow-600/20 to-orange-600/20 border-2 border-yellow-500/50' 
                    : 'bg-gray-800/50 border border-gray-700'
                }`}
              >
                <div className={`w-12 h-12 rounded-full mx-auto mb-3 flex items-center justify-center ${
                  premium ? 'bg-gradient-to-br from-yellow-400 to-orange-500' : 'bg-gray-700'
                }`}>
                  <Coins className="text-white" size={24} />
                </div>
                
                {pkg.bonus > 0 && (
                  <div className="text-gray-500 line-through text-xs mb-1">
                    {pkg.base_credits.toLocaleString()} créditos
                  </div>
                )}
                
                <div className={`font-bold mb-2 text-base ${premium ? 'text-yellow-400' : 'text-white'}`}>
                  {pkg.credits.toLocaleString()} créditos
                </div>
                
                <div className="text-xl font-bold text-white mb-3">
                  ${pkg.price.toLocaleString()}
                </div>
                
                <Button
                  className={`w-full ${
                    premium
                      ? 'bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 text-white font-semibold'
                      : 'bg-gray-700 hover:bg-gray-600 text-white'
                  }`}
                  onClick={() => handlePurchase(pkg.package_id)}
                  disabled={loading[pkg.package_id]}
                  size="sm"
                >
                  {loading[pkg.package_id] ? 'Procesando...' : 'Comprar ahora'}
                </Button>
              </div>
            );
          })}
        </div>

        {/* Custom Amount */}
        <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-3">
            <Input
              type="text"
              placeholder="+ Ingresar monto personalizado ($)"
              value={customAmount}
              onChange={(e) => setCustomAmount(e.target.value.replace(/[^0-9.]/g, ''))}
              className="flex-1 bg-gray-900 border-gray-700 text-white placeholder:text-gray-500"
            />
            <Button
              onClick={handleCustomPurchase}
              disabled={loading.custom || !customAmount || parseFloat(customAmount) < 1}
              className="bg-gray-700 hover:bg-gray-600 px-8"
            >
              {loading.custom ? 'Procesando...' : 'Comprar'}
            </Button>
          </div>
        </div>

        {/* How Credits Work - Collapsible */}
        <Collapsible open={isInfoOpen} onOpenChange={setIsInfoOpen}>
          <CollapsibleTrigger className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors w-full">
            <span className="text-sm">¿Cómo funcionan los créditos?</span>
            <ChevronDown 
              className={`w-4 h-4 transition-transform ${isInfoOpen ? 'rotate-180' : ''}`} 
            />
          </CollapsibleTrigger>
          <CollapsibleContent className="mt-4">
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div className="bg-gray-800/50 rounded-lg p-4">
                <div className="text-green-400 font-semibold mb-2">1 crédito = 1 token de IA</div>
                <p className="text-gray-400">Los créditos se consumen según el uso real de la IA.</p>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4">
                <div className="text-blue-400 font-semibold mb-2">Sin expiración</div>
                <p className="text-gray-400">Tus créditos nunca expiran, úsalos cuando quieras.</p>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4">
                <div className="text-purple-400 font-semibold mb-2">Pago seguro</div>
                <p className="text-gray-400">Procesado por Stripe, el método más seguro.</p>
              </div>
            </div>
          </CollapsibleContent>
        </Collapsible>
      </DialogContent>
    </Dialog>
  );
};

export default CreditModal;
