# JamesOS Frontend

The frontend interface for JamesOS - AI Operating System. This Vue 3 application provides a comprehensive UI for managing MCPs, HTC training, pipeline operations, audits, and AI assistant interactions.

## 🚀 Features

### **Dashboard**
- Real-time system statistics and metrics
- Daily activity logs with filtering
- User inbox for notifications and alerts
- Pipeline status monitoring
- Recent activity charts

### **MCP Library**
- Browse and search job categories
- View resources (markdown/text) and tools (YAML/scripts)
- Filter by tags, categories, and usage
- Expandable MCP cards with full details
- Role-based views showing all related content

### **HTC (Hyperbolic Time Chamber)**
- Upload Q&A pairs for training
- Submit failed prompts for retry
- Track pass/fail cycles (up to 4 attempts)
- Training history and analytics
- Success rate monitoring

### **Pipeline (James Learning Flow)**
- Upload data for processing
- View sanitized content
- Review generated MCPs
- Human approval/rejection workflow
- Trigger reruns for failed operations

### **Audit**
- Input GitHub repos or client names
- Comprehensive audit posture analysis
- Security, GitOps, and migration readiness
- Auto-generated custom audit MCPs

### **James Assistant**
- Main AI assistant interface
- Task completion and automation
- Tool and resource retrieval
- Integration with all other modules

## 🛠 Tech Stack

- **Vue 3** - Progressive JavaScript framework
- **Vite** - Fast build tool and dev server
- **Vue Router** - Official router for Vue.js
- **Pinia** - State management for Vue
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls
- **Chart.js** - Charting library
- **ECharts** - Advanced charting library
- **Heroicons** - Beautiful hand-crafted SVG icons
- **Marked** - Markdown parser
- **Highlight.js** - Syntax highlighting
- **YAML** - YAML parser for tool definitions

## 📁 Project Structure

```
src/
├── components/          # Reusable Vue components
│   ├── McpCard.vue     # MCP resource/tool display card
│   └── RoleView.vue    # Complete role overview component
├── stores/             # Pinia state management
│   ├── index.js        # Store configuration
│   ├── mcp.js          # MCP library state
│   └── htc.js          # HTC training state
├── views/              # Page components
│   ├── Dashboard.vue   # Main dashboard
│   ├── McpLibrary.vue  # MCP browsing interface
│   ├── Htc.vue         # HTC training interface
│   ├── Pipeline.vue    # Pipeline management
│   ├── Audit.vue       # Audit interface
│   ├── James.vue       # AI assistant interface
│   ├── Login.vue       # Authentication
│   └── NotFound.vue    # 404 page
├── router/             # Vue Router configuration
│   └── index.js        # Route definitions
├── assets/             # Static assets
│   ├── tailwind.css    # Tailwind styles
│   └── holo-theme.css  # Custom theme styles
├── App.vue             # Root component
└── main.js             # Application entry point
```

## 🎨 Design System

### **Color Palette**
- **Primary**: Cyan (#00d4ff) - Main accent color
- **Secondary**: Purple (#ff00ff) - Gradient partner
- **Background**: Dark grays (#0a0a0a, #1a1a2e, #16213e)
- **Surface**: Gray-800 (#1f2937) - Card backgrounds
- **Text**: White (#ffffff) - Primary text
- **Muted**: Gray-300 (#d1d5db) - Secondary text

### **Typography**
- **Font Family**: Orbitron, Courier New, monospace
- **Weights**: 400 (normal), 600 (semibold), 700 (bold)
- **Sizes**: Responsive scale from 0.75rem to 3rem

### **Components**
- **Cards**: Rounded corners, subtle borders, hover effects
- **Buttons**: Gradient backgrounds, hover animations
- **Navigation**: Sticky header with blur effects
- **Forms**: Dark theme with cyan focus states

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm 8+

### Installation
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Development Commands
```bash
# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Format code
npm run format

# Type checking
npm run type-check

# Run tests
npm run test

# Test with UI
npm run test:ui

# Coverage report
npm run test:coverage
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=JamesOS
VITE_APP_VERSION=1.0.0
```

### API Integration
The frontend expects the following API endpoints:

- `GET /api/job-categories` - Fetch job categories
- `GET /api/resources` - Fetch MCP resources
- `GET /api/tools` - Fetch MCP tools
- `GET /api/search` - Global MCP search
- `GET /api/htc/qa-pairs` - Fetch HTC questions
- `POST /api/htc/upload` - Upload Q&A pairs
- `POST /api/htc/submit-answer` - Submit HTC answers

## 🎯 Key Components

### **McpCard.vue**
Reusable component for displaying MCP resources and tools:
- Expandable content view
- Tag filtering
- Markdown rendering
- Usage statistics
- Action buttons (view, edit, delete, use)

### **RoleView.vue**
Comprehensive role overview component:
- Tabbed interface (Duties, Resources, Tools, Keywords, Analytics)
- Search and filtering
- Usage statistics
- Related content linking

### **Global Search**
- Real-time search across all MCPs
- Tag-based filtering
- Search result navigation
- Keyboard shortcuts

## 🔄 State Management

### **MCP Store** (`stores/mcp.js`)
Manages MCP library state:
- Job categories
- Resources and tools
- Search functionality
- Filtering and sorting

### **HTC Store** (`stores/htc.js`)
Manages HTC training state:
- Q&A pairs
- Failed prompts
- Training history
- Success metrics

## 🎨 Customization

### **Themes**
Modify `assets/holo-theme.css` for custom styling:
```css
:root {
  --primary-color: #00d4ff;
  --secondary-color: #ff00ff;
  --background-gradient: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
}
```

### **Components**
All components use Tailwind CSS classes and can be customized by:
- Modifying component templates
- Adding custom CSS classes
- Extending Tailwind configuration

## 🧪 Testing

### **Unit Tests**
```bash
# Run all tests
npm run test

# Run tests with coverage
npm run test:coverage

# Watch mode
npm run test -- --watch
```

### **Component Testing**
Components are tested using Vitest and Vue Test Utils:
- Props validation
- Event emission
- User interactions
- State changes

## 📦 Build & Deployment

### **Production Build**
```bash
npm run build
```

### **Docker Deployment**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 80
CMD ["npm", "run", "preview"]
```

### **Environment-Specific Builds**
```bash
# Development
npm run dev

# Staging
npm run build -- --mode staging

# Production
npm run build -- --mode production
```

## 🔍 Performance

### **Optimizations**
- Code splitting with Vue Router
- Lazy loading of components
- Image optimization
- Tree shaking for unused code
- CSS purging with Tailwind

### **Monitoring**
- Bundle size analysis
- Performance metrics
- Error tracking
- User analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### **Code Style**
- Use Vue 3 Composition API
- Follow ESLint rules
- Use Prettier for formatting
- Write meaningful commit messages

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation
- Review existing issues
- Create a new issue with details
- Contact the development team

---

**JamesOS Frontend** - Empowering AI operations with a beautiful, intuitive interface.
