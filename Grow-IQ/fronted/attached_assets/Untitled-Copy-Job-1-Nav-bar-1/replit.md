# Overview

GrowIQ is a modern job search and application platform built as a full-stack web application. The platform allows users to browse job listings, view detailed job information, apply for positions, manage their profiles, and track their applications through a comprehensive dashboard. It features a clean, professional interface with company profiles, user authentication, and settings management.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The frontend is built using React with TypeScript and follows a component-based architecture using shadcn/ui design system. Key architectural decisions include:

- **React with Wouter**: Uses Wouter for client-side routing instead of React Router for a lighter footprint
- **Component Library**: Built on shadcn/ui components with Radix UI primitives for accessibility
- **Styling**: Tailwind CSS with custom CSS variables for theming and consistent design
- **State Management**: TanStack Query (React Query) for server state management and caching
- **Form Handling**: React Hook Form with Zod validation for type-safe form validation
- **TypeScript**: Full TypeScript implementation for type safety across the application

The application follows a page-based routing structure with dedicated pages for job listings, job details, applications, user profiles, company profiles, dashboard, login, and settings.

## Backend Architecture
The backend uses Node.js with Express in a modern ESM setup:

- **Express Server**: RESTful API with middleware for JSON parsing and request logging
- **Database Layer**: Drizzle ORM with PostgreSQL for type-safe database operations
- **Storage Interface**: Abstracted storage layer with both in-memory implementation (MemStorage) for development and database implementation for production
- **Session Management**: Uses connect-pg-simple for PostgreSQL-based session storage
- **Development Setup**: Hot reload with tsx and integrated Vite development server

## Database Design
The database schema is defined using Drizzle ORM with PostgreSQL:

- **Users Table**: Basic user authentication with username/password
- **Type Safety**: Drizzle Zod integration for runtime validation matching database schema
- **Migrations**: Automated migrations through Drizzle Kit

## Development Workflow
The application uses a monorepo structure with shared types and schema:

- **Shared Schema**: Common types and validation schemas between client and server
- **Vite Integration**: Development server with hot module replacement
- **TypeScript Configuration**: Unified TypeScript setup with path aliases for clean imports
- **Build Process**: Separate build processes for client (Vite) and server (esbuild)

# External Dependencies

## UI and Components
- **shadcn/ui**: Complete UI component library built on Radix UI primitives
- **Radix UI**: Low-level UI primitives for accessibility and behavior
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Lucide React**: Icon library for consistent iconography
- **class-variance-authority**: Utility for creating variant-based component APIs

## State Management and Data Fetching
- **TanStack Query**: Server state management with caching, background updates, and optimistic updates
- **React Hook Form**: Form handling with minimal re-renders
- **Zod**: Schema validation library for type-safe form validation

## Database and Backend
- **Drizzle ORM**: Type-safe ORM for PostgreSQL with migration support
- **Neon Database**: Serverless PostgreSQL database service (@neondatabase/serverless)
- **Express**: Web framework for the API server
- **connect-pg-simple**: PostgreSQL session store for Express sessions

## Development Tools
- **Vite**: Build tool and development server for the frontend
- **tsx**: TypeScript execution engine for Node.js development
- **esbuild**: Fast bundler for production server builds
- **Replit integrations**: Development environment specific plugins and tools

## Routing and Navigation
- **Wouter**: Minimalist routing library for React applications

The architecture emphasizes type safety, developer experience, and modern web development practices while maintaining a clean separation between frontend, backend, and shared concerns.