# 🔒 Security Guide for MCP Server OpenAI

## 🚨 CRITICAL SECURITY ALERT

**API keys were previously exposed in this repository and must be regenerated immediately.**

## Immediate Actions Required

### 1. Regenerate All API Keys
All the following API keys were exposed and must be regenerated:

- **OpenAI API Key**: https://platform.openai.com/api-keys
- **Anthropic API Key**: https://console.anthropic.com/
- **Google API Key**: https://console.cloud.google.com/apis/credentials
- **Unsplash API Keys**: https://unsplash.com/developers
- **Pixabay API Key**: https://pixabay.com/api/docs/

### 2. Monitor for Unauthorized Usage
Check your API provider billing dashboards immediately for any unauthorized usage.

### 3. Set Up Billing Alerts
Configure billing alerts on all API providers to detect unusual activity.

## Secure Environment Setup

### For Development

1. **Copy the template**:
   ```bash
   cp .env.template .env
   ```

2. **Fill in your new API keys** in `.env`

3. **Verify `.env` is in `.gitignore`**:
   ```bash
   grep -n "\.env" .gitignore
   ```

### For Production (GCP Cloud Run)

Use GCP Secret Manager instead of environment variables:

#### 1. Create Secrets in GCP Secret Manager

```bash
# Create secrets for each API key
echo -n "your-new-openai-key" | gcloud secrets create openai-api-key --data-file=-
echo -n "your-new-anthropic-key" | gcloud secrets create anthropic-api-key --data-file=-
echo -n "your-new-google-key" | gcloud secrets create google-api-key --data-file=-
echo -n "your-new-unsplash-key" | gcloud secrets create unsplash-access-key --data-file=-
echo -n "your-new-unsplash-secret" | gcloud secrets create unsplash-secret-key --data-file=-
echo -n "your-pixabay-key" | gcloud secrets create pixabay-api-key --data-file=-
```

#### 2. Grant Cloud Run Access to Secrets

```bash
# Get the Cloud Run service account
gcloud run services describe mcp-server-openai --region=us-central1 --format="value(spec.template.spec.serviceAccountName)"

# Grant access to secrets (replace SERVICE_ACCOUNT with actual value)
gcloud secrets add-iam-policy-binding openai-api-key \
    --member="serviceAccount:SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding anthropic-api-key \
    --member="serviceAccount:SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"

# Repeat for all other secrets...
```

#### 3. Update Cloud Run Service Configuration

Create `cloud-run-secure.yaml`:

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: mcp-server-openai
  annotations:
    run.googleapis.com/ingress: all
    run.googleapis.com/execution-environment: gen2
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/secrets/OPENAI_API_KEY: "openai-api-key:latest"
        run.googleapis.com/secrets/ANTHROPIC_API_KEY: "anthropic-api-key:latest"
        run.googleapis.com/secrets/GOOGLE_API_KEY: "google-api-key:latest"
        run.googleapis.com/secrets/UNSPLASH_ACCESS_KEY: "unsplash-access-key:latest"
        run.googleapis.com/secrets/UNSPLASH_SECRET_ACCESS_KEY: "unsplash-secret-key:latest"
        run.googleapis.com/secrets/PIXABAY_API_KEY: "pixabay-api-key:latest"
    spec:
      containers:
      - image: gcr.io/PROJECT_ID/mcp-server-openai:latest
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        # Secrets are automatically injected as environment variables
        resources:
          limits:
            cpu: "2"
            memory: "2Gi"
          requests:
            cpu: "500m"
            memory: "512Mi"
```

#### 4. Deploy Securely

```bash
gcloud run services replace cloud-run-secure.yaml --region=us-central1
```

## Code Security Improvements

### 1. Update Application Code

Create `src/mcp_server_openai/security.py`:

```python
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SecureConfig:
    """Secure configuration management for production deployment."""
    
    @staticmethod
    def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret value with proper error handling.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Secret value or None if not found and no default
        """
        value = os.getenv(key, default)
        
        if not value:
            logger.warning(f"Secret {key} not found")
            return None
            
        if value in ["COMPROMISED_KEY_REPLACED", "your_api_key_here"]:
            logger.error(f"Secret {key} contains placeholder value")
            raise ValueError(f"Invalid API key for {key}")
            
        return value
    
    @staticmethod
    def validate_required_secrets() -> bool:
        """Validate that all required secrets are properly configured."""
        required_keys = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY"
        ]
        
        missing = []
        for key in required_keys:
            if not SecureConfig.get_secret(key):
                missing.append(key)
        
        if missing:
            logger.error(f"Missing required secrets: {missing}")
            return False
            
        return True

# Usage in your application startup
def validate_configuration():
    """Validate configuration on startup."""
    if not SecureConfig.validate_required_secrets():
        raise RuntimeError("Required API keys are not properly configured")
```

### 2. Update Server Startup

In `src/mcp_server_openai/server.py`, add configuration validation:

```python
from .security import validate_configuration

def create_app():
    """Create and configure the MCP application."""
    # Validate configuration first
    validate_configuration()
    
    # Rest of your app creation code...
```

## Monitoring & Alerts

### 1. Set Up GCP Monitoring

Create monitoring alerts for:
- Unusual API usage patterns
- Failed authentication attempts
- High error rates
- Unexpected traffic spikes

### 2. Log Security Events

```python
import logging

security_logger = logging.getLogger('security')

def log_security_event(event_type: str, details: dict):
    """Log security-related events."""
    security_logger.warning(
        f"Security event: {event_type}",
        extra={
            'event_type': event_type,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
    )
```

## Additional Security Measures

### 1. Network Security

```yaml
# Add to Cloud Run service
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/vpc-access-connector: "projects/PROJECT_ID/locations/REGION/connectors/CONNECTOR_NAME"
```

### 2. Authentication & Authorization

Consider implementing:
- API key authentication for external access
- JWT tokens for user sessions
- Rate limiting per client
- IP whitelisting for admin endpoints

### 3. Security Headers

Add security headers to your HTTP responses:

```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

## Security Checklist

- [ ] All API keys regenerated
- [ ] Billing alerts configured
- [ ] `.env` file secured (not in git)
- [ ] GCP Secret Manager configured
- [ ] Cloud Run service updated with secrets
- [ ] Security monitoring enabled
- [ ] Code updated with security validation
- [ ] Network security configured
- [ ] Security headers implemented
- [ ] Regular security audits scheduled

## Emergency Contact

If you suspect unauthorized access or security breach:

1. **Immediately revoke all API keys**
2. **Check billing dashboards**
3. **Review access logs**
4. **Contact API providers' security teams**
5. **Document the incident**

## Regular Security Maintenance

- **Monthly**: Review API usage and billing
- **Quarterly**: Rotate API keys
- **Annually**: Security audit and penetration testing