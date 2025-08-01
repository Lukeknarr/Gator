# 🚀 Gator Quick Deploy Guide

This guide provides the fastest deployment path for the Gator personalized media discovery engine.

## 📋 Prerequisites

- GitHub repository with your Gator code
- Railway account ([railway.app](https://railway.app))
- Vercel account ([vercel.com](https://vercel.com))
- Supabase account ([supabase.com](https://supabase.com))
- Neo4j AuraDB account ([neo4j.com/aura](https://neo4j.com/aura))

## 🎯 Quick Deploy Steps

### 1️⃣ Deploy Backend to Railway

1. **Go to Railway Dashboard**
   - Visit [railway.app](https://railway.app)
   - Sign in with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Settings**
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**
   ```bash
   POSTGRES_URL=your-supabase-url
   NEO4J_URI=your-aura-uri
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your-password
   SECRET_KEY=your-secret-key
   CORS_ORIGINS=https://gator.vercel.app,http://localhost:3000
   ENVIRONMENT=production
   ```

5. **Deploy**
   - Railway will automatically build and deploy
   - Get your API URL: `https://gator-api.up.railway.app`

### 2️⃣ Deploy Frontend to Vercel

1. **Go to Vercel Dashboard**
   - Visit [vercel.com](https://vercel.com)
   - Sign in with GitHub

2. **Import Project**
   - Click "New Project"
   - Select "Import Git Repository"
   - Choose your repository

3. **Configure Settings**
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)

4. **Add Environment Variables**
   ```bash
   NEXT_PUBLIC_API_URL=https://gator-api.up.railway.app
   NODE_ENV=production
   ```

5. **Deploy**
   - Vercel will build and deploy
   - Get your frontend URL: `https://gator.vercel.app`

### 3️⃣ Set Up Databases

#### PostgreSQL (Supabase)
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Get database URL from Settings → Database
4. Add to Railway environment variables

#### Neo4j AuraDB
1. Go to [neo4j.com/aura](https://neo4j.com/aura)
2. Create free AuraDB instance
3. Get connection details
4. Add to Railway environment variables

### 4️⃣ Test Deployment

1. **Test Backend**
   ```bash
   curl https://gator-api.up.railway.app/
   # Should return: {"message": "Gator API - Personalized Media Discovery Engine"}
   ```

2. **Test Frontend**
   - Visit `https://gator.vercel.app`
   - Should load the Gator dashboard

3. **Test API Documentation**
   - Visit `https://gator-api.up.railway.app/docs`
   - Should show FastAPI interactive docs

## 🔧 Configuration Files

### Backend (Railway)
- `backend/railway.json` - Railway configuration
- `backend/Procfile` - Start command
- `backend/requirements.txt` - Python dependencies

### Frontend (Vercel)
- `frontend/vercel.json` - Vercel configuration
- `frontend/next.config.js` - Next.js configuration
- `frontend/package.json` - Node.js dependencies

## 🌐 URLs

After deployment, you'll have:

- **Frontend**: `https://gator.vercel.app`
- **Backend**: `https://gator-api.up.railway.app`
- **API Docs**: `https://gator-api.up.railway.app/docs`

## 🔄 Automatic Deployments

Both Railway and Vercel will automatically:
- Deploy on every push to `main` branch
- Provide preview deployments for pull requests
- Handle HTTPS certificates automatically
- Scale based on traffic

## 🚨 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check that all dependencies are in requirements.txt/package.json
   - Verify Python/Node.js versions
   - Check build logs for specific errors

2. **Database Connection Errors**
   - Verify environment variables are set correctly
   - Check database URLs and credentials
   - Ensure databases are accessible from Railway

3. **CORS Errors**
   - Update CORS_ORIGINS to include your Vercel domain
   - Check that frontend URL is correct

4. **API Connection Errors**
   - Verify NEXT_PUBLIC_API_URL is set correctly
   - Check that Railway backend is running
   - Test API endpoints directly

### Debug Commands

```bash
# Railway
railway logs
railway status
railway variables

# Vercel
vercel logs
vercel ls
vercel env ls
```

## 📊 Monitoring

### Railway Dashboard
- View deployment history
- Monitor resource usage
- Check application logs
- Manage environment variables

### Vercel Dashboard
- View deployment status
- Monitor performance metrics
- Check build logs
- Manage domains

## 💰 Cost Estimation

### Free Tier Limits
- **Railway**: $5/month credit (usually sufficient for MVP)
- **Vercel**: 100GB bandwidth, 100 serverless function executions
- **Supabase**: 500MB database, 50MB file storage
- **Neo4j AuraDB**: 50,000 nodes, 175,000 relationships

### Scaling Considerations
- Monitor usage and upgrade plans as needed
- Consider paid tiers for production traffic
- Implement caching to reduce costs

## 🔐 Security Checklist

- [ ] Use strong, unique passwords for all services
- [ ] Enable 2FA on all accounts
- [ ] Use environment variables for sensitive data
- [ ] Regularly rotate API keys and tokens
- [ ] Monitor for suspicious activity
- [ ] Keep dependencies updated
- [ ] Use HTTPS for all communications

## 🎉 Success!

After completing these steps, you'll have:

✅ **Live Frontend**: `https://gator.vercel.app`
✅ **Live Backend**: `https://gator-api.up.railway.app`
✅ **Automatic Deployments**: On every git push
✅ **HTTPS Certificates**: Automatically managed
✅ **Global CDN**: Fast loading worldwide
✅ **Scalable Infrastructure**: Ready for growth

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Vercel Documentation](https://vercel.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Neo4j AuraDB Documentation](https://neo4j.com/docs/aura/)

---

**Deployment Time**: ~15-30 minutes
**Difficulty**: Beginner-friendly
**Cost**: Free tier available
**Auto-scaling**: Yes 