"""
MelusAI Templates
Pre-built templates for different application types
"""
from typing import Dict, List


def get_todo_app_template() -> List[Dict]:
    """Get template for a todo/task application"""
    return [
        {
            "path": "App.jsx",
            "content": '''import React, { useState } from 'react';

const App = () => {
  const [tasks, setTasks] = useState([
    { id: 1, text: 'Completar proyecto', completed: false },
    { id: 2, text: 'Revisar código', completed: true },
    { id: 3, text: 'Hacer deploy', completed: false }
  ]);
  const [newTask, setNewTask] = useState('');
  const [filter, setFilter] = useState('all');

  const addTask = () => {
    if (!newTask.trim()) return;
    setTasks([...tasks, { 
      id: Date.now(), 
      text: newTask, 
      completed: false 
    }]);
    setNewTask('');
  };

  const toggleTask = (id) => {
    setTasks(tasks.map(task => 
      task.id === id ? { ...task, completed: !task.completed } : task
    ));
  };

  const deleteTask = (id) => {
    setTasks(tasks.filter(task => task.id !== id));
  };

  const filteredTasks = tasks.filter(task => {
    if (filter === 'active') return !task.completed;
    if (filter === 'completed') return task.completed;
    return true;
  });

  const completedCount = tasks.filter(t => t.completed).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900">
      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Mis Tareas</h1>
          <p className="text-purple-200">{completedCount} de {tasks.length} completadas</p>
        </div>
        
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 shadow-2xl border border-white/20">
          <div className="flex gap-3 mb-6">
            <input
              type="text"
              value={newTask}
              onChange={(e) => setNewTask(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addTask()}
              placeholder="Nueva tarea..."
              className="flex-1 bg-white/20 border border-white/30 rounded-xl px-4 py-3 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-pink-500"
            />
            <button
              onClick={addTask}
              className="bg-gradient-to-r from-pink-500 to-purple-500 text-white px-6 py-3 rounded-xl font-semibold hover:opacity-90 transition-opacity"
            >
              Añadir
            </button>
          </div>

          <div className="flex gap-2 mb-4">
            {['all', 'active', 'completed'].map(f => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  filter === f 
                    ? 'bg-white text-purple-900' 
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                }`}
              >
                {f === 'all' ? 'Todas' : f === 'active' ? 'Activas' : 'Completadas'}
              </button>
            ))}
          </div>

          <ul className="space-y-2">
            {filteredTasks.map(task => (
              <li 
                key={task.id}
                className="flex items-center gap-3 bg-white/10 rounded-xl p-4 group"
              >
                <button
                  onClick={() => toggleTask(task.id)}
                  className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
                    task.completed 
                      ? 'bg-green-500 border-green-500' 
                      : 'border-white/50 hover:border-pink-500'
                  }`}
                >
                  {task.completed && (
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
                <span className={`flex-1 text-white ${task.completed ? 'line-through opacity-50' : ''}`}>
                  {task.text}
                </span>
                <button
                  onClick={() => deleteTask(task.id)}
                  className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 transition-opacity"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </li>
            ))}
          </ul>

          {filteredTasks.length === 0 && (
            <div className="text-center py-8 text-white/50">
              No hay tareas {filter !== 'all' ? `${filter === 'active' ? 'activas' : 'completadas'}` : ''}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;''',
            "type": "component"
        }
    ]


