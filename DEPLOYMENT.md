# ==============================================================================
# StirCraft Deployment Infrastructure Guide
# ==============================================================================
# This document explains the deployment infrastructure setup for StirCraft
# ==============================================================================

## Overview

The StirCraft deployment infrastructure uses Docker containers orchestrated with Docker Compose. This setup provides:

- **Containerized Application**: Django app runs in isolated containers
- **Database**: PostgreSQL for persistent data storage
- **Caching**: Redis for session storage and caching
- **Web Server**: Nginx for serving static files and reverse proxy
- **SSL/HTTPS**: Let's Encrypt integration for secure connections
- **Environment Management**: Separate configs for dev/staging/production

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   Django Web    │    │   PostgreSQL    │
│  (Port 80/443)  │────│   (Port 8000)   │────│   (Port 5432)   │
│  Static Files   │    │   Application   │    │    Database     │
│  SSL Termination│    │     Logic       │    │    Storage      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              │
                       ┌─────────────────┐
                       │      Redis      │
                       │   (Port 6379)   │
                       │  Cache/Sessions │
                       └─────────────────┘
```

## Files Explained

### Core Docker Files

#### `Dockerfile`
- **Purpose**: Builds the Django application container
- **Multi-stage build**: Optimizes image size and security
- **Base image**: Python 3.11 slim for smaller footprint
- **Security**: Runs as non-root user 'stircraft'
- **Production server**: Uses Gunicorn WSGI server

#### `docker-compose.yml`
- **Purpose**: Orchestrates all services for development
- **Services**: Database, Redis, Web app, Nginx
- **Volumes**: Persistent storage for database and media files
- **Networks**: Isolated network for service communication
- **Health checks**: Ensures services are ready before dependencies start

#### `docker-compose.prod.yml`
- **Purpose**: Production-specific overrides
- **Security**: Removes port exposure, adds SSL configuration
- **Performance**: Optimized database and Redis settings
- **Monitoring**: Production logging and health checks

### Nginx Configuration

#### `docker/nginx/nginx.conf`
- **Purpose**: Main Nginx configuration
- **Settings**: Worker processes, logging, MIME types
- **Security**: Hides server version, optimizes connections

#### `docker/nginx/default.conf`
- **Purpose**: Development reverse proxy configuration
- **Features**: Static file serving, request proxying to Django
- **Caching**: Aggressive caching for static assets
- **Security**: Basic security headers

#### `docker/nginx/production.conf`
- **Purpose**: Production Nginx configuration with SSL
- **Features**: HTTPS redirect, SSL termination, rate limiting
- **Security**: HSTS, CSP headers, IP restrictions for admin
- **Performance**: Gzip compression, optimized caching

### Environment Configuration

#### `.env.example`
- **Purpose**: Template for development environment variables
- **Contains**: Database URLs, debug settings, API keys
- **Usage**: Copy to `.env` and customize for local development

#### `.env.prod.example`
- **Purpose**: Template for production environment variables
- **Security**: Production secret keys, SSL settings
- **Performance**: Gunicorn worker configuration
- **Monitoring**: Sentry integration, logging levels

### Deployment Scripts

#### `deploy.sh`
- **Purpose**: Automated deployment and management script
- **Commands**: 
  - `./deploy.sh dev` - Set up development environment
  - `./deploy.sh prod` - Deploy to production
  - `./deploy.sh backup` - Create database backup
  - `./deploy.sh ssl domain.com` - Set up SSL certificates

## Quick Start

### Development Setup

1. **Prerequisites**: Install Docker and Docker Compose
2. **Configuration**: Copy `.env.example` to `.env` and configure
3. **Start services**: `./deploy.sh dev`
4. **Access application**: http://localhost:8000

### Production Deployment

1. **Server setup**: Install Docker on production server
2. **Configuration**: Copy `.env.prod.example` to `.env.prod` and configure
3. **Deploy**: `./deploy.sh prod`
4. **SSL setup**: `./deploy.sh ssl yourdomain.com`
5. **Access application**: https://yourdomain.com

## Security Features

### Container Security
- Non-root user execution
- Minimal base images
- Multi-stage builds to reduce attack surface
- Health checks for service monitoring

### Network Security
- Isolated Docker networks
- No unnecessary port exposure in production
- Rate limiting on authentication endpoints
- IP restrictions for admin interface (configurable)

### SSL/HTTPS
- Automatic HTTP to HTTPS redirection
- Modern SSL/TLS configuration
- HSTS headers for security
- Let's Encrypt integration for free certificates

### Data Security
- Environment variable isolation
- Database connection encryption
- Secure session management with Redis
- Content Security Policy headers

## Performance Optimizations

### Application Layer
- Gunicorn WSGI server with multiple workers
- Connection pooling for database
- Redis caching for sessions and data
- Static file serving with aggressive caching

### Web Server Layer
- Nginx reverse proxy for better performance
- Gzip compression for text content
- Browser caching for static assets
- HTTP/2 support for modern browsers

### Database Layer
- PostgreSQL with optimized settings
- Connection pooling and timeout management
- Regular backups with retention policy
- Health monitoring and alerting

## Monitoring and Maintenance

### Logging
- Centralized logging for all services
- Structured log format for analysis
- Log rotation and retention policies
- Error tracking with Sentry (optional)

### Backups
- Automated database backups
- Configurable retention periods
- Easy restore procedures
- Media file backup strategies

### Updates
- Blue-green deployment strategy
- Database migration automation
- Dependency update procedures
- Security patch management

## Scaling Considerations

### Horizontal Scaling
- Load balancer configuration
- Multiple Django application instances
- Database read replicas
- CDN integration for static files

### Vertical Scaling
- Resource allocation guidelines
- Memory and CPU optimization
- Database tuning parameters
- Cache size configuration

## Troubleshooting

### Common Issues
- Container startup failures
- Database connection problems
- SSL certificate issues
- Performance bottlenecks

### Debugging Commands
```bash
# View service logs
./deploy.sh logs [service]

# Check service health
docker-compose ps

# Access container shell
docker-compose exec web bash

# Database connection test
docker-compose exec web python stircraft/manage.py dbshell
```

## Production Checklist

- [ ] Configure production environment variables
- [ ] Set up SSL certificates
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerting
- [ ] Configure email settings
- [ ] Review security settings
- [ ] Test disaster recovery procedures
- [ ] Document operational procedures
