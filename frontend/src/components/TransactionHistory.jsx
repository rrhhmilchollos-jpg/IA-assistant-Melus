import React, { useState, useEffect } from 'react';
import { creditsAPI } from '../api/client';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { ScrollArea } from './ui/scroll-area';
import { Receipt, CheckCircle, Clock, XCircle } from 'lucide-react';

const TransactionHistory = ({ isOpen, onClose }) => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      loadTransactions();
    }
  }, [isOpen]);

  const loadTransactions = async () => {
    try {
      const txns = await creditsAPI.getTransactions();
      setTransactions(txns);
    } catch (error) {
      console.error('Failed to load transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="text-green-500" size={20} />;
      case 'pending':
        return <Clock className="text-yellow-500" size={20} />;
      case 'failed':
        return <XCircle className="text-red-500" size={20} />;
      default:
        return <Receipt className="text-gray-500" size={20} />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return 'Completado';
      case 'pending':
        return 'Pendiente';
      case 'failed':
        return 'Fallido';
      default:
        return status;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl bg-gray-900/95 backdrop-blur-xl border-gray-700 text-white">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <Receipt className="w-6 h-6 text-purple-400" />
            <DialogTitle className="text-xl text-white">Historial de Transacciones</DialogTitle>
          </div>
        </DialogHeader>

        <ScrollArea className="h-[500px] pr-4">
          {loading ? (
            <div className="text-center py-8 text-gray-400">Cargando...</div>
          ) : transactions.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              No tienes transacciones aún
            </div>
          ) : (
            <div className="space-y-3">
              {transactions.map((txn) => (
                <div
                  key={txn.transaction_id}
                  className="bg-gray-800/50 border border-gray-700 rounded-lg p-4"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(txn.status)}
                      <div>
                        <div className="font-semibold text-white">
                          {txn.credits.toLocaleString()} créditos
                        </div>
                        <div className="text-sm text-gray-400">
                          {getStatusText(txn.status)}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-white">
                        ${txn.amount.toFixed(2)}
                      </div>
                      <div className="text-xs text-gray-400">
                        {new Date(txn.created_at).toLocaleDateString('es-ES', {
                          day: 'numeric',
                          month: 'short',
                          year: 'numeric',
                        })}
                      </div>
                    </div>
                  </div>
                  <div className="text-xs text-gray-500 font-mono">
                    ID: {txn.transaction_id}
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
};

export default TransactionHistory;