def get_ecommerce_template() -> List[Dict]:
    """Get template for an e-commerce application"""
    return [
        {
            "path": "App.jsx",
            "content": '''import React, { useState } from 'react';

const ProductCard = ({ product, onAddToCart }) => (
  <div className="bg-white rounded-2xl shadow-lg overflow-hidden group">
    <div className="aspect-square bg-gray-100 relative overflow-hidden">
      <img 
        src={product.image} 
        alt={product.name}
        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
      />
      {product.badge && (
        <span className="absolute top-3 left-3 bg-pink-500 text-white text-xs font-bold px-2 py-1 rounded-full">
          {product.badge}
        </span>
      )}
    </div>
    <div className="p-4">
      <h3 className="font-semibold text-gray-800">{product.name}</h3>
      <p className="text-gray-500 text-sm mb-2">{product.category}</p>
      <div className="flex items-center justify-between">
        <span className="text-xl font-bold text-gray-900">${product.price}</span>
        <button 
          onClick={() => onAddToCart(product)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
        >
          Añadir
        </button>
      </div>
    </div>
  </div>
);

const CartItem = ({ item, onRemove, onUpdateQty }) => (
  <div className="flex items-center gap-4 py-4 border-b">
    <img src={item.image} alt={item.name} className="w-16 h-16 rounded-lg object-cover" />
    <div className="flex-1">
      <h4 className="font-medium text-gray-800">{item.name}</h4>
      <p className="text-gray-500 text-sm">${item.price}</p>
    </div>
    <div className="flex items-center gap-2">
      <button 
        onClick={() => onUpdateQty(item.id, item.qty - 1)}
        className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200"
      >
        -
      </button>
      <span className="w-8 text-center">{item.qty}</span>
      <button 
        onClick={() => onUpdateQty(item.id, item.qty + 1)}
        className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200"
      >
        +
      </button>
    </div>
    <button onClick={() => onRemove(item.id)} className="text-red-500 hover:text-red-600">
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>
);

const App = () => {
  const [products] = useState([
    { id: 1, name: 'Camiseta Premium', price: 29.99, category: 'Ropa', image: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400', badge: 'Nuevo' },
    { id: 2, name: 'Zapatillas Running', price: 89.99, category: 'Calzado', image: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400', badge: 'Popular' },
    { id: 3, name: 'Mochila Urban', price: 49.99, category: 'Accesorios', image: 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400' },
    { id: 4, name: 'Gorra Vintage', price: 24.99, category: 'Accesorios', image: 'https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=400' },
    { id: 5, name: 'Sudadera Hoodie', price: 59.99, category: 'Ropa', image: 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400', badge: '-20%' },
    { id: 6, name: 'Reloj Minimal', price: 129.99, category: 'Accesorios', image: 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400' }
  ]);
  
  const [cart, setCart] = useState([]);
  const [showCart, setShowCart] = useState(false);

  const addToCart = (product) => {
    const existing = cart.find(item => item.id === product.id);
    if (existing) {
      setCart(cart.map(item => 
        item.id === product.id ? { ...item, qty: item.qty + 1 } : item
      ));
    } else {
      setCart([...cart, { ...product, qty: 1 }]);
    }
  };

  const removeFromCart = (id) => {
    setCart(cart.filter(item => item.id !== id));
  };

  const updateQty = (id, qty) => {
    if (qty < 1) {
      removeFromCart(id);
    } else {
      setCart(cart.map(item => 
        item.id === id ? { ...item, qty } : item
      ));
    }
  };

  const cartTotal = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
  const cartCount = cart.reduce((sum, item) => sum + item.qty, 0);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-pink-600 bg-clip-text text-transparent">
            MiTienda
          </h1>
          <button 
            onClick={() => setShowCart(true)}
            className="relative p-2 hover:bg-gray-100 rounded-full"
          >
            <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
            {cartCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-pink-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">
                {cartCount}
              </span>
            )}
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-8">Productos Destacados</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map(product => (
            <ProductCard key={product.id} product={product} onAddToCart={addToCart} />
          ))}
        </div>
      </main>

      {showCart && (
        <div className="fixed inset-0 bg-black/50 z-50 flex justify-end">
          <div className="w-full max-w-md bg-white h-full shadow-2xl flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-xl font-bold">Carrito ({cartCount})</h2>
              <button onClick={() => setShowCart(false)} className="p-2 hover:bg-gray-100 rounded-full">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="flex-1 overflow-y-auto px-4">
              {cart.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <svg className="w-16 h-16 mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                  </svg>
                  <p>Tu carrito está vacío</p>
                </div>
              ) : (
                cart.map(item => (
                  <CartItem 
                    key={item.id} 
                    item={item} 
                    onRemove={removeFromCart} 
                    onUpdateQty={updateQty} 
                  />
                ))
              )}
            </div>
            {cart.length > 0 && (
              <div className="p-4 border-t bg-gray-50">
                <div className="flex justify-between mb-4">
                  <span className="font-medium">Total:</span>
                  <span className="text-xl font-bold">${cartTotal.toFixed(2)}</span>
                </div>
                <button className="w-full bg-indigo-600 text-white py-3 rounded-xl font-semibold hover:bg-indigo-700 transition-colors">
                  Proceder al Pago
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default App;''',
            "type": "component"
        }
    ]


