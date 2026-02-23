import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Zap, Code2, Layers, Database, Globe, Sparkles, 
  ChevronRight, ChevronDown, Play, Check, Star,
  Cpu, Bot, Rocket, Shield, CreditCard, Users,
  ArrowRight, Menu, X, Github, Mail
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Navigation Component
const Navigation = ({ onGetStarted }) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      isScrolled ? 'bg-gray-900/95 backdrop-blur-md shadow-lg' : 'bg-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">
              Melus<span className="text-cyan-400">AI</span>
            </span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-gray-300 hover:text-white transition-colors">Características</a>
            <a href="#how-it-works" className="text-gray-300 hover:text-white transition-colors">Cómo Funciona</a>
            <a href="#pricing" className="text-gray-300 hover:text-white transition-colors">Precios</a>
            <Link to="/docs" className="text-gray-300 hover:text-white transition-colors">Docs</Link>
          </div>

          {/* CTA Buttons */}
          <div className="hidden md:flex items-center gap-4">
            <Link to="/login" className="text-gray-300 hover:text-white transition-colors">
              Iniciar Sesión
            </Link>
            <button 
              onClick={onGetStarted}
              className="px-5 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-full font-medium hover:opacity-90 transition-opacity flex items-center gap-2"
            >
              Comenzar <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button 
            className="md:hidden text-white"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-gray-900/95 backdrop-blur-md border-t border-gray-800">
            <div className="px-4 py-4 space-y-3">
              <a href="#features" className="block text-gray-300 hover:text-white py-2">Características</a>
              <a href="#how-it-works" className="block text-gray-300 hover:text-white py-2">Cómo Funciona</a>
              <a href="#pricing" className="block text-gray-300 hover:text-white py-2">Precios</a>
              <Link to="/docs" className="block text-gray-300 hover:text-white py-2">Docs</Link>
              <hr className="border-gray-800" />
              <Link to="/login" className="block text-gray-300 hover:text-white py-2">Iniciar Sesión</Link>
              <button 
                onClick={onGetStarted}
                className="w-full px-5 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-full font-medium"
              >
                Comenzar
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

