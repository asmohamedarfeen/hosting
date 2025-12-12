# Overview

This is a full-stack web application built with React, TypeScript, and Express.js that appears to be a career platform called "GrowIQ". The application features an AI-powered job matching system that analyzes user profiles and matches them with relevant opportunities. The platform includes a modern landing page with sections for statistics, company information, and opportunities.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **Styling**: Tailwind CSS with custom design tokens and CSS variables
- **Component Library**: Radix UI primitives with shadcn/ui components for consistent design
- **Routing**: Wouter for lightweight client-side routing
- **State Management**: TanStack Query (React Query) for server state management
- **Form Handling**: React Hook Form with Zod validation resolvers

## Backend Architecture
- **Runtime**: Node.js with Express.js framework
- **Language**: TypeScript with ES modules
- **API Design**: RESTful API with `/api` prefix for all endpoints
- **Database ORM**: Drizzle ORM for type-safe database operations
- **Database**: PostgreSQL (configured for Neon Database serverless)
- **Session Management**: Express sessions with PostgreSQL store using connect-pg-simple

## Data Storage
- **Primary Database**: PostgreSQL with connection pooling via Neon Database serverless driver
- **ORM**: Drizzle ORM with schema-first approach
- **Migrations**: Drizzle Kit for database schema management
- **Schema Location**: Shared schema definitions in `/shared/schema.ts`
- **Session Storage**: PostgreSQL-backed session store for user authentication

## Development Environment
- **Monorepo Structure**: Client and server code in single repository
- **Hot Reload**: Vite HMR for frontend, tsx for backend development
- **Path Aliases**: Configured for clean imports (`@/`, `@shared/`)
- **Error Handling**: Runtime error overlay for development
- **Development Tools**: Replit-specific plugins for enhanced development experience

## Key Design Patterns
- **Shared Types**: Common TypeScript types and schemas shared between client and server
- **Component Composition**: Radix UI primitives wrapped with custom styling
- **Server-Side Rendering Ready**: Vite configured for potential SSR implementation
- **Storage Abstraction**: Interface-based storage layer with in-memory implementation for development

# External Dependencies

## Database Services
- **Neon Database**: Serverless PostgreSQL database with connection pooling
- **Environment Variables**: `DATABASE_URL` required for database connectivity

## UI and Styling
- **Radix UI**: Comprehensive set of accessible, unstyled UI primitives
- **Tailwind CSS**: Utility-first CSS framework with custom configuration
- **Lucide React**: Icon library for consistent iconography
- **Google Fonts**: Custom font integration (Sora, DM Sans, Fira Code, Geist Mono)

## Development Tools
- **Replit Integration**: Enhanced development experience with cartographer and dev banner plugins
- **TypeScript**: Full type safety across the stack
- **ESBuild**: Fast bundling for production builds
- **PostCSS**: CSS processing with Tailwind and Autoprefixer

## Form and Validation
- **React Hook Form**: Performant form library with minimal re-renders
- **Zod**: TypeScript-first schema validation
- **Drizzle Zod**: Integration between Drizzle ORM and Zod for consistent validation

## Potential Future Integrations
- **Authentication Provider**: Ready for integration with services like Auth0, Firebase Auth, or custom JWT
- **File Storage**: Prepared for integration with AWS S3, Cloudinary, or similar
- **Email Service**: Structure supports integration with SendGrid, Mailgun, or similar
- **Analytics**: Ready for Google Analytics, Mixpanel, or similar tracking services