def get_dashboard_template() -> List[Dict]:
    """Get template for a dashboard application"""
    return [
        {
            "path": "App.jsx",
            "content": '''import React, { useState } from 'react';

const StatCard = ({ title, value, change, icon, color }) => (
  <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
    <div className="flex items-center justify-between mb-4">
      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center`}>
        {icon}
      </div>
      <span className={`text-sm font-medium ${change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
        {change >= 0 ? '+' : ''}{change}%
      </span>
    </div>
    <h3 className="text-gray-400 text-sm mb-1">{title}</h3>
    <p className="text-2xl font-bold text-white">{value}</p>
  </div>
);

const ChartPlaceholder = ({ title }) => (
  <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
    <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
    <div className="h-48 flex items-end justify-between gap-2">
      {[65, 45, 75, 50, 85, 60, 90, 70, 80, 55, 95, 65].map((h, i) => (
        <div
          key={i}
          className="flex-1 bg-gradient-to-t from-cyan-500 to-purple-500 rounded-t-lg opacity-80 hover:opacity-100 transition-opacity"
          style={{ height: `${h}%` }}
        />
      ))}
    </div>
    <div className="flex justify-between mt-4 text-xs text-gray-500">
      <span>Ene</span><span>Feb</span><span>Mar</span><span>Abr</span><span>May</span><span>Jun</span>
      <span>Jul</span><span>Ago</span><span>Sep</span><span>Oct</span><span>Nov</span><span>Dic</span>
    </div>
  </div>
);

const RecentActivity = () => {
  const activities = [
    { id: 1, user: 'Carlos M.', action: 'Nueva compra', time: 'Hace 5 min', amount: '$125.00' },
    { id: 2, user: 'Ana G.', action: 'Registro nuevo', time: 'Hace 15 min', amount: null },
    { id: 3, user: 'Luis R.', action: 'Suscripción Pro', time: 'Hace 1 hora', amount: '$29.99/mes' },
    { id: 4, user: 'María S.', action: 'Nueva compra', time: 'Hace 2 horas', amount: '$89.50' },
  ];

  return (
    <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
      <h3 className="text-lg font-semibold text-white mb-4">Actividad Reciente</h3>
      <div className="space-y-4">
        {activities.map(activity => (
          <div key={activity.id} className="flex items-center justify-between py-3 border-b border-gray-700 last:border-0">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center text-white font-semibold">
                {activity.user.charAt(0)}
              </div>
              <div>
                <p className="text-white font-medium">{activity.user}</p>
                <p className="text-gray-500 text-sm">{activity.action}</p>
              </div>
            </div>
            <div className="text-right">
              {activity.amount && <p className="text-green-400 font-medium">{activity.amount}</p>}
              <p className="text-gray-500 text-sm">{activity.time}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const App = () => {
  const stats = [
    { 
      title: 'Ingresos Totales', 
      value: '$45,678', 
      change: 12.5, 
      color: 'from-cyan-500 to-blue-500',
      icon: <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
    },
    { 
      title: 'Usuarios Activos', 
      value: '12,345', 
      change: 8.2, 
      color: 'from-purple-500 to-pink-500',
      icon: <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
    },
    { 
      title: 'Pedidos', 
      value: '1,892', 
      change: 23.1, 
      color: 'from-orange-500 to-red-500',
      icon: <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" /></svg>
    },
    { 
      title: 'Tasa Conversión', 
      value: '3.24%', 
      change: -2.4, 
      color: 'from-green-500 to-emerald-500',
      icon: <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
    }
  ];

  return (
    <div className="min-h-screen bg-gray-900">
      <nav className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            Dashboard
          </h1>
          <div className="flex items-center gap-4">
            <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>
            </button>
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center text-white font-semibold">
              A
            </div>
          </div>
        </div>
      </nav>

      <main className="p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, i) => (
            <StatCard key={i} {...stat} />
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <ChartPlaceholder title="Ingresos Mensuales" />
          </div>
          <RecentActivity />
        </div>
      </main>
    </div>
  );
};

export default App;''',
            "type": "component"
        }
    ]


def get_landing_template() -> List[Dict]:
    """Get template for a landing page"""
    return [
        {
            "path": "App.jsx",
            "content": '''import React from 'react';

const Feature = ({ icon, title, description }) => (
  <div className="text-center p-6">
    <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
      {icon}
    </div>
    <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
    <p className="text-purple-200">{description}</p>
  </div>
);

const App = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900">
      <nav className="container mx-auto px-6 py-6 flex items-center justify-between">
        <div className="text-2xl font-bold text-white">MiMarca</div>
        <div className="hidden md:flex items-center gap-8">
          <a href="#features" className="text-purple-200 hover:text-white transition-colors">Características</a>
          <a href="#pricing" className="text-purple-200 hover:text-white transition-colors">Precios</a>
          <a href="#contact" className="text-purple-200 hover:text-white transition-colors">Contacto</a>
        </div>
        <button className="bg-white text-purple-900 px-6 py-2 rounded-full font-semibold hover:bg-purple-100 transition-colors">
          Comenzar
        </button>
      </nav>

      <section className="container mx-auto px-6 py-20 text-center">
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
          Transforma tu<br />
          <span className="bg-gradient-to-r from-cyan-400 to-pink-400 bg-clip-text text-transparent">
            idea en realidad
          </span>
        </h1>
        <p className="text-xl text-purple-200 mb-8 max-w-2xl mx-auto">
          La plataforma que necesitas para llevar tu proyecto al siguiente nivel. 
          Simple, potente y diseñada para el éxito.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button className="bg-white text-purple-900 px-8 py-4 rounded-full font-semibold text-lg hover:bg-purple-100 transition-colors shadow-lg shadow-purple-500/30">
            Empezar Gratis
          </button>
          <button className="border-2 border-white/30 text-white px-8 py-4 rounded-full font-semibold text-lg hover:bg-white/10 transition-colors">
            Ver Demo
          </button>
        </div>
      </section>

      <section id="features" className="container mx-auto px-6 py-20">
        <h2 className="text-3xl font-bold text-white text-center mb-12">
          Todo lo que necesitas
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <Feature 
            icon={<svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>}
            title="Súper Rápido"
            description="Rendimiento optimizado para que tu proyecto vuele."
          />
          <Feature 
            icon={<svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>}
            title="100% Seguro"
            description="Tu información protegida con los más altos estándares."
          />
          <Feature 
            icon={<svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" /></svg>}
            title="Fácil de Usar"
            description="Interfaz intuitiva que cualquiera puede dominar."
          />
        </div>
      </section>

      <section id="cta" className="container mx-auto px-6 py-20">
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl p-12 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            ¿Listo para empezar?
          </h2>
          <p className="text-purple-100 mb-8 max-w-xl mx-auto">
            Únete a miles de usuarios que ya están transformando sus ideas con nuestra plataforma.
          </p>
          <button className="bg-white text-purple-600 px-8 py-4 rounded-full font-semibold text-lg hover:bg-purple-100 transition-colors">
            Crear Cuenta Gratis
          </button>
        </div>
      </section>

      <footer className="container mx-auto px-6 py-12 border-t border-white/10">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-purple-300">© 2024 MiMarca. Todos los derechos reservados.</div>
          <div className="flex gap-6">
            <a href="#" className="text-purple-300 hover:text-white transition-colors">Términos</a>
            <a href="#" className="text-purple-300 hover:text-white transition-colors">Privacidad</a>
            <a href="#" className="text-purple-300 hover:text-white transition-colors">Contacto</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;''',
            "type": "component"
        }
    ]


