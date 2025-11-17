# Deployment Guide

Complete guide for deploying the Freelance MCP Server in various environments.

## Table of Contents

1. [Local Development](#local-development)
2. [Claude Desktop Integration](#claude-desktop-integration)
3. [Cloud Deployment](#cloud-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Production Considerations](#production-considerations)

## Local Development

### Quick Setup

```bash
# Clone repository
git clone https://github.com/N1KH1LT0X1N/Freelance-MCP-Server.git
cd Freelance-MCP-Server

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run server
python freelance_server.py stdio
```

### Testing Locally

```bash
# Run tests
pytest tests/ -v

# Check environment
python freelance_client.py --check-env

# Run demo
python main.py
```

## Claude Desktop Integration

### Windows

1. **Locate config file:**
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **Add server configuration:**
   ```json
   {
     "mcpServers": {
       "freelance": {
         "command": "C:\\Users\\YourName\\.local\\bin\\uv.EXE",
         "args": [
           "run",
           "--with", "mcp",
           "--with", "python-dotenv",
           "--with", "langchain-groq",
           "--with", "pydantic",
           "C:\\path\\to\\freelance_server.py",
           "stdio"
         ],
         "env": {
           "GROQ_API_KEY": "your_groq_api_key",
           "OWNER_COUNTRY_CODE": "1",
           "OWNER_PHONE_NUMBER": "5551234567"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

### macOS / Linux

1. **Locate config file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Add server configuration:**
   ```json
   {
     "mcpServers": {
       "freelance": {
         "command": "uv",
         "args": [
           "run",
           "--with", "mcp",
           "--with", "python-dotenv",
           "--with", "langchain-groq",
           "--with", "pydantic",
           "/absolute/path/to/freelance_server.py",
           "stdio"
         ],
         "env": {
           "GROQ_API_KEY": "your_groq_api_key",
           "OWNER_COUNTRY_CODE": "1",
           "OWNER_PHONE_NUMBER": "5551234567"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

### Troubleshooting Claude Desktop

**Issue: Server shows as "failed"**
- Check logs in Claude Desktop error message
- Verify all dependencies are installed
- Ensure absolute path to freelance_server.py
- Check that `stdio` is the last argument

**Issue: Environment variables not loading**
- Verify .env file exists
- Check env values in claude_desktop_config.json
- No extra quotes or spaces in values

## Cloud Deployment

### AWS Lambda

**Note:** Lambda has limitations with stdio transport. Consider using SSE or HTTP mode.

```python
# lambda_handler.py
import json
from freelance_server import mcp

def lambda_handler(event, context):
    # Adapt server for Lambda environment
    # This is a starting point - needs full implementation
    return {
        'statusCode': 200,
        'body': json.dumps('MCP Server running')
    }
```

### Heroku

1. **Create Procfile:**
   ```
   web: python freelance_server.py streamable-http --port $PORT
   ```

2. **Create runtime.txt:**
   ```
   python-3.11.0
   ```

3. **Deploy:**
   ```bash
   heroku create your-app-name
   heroku config:set GROQ_API_KEY=your_key
   heroku config:set OWNER_COUNTRY_CODE=1
   heroku config:set OWNER_PHONE_NUMBER=5551234567
   git push heroku main
   ```

### Railway

1. **Create railway.toml:**
   ```toml
   [build]
   builder = "NIXPACKS"

   [deploy]
   startCommand = "python freelance_server.py streamable-http --port $PORT"
   ```

2. **Set environment variables:**
   ```bash
   railway variables set GROQ_API_KEY=your_key
   railway variables set OWNER_COUNTRY_CODE=1
   railway variables set OWNER_PHONE_NUMBER=5551234567
   ```

3. **Deploy:**
   ```bash
   railway up
   ```

### Google Cloud Run

1. **Create Dockerfile** (see Docker section below)

2. **Deploy:**
   ```bash
   gcloud run deploy freelance-mcp \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GROQ_API_KEY=your_key,OWNER_COUNTRY_CODE=1,OWNER_PHONE_NUMBER=5551234567
   ```

## Docker Deployment

### Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run server
CMD ["python", "freelance_server.py", "streamable-http", "--port", "8080"]
```

### Create docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  freelance-mcp:
    build: .
    ports:
      - "8080:8080"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - OWNER_COUNTRY_CODE=${OWNER_COUNTRY_CODE}
      - OWNER_PHONE_NUMBER=${OWNER_PHONE_NUMBER}
    env_file:
      - .env
    restart: unless-stopped
```

### Build and Run

```bash
# Build image
docker build -t freelance-mcp:latest .

# Run container
docker run -p 8080:8080 \
  -e GROQ_API_KEY=your_key \
  -e OWNER_COUNTRY_CODE=1 \
  -e OWNER_PHONE_NUMBER=5551234567 \
  freelance-mcp:latest

# Or use docker-compose
docker-compose up -d
```

### Docker Hub

```bash
# Tag image
docker tag freelance-mcp:latest yourusername/freelance-mcp:latest

# Push to Docker Hub
docker push yourusername/freelance-mcp:latest

# Pull and run on any machine
docker pull yourusername/freelance-mcp:latest
docker run -p 8080:8080 --env-file .env yourusername/freelance-mcp:latest
```

## Production Considerations

### Security

1. **Environment Variables**
   - Never commit .env to git
   - Use secrets management (AWS Secrets Manager, HashiCorp Vault)
   - Rotate API keys regularly

2. **Authentication**
   - Enable MCP_AUTH_TOKEN in production
   - Use HTTPS/TLS for all connections
   - Implement rate limiting

3. **Input Validation**
   - Server includes basic validation
   - Add custom validation for your use case
   - Sanitize all user inputs

### Performance

1. **Caching**
   - Cache gig searches
   - Store frequently accessed resources
   - Use Redis for distributed caching

2. **Rate Limiting**
   - Implement per-client rate limits
   - Monitor GROQ API usage
   - Add backoff strategies

3. **Monitoring**
   - Log all requests and errors
   - Track tool usage metrics
   - Monitor server health

### Scaling

1. **Horizontal Scaling**
   - Deploy multiple instances
   - Use load balancer
   - Share state via database/cache

2. **Database**
   - Replace in-memory storage with PostgreSQL/MongoDB
   - Implement proper migrations
   - Add connection pooling

3. **Load Balancing**
   ```nginx
   # nginx.conf
   upstream mcp_servers {
       server mcp1.example.com:8080;
       server mcp2.example.com:8080;
       server mcp3.example.com:8080;
   }

   server {
       listen 80;
       location / {
           proxy_pass http://mcp_servers;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Monitoring & Logging

1. **Structured Logging**
   ```python
   import logging
   import json

   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )

   logger = logging.getLogger(__name__)
   ```

2. **Health Checks**
   ```python
   @app.route('/health')
   def health_check():
       return {'status': 'healthy', 'version': '1.0.0'}
   ```

3. **Metrics**
   - Request count
   - Response times
   - Error rates
   - Tool usage statistics

### Backup & Recovery

1. **Data Backup**
   - Regular database backups
   - Store in multiple locations
   - Test restore procedures

2. **Configuration Backup**
   - Version control all configs
   - Document environment setup
   - Keep deployment runbooks

### Cost Optimization

1. **GROQ API Usage**
   - Cache AI responses
   - Implement response pooling
   - Monitor token usage

2. **Infrastructure**
   - Use spot instances for non-critical
   - Auto-scale based on load
   - Optimize resource allocation

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] API keys valid and not expired
- [ ] Dependencies up to date
- [ ] Security scan completed
- [ ] Documentation updated

### Deployment

- [ ] Deploy to staging first
- [ ] Run smoke tests
- [ ] Check logs for errors
- [ ] Verify all tools working
- [ ] Test Claude Desktop integration
- [ ] Monitor for 24 hours

### Post-Deployment

- [ ] Update DNS records
- [ ] Configure monitoring alerts
- [ ] Document deployment process
- [ ] Train team on new features
- [ ] Create rollback plan
- [ ] Schedule regular reviews

## Environment-Specific Configurations

### Development

```bash
# .env.development
GROQ_API_KEY=dev_key
DEBUG=true
LOG_LEVEL=DEBUG
```

### Staging

```bash
# .env.staging
GROQ_API_KEY=staging_key
DEBUG=false
LOG_LEVEL=INFO
```

### Production

```bash
# .env.production
GROQ_API_KEY=prod_key
DEBUG=false
LOG_LEVEL=WARNING
MCP_AUTH_TOKEN=secure_token_here
```

## Support & Maintenance

### Regular Maintenance

1. **Weekly**
   - Check error logs
   - Review API usage
   - Update dependencies (if needed)

2. **Monthly**
   - Security audit
   - Performance review
   - Cost analysis

3. **Quarterly**
   - Major dependency updates
   - Architecture review
   - Disaster recovery test

### Getting Help

- **Issues**: GitHub Issues
- **Documentation**: See docs/ directory
- **Community**: GitHub Discussions

## Additional Resources

- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [USAGE.md](USAGE.md) - Detailed usage instructions
- [README.md](README.md) - Project overview
- [CHANGELOG.md](CHANGELOG.md) - Version history

---

**Need help with deployment?** Open an issue on GitHub with the `deployment` label.
