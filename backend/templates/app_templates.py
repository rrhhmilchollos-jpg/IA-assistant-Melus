"""Pre-built Application Templates for Quick Generation"""

# E-commerce Template
ECOMMERCE_TEMPLATE = {
    "name": "E-Commerce Store",
    "description": "Tienda online completa con catálogo de productos, carrito de compras, checkout y gestión de pedidos",
    "icon": "ShoppingCart",
    "color": "from-green-500 to-emerald-600",
    "estimated_credits": 450,
    "features": [
        "Catálogo de productos con filtros",
        "Carrito de compras",
        "Proceso de checkout",
        "Gestión de pedidos",
        "Panel de admin"
    ],
    "prompt": """Create a complete e-commerce store with:

1. HOME PAGE:
- Hero banner with featured products
- Product categories grid
- Featured products carousel
- Newsletter signup

2. PRODUCT CATALOG:
- Grid of product cards (image, name, price, rating)
- Filter sidebar (category, price range, rating)
- Sort options (price, popularity, newest)
- Pagination

3. PRODUCT DETAIL:
- Large product images gallery
- Product info (name, price, description, stock)
- Size/variant selector
- Add to cart button
- Related products

4. SHOPPING CART:
- List of cart items with quantity controls
- Remove item button
- Cart summary (subtotal, shipping, total)
- Proceed to checkout button

5. CHECKOUT:
- Shipping address form
- Payment method selection (mock)
- Order summary
- Place order button

Use dark theme with accent colors. Make it beautiful and modern with Tailwind CSS."""
}

# Blog Template
BLOG_TEMPLATE = {
    "name": "Blog Platform",
    "description": "Blog moderno con artículos, categorías, sistema de comentarios y panel de autor",
    "icon": "FileText",
    "color": "from-blue-500 to-indigo-600",
    "estimated_credits": 350,
    "features": [
        "Listado de artículos",
        "Categorías y tags",
        "Página de artículo",
        "Sistema de comentarios",
        "Panel de autor"
    ],
    "prompt": """Create a modern blog platform with:

1. HOME PAGE:
- Hero section with featured post
- Latest posts grid (3 columns)
- Categories sidebar
- Popular posts widget
- Newsletter signup

2. BLOG LISTING:
- Post cards (thumbnail, title, excerpt, date, author)
- Category filter
- Search bar
- Pagination

3. SINGLE POST PAGE:
- Post header (title, author, date, reading time)
- Featured image
- Rich content area
- Author bio box
- Related posts
- Comments section

4. CATEGORIES PAGE:
- Category list with post count
- Posts filtered by category

5. ABOUT/AUTHOR PAGE:
- Author profile
- Author's posts

Use dark theme. Typography should be excellent for reading. Tailwind CSS."""
}

# Dashboard Template
DASHBOARD_TEMPLATE = {
    "name": "Admin Dashboard",
    "description": "Panel de administración con métricas, gráficos, tablas de datos y gestión de usuarios",
    "icon": "LayoutDashboard",
    "color": "from-purple-500 to-pink-600",
    "estimated_credits": 500,
    "features": [
        "Métricas en tiempo real",
        "Gráficos interactivos",
        "Tablas de datos",
        "Gestión de usuarios",
        "Configuración"
    ],
    "prompt": """Create an admin dashboard with:

1. SIDEBAR:
- Logo
- Navigation menu (Dashboard, Users, Analytics, Settings)
- Collapse toggle
- User profile at bottom

2. DASHBOARD PAGE:
- Stats cards (Total Users, Revenue, Orders, Growth)
- Line chart for revenue over time
- Bar chart for user activity
- Recent orders table
- Recent users list

3. USERS PAGE:
- Users table (avatar, name, email, role, status, actions)
- Search and filter
- Add user button
- Edit/Delete actions
- Pagination

4. ANALYTICS PAGE:
- Multiple charts
- Date range selector
- Export button
- Key metrics

5. SETTINGS PAGE:
- Profile settings form
- Notification preferences
- Security settings
- Theme toggle

Use dark theme with purple accents. Professional look. Tailwind CSS."""
}