def get_saas_template() -> List[Dict]:
    """Get template for a SaaS application"""
    return [
        {
            "path": "App.jsx",
            "content": '''import React, { useState } from 'react';

const Sidebar = ({ currentPage, setCurrentPage }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
    { id: 'projects', label: 'Proyectos', icon: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z' },
    { id: 'team', label: 'Equipo', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z' },
    { id: 'settings', label: 'Ajustes', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z' }
  ];

  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
      <div className="p-6">
        <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
          SaaSApp
        </h1>
      </div>
      <nav className="flex-1 px-4">
        {menuItems.map(item => (
          <button
            key={item.id}
            onClick={() => setCurrentPage(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl mb-1 transition-all ${
              currentPage === item.id 
                ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-white' 
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
            }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
            </svg>
            {item.label}
          </button>
        ))}
      </nav>
      <div className="p-4 m-4 rounded-xl bg-gradient-to-br from-purple-600 to-pink-600">
        <p className="text-white font-medium mb-2">Plan Pro</p>
        <p className="text-purple-200 text-sm mb-3">Desbloquea todas las funciones</p>
        <button className="w-full bg-white text-purple-600 py-2 rounded-lg font-medium hover:bg-purple-100 transition-colors">
          Upgrade
        </button>
      </div>
    </aside>
  );
};

const DashboardPage = () => (
  <div className="space-y-6">
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {[
        { label: 'Proyectos Activos', value: '12', change: '+3' },
        { label: 'Tareas Pendientes', value: '48', change: '-5' },
        { label: 'Colaboradores', value: '8', change: '+1' }
      ].map((stat, i) => (
        <div key={i} className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
          <p className="text-gray-400 text-sm mb-2">{stat.label}</p>
          <div className="flex items-end justify-between">
            <p className="text-3xl font-bold text-white">{stat.value}</p>
            <span className={`text-sm ${stat.change.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
              {stat.change} esta semana
            </span>
          </div>
        </div>
      ))}
    </div>
    <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
      <h3 className="text-lg font-semibold text-white mb-4">Proyectos Recientes</h3>
      <div className="space-y-3">
        {['App Móvil', 'Dashboard Admin', 'API Backend'].map((project, i) => (
          <div key={i} className="flex items-center justify-between py-3 border-b border-gray-700 last:border-0">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center text-white font-medium">
                {project.charAt(0)}
              </div>
              <div>
                <p className="text-white font-medium">{project}</p>
                <p className="text-gray-500 text-sm">Actualizado hace 2 horas</p>
              </div>
            </div>
            <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">Activo</span>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const App = () => {
  const [currentPage, setCurrentPage] = useState('dashboard');

  return (
    <div className="min-h-screen bg-gray-950 flex">
      <Sidebar currentPage={currentPage} setCurrentPage={setCurrentPage} />
      <main className="flex-1 flex flex-col">
        <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
          <div className="flex items-center justify-between">
            <input
              type="text"
              placeholder="Buscar..."
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 w-64"
            />
            <div className="flex items-center gap-4">
              <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
              </button>
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center text-white font-semibold">
                U
              </div>
            </div>
          </div>
        </header>
        <div className="flex-1 p-6 overflow-y-auto">
          <DashboardPage />
        </div>
      </main>
    </div>
  );
};

export default App;''',
            "type": "component"
        }
    ]


# Template registry
TEMPLATES = {
    "todo": get_todo_app_template,
    "tasks": get_todo_app_template,
    "tareas": get_todo_app_template,
    "ecommerce": get_ecommerce_template,
    "tienda": get_ecommerce_template,
    "shop": get_ecommerce_template,
    "dashboard": get_dashboard_template,
    "panel": get_dashboard_template,
    "landing": get_landing_template,
    "landing_page": get_landing_template,
    "saas": get_saas_template,
    "saas_app": get_saas_template,
    "web_app": get_todo_app_template,
}


