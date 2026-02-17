import React, { useState, useEffect } from 'react';
import { modelsAPI } from '../api/client';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { Sparkles } from 'lucide-react';

const ModelSelector = ({ value, onChange, disabled = false }) => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const modelsList = await modelsAPI.getAll();
      setModels(modelsList);
    } catch (error) {
      console.error('Failed to load models:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-sm text-gray-400">Cargando modelos...</div>;
  }

  return (
    <Select value={value} onValueChange={onChange} disabled={disabled}>
      <SelectTrigger className="w-full bg-white border-gray-300 text-gray-900 hover:bg-gray-50">
        <div className="flex items-center gap-2">
          <Sparkles size={16} className="text-purple-500" />
          <SelectValue placeholder="Selecciona un modelo" />
        </div>
      </SelectTrigger>
      <SelectContent className="bg-white border-gray-200">
        {models.map((model) => (
          <SelectItem 
            key={model.model_id} 
            value={model.model_id}
            className="hover:bg-gray-100"
          >
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-900">{model.name}</span>
                {model.popular && (
                  <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">Popular</span>
                )}
              </div>
              <span className="text-xs text-gray-500">{model.description}</span>
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
};

export default ModelSelector;
