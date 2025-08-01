# Gator MVP Deployment Guide

This guide walks you through deploying the Gator system using the recommended MVP hosting stack.

## Hosting Stack Overview

- **Frontend**: Vercel (Next.js)
- **Backend**: Railway (FastAPI)
- **PostgreSQL**: Supabase
- **Neo4j**: AuraDB Free
- **Domain**: Namecheap
- **CI/CD**: GitHub Actions

## Prerequisites

1. GitHub repository with the Gator codebase
2. Vercel account
3. Railway account
4. Supabase account
5. Neo4j AuraDB account
6. Namecheap domain (optional)

## Step 1: Set Up Databases

### Supabase (PostgreSQL)

1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Note down your database URL and API keys

2. **Initialize Database**
   ```bash
   # Connect to your Supabase database
   psql "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"
   
   # Run the schema
   \i database/schema.sql
   ```

3. **Get Connection Details**
   - Database URL: `postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`
   - API Key: Available in your Supabase dashboard

### Neo4j AuraDB

1. **Create AuraDB Instance**
   - Go to [neo4j.com/aura](https://neo4j.com/aura)
   - Create a free AuraDB instance
   - Note down your connection details

2. **Connection Details**
   - URI: `bolt://[INSTANCE-ID].databases.neo4j.io:7687`
   - Username: `neo4j`
   - Password: Your chosen password

## Step 2: Deploy Backend to Railway

1. **Connect Railway to GitHub**
   - Go to [railway.app](https://railway.app)
   - Connect your GitHub account
   - Select the Gator repository

2. **Create New Service**
   - Click "New Service" → "GitHub Repo"
   - Select your repository
   - Set the root directory to `backend`

3. **Configure Environment Variables**
   ```bash
   POSTGRES_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   NEO4J_URI=bolt://[INSTANCE-ID].databases.neo4j.io:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=[YOUR-NEO4J-PASSWORD]
   SECRET_KEY=[GENERATE-A-SECURE-SECRET-KEY]
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   CORS_ORIGINS=https://your-domain.vercel.app,http://localhost:3000
   ENVIRONMENT=production
   ```

4. **Deploy**
   - Railway will automatically detect the Python app
   - It will install dependencies from `requirements.txt`
   - The app will start using the `Procfile`

5. **Get Railway URL**
   - Note down your Railway app URL (e.g., `https://gator-backend.railway.app`)

## Step 3: Deploy Frontend to Vercel

1. **Connect Vercel to GitHub**
   - Go to [vercel.com](https://vercel.com)
   - Connect your GitHub account
   - Import your repository

2. **Configure Project**
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

3. **Set Environment Variables**
   ```bash
   NEXT_PUBLIC_API_URL=https://gator-backend.railway.app
   ```

4. **Deploy**
   - Vercel will automatically build and deploy your app
   - You'll get a URL like `https://gator-frontend.vercel.app`

## Step 4: Set Up Domain (Optional)

1. **Purchase Domain on Namecheap**
   - Go to [namecheap.com](https://namecheap.com)
   - Purchase your domain (e.g., `gator-app.com`)

2. **Configure DNS**
   - Add CNAME record for frontend:
     - Name: `@` or `www`
     - Value: `cname.vercel-dns.com`
   - Add CNAME record for backend:
     - Name: `api`
     - Value: `[YOUR-RAILWAY-APP].railway.app`

3. **Update Vercel Domain**
   - In Vercel dashboard, add your custom domain
   - Vercel will provide DNS records to configure

4. **Update Railway Domain**
   - In Railway dashboard, add custom domain
   - Configure SSL certificate

## Step 5: Configure CI/CD

1. **Set Up GitHub Secrets**
   Go to your GitHub repository → Settings → Secrets and variables → Actions

   Add these secrets:
   ```bash
   RAILWAY_TOKEN=[YOUR-RAILWAY-TOKEN]
   VERCEL_TOKEN=[YOUR-VERCEL-TOKEN]
   VERCEL_ORG_ID=[YOUR-VERCEL-ORG-ID]
   VERCEL_PROJECT_ID=[YOUR-VERCEL-PROJECT-ID]
   ```

2. **Get Railway Token**
   - Go to Railway dashboard → Account → Tokens
   - Create a new token

3. **Get Vercel Token**
   - Go to Vercel dashboard → Settings → Tokens
   - Create a new token

4. **Get Vercel Project ID**
   - In Vercel dashboard, go to your project
   - The project ID is in the URL or settings

## Step 6: Initialize Production Database

1. **Run Database Initialization**
   ```bash
   # Set environment variables
   export POSTGRES_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"
   export NEO4J_URI="bolt://[INSTANCE-ID].databases.neo4j.io:7687"
   export NEO4J_USER="neo4j"
   export NEO4J_PASSWORD="[YOUR-PASSWORD]"
   
   # Run initialization script
   cd backend
   python migrations/init_db.py
   ```

2. **Run Data Ingestion**
   ```bash
   cd data_ingestion
   python ingestion_pipeline.py
   ```

## Step 7: Test Deployment

1. **Test Backend API**
   ```bash
   curl https://gator-backend.railway.app/
   # Should return: {"message": "Gator API - Personalized Media Discovery Engine"}
   ```

2. **Test Frontend**
   - Visit your Vercel URL
   - Should load the Gator dashboard

3. **Test API Documentation**
   - Visit `https://gator-backend.railway.app/docs`
   - Should show FastAPI interactive docs

## Environment Variables Reference

### Backend (Railway)
```bash
POSTGRES_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
NEO4J_URI=bolt://[INSTANCE-ID].databases.neo4j.io:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=[YOUR-NEO4J-PASSWORD]
SECRET_KEY=[GENERATE-A-SECURE-SECRET-KEY]
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://your-domain.vercel.app,http://localhost:3000
ENVIRONMENT=production
```

### Frontend (Vercel)
```bash
NEXT_PUBLIC_API_URL=https://gator-backend.railway.app
```

## Monitoring and Maintenance

### Railway Monitoring
- Check Railway dashboard for app logs
- Monitor resource usage
- Set up alerts for downtime

### Vercel Monitoring
- Check Vercel dashboard for build status
- Monitor performance metrics
- Set up error tracking

### Database Monitoring
- Supabase dashboard for PostgreSQL metrics
- Neo4j AuraDB dashboard for graph database metrics

## Troubleshooting

### Common Issues

1. **Backend Deployment Fails**
   - Check Railway logs for Python errors
   - Verify environment variables are set correctly
   - Ensure all dependencies are in `requirements.txt`

2. **Frontend Build Fails**
   - Check Vercel build logs
   - Verify TypeScript compilation
   - Ensure all dependencies are in `package.json`

3. **Database Connection Issues**
   - Verify database URLs are correct
   - Check firewall settings
   - Ensure database is accessible from Railway

4. **CORS Errors**
   - Update `CORS_ORIGINS` in Railway environment variables
   - Include your Vercel domain in the list

### Support Resources
- [Railway Documentation](https://docs.railway.app/)
- [Vercel Documentation](https://vercel.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Neo4j AuraDB Documentation](https://neo4j.com/docs/aura/)

## Cost Estimation

### Free Tier Limits
- **Vercel**: 100GB bandwidth, 100 serverless function executions
- **Railway**: $5/month credit (usually sufficient for MVP)
- **Supabase**: 500MB database, 50MB file storage
- **Neo4j AuraDB**: 50,000 nodes, 175,000 relationships

### Scaling Considerations
- Monitor usage and upgrade plans as needed
- Consider paid tiers for production traffic
- Implement caching to reduce database calls

## Security Checklist

- [ ] Use strong, unique passwords for all services
- [ ] Enable 2FA on all accounts
- [ ] Use environment variables for sensitive data
- [ ] Regularly rotate API keys and tokens
- [ ] Monitor for suspicious activity
- [ ] Keep dependencies updated
- [ ] Use HTTPS for all communications
- [ ] Implement rate limiting (Railway Pro)
- [ ] Set up error monitoring and alerting 