def get_game2d_template() -> List[Dict]:
    """Get template for a 2D game using Phaser.js"""
    return [
        {
            "path": "index.html",
            "content": '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mi Juego 2D</title>
    <script src="https://cdn.jsdelivr.net/npm/phaser@3.60.0/dist/phaser.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            background: #1a1a2e; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            min-height: 100vh;
            font-family: 'Segoe UI', sans-serif;
        }
        #game-container {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }
        .ui-overlay {
            position: absolute;
            top: 20px;
            left: 20px;
            color: white;
            font-size: 18px;
            z-index: 100;
        }
    </style>
</head>
<body>
    <div id="game-container"></div>
    <script src="game.js"></script>
</body>
</html>''',
            "type": "html"
        },
        {
            "path": "game.js",
            "content": '''// Configuración del juego
const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    parent: 'game-container',
    backgroundColor: '#16213e',
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 500 },
            debug: false
        }
    },
    scene: [MenuScene, GameScene, GameOverScene]
};

// Escena del Menú
class MenuScene extends Phaser.Scene {
    constructor() {
        super({ key: 'MenuScene' });
    }

    create() {
        const { width, height } = this.cameras.main;
        
        // Título
        this.add.text(width / 2, height / 3, '🎮 MI JUEGO 2D', {
            fontSize: '48px',
            fontFamily: 'Arial',
            color: '#e94560',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        
        // Subtítulo
        this.add.text(width / 2, height / 3 + 60, 'Plataformas con Phaser.js', {
            fontSize: '20px',
            color: '#a8d8ea'
        }).setOrigin(0.5);
        
        // Botón de inicio
        const startBtn = this.add.text(width / 2, height / 2 + 50, '▶ JUGAR', {
            fontSize: '32px',
            color: '#ffffff',
            backgroundColor: '#e94560',
            padding: { x: 40, y: 15 }
        }).setOrigin(0.5).setInteractive({ useHandCursor: true });
        
        startBtn.on('pointerover', () => startBtn.setStyle({ backgroundColor: '#ff6b6b' }));
        startBtn.on('pointerout', () => startBtn.setStyle({ backgroundColor: '#e94560' }));
        startBtn.on('pointerdown', () => this.scene.start('GameScene'));
        
        // Instrucciones
        this.add.text(width / 2, height - 80, '← → para mover | ESPACIO para saltar', {
            fontSize: '16px',
            color: '#888888'
        }).setOrigin(0.5);
    }
}

// Escena Principal del Juego
class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene' });
        this.score = 0;
    }

    create() {
        const { width, height } = this.cameras.main;
        
        // Crear plataformas
        this.platforms = this.physics.add.staticGroup();
        
        // Suelo
        const ground = this.add.rectangle(width / 2, height - 20, width, 40, 0x0f3460);
        this.platforms.add(ground);
        
        // Plataformas flotantes
        const platformPositions = [
            { x: 600, y: 450 },
            { x: 200, y: 350 },
            { x: 500, y: 250 },
            { x: 100, y: 150 }
        ];
        
        platformPositions.forEach(pos => {
            const platform = this.add.rectangle(pos.x, pos.y, 150, 20, 0x533483);
            this.platforms.add(platform);
        });
        
        // Crear jugador
        this.player = this.add.rectangle(100, height - 100, 40, 50, 0xe94560);
        this.physics.add.existing(this.player);
        this.player.body.setBounce(0.1);
        this.player.body.setCollideWorldBounds(true);
        
        // Colisión con plataformas
        this.physics.add.collider(this.player, this.platforms);
        
        // Crear monedas
        this.coins = this.physics.add.group();
        this.createCoins();
        this.physics.add.collider(this.coins, this.platforms);
        this.physics.add.overlap(this.player, this.coins, this.collectCoin, null, this);
        
        // Controles
        this.cursors = this.input.keyboard.createCursorKeys();
        this.spaceKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);
        
        // UI
        this.scoreText = this.add.text(20, 20, 'Puntos: 0', {
            fontSize: '24px',
            color: '#ffffff'
        });
        
