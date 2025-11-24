# Azure Production Deployment Plan

This guide outlines the recommended Azure components and deployment steps for RBTL GraphRAG production deployment.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Azure Cloud                              │
│                                                                   │
│  ┌──────────────────┐         ┌──────────────────┐            │
│  │  Frontend        │         │  Backend API      │            │
│  │  (Next.js)       │◄───────►│  (FastAPI)       │            │
│  │                  │  HTTPS  │                   │            │
│  │  Azure Static    │  REST   │  Azure Container │            │
│  │  Web Apps        │  +      │  Apps             │            │
│  │  (CDN)           │  WS/SSE │  (Auto-scaling)   │            │
│  └──────────────────┘         └─────────┬─────────┘            │
│                                          │                       │
│                                          ▼                       │
│  ┌──────────────────────────────────────────────────┐           │
│  │         Azure Services                           │           │
│  │  • Azure OpenAI (or OpenAI API)                │           │
│  │  • Neo4j Aura (managed)                         │           │
│  │  • Azure Cosmos DB (MongoDB API)                │           │
│  │  • Azure Key Vault (secrets)                    │           │
│  │  • Azure Application Insights (monitoring)       │           │
│  │  • Azure Container Registry (ACR)               │           │
│  └──────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

## Recommended Azure Components

| Component | Service | Purpose |
|-----------|---------|---------|
| **Frontend Hosting** | Azure Static Web Apps | Host Next.js frontend with CDN and auto-scaling |
| **Backend Hosting** | Azure Container Apps | Run FastAPI backend with auto-scaling |
| **Container Registry** | Azure Container Registry (ACR) | Store Docker images |
| **Secrets Management** | Azure Key Vault | Secure storage for API keys and credentials |
| **Database** | Azure Cosmos DB (MongoDB API) | Knowledge base storage |
| **Monitoring** | Azure Application Insights | Application performance and error tracking |
| **CI/CD** | GitHub Actions | Automated deployment pipeline |

### External Services

- **Neo4j Aura** (managed Neo4j)
- **OpenAI API** (or Azure OpenAI)
- **Langfuse** (cloud or self-hosted)

## Prerequisites

- Azure Subscription
- Azure CLI installed (`az login`)
- Docker installed locally
- GitHub repository access

## Deployment Phases

### Phase 1: Infrastructure Setup

#### 1.1 Create Resource Group

```bash
az group create \
  --name rg-rbtl-graphrag-prod \
  --location westeurope
```

#### 1.2 Create Azure Container Registry (ACR)

```bash
az acr create \
  --resource-group rg-rbtl-graphrag-prod \
  --name acrrbtlgraphrag \
  --sku Basic \
  --admin-enabled true
```

#### 1.3 Create Azure Key Vault

```bash
az keyvault create \
  --name kv-rbtl-graphrag-prod \
  --resource-group rg-rbtl-graphrag-prod \
  --location westeurope \
  --sku standard
```

#### 1.4 Create Azure Container Apps Environment

```bash
az containerapp env create \
  --name env-rbtl-graphrag-prod \
  --resource-group rg-rbtl-graphrag-prod \
  --location westeurope
```

#### 1.5 Create Azure Static Web App (Frontend)

```bash
az staticwebapp create \
  --name swa-rbtl-graphrag-prod \
  --resource-group rg-rbtl-graphrag-prod \
  --location westeurope \
  --sku Standard
```

#### 1.6 Create Azure Cosmos DB (MongoDB API)

```bash
az cosmosdb create \
  --name cosmos-rbtl-graphrag-prod \
  --resource-group rg-rbtl-graphrag-prod \
  --kind MongoDB \
  --locations regionName=westeurope failoverPriority=0
```

### Phase 2: Secrets Configuration

#### 2.1 Store Secrets in Key Vault

```bash
# Neo4j credentials
az keyvault secret set \
  --vault-name kv-rbtl-graphrag-prod \
  --name "NEO4J-URI" \
  --value "neo4j+s://your-db-id.databases.neo4j.io"

az keyvault secret set \
  --vault-name kv-rbtl-graphrag-prod \
  --name "NEO4J-USER" \
  --value "neo4j"

az keyvault secret set \
  --vault-name kv-rbtl-graphrag-prod \
  --name "NEO4J-PASSWORD" \
  --value "your-secure-password"

# OpenAI
az keyvault secret set \
  --vault-name kv-rbtl-graphrag-prod \
  --name "OPENAI-API-KEY" \
  --value "sk-proj-..."

# Langfuse
az keyvault secret set \
  --vault-name kv-rbtl-graphrag-prod \
  --name "LANGFUSE-HOST" \
  --value "https://cloud.langfuse.com"

az keyvault secret set \
  --vault-name kv-rbtl-graphrag-prod \
  --name "LANGFUSE-PUBLIC-KEY" \
  --value "pk-lf-..."

az keyvault secret set \
  --vault-name kv-rbtl-graphrag-prod \
  --name "LANGFUSE-SECRET-KEY" \
  --value "sk-lf-..."

# MongoDB (Cosmos DB)
az keyvault secret set \
  --vault-name kv-rbtl-graphrag-prod \
  --name "MONGODB-URI" \
  --value "$(az cosmosdb keys list \
    --name cosmos-rbtl-graphrag-prod \
    --resource-group rg-rbtl-graphrag-prod \
    --type connection-strings \
    --query 'connectionStrings[0].connectionString' -o tsv)"
```

