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

# CRM Template
CRM_TEMPLATE = {
    "name": "CRM System",
    "description": "Sistema de gestión de clientes con pipeline de ventas, contactos y seguimiento",
    "icon": "Users",
    "color": "from-blue-500 to-cyan-600",
    "estimated_credits": 550,
    "features": [
        "Pipeline de ventas",
        "Gestión de contactos",
        "Historial de interacciones",
        "Dashboard de métricas",
        "Filtros avanzados"
    ],
    "prompt": """Create a CRM (Customer Relationship Management) system with:

1. SIDEBAR:
- Logo
- Navigation: Dashboard, Contacts, Deals, Tasks, Reports
- User profile

2. DASHBOARD:
- Stats cards (Total Contacts, Active Deals, Revenue, Conversion Rate)
- Sales pipeline chart
- Recent activities list
- Upcoming tasks

3. CONTACTS PAGE:
- Contacts table (avatar, name, company, email, phone, status)
- Search and filters
- Add contact button with modal form
- Contact detail view with history

4. DEALS/PIPELINE PAGE:
- Kanban board with stages (Lead, Qualified, Proposal, Negotiation, Won, Lost)
- Deal cards with value, contact, probability
- Drag and drop between stages
- Deal detail modal

5. TASKS PAGE:
- Task list with due dates
- Filter by status, assignee
- Add task form

Dark theme with blue accents. Professional CRM look. Tailwind CSS."""
}

# Chat App Template
CHAT_APP_TEMPLATE = {
    "name": "Chat Application",
    "description": "Aplicación de mensajería en tiempo real con chats, grupos y notificaciones",
    "icon": "MessageCircle",
    "color": "from-green-500 to-teal-600",
    "estimated_credits": 450,
    "features": [
        "Chat en tiempo real",
        "Lista de conversaciones",
        "Mensajes con timestamps",
        "Estados de usuario",
        "Búsqueda de mensajes"
    ],
    "prompt": """Create a modern chat application with:

1. SIDEBAR (Left):
- User profile header
- Search conversations
- Conversation list (avatar, name, last message, time, unread count)
- Online/offline status indicators
- New chat button

2. CHAT AREA (Center):
- Chat header (contact info, status, actions)
- Messages area with bubbles
- Own messages on right (purple/blue)
- Others messages on left (gray)
- Timestamps
- Message input with send button
- Emoji picker button
- Attachment button

3. INFO PANEL (Right, optional):
- Contact details
- Shared media
- Shared files

4. FEATURES:
- Typing indicator
- Read receipts
- Message timestamps
- Online status dots

Dark theme like Discord/Telegram. Modern chat UI. Tailwind CSS."""
}

# Social Network Template
SOCIAL_TEMPLATE = {
    "name": "Social Network",
    "description": "Red social con feed de publicaciones, perfiles, likes y comentarios",
    "icon": "Share2",
    "color": "from-pink-500 to-rose-600",
    "estimated_credits": 500,
    "features": [
        "Feed de publicaciones",
        "Perfiles de usuario",
        "Likes y comentarios",
        "Seguir usuarios",
        "Notificaciones"
    ],
    "prompt": """Create a social network application with:

1. HEADER:
- Logo
- Search bar
- Navigation icons (Home, Explore, Notifications, Messages)
- User profile dropdown

2. FEED (Center):
- Create post card (avatar, input, media buttons)
- Post cards with:
  - Author info (avatar, name, time)
  - Post content (text, images)
  - Action buttons (Like, Comment, Share)
  - Like count, comment count
  - Comments section (expandable)

3. SIDEBAR LEFT:
- User profile card
- Quick stats (posts, followers, following)
- Navigation links

4. SIDEBAR RIGHT:
- Trending topics
- Suggested users to follow
- Footer links

5. PROFILE PAGE:
- Cover photo
- Profile info
- Tab navigation (Posts, About, Photos, Friends)
- User's posts

Dark theme like Twitter/Instagram dark mode. Tailwind CSS."""
}