        // Crear enemigos
        this.enemies = this.physics.add.group();
        this.createEnemies();
        this.physics.add.collider(this.enemies, this.platforms);
        this.physics.add.overlap(this.player, this.enemies, this.hitEnemy, null, this);
    }

    createCoins() {
        const coinPositions = [
            { x: 600, y: 400 },
            { x: 200, y: 300 },
            { x: 500, y: 200 },
            { x: 100, y: 100 },
            { x: 400, y: 500 },
            { x: 700, y: 350 }
        ];
        
        coinPositions.forEach(pos => {
            const coin = this.add.circle(pos.x, pos.y, 15, 0xffd700);
            this.coins.add(coin);
            coin.body.setAllowGravity(false);
            
            // Animación de brillo
            this.tweens.add({
                targets: coin,
                scale: { from: 1, to: 1.2 },
                duration: 500,
                yoyo: true,
                repeat: -1
            });
        });
    }

    createEnemies() {
        const enemy = this.add.rectangle(400, 530, 35, 35, 0xff4757);
        this.enemies.add(enemy);
        enemy.body.setCollideWorldBounds(true);
        enemy.body.setBounce(1);
        enemy.body.setVelocityX(100);
    }

    collectCoin(player, coin) {
        coin.destroy();
        this.score += 10;
        this.scoreText.setText('Puntos: ' + this.score);
        
        // Efecto visual
        this.cameras.main.flash(100, 255, 215, 0);
        
        // Verificar victoria
        if (this.coins.countActive() === 0) {
            this.createCoins();
            this.score += 50; // Bonus por completar ronda
        }
    }

    hitEnemy(player, enemy) {
        this.physics.pause();
        player.setFillStyle(0x666666);
        
        this.time.delayedCall(1000, () => {
            this.scene.start('GameOverScene', { score: this.score });
        });
    }

    update() {
        // Movimiento horizontal
        if (this.cursors.left.isDown) {
            this.player.body.setVelocityX(-200);
        } else if (this.cursors.right.isDown) {
            this.player.body.setVelocityX(200);
        } else {
            this.player.body.setVelocityX(0);
        }
        
        // Salto
        if ((this.cursors.up.isDown || this.spaceKey.isDown) && this.player.body.touching.down) {
            this.player.body.setVelocityY(-400);
        }
    }
}

