// Mock data for Assistant Melus
export const mockConversations = [
  {
    id: '1',
    title: 'Bienvenida a Assistant Melus',
    timestamp: new Date('2025-01-15T10:30:00'),
    messages: [
      {
        id: 'm1',
        role: 'user',
        content: 'Hola, ¿qué puedes hacer?',
        timestamp: new Date('2025-01-15T10:30:00')
      },
      {
        id: 'm2',
        role: 'assistant',
        content: '¡Hola! Soy Assistant Melus, tu asistente de inteligencia artificial. Puedo ayudarte con una amplia variedad de tareas como:\n\n• Responder preguntas sobre cualquier tema\n• Ayudarte con programación y código\n• Escribir y editar textos\n• Analizar información\n• Resolver problemas\n• Y mucho más\n\n¿En qué puedo ayudarte hoy?',
        timestamp: new Date('2025-01-15T10:30:15')
      }
    ]
  },
  {
    id: '2',
    title: 'Consejos de programación',
    timestamp: new Date('2025-01-14T15:20:00'),
    messages: [
      {
        id: 'm3',
        role: 'user',
        content: '¿Cuáles son las mejores prácticas para escribir código limpio?',
        timestamp: new Date('2025-01-14T15:20:00')
      },
      {
        id: 'm4',
        role: 'assistant',
        content: 'Excelente pregunta. Aquí están algunas de las mejores prácticas para código limpio:\n\n1. **Nombres descriptivos**: Usa nombres claros que expliquen el propósito\n2. **Funciones pequeñas**: Cada función debe hacer una sola cosa\n3. **Comentarios útiles**: Comenta el "por qué", no el "qué"\n4. **DRY**: No te repitas (Don\'t Repeat Yourself)\n5. **Manejo de errores**: Siempre valida y maneja errores apropiadamente\n6. **Formateo consistente**: Usa un estilo de código uniforme\n\n¿Quieres profundizar en alguno de estos puntos?',
        timestamp: new Date('2025-01-14T15:20:20')
      }
    ]
  },
  {
    id: '3',
    title: 'Recetas de cocina',
    timestamp: new Date('2025-01-13T09:15:00'),
    messages: [
      {
        id: 'm5',
        role: 'user',
        content: 'Dame una receta fácil para el almuerzo',
        timestamp: new Date('2025-01-13T09:15:00')
      },
      {
        id: 'm6',
        role: 'assistant',
        content: 'Aquí tienes una receta súper fácil y deliciosa:\n\n**Pasta con Ajo y Aceite de Oliva**\n\n**Ingredientes:**\n- 400g de pasta\n- 4 dientes de ajo\n- 100ml de aceite de oliva\n- Perejil fresco\n- Sal y pimienta\n- Queso parmesano (opcional)\n\n**Preparación:**\n1. Cocina la pasta según las instrucciones del paquete\n2. Mientras tanto, pica el ajo finamente\n3. Calienta el aceite y sofríe el ajo hasta dorar\n4. Mezcla la pasta con el aceite de ajo\n5. Añade perejil, sal y pimienta\n6. Sirve con parmesano\n\n¡Listo en 15 minutos!',
        timestamp: new Date('2025-01-13T09:15:25')
      }
    ]
  }
];

export const getMockConversations = () => {
  return [...mockConversations];
};

export const getMockConversationById = (id) => {
  return mockConversations.find(conv => conv.id === id);
};

export const createMockMessage = (role, content) => {
  return {
    id: `m${Date.now()}`,
    role,
    content,
    timestamp: new Date()
  };
};

export const getMockAIResponse = (userMessage) => {
  // Simulate AI response delay and content
  const responses = [
    'Esa es una excelente pregunta. Déjame ayudarte con eso...',
    'Entiendo lo que necesitas. Aquí está mi respuesta...',
    'Claro, con gusto te ayudo con eso...',
    'Interesante pregunta. Te explico...',
    'Por supuesto, aquí tienes la información que buscas...'
  ];
  
  const randomResponse = responses[Math.floor(Math.random() * responses.length)];
  return `${randomResponse}\n\nEsta es una respuesta de demostración a tu mensaje: "${userMessage}". En la versión completa con backend, aquí aparecerán las respuestas reales de la IA usando modelos avanzados de lenguaje.`;
};