// Hero Section
const HeroSection = ({ onGetStarted }) => {
  const [prompt, setPrompt] = useState('');
  
  const examplePrompts = [
    "Crea un dashboard SaaS con analíticas",
    "Construye una tienda online con pagos Stripe",
    "Diseña un foro comunitario con chat en tiempo real",
    "Crea una herramienta de gestión de proyectos"
  ];

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gray-950 pt-16">
      {/* Background Effects */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=%2260%22 height=%2260%22 viewBox=%220 0 60 60%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cg fill=%22none%22 fill-rule=%22evenodd%22%3E%3Cg fill=%22%239C92AC%22 fill-opacity=%220.05%22%3E%3Cpath d=%22M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-30" />
      </div>

      <div className="relative z-10 max-w-5xl mx-auto px-4 text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-full text-sm text-gray-300 mb-8">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <span>Plataforma de Desarrollo con IA</span>
          <span className="px-2 py-0.5 bg-cyan-500/20 text-cyan-400 rounded-full text-xs font-medium">NUEVO</span>
        </div>

        {/* Main Headline - KEEP IN ENGLISH */}
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
          Build Full-Stack Apps
          <br />
          <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 bg-clip-text text-transparent">
            in Minutes, Not Months
          </span>
        </h1>

        <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
          Describe tu idea en lenguaje natural. Nuestro sistema multi-agente de IA construye 
          aplicaciones web y móviles completas con frontend, backend, base de datos y despliegue.
        </p>

        {/* Prompt Input */}
        <div className="max-w-2xl mx-auto mb-8">
          <div className="relative bg-gray-900/80 backdrop-blur-sm border border-gray-700 rounded-2xl p-2 focus-within:border-cyan-500/50 transition-colors">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe tu idea de app... ej: 'Crea una app de gestión de tareas con equipos y actualizaciones en tiempo real'"
              className="w-full bg-transparent text-white placeholder-gray-500 px-4 py-3 resize-none focus:outline-none text-lg"
              rows={2}
            />
            <div className="flex items-center justify-between px-2">
              <div className="flex items-center gap-2 text-gray-500 text-sm">
                <Cpu className="w-4 h-4" />
                <span>Impulsado por GPT-4o</span>
              </div>
              <button 
                onClick={onGetStarted}
                className="px-6 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-xl font-medium hover:opacity-90 transition-opacity flex items-center gap-2"
              >
                <Play className="w-4 h-4" /> Comenzar
              </button>
            </div>
          </div>
        </div>

        {/* Example Prompts */}
        <div className="flex flex-wrap justify-center gap-2 mb-12">
          {examplePrompts.map((example, i) => (
            <button
              key={i}
              onClick={() => setPrompt(example)}
              className="px-4 py-2 bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 rounded-full text-sm text-gray-400 hover:text-white transition-colors"
            >
              {example}
            </button>
          ))}
        </div>

        {/* Stats */}
        <div className="flex flex-wrap justify-center gap-8 md:gap-16">
          {[
            { value: '50K+', label: 'Apps Creadas' },
            { value: '10x', label: 'Más Rápido' },
            { value: '99%', label: 'Uptime' },
            { value: '4.9', label: 'Valoración', icon: Star }
          ].map((stat, i) => (
            <div key={i} className="text-center">
              <div className="text-3xl font-bold text-white flex items-center justify-center gap-1">
                {stat.value}
                {stat.icon && <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />}
              </div>
              <div className="text-gray-500 text-sm">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
        <ChevronDown className="w-6 h-6 text-gray-500" />
      </div>
    </section>
  );
};

// Features Section
const FeaturesSection = () => {
  const features = [
    {
      icon: Bot,
      title: 'Sistema Multi-Agente IA',
      description: '6 agentes de IA especializados trabajan juntos: Planificador, Investigador, Desarrollador, QA, Optimizador y Control de Costos.',
      color: 'cyan'
    },
    {
      icon: Code2,
      title: 'Generación Full-Stack',
      description: 'Frontend completo (React/Vue), backend (FastAPI/Node), esquemas de base de datos e integraciones API.',
      color: 'blue'
    },
    {
      icon: Layers,
      title: 'Vista Previa en Vivo',
      description: 'Ve tu app mientras se construye. Itera con comandos en lenguaje natural para refinar el resultado.',
      color: 'purple'
    },
    {
      icon: Database,
      title: 'Base de Datos y APIs',
      description: 'Diseño automático de base de datos, migraciones y conexiones a APIs externas como Stripe, Auth, etc.',
      color: 'green'
    },
    {
      icon: Rocket,
      title: 'Despliegue en Un Clic',
      description: 'Despliega instantáneamente a hosting en la nube con SSL, CDN y auto-escalado incluido.',
      color: 'orange'
    },
    {
      icon: Shield,
      title: 'Seguridad Empresarial',
      description: 'Mejores prácticas de seguridad integradas, limitación de velocidad y cumplimiento de protección de datos.',
      color: 'red'
    }
  ];

  const colorClasses = {
    cyan: 'from-cyan-500/20 to-cyan-500/5 border-cyan-500/20 text-cyan-400',
    blue: 'from-blue-500/20 to-blue-500/5 border-blue-500/20 text-blue-400',
    purple: 'from-purple-500/20 to-purple-500/5 border-purple-500/20 text-purple-400',
    green: 'from-green-500/20 to-green-500/5 border-green-500/20 text-green-400',
    orange: 'from-orange-500/20 to-orange-500/5 border-orange-500/20 text-orange-400',
    red: 'from-red-500/20 to-red-500/5 border-red-500/20 text-red-400'
  };

  return (
    <section id="features" className="py-24 bg-gray-950">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            Todo lo que Necesitas para Construir
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            De la idea a producción en minutos. Nuestra IA maneja la complejidad para que te enfoques en lo que importa.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, i) => (
            <div 
              key={i}
              className={`p-6 rounded-2xl bg-gradient-to-b ${colorClasses[feature.color]} border backdrop-blur-sm hover:scale-105 transition-transform duration-300`}
            >
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colorClasses[feature.color]} flex items-center justify-center mb-4`}>
                <feature.icon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-gray-400">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// How It Works Section
const HowItWorksSection = () => {
  const steps = [
    {
      number: '01',
      title: 'Describe Tu Idea',
      description: 'Dile a nuestra IA qué quieres construir en español simple. Sé tan detallado o breve como quieras.',
      visual: 'prompt'
    },
    {
      number: '02',
      title: 'La IA Planifica y Construye',
      description: 'Nuestro sistema multi-agente analiza requisitos, diseña arquitectura y genera código.',
      visual: 'agents'
    },
    {
      number: '03',
      title: 'Revisa e Itera',
      description: 'Previsualiza tu app en tiempo real. Solicita cambios y refinamientos a través de conversación.',
      visual: 'preview'
    },
    {
      number: '04',
      title: 'Despliega y Escala',
      description: 'Un clic para desplegar. Tu app sale en vivo con hosting, SSL y escalado gestionado.',
      visual: 'deploy'
    }
  ];

  return (
    <section id="how-it-works" className="py-24 bg-gray-900">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            Cómo Funciona
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Del concepto a producción en cuatro simples pasos
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, i) => (
            <div key={i} className="relative">
              {i < steps.length - 1 && (
                <div className="hidden lg:block absolute top-8 left-full w-full h-0.5 bg-gradient-to-r from-cyan-500/50 to-transparent" />
              )}
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 text-white text-2xl font-bold mb-4">
                  {step.number}
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">{step.title}</h3>
                <p className="text-gray-400">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Pricing Section
const PricingSection = ({ onGetStarted }) => {
  const plans = [
    {
      name: 'Gratis',
      price: '$0',
      period: 'para siempre',
      description: 'Perfecto para probar MelusAI',
      credits: '1,000',
      features: [
        '1,000 créditos/mes',
        'Modelos IA básicos',
        'Soporte comunitario',
        'Exportar a GitHub',
        '3 proyectos activos'
      ],
      cta: 'Comenzar Gratis',
      highlighted: false
    },
    {
      name: 'Pro',
      price: '$29',
      period: '/mes',
      description: 'Para constructores serios',
      credits: '50,000',
      features: [
        '50,000 créditos/mes',
        'GPT-4o y modelos avanzados',
        'Soporte prioritario',
        'Proyectos ilimitados',
        'Despliegues personalizados',
        'Acceso API'
      ],
      cta: 'Prueba Pro Gratis',
      highlighted: true
    },
    {
      name: 'Empresa',
      price: 'Personalizado',
      period: '',
      description: 'Para organizaciones a escala',
      credits: 'Ilimitado',
      features: [
        'Créditos ilimitados',
        'Modelos IA personalizados',
        'Soporte dedicado',
        'Opción marca blanca',
        'Garantía SLA',
        'Despliegue on-premise'
      ],
      cta: 'Contactar Ventas',
      highlighted: false
    }
  ];

  return (
    <section id="pricing" className="py-24 bg-gray-950">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            Precios Simples y Transparentes
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Comienza gratis, escala mientras creces. Sin costos ocultos.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {plans.map((plan, i) => (
            <div 
              key={i}
              className={`relative p-8 rounded-2xl border ${
                plan.highlighted 
                  ? 'bg-gradient-to-b from-cyan-500/10 to-blue-600/10 border-cyan-500/50' 
                  : 'bg-gray-900/50 border-gray-800'
              }`}
            >
              {plan.highlighted && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full text-sm font-medium text-white">
                  Más Popular
                </div>
              )}
              
              <div className="text-center mb-6">
                <h3 className="text-xl font-semibold text-white mb-2">{plan.name}</h3>
                <div className="flex items-baseline justify-center gap-1">
                  <span className="text-4xl font-bold text-white">{plan.price}</span>
                  <span className="text-gray-400">{plan.period}</span>
                </div>
                <p className="text-gray-400 text-sm mt-2">{plan.description}</p>
              </div>

              <div className="mb-6 p-4 bg-gray-800/50 rounded-xl text-center">
                <span className="text-2xl font-bold text-cyan-400">{plan.credits}</span>
                <span className="text-gray-400 text-sm block">créditos/mes</span>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, j) => (
                  <li key={j} className="flex items-center gap-3 text-gray-300">
                    <Check className="w-5 h-5 text-cyan-400 flex-shrink-0" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <button 
                onClick={onGetStarted}
                className={`w-full py-3 rounded-xl font-medium transition-colors ${
                  plan.highlighted
                    ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white hover:opacity-90'
                    : 'bg-gray-800 text-white hover:bg-gray-700'
                }`}
              >
                {plan.cta}
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// FAQ Section
const FAQSection = () => {
  const [openIndex, setOpenIndex] = useState(null);
  
  const faqs = [
    {
      question: '¿Qué puedo construir con MelusAI?',
      answer: 'Puedes construir virtualmente cualquier aplicación web o móvil: plataformas SaaS, tiendas e-commerce, dashboards, sitios comunitarios, APIs y más. Nuestra IA maneja frontend, backend, base de datos e integraciones.'
    },
    {
      question: '¿Necesito experiencia en programación?',
      answer: '¡No se requiere experiencia en código! Simplemente describe lo que quieres en lenguaje simple. Sin embargo, los desarrolladores también pueden usar MelusAI para acelerar su flujo de trabajo y completar proyectos más complejos más rápido.'
    },
    {
      question: '¿Cómo funcionan los créditos?',
      answer: 'Los créditos se consumen según la complejidad de las operaciones. Las tareas simples usan menos créditos, mientras que las operaciones IA complejas usan más. Puedes ver el uso de créditos en tiempo real en tu panel.'
    },
    {
      question: '¿Puedo exportar mi código?',
      answer: '¡Sí! Eres dueño del 100% del código generado. Exporta a GitHub, descarga como ZIP o despliega directamente a tu propia infraestructura.'
    },
    {
      question: '¿Qué modelos de IA usan?',
      answer: 'Usamos un enfoque multi-modelo incluyendo GPT-4o para razonamiento complejo, con fallbacks automáticos y optimización de costos. Los usuarios empresariales también pueden traer sus propios modelos.'
    },
    {
      question: '¿Mis datos están seguros?',
      answer: 'Absolutamente. Seguimos las mejores prácticas de la industria incluyendo cifrado en reposo y en tránsito, cumplimiento SOC 2, y nunca entrenamos con tus datos sin consentimiento explícito.'
    }
  ];

  return (
    <section className="py-24 bg-gray-900">
      <div className="max-w-3xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            Preguntas Frecuentes
          </h2>
          <p className="text-xl text-gray-400">
            Todo lo que necesitas saber sobre MelusAI
          </p>
        </div>

        <div className="space-y-4">
          {faqs.map((faq, i) => (
            <div 
              key={i}
              className="border border-gray-800 rounded-xl overflow-hidden"
            >
              <button
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                className="w-full px-6 py-4 flex items-center justify-between text-left bg-gray-900/50 hover:bg-gray-800/50 transition-colors"
              >
                <span className="text-lg font-medium text-white">{faq.question}</span>
                <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${openIndex === i ? 'rotate-180' : ''}`} />
              </button>
              {openIndex === i && (
                <div className="px-6 py-4 bg-gray-800/30 text-gray-400">
                  {faq.answer}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// CTA Section
const CTASection = ({ onGetStarted }) => {
  return (
    <section className="py-24 bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
      <div className="max-w-4xl mx-auto px-4 text-center">
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
          ¿Listo para Construir Tu Próxima
          <br />
          <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            Gran Idea?
          </span>
        </h2>
        <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
          Únete a miles de constructores que están enviando productos más rápido con MelusAI.
          Comienza gratis, sin tarjeta de crédito requerida.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button 
            onClick={onGetStarted}
            className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-full font-medium text-lg hover:opacity-90 transition-opacity flex items-center gap-2"
          >
            Comenzar Gratis <ArrowRight className="w-5 h-5" />
          </button>
          <Link 
            to="/docs"
            className="px-8 py-4 bg-gray-800 hover:bg-gray-700 text-white rounded-full font-medium text-lg transition-colors"
          >
            Leer Documentación
          </Link>
        </div>
      </div>
    </section>
  );
};

// Footer
const Footer = () => {
  const links = {
    Producto: ['Características', 'Precios', 'Integraciones', 'Changelog', 'Roadmap'],
    Recursos: ['Documentación', 'Tutoriales', 'Blog', 'Casos de Éxito', 'Referencia API'],
    Empresa: ['Nosotros', 'Carreras', 'Prensa', 'Contacto', 'Socios'],
    Legal: ['Política de Privacidad', 'Términos de Servicio', 'Cookies', 'Seguridad']
  };

  return (
    <footer className="bg-gray-950 border-t border-gray-800">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid md:grid-cols-2 lg:grid-cols-6 gap-8 mb-12">
          {/* Brand */}
          <div className="lg:col-span-2">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white">
                Melus<span className="text-cyan-400">AI</span>
              </span>
            </Link>
            <p className="text-gray-400 mb-4">
              Construye aplicaciones full-stack en minutos con IA. 
              De la idea a producción, más rápido que nunca.
            </p>
            <div className="flex gap-4">
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <Github className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Links */}
          {Object.entries(links).map(([category, items]) => (
            <div key={category}>
              <h4 className="font-semibold text-white mb-4">{category}</h4>
              <ul className="space-y-2">
                {items.map((item) => (
                  <li key={item}>
                    <a href="#" className="text-gray-400 hover:text-white transition-colors">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom */}
        <div className="flex flex-col md:flex-row items-center justify-between pt-8 border-t border-gray-800">
          <p className="text-gray-500 text-sm">
            © 2024 MelusAI. Todos los derechos reservados.
          </p>
          <div className="flex items-center gap-4 mt-4 md:mt-0">
            <span className="flex items-center gap-2 text-gray-500 text-sm">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              Todos los sistemas operativos
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};

// Main Landing Page Component
const LandingPageNew = () => {
  const navigate = useNavigate();
  const { user, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && user) {
      navigate('/home');
    }
  }, [user, isLoading, navigate]);

  const handleGetStarted = () => {
    navigate('/login');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950">
      <Navigation onGetStarted={handleGetStarted} />
      <HeroSection onGetStarted={handleGetStarted} />
      <FeaturesSection />
      <HowItWorksSection />
      <PricingSection onGetStarted={handleGetStarted} />
      <FAQSection />
      <CTASection onGetStarted={handleGetStarted} />
      <Footer />
    </div>
  );
};

export default LandingPageNew;