// Escena Game Over
class GameOverScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameOverScene' });
    }

    init(data) {
        this.finalScore = data.score || 0;
    }

    create() {
        const { width, height } = this.cameras.main;
        
        this.add.text(width / 2, height / 3, '💀 GAME OVER', {
            fontSize: '48px',
            color: '#e94560',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        
        this.add.text(width / 2, height / 2, `Puntuación: ${this.finalScore}`, {
            fontSize: '32px',
            color: '#ffffff'
        }).setOrigin(0.5);
        
        const retryBtn = this.add.text(width / 2, height / 2 + 80, '🔄 REINTENTAR', {
            fontSize: '24px',
            color: '#ffffff',
            backgroundColor: '#533483',
            padding: { x: 30, y: 10 }
        }).setOrigin(0.5).setInteractive({ useHandCursor: true });
        
        retryBtn.on('pointerover', () => retryBtn.setStyle({ backgroundColor: '#6b4c9a' }));
        retryBtn.on('pointerout', () => retryBtn.setStyle({ backgroundColor: '#533483' }));
        retryBtn.on('pointerdown', () => this.scene.start('GameScene'));
        
        const menuBtn = this.add.text(width / 2, height / 2 + 140, '🏠 MENÚ', {
            fontSize: '20px',
            color: '#888888'
        }).setOrigin(0.5).setInteractive({ useHandCursor: true });
        
        menuBtn.on('pointerdown', () => this.scene.start('MenuScene'));
    }
}

// Iniciar juego
const game = new Phaser.Game(config);''',
            "type": "javascript"
        }
    ]


def get_game3d_template() -> List[Dict]:
    """Get template for a 3D game/experience using Three.js"""
    return [
        {
            "path": "index.html",
            "content": '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mi Experiencia 3D</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            overflow: hidden;
            background: #000;
        }
        #info {
            position: absolute;
            top: 20px;
            left: 20px;
            color: white;
            font-family: 'Segoe UI', sans-serif;
            z-index: 100;
            background: rgba(0,0,0,0.7);
            padding: 15px 25px;
            border-radius: 10px;
        }
        #info h1 {
            font-size: 24px;
            margin-bottom: 10px;
            color: #00d4ff;
        }
        #info p {
            font-size: 14px;
            color: #888;
        }
        #score {
            position: absolute;
            top: 20px;
            right: 20px;
            color: #00ff88;
            font-family: 'Segoe UI', sans-serif;
            font-size: 28px;
            z-index: 100;
        }
        #loading {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #0a0a0a;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            font-family: 'Segoe UI', sans-serif;
            z-index: 1000;
        }
        #loading.hidden { display: none; }
        canvas { display: block; }
    </style>
</head>
<body>
    <div id="loading">
        <div>
            <h2>🎮 Cargando Experiencia 3D...</h2>
            <p>Preparando el mundo virtual</p>
        </div>
    </div>
    <div id="info">
        <h1>🌌 Experiencia 3D</h1>
        <p>WASD para mover | Mouse para rotar</p>
    </div>
    <div id="score">Puntos: <span id="points">0</span></div>
    
    <script type="importmap">
    {
        "imports": {
            "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
            "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
        }
    }
    </script>
    <script type="module" src="game3d.js"></script>
</body>
</html>''',
            "type": "html"
        },
        {
            "path": "game3d.js",
            "content": '''import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// Variables globales
let scene, camera, renderer, controls;
let player, collectibles = [];
let score = 0;
let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
const velocity = new THREE.Vector3();
const direction = new THREE.Vector3();

// Inicialización
function init() {
    // Escena
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a1a);
    scene.fog = new THREE.Fog(0x0a0a1a, 10, 50);

    // Cámara
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 5, 10);

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.body.appendChild(renderer.domElement);

    // Controles
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2.2;

    // Luces
    setupLights();

    // Crear mundo
    createWorld();

    // Crear jugador
    createPlayer();

    // Crear coleccionables
    createCollectibles();

    // Eventos
    setupEvents();

    // Ocultar loading
    setTimeout(() => {
        document.getElementById('loading').classList.add('hidden');
    }, 1000);

    // Animar
    animate();
}

function setupLights() {
    // Luz ambiental
    const ambient = new THREE.AmbientLight(0x404080, 0.5);
    scene.add(ambient);

    // Luz direccional (sol)
    const sun = new THREE.DirectionalLight(0xffffff, 1);
    sun.position.set(10, 20, 10);
    sun.castShadow = true;
    sun.shadow.mapSize.width = 2048;
    sun.shadow.mapSize.height = 2048;
    sun.shadow.camera.near = 0.5;
    sun.shadow.camera.far = 50;
    scene.add(sun);

    // Luz puntual decorativa
    const pointLight = new THREE.PointLight(0x00d4ff, 1, 20);
    pointLight.position.set(0, 5, 0);
    scene.add(pointLight);
}

function createWorld() {
    // Suelo
    const groundGeometry = new THREE.PlaneGeometry(100, 100);
    const groundMaterial = new THREE.MeshStandardMaterial({ 
        color: 0x1a1a2e,
        roughness: 0.8
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Grid
    const grid = new THREE.GridHelper(100, 50, 0x333366, 0x222244);
    scene.add(grid);

    // Plataformas flotantes
    const platformPositions = [
        { x: 5, y: 2, z: 0 },
        { x: -5, y: 3, z: -5 },
        { x: 0, y: 4, z: -10 },
        { x: 8, y: 2.5, z: -8 },
        { x: -8, y: 3.5, z: 5 }
    ];

    platformPositions.forEach(pos => {
        const platformGeom = new THREE.BoxGeometry(4, 0.5, 4);
        const platformMat = new THREE.MeshStandardMaterial({ 
            color: 0x533483,
            metalness: 0.3,
            roughness: 0.7
        });
        const platform = new THREE.Mesh(platformGeom, platformMat);
        platform.position.set(pos.x, pos.y, pos.z);
        platform.castShadow = true;
        platform.receiveShadow = true;
        scene.add(platform);
    });

    // Decoraciones (torres de luz)
    for (let i = 0; i < 8; i++) {
        const angle = (i / 8) * Math.PI * 2;
        const radius = 15;
        
        const towerGeom = new THREE.CylinderGeometry(0.3, 0.5, 8, 8);
        const towerMat = new THREE.MeshStandardMaterial({ 
            color: 0x0f3460,
            emissive: 0x001133,
            emissiveIntensity: 0.2
        });
        const tower = new THREE.Mesh(towerGeom, towerMat);
        tower.position.set(
            Math.cos(angle) * radius,
            4,
            Math.sin(angle) * radius
        );
        tower.castShadow = true;
        scene.add(tower);

        // Luz en la torre
        const towerLight = new THREE.PointLight(0x00d4ff, 0.5, 8);
        towerLight.position.set(
            Math.cos(angle) * radius,
            8,
            Math.sin(angle) * radius
        );
        scene.add(towerLight);
    }
}

function createPlayer() {
    // Jugador (esfera brillante)
    const playerGeom = new THREE.SphereGeometry(0.5, 32, 32);
    const playerMat = new THREE.MeshStandardMaterial({ 
        color: 0xe94560,
        emissive: 0xe94560,
        emissiveIntensity: 0.3,
        metalness: 0.8,
        roughness: 0.2
    });
    player = new THREE.Mesh(playerGeom, playerMat);
    player.position.set(0, 1, 0);
    player.castShadow = true;
    scene.add(player);

    // Luz del jugador
    const playerLight = new THREE.PointLight(0xe94560, 1, 5);
    player.add(playerLight);
}

function createCollectibles() {
    const positions = [
        { x: 5, y: 3.5, z: 0 },
        { x: -5, y: 4.5, z: -5 },
        { x: 0, y: 5.5, z: -10 },
        { x: 8, y: 4, z: -8 },
        { x: -8, y: 5, z: 5 },
        { x: 3, y: 1.5, z: 3 },
        { x: -3, y: 1.5, z: -3 }
    ];

    positions.forEach((pos, i) => {
        const gemGeom = new THREE.OctahedronGeometry(0.4);
        const gemMat = new THREE.MeshStandardMaterial({ 
            color: 0x00ff88,
            emissive: 0x00ff88,
            emissiveIntensity: 0.5,
            metalness: 1,
            roughness: 0
        });
        const gem = new THREE.Mesh(gemGeom, gemMat);
        gem.position.set(pos.x, pos.y, pos.z);
        gem.userData.collected = false;
        collectibles.push(gem);
        scene.add(gem);
    });
}

function setupEvents() {
    // Teclado
    document.addEventListener('keydown', (e) => {
        switch(e.code) {
            case 'KeyW': case 'ArrowUp': moveForward = true; break;
            case 'KeyS': case 'ArrowDown': moveBackward = true; break;
            case 'KeyA': case 'ArrowLeft': moveLeft = true; break;
            case 'KeyD': case 'ArrowRight': moveRight = true; break;
        }
    });

    document.addEventListener('keyup', (e) => {
        switch(e.code) {
            case 'KeyW': case 'ArrowUp': moveForward = false; break;
            case 'KeyS': case 'ArrowDown': moveBackward = false; break;
            case 'KeyA': case 'ArrowLeft': moveLeft = false; break;
            case 'KeyD': case 'ArrowRight': moveRight = false; break;
        }
    });

    // Resize
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

function checkCollisions() {
    collectibles.forEach(gem => {
        if (!gem.userData.collected) {
            const distance = player.position.distanceTo(gem.position);
            if (distance < 1) {
                gem.userData.collected = true;
                gem.visible = false;
                score += 100;
                document.getElementById('points').textContent = score;
                
                // Efecto visual
                const flash = new THREE.PointLight(0x00ff88, 3, 10);
                flash.position.copy(gem.position);
                scene.add(flash);
                setTimeout(() => scene.remove(flash), 200);
            }
        }
    });
}

function animate() {
    requestAnimationFrame(animate);

    // Movimiento del jugador
    const speed = 0.15;
    
    // Obtener dirección de la cámara
    const cameraDirection = new THREE.Vector3();
    camera.getWorldDirection(cameraDirection);
    cameraDirection.y = 0;
    cameraDirection.normalize();

    const right = new THREE.Vector3();
    right.crossVectors(cameraDirection, new THREE.Vector3(0, 1, 0));

    if (moveForward) player.position.add(cameraDirection.clone().multiplyScalar(speed));
    if (moveBackward) player.position.add(cameraDirection.clone().multiplyScalar(-speed));
    if (moveLeft) player.position.add(right.clone().multiplyScalar(-speed));
    if (moveRight) player.position.add(right.clone().multiplyScalar(speed));

    // Mantener jugador sobre el suelo
    player.position.y = Math.max(player.position.y, 1);

    // Rotación de coleccionables
    collectibles.forEach(gem => {
        if (!gem.userData.collected) {
            gem.rotation.y += 0.02;
            gem.rotation.x += 0.01;
        }
    });

    // Verificar colisiones
    checkCollisions();

    // Actualizar cámara para seguir al jugador
    controls.target.copy(player.position);
    controls.update();

    renderer.render(scene, camera);
}

// Iniciar
init();''',
            "type": "javascript"
        }
    ]


