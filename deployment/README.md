# StirCraft Deployment Options

This folder contains deployment configurations for the StirCraft application.

## Current Deployment Strategy: Heroku ✅

**StirCraft is currently deployed and running on Heroku:**
- **Live URL**: https://stircraft-app-0dd06cf5d30a.herokuapp.com/
- **Admin Panel**: https://stircraft-app-0dd06cf5d30a.herokuapp.com/admin/
- **Status**: ✅ Production-ready and fully functional

### Heroku Deployment Files (Root Level)
- `Procfile` - Defines how Heroku runs the application
- `requirements.txt` - Python dependencies for Heroku
- `.env.example` - Environment variable template

## Alternative Deployment: Docker 🐳

The `docker/` folder contains a complete containerized deployment setup for teams that prefer Docker or need to deploy on other platforms.

### Docker Files
```
deployment/docker/
├── Dockerfile              # Multi-stage production build
├── docker-compose.yml      # Development environment
├── docker-compose.prod.yml # Production overrides
├── .dockerignore          # Files to exclude from Docker context
└── nginx/                 # Nginx reverse proxy configuration
    ├── nginx.conf
    ├── default.conf
    └── production.conf
```

### When to Use Docker
- **Local Development**: Consistent environment across team members
- **Alternative Platforms**: AWS ECS, DigitalOcean, self-hosted servers
- **Microservices**: If expanding to multiple services
- **Team Preference**: If team is more comfortable with containerization

### Docker Quick Start
```bash
# Development environment
cd deployment/docker
docker-compose up

# Production environment  
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## Deployment Scripts

### `deploy.sh`
Comprehensive deployment automation script with support for:
- Development environment setup
- Docker deployment
- Environment validation
- Database management

**Note**: Currently Docker-focused. For Heroku deployment, use the standard `git push heroku main` workflow.

## Choosing Your Deployment Strategy

### Use Heroku (Current) When:
- ✅ **Simplicity**: You want minimal DevOps overhead
- ✅ **Speed**: Quick deployment and scaling
- ✅ **Team Focus**: More time for features, less for infrastructure
- ✅ **Cost**: Free tier available, predictable pricing
- ✅ **Add-ons**: Easy PostgreSQL, Redis, monitoring integration

### Use Docker When:
- 🐳 **Control**: Need more control over environment and configuration
- 🐳 **Cost**: Long-term cost optimization on other platforms
- 🐳 **Portability**: Need to deploy on multiple platforms
- 🐳 **Complexity**: Application grows to multiple services
- 🐳 **Team Expertise**: Team has strong Docker/Kubernetes experience

## Security Considerations

### Heroku
- Uses environment variables for secrets (via `heroku config:set`)
- HTTPS enabled by default
- Automatic security updates
- Managed PostgreSQL with backups

### Docker
- Use Docker secrets or external secret management
- Configure SSL/TLS termination (Nginx or load balancer)
- Regular base image updates required
- Database backup strategy needed

## Monitoring & Logging

### Heroku
- Built-in application metrics
- Log aggregation via `heroku logs`
- Add-ons for advanced monitoring (New Relic, DataDog)

### Docker
- Configure logging drivers
- Set up monitoring stack (Prometheus, Grafana)
- Health checks configured in docker-compose

## Migration Between Strategies

### From Heroku to Docker
1. Use existing Docker configuration in this folder
2. Export database: `heroku pg:backups:capture` and `heroku pg:backups:download`
3. Import to new environment
4. Update DNS to point to new deployment

### From Docker to Heroku
1. Create Heroku app: `heroku create`
2. Add PostgreSQL: `heroku addons:create heroku-postgresql`
3. Set environment variables: `heroku config:set`
4. Deploy: `git push heroku main`

## Support

- **Heroku Issues**: Check [deployment-guide.md](../docs/deployment-guide.md)
- **Docker Issues**: Review Docker documentation in this folder
- **General Setup**: See [development-guide.md](../docs/development-guide.md)

---

**Current Status**: ✅ **Heroku deployment active and stable**  
**Recommendation**: Continue with Heroku unless specific requirements demand Docker
