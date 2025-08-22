# StirCraft Docker Deployment Infrastructure

This document covers the Docker-based deployment infrastructure for StirCraft. For quick Heroku deployment, see `CONSOLIDATED_DEPLOYMENT_GUIDE.md`.

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

## Docker Files Overview

### Core Files
- **`Dockerfile`** - Multi-stage Django app container with security best practices
- **`docker-compose.yml`** - Development orchestration (DB, Redis, Web, Nginx)
- **`docker-compose.prod.yml`** - Production overrides with SSL and security

### Nginx Configuration
- **`docker/nginx/nginx.conf`** - Main Nginx configuration
- **`docker/nginx/default.conf`** - Development proxy settings
- **`docker/nginx/production.conf`** - Production SSL and security headers

## Quick Start

### Development with Docker
```bash
# Setup environment
cp .env.example .env  # Edit as needed

# Start all services
./deploy.sh dev

# Access application
http://localhost:8000
```

### Production Deployment
```bash
# Configure production environment
cp .env.prod.example .env.prod  # Edit with production values

# Deploy to production
./deploy.sh prod

# Setup SSL (optional)
./deploy.sh ssl yourdomain.com
```

## Security Features

- **Container Security**: Non-root execution, minimal base images, health checks
- **Network Security**: Isolated Docker networks, rate limiting, IP restrictions
- **SSL/HTTPS**: Auto-redirect, modern TLS configuration, Let's Encrypt integration
- **Data Security**: Environment isolation, encrypted connections, secure sessions

## Production Checklist

- [ ] Configure production environment variables in `.env.prod`
- [ ] Set up SSL certificates with `./deploy.sh ssl domain.com`
- [ ] Configure backup strategy for database
- [ ] Set up monitoring and log aggregation
- [ ] Test disaster recovery procedures

## Troubleshooting

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

---

*For simpler Heroku deployment without Docker, see `CONSOLIDATED_DEPLOYMENT_GUIDE.md`*

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
