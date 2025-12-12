# Overview

GrowIQ is a modern job search and application platform built as a full-stack web application. The platform allows users to browse job listings, view detailed job information, apply for positions, manage their profiles, and track application status through a comprehensive dashboard system.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The frontend is built using React with TypeScript and follows a component-based architecture using shadcn/ui design system. Key architectural decisions include:

- **React with Wouter**: Uses Wouter for client-side routing instead of React Router for a lighter footprint and better performance
- **Component Library**: Built on shadcn/ui components with Radix UI primitives for accessibility and consistent design patterns
- **Styling**: Tailwind CSS with custom CSS variables for theming, using the "new-york" style variant with neutral base colors
- **State Management**: TanStack Query (React Query) for server state management and caching, with custom query client configuration
- **Form Handling**: React Hook Form with Zod validation for type-safe form validation and error handling
- **Animations**: Custom transition system with Figma-style gradient ball animations and bounce effects for page transitions
- **TypeScript**: Full TypeScript implementation for type safety across the application

The application follows a page-based routing structure with dedicated pages for job listings, job details, applications, user profiles, company profiles, dashboard, login, and settings.

## Backend Architecture
The backend uses Node.js with Express in a modern ESM setup:

- **Express Server**: RESTful API with middleware for JSON parsing, URL encoding, and comprehensive request logging
- **Database Layer**: Drizzle ORM with PostgreSQL for type-safe database operations and schema management
- **Storage Interface**: Abstracted storage layer with IStorage interface, including MemStorage implementation for development and database implementation for production
- **Development Integration**: Hot reload with tsx and integrated Vite development server for seamless development experience
- **Error Handling**: Centralized error handling middleware with proper HTTP status codes and JSON responses

## Database Design
The database schema is defined using Drizzle ORM with PostgreSQL:

- **Users Table**: Basic user authentication with username/password fields, using serial primary key
- **Type Safety**: Drizzle Zod integration for runtime validation that matches database schema definitions
- **Migrations**: Automated migrations through Drizzle Kit with proper configuration for PostgreSQL dialect

## Development Workflow
The application uses a monorepo structure with shared types and schema:

- **Shared Schema**: Common types and validation schemas between client and server in the shared directory
- **Vite Integration**: Development server with hot module replacement and runtime error overlay
- **TypeScript Configuration**: Unified TypeScript setup with path aliases for clean imports (@/, @shared/, @assets/)
- **Build Process**: Separate optimized build processes for client (Vite) and server (esbuild)
- **Replit Integration**: Custom Vite plugins for Replit development environment including cartographer and runtime error modal

## UI/UX Design System
The application implements a comprehensive design system:

- **Custom Color Palette**: Gradient-based theming with primary purple (#673ab7) and secondary teal (#00bfa6) colors
- **Typography**: Sora font family with defined font sizes and weights for consistency
- **Animation System**: Custom animations including fade-in, fade-up, marquee, and bounce effects
- **Responsive Design**: Mobile-first approach with proper breakpoints and responsive components

# External Dependencies

## UI and Components
- **shadcn/ui**: Complete UI component library built on Radix UI primitives for accessibility
- **Radix UI**: Comprehensive set of low-level UI primitives for building high-quality design systems
- **Tailwind CSS**: Utility-first CSS framework with PostCSS and Autoprefixer integration
- **Lucide React**: Icon library providing consistent iconography throughout the application

## Frontend State and Routing
- **TanStack Query**: Powerful data synchronization library for React applications
- **Wouter**: Minimalist routing library as lightweight alternative to React Router
- **React Hook Form**: Performant forms library with easy validation integration
- **Zod**: TypeScript-first schema validation library

## Backend Infrastructure
- **Express.js**: Fast, unopinionated web framework for Node.js
- **Drizzle ORM**: Lightweight TypeScript ORM with excellent PostgreSQL support
- **Neon Database**: Serverless PostgreSQL database service (@neondatabase/serverless)
- **connect-pg-simple**: Session storage using PostgreSQL for Express sessions

## Development Tools
- **Vite**: Next generation frontend build tool with fast HMR and optimized builds
- **TypeScript**: Static type checking for enhanced developer experience and code reliability
- **tsx**: TypeScript execution environment for Node.js development
- **esbuild**: Extremely fast JavaScript bundler for production server builds

## Styling and Animation
- **class-variance-authority**: Utility for creating variant-based component APIs
- **clsx**: Utility for constructing className strings conditionally
- **tailwind-merge**: Utility for merging Tailwind CSS classes without style conflicts
- **Embla Carousel**: Lightweight carousel library with React bindings

## Validation and Forms
- **@hookform/resolvers**: Validation resolver for React Hook Form
- **drizzle-zod**: Integration layer between Drizzle ORM and Zod validation
- **date-fns**: Modern JavaScript date utility library for date manipulation

## Development Environment
- **@replit/vite-plugin-runtime-error-modal**: Replit-specific plugin for enhanced error reporting
- **@replit/vite-plugin-cartographer**: Replit integration for development environment mapping