# Landing Page Template
LANDING_TEMPLATE = {
    "name": "Landing Page",
    "description": "Página de aterrizaje para producto SaaS con hero, features, pricing y CTA",
    "icon": "Rocket",
    "color": "from-orange-500 to-red-600",
    "estimated_credits": 300,
    "features": [
        "Hero section animada",
        "Features grid",
        "Pricing tables",
        "Testimonials",
        "Contact form"
    ],
    "prompt": """Create a stunning SaaS landing page with:

1. HERO SECTION:
- Catchy headline
- Subheadline with value proposition
- CTA buttons (Get Started, Watch Demo)
- Hero image or illustration
- Gradient background

2. FEATURES SECTION:
- 6 feature cards with icons
- Title and description each
- Hover animations

3. HOW IT WORKS:
- 3 step process
- Icons/illustrations
- Brief descriptions

4. TESTIMONIALS:
- 3 testimonial cards
- Avatar, name, role, company
- Quote text
- Star rating

5. PRICING:
- 3 pricing tiers (Free, Pro, Enterprise)
- Feature list per tier
- CTA buttons
- Popular badge on middle tier

6. FAQ:
- Accordion FAQ items
- Common questions

7. CTA SECTION:
- Final call to action
- Email signup form

8. FOOTER:
- Links, social icons, copyright

Make it BEAUTIFUL with animations, gradients, and modern design. Dark theme. Tailwind CSS."""
}

# Task Manager Template
TASKMANAGER_TEMPLATE = {
    "name": "Task Manager",
    "description": "Aplicación de gestión de tareas estilo Trello/Notion con boards, listas y drag & drop",
    "icon": "CheckSquare",
    "color": "from-cyan-500 to-blue-600",
    "estimated_credits": 400,
    "features": [
        "Boards/Proyectos",
        "Listas de tareas",
        "Cards con detalles",
        "Drag & drop",
        "Filtros y búsqueda"
    ],
    "prompt": """Create a task management app like Trello with:

1. SIDEBAR:
- Workspace name
- Boards list
- Create new board button
- Settings link

2. BOARD VIEW:
- Board title
- Lists in horizontal scroll (To Do, In Progress, Done)
- Add new list button

3. LIST:
- List title (editable)
- Task cards
- Add task button
- Delete list option

4. TASK CARD:
- Task title
- Labels/tags (color coded)
- Due date badge
- Assignee avatar
- Click to open modal

5. TASK MODAL:
- Full task details
- Description editor
- Checklist
- Due date picker
- Labels selector
- Comments section
- Delete button

Use dark theme with colorful labels. Clean, minimal design. Tailwind CSS."""
}

# Portfolio Template
PORTFOLIO_TEMPLATE = {
    "name": "Portfolio",
    "description": "Portfolio personal para desarrolladores/diseñadores con proyectos, skills y contacto",
    "icon": "User",
    "color": "from-violet-500 to-purple-600",
    "estimated_credits": 300,
    "features": [
        "Hero con introducción",
        "Galería de proyectos",
        "Sección de skills",
        "Timeline experiencia",
        "Formulario de contacto"
    ],
    "prompt": """Create a developer portfolio website with:

1. HERO SECTION:
- Name and title
- Brief intro text
- Profile photo
- Social links (GitHub, LinkedIn, Twitter)
- Download CV button
- Animated background

2. ABOUT SECTION:
- Detailed bio
- Photo
- Stats (years experience, projects, clients)

3. SKILLS SECTION:
- Skill categories (Frontend, Backend, Tools)
- Skill bars or badges
- Icons for each technology

4. PROJECTS SECTION:
- Project cards grid
- Screenshot, title, description
- Tech stack tags
- Live demo and GitHub links
- Hover effects

5. EXPERIENCE TIMELINE:
- Work history
- Company, role, dates
- Key achievements

6. CONTACT SECTION:
- Contact form (name, email, message)
- Email and location info
- Social links

Make it visually stunning with smooth animations. Dark theme with accent color. Tailwind CSS."""
}

# All templates
TEMPLATES = {
    "ecommerce": ECOMMERCE_TEMPLATE,
    "blog": BLOG_TEMPLATE,
    "dashboard": DASHBOARD_TEMPLATE,
    "landing": LANDING_TEMPLATE,
    "taskmanager": TASKMANAGER_TEMPLATE,
    "portfolio": PORTFOLIO_TEMPLATE
}

def get_template(template_id: str) -> dict:
    """Get a template by ID"""
    return TEMPLATES.get(template_id)

def get_all_templates() -> list:
    """Get all available templates"""
    return [
        {"id": k, **{key: v[key] for key in ["name", "description", "icon", "color", "estimated_credits", "features"]}}
        for k, v in TEMPLATES.items()
    ]