#### 2.2 Grant Container Apps Access to Key Vault

```bash
# Get managed identity (will be created with container app)
# Then grant access:
az keyvault set-policy \
  --name kv-rbtl-graphrag-prod \
  --object-id <container-app-identity-id> \
  --secret-permissions get list
```

### Phase 3: Backend Deployment

#### 3.1 Build and Push Docker Image

```bash
# Login to ACR
az acr login --name acrrbtlgraphrag

# Build image
docker build -t acrrbtlgraphrag.azurecr.io/rbtl-graphrag-backend:latest .

# Push to ACR
docker push acrrbtlgraphrag.azurecr.io/rbtl-graphrag-backend:latest
```

#### 3.2 Create Container App for Backend

```bash
az containerapp create \
  --name ca-rbtl-graphrag-backend \
  --resource-group rg-rbtl-graphrag-prod \
  --environment env-rbtl-graphrag-prod \
  --image acrrbtlgraphrag.azurecr.io/rbtl-graphrag-backend:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server acrrbtlgraphrag.azurecr.io \
  --registry-username $(az acr credential show --name acrrbtlgraphrag --query username -o tsv) \
  --registry-password $(az acr credential show --name acrrbtlgraphrag --query passwords[0].value -o tsv) \
  --min-replicas 1 \
  --max-replicas 5 \
  --cpu 1.0 \
  --memory 2.0Gi \
  --env-vars \
    NEO4J_URI="@Microsoft.KeyVault(SecretUri=https://kv-rbtl-graphrag-prod.vault.azure.net/secrets/NEO4J-URI/)" \
    NEO4J_USER="@Microsoft.KeyVault(SecretUri=https://kv-rbtl-graphrag-prod.vault.azure.net/secrets/NEO4J-USER/)" \
    NEO4J_PASSWORD="@Microsoft.KeyVault(SecretUri=https://kv-rbtl-graphrag-prod.vault.azure.net/secrets/NEO4J-PASSWORD/)" \
    OPENAI_API_KEY="@Microsoft.KeyVault(SecretUri=https://kv-rbtl-graphrag-prod.vault.azure.net/secrets/OPENAI-API-KEY/)" \
    LANGFUSE_HOST="@Microsoft.KeyVault(SecretUri=https://kv-rbtl-graphrag-prod.vault.azure.net/secrets/LANGFUSE-HOST/)" \
    LANGFUSE_PUBLIC_KEY="@Microsoft.KeyVault(SecretUri=https://kv-rbtl-graphrag-prod.vault.azure.net/secrets/LANGFUSE-PUBLIC-KEY/)" \
    LANGFUSE_SECRET_KEY="@Microsoft.KeyVault(SecretUri=https://kv-rbtl-graphrag-prod.vault.azure.net/secrets/LANGFUSE-SECRET-KEY/)" \
    MONGODB_URI="@Microsoft.KeyVault(SecretUri=https://kv-rbtl-graphrag-prod.vault.azure.net/secrets/MONGODB-URI/)" \
    MONGODB_DATABASE=graphrag \
    OPENAI_MODEL=gpt-4o \
    PROMPT_LABEL=production \
    ENABLE_ANALYTICS_AGENT=false
```

#### 3.3 Get Backend URL

```bash
BACKEND_URL=$(az containerapp show \
  --name ca-rbtl-graphrag-backend \
  --resource-group rg-rbtl-graphrag-prod \
  --query properties.configuration.ingress.fqdn -o tsv)

echo "Backend URL: https://$BACKEND_URL"
```

### Phase 4: Frontend Deployment

#### 4.1 Configure Frontend Environment

Create `frontend/.env.production`:

```bash
NEXT_PUBLIC_API_URL=https://<your-backend-url>
```

#### 4.2 Build Frontend

```bash
cd frontend
npm ci
npm run build
```

#### 4.3 Deploy to Azure Static Web Apps

**Option A: Using Azure CLI**

```bash
az staticwebapp deploy \
  --name swa-rbtl-graphrag-prod \
  --resource-group rg-rbtl-graphrag-prod \
  --source-location frontend \
  --app-location frontend \
  --output-location .next
```

**Option B: Using GitHub Actions (Recommended)**