# Inventory System Template
INVENTORY_TEMPLATE = {
    "name": "Inventory System",
    "description": "Sistema de inventario con productos, stock, categorías y alertas",
    "icon": "Package",
    "color": "from-amber-500 to-orange-600",
    "estimated_credits": 450,
    "features": [
        "Gestión de productos",
        "Control de stock",
        "Categorías",
        "Alertas de stock bajo",
        "Historial de movimientos"
    ],
    "prompt": """Create an inventory management system with:

1. SIDEBAR:
- Dashboard
- Products
- Categories
- Stock Movements
- Suppliers
- Reports
- Settings

2. DASHBOARD:
- Stats (Total Products, Low Stock Alerts, Total Value, Categories)
- Low stock alerts list
- Recent movements
- Stock value chart

3. PRODUCTS PAGE:
- Products table (image, SKU, name, category, stock, price, status)
- Search and category filter
- Add product button
- Edit/Delete actions
- Stock quantity badges (green=ok, yellow=low, red=out)

4. STOCK MOVEMENTS:
- Movement history table
- Filter by type (In/Out)
- Add movement form
- Movement details

5. CATEGORIES PAGE:
- Category list with product count
- Add/Edit category

Dark theme with amber/orange accents. Clean inventory UI. Tailwind CSS."""
}

# Booking System Template
BOOKING_TEMPLATE = {
    "name": "Booking System",
    "description": "Sistema de reservas para servicios con calendario, disponibilidad y confirmaciones",
    "icon": "Calendar",
    "color": "from-indigo-500 to-violet-600",
    "estimated_credits": 500,
    "features": [
        "Calendario interactivo",
        "Gestión de citas",
        "Servicios y precios",
        "Confirmaciones",
        "Panel de admin"
    ],
    "prompt": """Create a booking/appointment system with:

1. PUBLIC BOOKING PAGE:
- Service selection cards
- Date picker calendar
- Available time slots
- Customer info form
- Booking confirmation

2. ADMIN DASHBOARD:
- Today's appointments
- Upcoming appointments
- Stats (Total bookings, Revenue, Cancellations)
- Calendar overview

3. CALENDAR VIEW:
- Monthly/Weekly/Daily views
- Appointments shown as colored blocks
- Click to view details
- Drag to reschedule

4. SERVICES MANAGEMENT:
- Services list (name, duration, price)
- Add/Edit service
- Enable/Disable service

5. BOOKINGS LIST:
- All bookings table
- Filter by date, status, service
- Booking details modal
- Confirm/Cancel actions

Dark theme with indigo/violet accents. Clean booking UI. Tailwind CSS."""
}

# Analytics Dashboard Template
ANALYTICS_TEMPLATE = {
    "name": "Analytics Dashboard",
    "description": "Dashboard de analytics con gráficos, métricas y reportes en tiempo real",
    "icon": "BarChart3",
    "color": "from-emerald-500 to-green-600",
    "estimated_credits": 450,
    "features": [
        "Métricas en tiempo real",
        "Gráficos interactivos",
        "Reportes exportables",
        "Filtros de fecha",
        "KPIs personalizables"
    ],
    "prompt": """Create an analytics dashboard with:

1. HEADER:
- Dashboard title
- Date range picker
- Refresh button
- Export button

2. KPI CARDS ROW:
- Total Users (with % change)
- Page Views (with % change)
- Bounce Rate (with % change)
- Avg Session Duration (with % change)
- Conversion Rate (with % change)

3. MAIN CHARTS:
- Line chart: Traffic over time
- Bar chart: Top pages
- Pie chart: Traffic sources
- Area chart: User engagement

4. DATA TABLES:
- Top pages table (page, views, unique views, bounce rate)
- Top referrers table
- Device breakdown

5. REAL-TIME SECTION:
- Active users now
- Live events feed
- Current page views

Dark theme with green accents. Data-rich dashboard. Tailwind CSS."""
}

# Update TEMPLATES dict
TEMPLATES.update({
    "crm": CRM_TEMPLATE,
    "chat": CHAT_APP_TEMPLATE,
    "social": SOCIAL_TEMPLATE,
    "inventory": INVENTORY_TEMPLATE,
    "booking": BOOKING_TEMPLATE,
    "analytics": ANALYTICS_TEMPLATE
})
