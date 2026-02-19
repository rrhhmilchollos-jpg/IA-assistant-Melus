"""
MelusAI - Code Generation Engine
Motor de generación de código real para cualquier tipo de proyecto
"""
import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ProjectType(Enum):
    WEB_STATIC = "web_static"
    WEB_APP = "web_app"
    ECOMMERCE = "ecommerce"
    MOBILE_APP = "mobile_app"
    GAME_2D = "game_2d"
    GAME_3D = "game_3d"
    FULLSTACK = "fullstack"


@dataclass
class GeneratedFile:
    path: str
    content: str
    language: str


@dataclass
class ProjectStructure:
    project_type: ProjectType
    name: str
    description: str
    stack: Dict[str, str]
    files: List[GeneratedFile]
    preview_entry: str
    build_commands: List[str]
    deploy_config: Dict[str, Any]


# ===========================================
# PROJECT TEMPLATES
# ===========================================

def get_react_template(name: str, features: List[str]) -> Dict[str, str]:
    """Genera estructura base de React con Vite"""
    files = {
        "package.json": json.dumps({
            "name": name.lower().replace(" ", "-"),
            "private": True,
            "version": "0.1.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.3.1",
                "react-dom": "^18.3.1",
                "react-router-dom": "^6.26.0",
                "lucide-react": "^0.400.0",
                "clsx": "^2.1.1",
                "tailwind-merge": "^2.4.0"
            },
            "devDependencies": {
                "@vitejs/plugin-react": "^4.3.1",
                "vite": "^5.4.0",
                "tailwindcss": "^3.4.7",
                "autoprefixer": "^10.4.19",
                "postcss": "^8.4.40"
            }
        }, indent=2),
        
        "vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true
  }
})
""",
        
        "tailwind.config.js": """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
""",
        
        "postcss.config.js": """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""",
        
        "index.html": f"""<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
""",
        
        "src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
""",
        
        "src/index.css": """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --primary: #6366f1;
  --secondary: #8b5cf6;
}

body {
  @apply bg-gray-50 text-gray-900 antialiased;
}
""",
        
        "src/App.jsx": """import React from 'react'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600">
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold text-white text-center">
          {/* PROJECT_NAME */}
        </h1>
        <p className="text-white/80 text-center mt-4">
          Tu aplicación está lista para personalizar
        </p>
      </div>
    </div>
  )
}

export default App
""".replace("{/* PROJECT_NAME */}", name)
    }
    
    return files


def get_game_2d_template(name: str, game_type: str) -> Dict[str, str]:
    """Genera estructura base para juego 2D con Phaser"""
    files = {
        "package.json": json.dumps({
            "name": name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "scripts": {
                "dev": "vite",
                "build": "vite build"
            },
            "dependencies": {
                "phaser": "^3.80.1"
            },
            "devDependencies": {
                "vite": "^5.4.0"
            }
        }, indent=2),
        
        "index.html": f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            min-height: 100vh;
            background: #1a1a2e;
        }}
        #game-container {{ 
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        }}
    </style>
</head>
<body>
    <div id="game-container"></div>
    <script type="module" src="/src/main.js"></script>
</body>
</html>
""",
        
        "src/main.js": """import Phaser from 'phaser'
import { BootScene } from './scenes/BootScene'
import { GameScene } from './scenes/GameScene'
import { UIScene } from './scenes/UIScene'

const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    parent: 'game-container',
    backgroundColor: '#2d2d44',
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 300 },
            debug: false
        }
    },
    scene: [BootScene, GameScene, UIScene]
}

const game = new Phaser.Game(config)
""",
        
        "src/scenes/BootScene.js": """import Phaser from 'phaser'

export class BootScene extends Phaser.Scene {
    constructor() {
        super({ key: 'BootScene' })
    }

    preload() {
        // Mostrar barra de carga
        const width = this.cameras.main.width
        const height = this.cameras.main.height
        
        const progressBar = this.add.graphics()
        const progressBox = this.add.graphics()
        progressBox.fillStyle(0x222222, 0.8)
        progressBox.fillRect(width/2 - 160, height/2 - 25, 320, 50)
        
        const loadingText = this.add.text(width/2, height/2 - 50, 'Cargando...', {
            font: '20px monospace',
            fill: '#ffffff'
        }).setOrigin(0.5, 0.5)
        
        this.load.on('progress', (value) => {
            progressBar.clear()
            progressBar.fillStyle(0x6366f1, 1)
            progressBar.fillRect(width/2 - 150, height/2 - 15, 300 * value, 30)
        })
        
        this.load.on('complete', () => {
            progressBar.destroy()
            progressBox.destroy()
            loadingText.destroy()
        })
        
        // Cargar assets aquí
        // this.load.image('player', 'assets/player.png')
        // this.load.spritesheet('player-run', 'assets/player-run.png', { frameWidth: 32, frameHeight: 32 })
    }