# Template registry
TEMPLATES = {
    "todo": get_todo_app_template,
    "tasks": get_todo_app_template,
    "tareas": get_todo_app_template,
    "ecommerce": get_ecommerce_template,
    "tienda": get_ecommerce_template,
    "shop": get_ecommerce_template,
    "dashboard": get_dashboard_template,
    "panel": get_dashboard_template,
    "landing": get_landing_template,
    "landing_page": get_landing_template,
    "saas": get_saas_template,
    "saas_app": get_saas_template,
    "game2d": get_game2d_template,
    "juego2d": get_game2d_template,
    "phaser": get_game2d_template,
    "game3d": get_game3d_template,
    "juego3d": get_game3d_template,
    "threejs": get_game3d_template,
    "3d": get_game3d_template,
    "web_app": get_todo_app_template,
}


def get_template_for_intent(intent_type: str, prompt: str = "") -> List[Dict]:
    """Get the best template based on intent type and prompt"""
    prompt_lower = prompt.lower()
    
    # Check for game keywords first
    if any(word in prompt_lower for word in ["juego 2d", "game 2d", "phaser", "plataformas", "arcade"]):
        return get_game2d_template()
    
    if any(word in prompt_lower for word in ["juego 3d", "game 3d", "three.js", "3d", "webgl", "mundo virtual"]):
        return get_game3d_template()
    
    if any(word in prompt_lower for word in ["tarea", "todo", "task", "lista"]):
        return get_todo_app_template()
    
    if any(word in prompt_lower for word in ["tienda", "shop", "ecommerce", "carrito", "producto"]):
        return get_ecommerce_template()
    
    if any(word in prompt_lower for word in ["dashboard", "panel", "métrica", "gráfico", "reporte"]):
        return get_dashboard_template()
    
    if any(word in prompt_lower for word in ["landing", "marketing", "página", "promoción"]):
        return get_landing_template()
    
    if any(word in prompt_lower for word in ["saas", "suscripción", "workspace", "equipo"]):
        return get_saas_template()
    
    # Fallback to intent type
    template_func = TEMPLATES.get(intent_type, get_todo_app_template)
    return template_func()
