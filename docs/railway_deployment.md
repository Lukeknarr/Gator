# Railway Deployment Guide for Gator Backend

This guide walks you through deploying the Gator backend to Railway with automatic deployments.

## Prerequisites

1. **GitHub Repository**: Your code must be in a GitHub repository
2. **Railway Account**: Sign up at [railway.app](https://railway.app)
3. **Database Accounts**: Supabase and Neo4j AuraDB accounts

## Step 1: Prepare Your Repository

Ensure your repository has the following structure:
```
gator-project/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── railway.json
│   ├── Procfile
│   └── ...
├── frontend/
│   ├── package.json
│   ├── vercel.json
│   └── ...
└── README.md
```

## Step 2: Deploy to Railway

### Option A: Using Railway Dashboard (Recommended)

1. **Go to Railway Dashboard**
   - Visit [railway.app](https://railway.app)
   - Sign in with your GitHub account

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Project Settings**
   - **Root Directory**: Set to `backend`
   - **Build Command**: Leave empty (Railway auto-detects)
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**
   Go to the "Variables" tab and add:

   ```bash
   # Database Configuration
   POSTGRES_URL=your-supabase-postgres-url
   NEO4J_URI=your-aura-db-uri
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your-aura-password
   
   # Security
   SECRET_KEY=your-secret-key-here
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # API Configuration
   CORS_ORIGINS=https://gator.vercel.app,http://localhost:3000
   
   # Environment
   ENVIRONMENT=production
   ```

5. **Deploy**
   - Railway will automatically build and deploy your app
   - You'll get a URL like `https://gator-api.up.railway.app`

### Option B: Using Railway CLI

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Deploy**
   ```bash
   cd backend
   railway up
   ```

## Step 3: Set Up Databases

### PostgreSQL (Supabase)

1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Wait for the project to be ready

2. **Get Database URL**
   - Go to Settings → Database
   - Copy the connection string
   - Format: `postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`

3. **Initialize Database**
   ```bash
   # Connect to your Supabase database
   psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"
   
   # Run the schema
   \i database/schema.sql
   ```

### Neo4j AuraDB

1. **Create AuraDB Instance**
   - Go to [neo4j.com/aura](https://neo4j.com/aura)
   - Create a free AuraDB instance
   - Note down your connection details

2. **Get Connection Details**
   - URI: `bolt://[INSTANCE-ID].databases.neo4j.io:7687`
   - Username: `neo4j`
   - Password: Your chosen password

## Step 4: Configure Environment Variables

In your Railway project dashboard, go to the "Variables" tab and add:

### Required Variables
```bash
POSTGRES_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
NEO4J_URI=bolt://[INSTANCE-ID].databases.neo4j.io:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=[YOUR-AURA-PASSWORD]
SECRET_KEY=[GENERATE-A-SECURE-SECRET-KEY]
CORS_ORIGINS=https://gator.vercel.app,http://localhost:3000
ENVIRONMENT=production
```

### Optional Variables
```bash
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379
```

## Step 5: Test Your Deployment

1. **Check Health Endpoint**
   ```bash
   curl https://gator-api.up.railway.app/
   # Should return: {"message": "Gator API - Personalized Media Discovery Engine"}
   ```

2. **Check API Documentation**
   - Visit: `https://gator-api.up.railway.app/docs`
   - Should show FastAPI interactive docs

3. **Test Database Connection**
   - Check Railway logs for database connection errors
   - Ensure all environment variables are set correctly

## Step 6: Set Up Automatic Deployments

1. **Connect GitHub Repository**
   - Railway automatically connects to your GitHub repo
   - Any push to the main branch will trigger a deployment

2. **Configure Branch**
   - Go to Settings → General
   - Set "Deploy Branch" to `main`

3. **Set Up Preview Deployments** (Optional)
   - Enable preview deployments for pull requests
   - Go to Settings → General → Enable "Deploy on Pull Request"

## Step 7: Monitor Your Deployment

### Railway Dashboard
- **Deployments**: View deployment history and status
- **Logs**: Real-time application logs
- **Metrics**: CPU, memory, and network usage
- **Variables**: Manage environment variables

### Useful Commands
```bash
# View logs
railway logs

# Check status
railway status

# Open in browser
railway open

# View variables
railway variables
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check that `requirements.txt` exists and is valid
   - Ensure Python version is specified in `railway.json`
   - Check build logs for dependency issues

2. **Database Connection Errors**
   - Verify environment variables are set correctly
   - Check database URLs and credentials
   - Ensure databases are accessible from Railway

3. **CORS Errors**
   - Update `CORS_ORIGINS` to include your frontend domain
   - Check that the frontend URL is correct

4. **Port Issues**
   - Railway automatically sets the `$PORT` environment variable
   - Ensure your app uses `$PORT` instead of a hardcoded port

### Debug Commands
```bash
# SSH into Railway container
railway shell

# View environment variables
railway variables

# Check app logs
railway logs --tail
```

## Performance Optimization

### Railway Settings
- **Auto-scaling**: Enable in Settings → General
- **Health checks**: Configure in `railway.json`
- **Resource limits**: Monitor in the dashboard

### Application Optimization
- **Database pooling**: Configure connection pooling
- **Caching**: Implement Redis caching
- **Async operations**: Use async/await for I/O operations

## Security Considerations

1. **Environment Variables**
   - Never commit secrets to your repository
   - Use Railway's variable management
   - Rotate secrets regularly

2. **Database Security**
   - Use strong passwords for databases
   - Enable SSL connections
   - Restrict database access

3. **API Security**
   - Implement rate limiting
   - Use HTTPS (Railway provides this)
   - Validate all inputs

## Cost Management

### Railway Pricing
- **Free Tier**: $5/month credit
- **Pro Plan**: $20/month for more resources
- **Enterprise**: Custom pricing

### Optimization Tips
- Monitor resource usage in the dashboard
- Use appropriate instance sizes
- Implement caching to reduce database calls
- Optimize your application code

## Next Steps

After successful deployment:

1. **Set up your frontend** on Vercel
2. **Configure CORS** to allow frontend access
3. **Test all API endpoints**
4. **Set up monitoring and alerts**
5. **Configure custom domain** (optional)

## Support Resources

- [Railway Documentation](https://docs.railway.app/)
- [Railway Discord](https://discord.gg/railway)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [Neo4j AuraDB Documentation](https://neo4j.com/docs/aura/)

---

Your Railway deployment should now be live and automatically updating with every push to your main branch! 