    create() {
        this.scene.start('GameScene')
    }
}
""",
        
        "src/scenes/GameScene.js": """import Phaser from 'phaser'

export class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene' })
        this.score = 0
    }

    create() {
        // Crear jugador (rectángulo temporal)
        this.player = this.add.rectangle(400, 300, 40, 40, 0x6366f1)
        this.physics.add.existing(this.player)
        this.player.body.setCollideWorldBounds(true)
        
        // Controles
        this.cursors = this.input.keyboard.createCursorKeys()
        this.wasd = this.input.keyboard.addKeys({
            up: Phaser.Input.Keyboard.KeyCodes.W,
            down: Phaser.Input.Keyboard.KeyCodes.S,
            left: Phaser.Input.Keyboard.KeyCodes.A,
            right: Phaser.Input.Keyboard.KeyCodes.D
        })
        
        // Iniciar UI
        this.scene.launch('UIScene')
        
        // Texto de instrucciones
        this.add.text(400, 50, 'Usa WASD o flechas para moverte', {
            font: '16px Arial',
            fill: '#ffffff'
        }).setOrigin(0.5)
    }

    update() {
        const speed = 200
        
        // Reset velocity
        this.player.body.setVelocity(0)
        
        // Horizontal movement
        if (this.cursors.left.isDown || this.wasd.left.isDown) {
            this.player.body.setVelocityX(-speed)
        } else if (this.cursors.right.isDown || this.wasd.right.isDown) {
            this.player.body.setVelocityX(speed)
        }
        
        // Vertical movement
        if (this.cursors.up.isDown || this.wasd.up.isDown) {
            this.player.body.setVelocityY(-speed)
        } else if (this.cursors.down.isDown || this.wasd.down.isDown) {
            this.player.body.setVelocityY(speed)
        }
    }
    
    addScore(points) {
        this.score += points
        this.events.emit('updateScore', this.score)
    }
}
""",
        
        "src/scenes/UIScene.js": """import Phaser from 'phaser'

export class UIScene extends Phaser.Scene {
    constructor() {
        super({ key: 'UIScene' })
    }

    create() {
        // Score display
        this.scoreText = this.add.text(16, 16, 'Score: 0', {
            font: '24px Arial',
            fill: '#ffffff',
            stroke: '#000000',
            strokeThickness: 4
        })
        
        // Listen for score updates
        const gameScene = this.scene.get('GameScene')
        gameScene.events.on('updateScore', (score) => {
            this.scoreText.setText('Score: ' + score)
        })
    }
}
"""
    }
    
    return files


def get_game_3d_template(name: str) -> Dict[str, str]:
    """Genera estructura base para juego 3D con Three.js"""
    files = {
        "package.json": json.dumps({
            "name": name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "scripts": {
                "dev": "vite",
                "build": "vite build"
            },
            "dependencies": {
                "three": "^0.168.0",
                "@react-three/fiber": "^8.17.0",
                "@react-three/drei": "^9.111.0",
                "react": "^18.3.1",
                "react-dom": "^18.3.1"
            },
            "devDependencies": {
                "@vitejs/plugin-react": "^4.3.1",
                "vite": "^5.4.0"
            }
        }, indent=2),
        
        "index.html": f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <style>
        * {{ margin: 0; padding: 0; }}
        html, body, #root {{ width: 100%; height: 100%; overflow: hidden; }}
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
</body>
</html>
""",
        
        "src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Environment, PerspectiveCamera } from '@react-three/drei'
import Game from './Game'