1. Connect GitHub repo to Static Web App:
   ```bash
   az staticwebapp create \
     --name swa-rbtl-graphrag-prod \
     --resource-group rg-rbtl-graphrag-prod \
     --source https://github.com/bojan2110/rbtl_graphrag \
     --location westeurope \
     --branch main \
     --app-location frontend \
     --output-location .next \
     --login-with-github
   ```

2. Configure build settings in Azure Portal:
   - App location: `frontend`
   - Output location: `.next`
   - Build command: `npm run build`

3. Add environment variables in Azure Portal:
   - `NEXT_PUBLIC_API_URL`: `https://<your-backend-url>`

### Phase 5: CI/CD Pipeline Setup

The GitHub Actions workflow (`.github/workflows/azure-deploy.yml`) automates deployment:

- **Backend**: Builds Docker image, pushes to ACR, updates Container App
- **Frontend**: Builds Next.js app, deploys to Static Web Apps

#### 5.1 Configure GitHub Secrets

Add these secrets in GitHub repository settings:

- `AZURE_CREDENTIALS`: Service principal credentials (create with `az ad sp create-for-rbac`)
- `AZURE_STATIC_WEB_APPS_API_TOKEN`: From Azure Portal → Static Web App → Manage deployment token
- `NEXT_PUBLIC_API_URL`: Your backend Container App URL

### Phase 6: Monitoring & Observability

#### 6.1 Enable Application Insights

```bash
az monitor app-insights component create \
  --app ai-rbtl-graphrag-prod \
  --location westeurope \
  --resource-group rg-rbtl-graphrag-prod \
  --application-type web
```

#### 6.2 Configure Logging

Add to Container App environment variables:

```bash
APPLICATIONINSIGHTS_CONNECTION_STRING="<from-app-insights>"
```

#### 6.3 Set Up Alerts

```bash
az monitor metrics alert create \
  --name alert-backend-errors \
  --resource-group rg-rbtl-graphrag-prod \
  --scopes /subscriptions/<sub-id>/resourceGroups/rg-rbtl-graphrag-prod/providers/Microsoft.App/containerApps/ca-rbtl-graphrag-backend \
  --condition "count ExceptionRate > 5" \
  --window-size 5m \
  --evaluation-frequency 1m
```

### Phase 7: Post-Deployment Verification

#### 7.1 Health Check

```bash
BACKEND_URL=$(az containerapp show \
  --name ca-rbtl-graphrag-backend \
  --resource-group rg-rbtl-graphrag-prod \
  --query properties.configuration.ingress.fqdn -o tsv)

curl https://$BACKEND_URL/api/health
```

#### 7.2 Test Endpoints

```bash
# Test chat endpoint
curl -X POST https://$BACKEND_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Return 5 Person nodes"}'

# Test graph info
curl https://$BACKEND_URL/api/graph-info
```

#### 7.3 Verify Frontend

1. Visit Static Web App URL (from Azure Portal)
2. Test chat interface
3. Verify API connectivity
4. Check browser console for errors

## Rollback Procedures

### Backend Rollback

```bash
# List revisions
az containerapp revision list \
  --name ca-rbtl-graphrag-backend \
  --resource-group rg-rbtl-graphrag-prod

# Activate previous revision
az containerapp revision activate \
  --name ca-rbtl-graphrag-backend \
  --resource-group rg-rbtl-graphrag-prod \
  --revision <previous-revision-name>
```

### Frontend Rollback

Revert the last commit in GitHub and push, or manually deploy a previous build from Azure Portal.

## Security Checklist

- [ ] All secrets stored in Azure Key Vault
- [ ] HTTPS enforced on all endpoints
- [ ] CORS configured correctly
- [ ] Container images scanned for vulnerabilities
- [ ] Managed identity used for Key Vault access
- [ ] Network security groups configured (if using VNet)
- [ ] Application Insights logging enabled
- [ ] Regular security updates scheduled

## Maintenance

### Regular Tasks

1. **Weekly**: Review Application Insights for errors and performance
2. **Monthly**: Update dependencies and container images
3. **As needed**: Rotate API keys and secrets

### Updates

```bash
# Update backend
az containerapp update \
  --name ca-rbtl-graphrag-backend \
  --resource-group rg-rbtl-graphrag-prod \
  --image acrrbtlgraphrag.azurecr.io/rbtl-graphrag-backend:latest

# Frontend updates automatically via GitHub Actions
```

## Troubleshooting

### Backend Not Starting

1. Check Container App logs: Azure Portal → Container App → Log stream
2. Verify Key Vault secrets are accessible
3. Check environment variables are correctly set
4. Review Application Insights for errors

### Frontend Can't Connect to Backend

1. Verify `NEXT_PUBLIC_API_URL` is set correctly
2. Check CORS settings in backend
3. Verify backend Container App is running
4. Check network connectivity

## Next Steps

After successful deployment:

1. Set up **staging environment** for testing before production
2. Configure **backup strategies** for Cosmos DB
3. Implement **disaster recovery** plan
4. Set up **performance testing** in CI/CD
5. Document **runbooks** for common issues

