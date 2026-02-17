import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Zap, CreditCard, User, LogOut, Settings, Receipt } from 'lucide-react';
import { Button } from './ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import CreditModal from './CreditModal';
import TransactionHistory from './TransactionHistory';

const Header = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [isCreditModalOpen, setIsCreditModalOpen] = useState(false);
  const [isTransactionHistoryOpen, setIsTransactionHistoryOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <>
      <header className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">M</span>
            </div>
            <h1 className="text-xl font-bold text-gray-900">Assistant Melus</h1>
          </div>

          {/* Right side - Credits and User */}
          <div className="flex items-center gap-4">
            {/* Credits Display */}
            <button
              onClick={() => setIsCreditModalOpen(true)}
              className="flex items-center gap-2 bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg px-4 py-2 hover:from-purple-100 hover:to-pink-100 transition-all"
            >
              <Zap size={18} className="text-yellow-500" />
              <div className="flex flex-col items-start">
                <span className="text-xs text-gray-600 font-medium">Créditos</span>
                <span className="text-lg font-bold text-purple-900">
                  {user?.credits?.toLocaleString() || 0}
                </span>
              </div>
              <CreditCard size={16} className="text-purple-600 ml-2" />
            </button>

            {/* User Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-3 hover:bg-gray-50 rounded-lg px-3 py-2 transition-colors">
                  {user?.picture ? (
                    <img 
                      src={user.picture} 
                      alt={user.name}
                      className="w-8 h-8 rounded-full border-2 border-purple-200"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center">
                      <User size={16} className="text-white" />
                    </div>
                  )}
                  <div className="text-left hidden md:block">
                    <div className="text-sm font-semibold text-gray-900">
                      {user?.name || 'Usuario'}
                    </div>
                    <div className="text-xs text-gray-500">
                      {user?.email || ''}
                    </div>
                  </div>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuItem onClick={() => setIsCreditModalOpen(true)}>
                  <CreditCard className="mr-2 h-4 w-4" />
                  Comprar Créditos
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setIsTransactionHistoryOpen(true)}>
                  <Receipt className="mr-2 h-4 w-4" />
                  Historial de Compras
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <Settings className="mr-2 h-4 w-4" />
                  Configuración
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                  <LogOut className="mr-2 h-4 w-4" />
                  Cerrar Sesión
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Modals */}
      <CreditModal 
        isOpen={isCreditModalOpen} 
        onClose={() => setIsCreditModalOpen(false)} 
      />
      <TransactionHistory
        isOpen={isTransactionHistoryOpen}
        onClose={() => setIsTransactionHistoryOpen(false)}
      />
    </>
  );
};

export default Header;