function App() {
    return (
        <Canvas shadows>
            <PerspectiveCamera makeDefault position={[0, 5, 10]} />
            <OrbitControls enableDamping />
            <ambientLight intensity={0.5} />
            <directionalLight 
                position={[10, 10, 5]} 
                intensity={1} 
                castShadow 
                shadow-mapSize={[2048, 2048]}
            />
            <Environment preset="sunset" />
            <Game />
        </Canvas>
    )
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />)
""",
        
        "src/Game.jsx": """import React, { useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { Box, Plane, Text } from '@react-three/drei'

function Player({ position }) {
    const meshRef = useRef()
    
    useFrame((state, delta) => {
        meshRef.current.rotation.y += delta * 0.5
    })
    
    return (
        <Box ref={meshRef} position={position} castShadow>
            <meshStandardMaterial color="#6366f1" />
        </Box>
    )
}

function Ground() {
    return (
        <Plane 
            args={[50, 50]} 
            rotation={[-Math.PI / 2, 0, 0]} 
            position={[0, -0.5, 0]}
            receiveShadow
        >
            <meshStandardMaterial color="#1a1a2e" />
        </Plane>
    )
}

export default function Game() {
    const [score, setScore] = useState(0)
    
    return (
        <>
            <Player position={[0, 0.5, 0]} />
            <Ground />
            <Text
                position={[0, 3, 0]}
                fontSize={0.5}
                color="white"
                anchorX="center"
                anchorY="middle"
            >
                Score: {score}
            </Text>
            <Text
                position={[0, 2.3, 0]}
                fontSize={0.2}
                color="#888"
                anchorX="center"
            >
                Usa el mouse para rotar la cámara
            </Text>
        </>
    )
}
"""
    }
    
    return files


def get_ecommerce_template(name: str) -> Dict[str, str]:
    """Genera estructura completa de E-commerce"""
    base_files = get_react_template(name, ["auth", "cart", "payments"])
    
    # Agregar más dependencias para e-commerce
    package_json = json.loads(base_files["package.json"])
    package_json["dependencies"].update({
        "@stripe/stripe-js": "^4.1.0",
        "@stripe/react-stripe-js": "^2.7.3",
        "zustand": "^4.5.4",
        "axios": "^1.7.3"
    })
    base_files["package.json"] = json.dumps(package_json, indent=2)
    
    # Agregar componentes de e-commerce
    base_files["src/store/cartStore.js"] = """import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useCartStore = create(
    persist(
        (set, get) => ({
            items: [],
            
            addItem: (product, quantity = 1) => {
                const items = get().items
                const existingItem = items.find(item => item.id === product.id)
                
                if (existingItem) {
                    set({
                        items: items.map(item =>
                            item.id === product.id
                                ? { ...item, quantity: item.quantity + quantity }
                                : item
                        )
                    })
                } else {
                    set({ items: [...items, { ...product, quantity }] })
                }
            },
            
            removeItem: (productId) => {
                set({ items: get().items.filter(item => item.id !== productId) })
            },
            
            updateQuantity: (productId, quantity) => {
                if (quantity <= 0) {
                    get().removeItem(productId)
                    return
                }
                set({
                    items: get().items.map(item =>
                        item.id === productId ? { ...item, quantity } : item
                    )
                })
            },
            
            clearCart: () => set({ items: [] }),
            
            get total() {
                return get().items.reduce(
                    (sum, item) => sum + item.price * item.quantity,
                    0
                )
            },
            
            get itemCount() {
                return get().items.reduce((sum, item) => sum + item.quantity, 0)
            }
        }),
        { name: 'cart-storage' }
    )
)
"""

    base_files["src/components/ProductCard.jsx"] = """import React from 'react'
import { ShoppingCart } from 'lucide-react'
import { useCartStore } from '../store/cartStore'

export function ProductCard({ product }) {
    const addItem = useCartStore(state => state.addItem)
    
    return (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden group">
            <div className="aspect-square bg-gray-100 relative overflow-hidden">
                <img 
                    src={product.image} 
                    alt={product.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                />
                {product.discount && (
                    <span className="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 text-sm rounded">
                        -{product.discount}%
                    </span>
                )}
            </div>
            <div className="p-4">
                <h3 className="font-semibold text-gray-900 truncate">{product.name}</h3>
                <p className="text-sm text-gray-500 mt-1 line-clamp-2">{product.description}</p>
                <div className="flex items-center justify-between mt-4">
                    <div>
                        <span className="text-xl font-bold text-indigo-600">
                            {product.price.toFixed(2)}€
                        </span>
                        {product.originalPrice && (
                            <span className="text-sm text-gray-400 line-through ml-2">
                                {product.originalPrice.toFixed(2)}€
                            </span>
                        )}
                    </div>
                    <button
                        onClick={() => addItem(product)}
                        className="p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                        <ShoppingCart size={20} />
                    </button>
                </div>
            </div>
        </div>
    )
}
"""

    base_files["src/components/Cart.jsx"] = """import React from 'react'
import { X, Plus, Minus, ShoppingBag } from 'lucide-react'
import { useCartStore } from '../store/cartStore'

export function Cart({ isOpen, onClose }) {
    const { items, removeItem, updateQuantity, total, clearCart } = useCartStore()
    
    if (!isOpen) return null
    
    return (
        <div className="fixed inset-0 z-50">
            <div className="absolute inset-0 bg-black/50" onClick={onClose} />
            <div className="absolute right-0 top-0 h-full w-full max-w-md bg-white shadow-xl">
                <div className="flex flex-col h-full">
                    <div className="flex items-center justify-between p-4 border-b">
                        <h2 className="text-xl font-bold flex items-center gap-2">
                            <ShoppingBag /> Carrito
                        </h2>
                        <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
                            <X size={24} />
                        </button>
                    </div>
                    
                    <div className="flex-1 overflow-auto p-4">
                        {items.length === 0 ? (
                            <div className="text-center text-gray-500 py-8">
                                Tu carrito está vacío
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {items.map(item => (
                                    <div key={item.id} className="flex gap-4 bg-gray-50 p-3 rounded-lg">
                                        <img 
                                            src={item.image} 
                                            alt={item.name}
                                            className="w-20 h-20 object-cover rounded"
                                        />
                                        <div className="flex-1">
                                            <h3 className="font-medium">{item.name}</h3>
                                            <p className="text-indigo-600 font-bold">{item.price.toFixed(2)}€</p>
                                            <div className="flex items-center gap-2 mt-2">
                                                <button 
                                                    onClick={() => updateQuantity(item.id, item.quantity - 1)}
                                                    className="p-1 bg-gray-200 rounded"
                                                >
                                                    <Minus size={16} />
                                                </button>
                                                <span className="w-8 text-center">{item.quantity}</span>
                                                <button 
                                                    onClick={() => updateQuantity(item.id, item.quantity + 1)}
                                                    className="p-1 bg-gray-200 rounded"
                                                >
                                                    <Plus size={16} />
                                                </button>
                                            </div>
                                        </div>
                                        <button 
                                            onClick={() => removeItem(item.id)}
                                            className="text-red-500 hover:text-red-700"
                                        >
                                            <X size={20} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                    
                    {items.length > 0 && (
                        <div className="border-t p-4 space-y-4">
                            <div className="flex justify-between text-xl font-bold">
                                <span>Total:</span>
                                <span className="text-indigo-600">{total.toFixed(2)}€</span>
                            </div>
                            <button className="w-full py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition-colors">
                                Proceder al pago
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
"""

    return base_files


# ===========================================
# CODE GENERATOR CLASS
# ===========================================

class CodeGenerator:
    """Motor principal de generación de código"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
        
    async def generate_project(
        self,
        description: str,
        project_type: ProjectType,
        custom_requirements: Optional[Dict] = None
    ) -> ProjectStructure:
        """Genera un proyecto completo basado en la descripción"""
        
        # 1. Obtener template base
        if project_type == ProjectType.GAME_2D:
            files = get_game_2d_template(description[:30], "platformer")
        elif project_type == ProjectType.GAME_3D:
            files = get_game_3d_template(description[:30])
        elif project_type == ProjectType.ECOMMERCE:
            files = get_ecommerce_template(description[:30])
        else:
            files = get_react_template(description[:30], [])
        
        # 2. Personalizar con LLM según descripción
        # (aquí iría la llamada al LLM para personalizar el código)
        
        # 3. Crear estructura de proyecto
        generated_files = [
            GeneratedFile(path=path, content=content, language=self._detect_language(path))
            for path, content in files.items()
        ]
        
        return ProjectStructure(
            project_type=project_type,
            name=description[:30],
            description=description,
            stack=self._get_stack_for_type(project_type),
            files=generated_files,
            preview_entry="index.html",
            build_commands=["npm install", "npm run dev"],
            deploy_config={"platform": "vercel", "framework": "vite"}
        )
    
    def _detect_language(self, filename: str) -> str:
        """Detecta el lenguaje por extensión"""
        ext_map = {
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".css": "css",
            ".html": "html",
            ".json": "json",
            ".py": "python",
            ".md": "markdown"
        }
        for ext, lang in ext_map.items():
            if filename.endswith(ext):
                return lang
        return "text"
    
    def _get_stack_for_type(self, project_type: ProjectType) -> Dict[str, str]:
        """Retorna el stack tecnológico por tipo de proyecto"""
        stacks = {
            ProjectType.WEB_STATIC: {
                "frontend": "React + Vite",
                "styling": "TailwindCSS",
                "deploy": "Vercel/Netlify"
            },
            ProjectType.WEB_APP: {
                "frontend": "React + Vite",
                "backend": "FastAPI",
                "database": "PostgreSQL",
                "styling": "TailwindCSS"
            },
            ProjectType.ECOMMERCE: {
                "frontend": "React + Vite",
                "backend": "FastAPI",
                "database": "PostgreSQL",
                "payments": "Stripe",
                "styling": "TailwindCSS"
            },
            ProjectType.GAME_2D: {
                "engine": "Phaser 3",
                "bundler": "Vite",
                "language": "JavaScript"
            },
            ProjectType.GAME_3D: {
                "engine": "Three.js + React Three Fiber",
                "bundler": "Vite",
                "language": "JavaScript/React"
            },
            ProjectType.MOBILE_APP: {
                "framework": "React Native + Expo",
                "backend": "FastAPI",
                "database": "PostgreSQL"
            },
            ProjectType.FULLSTACK: {
                "frontend": "React + Vite",
                "backend": "FastAPI",
                "database": "PostgreSQL",
                "mobile": "React Native",
                "styling": "TailwindCSS"
            }
        }
        return stacks.get(project_type, stacks[ProjectType.WEB_STATIC])
