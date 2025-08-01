# Vercel Deployment Guide for Gator Frontend

This guide walks you through deploying the Gator frontend to Vercel with automatic deployments.

## Prerequisites

1. **GitHub Repository**: Your code must be in a GitHub repository
2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
3. **Backend API**: Your Railway backend should be deployed and accessible

## Step 1: Prepare Your Repository

Ensure your repository has the following structure:
```
gator-project/
├── frontend/
│   ├── package.json
│   ├── vercel.json
│   ├── next.config.js
│   ├── app/
│   └── ...
├── backend/
│   └── ...
└── README.md
```

## Step 2: Deploy to Vercel

### Option A: Using Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**
   - Visit [vercel.com](https://vercel.com)
   - Sign in with your GitHub account

2. **Import Project**
   - Click "New Project"
   - Select "Import Git Repository"
   - Choose your repository

3. **Configure Project Settings**
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

4. **Add Environment Variables**
   Go to the "Environment Variables" section and add:

   ```bash
   NEXT_PUBLIC_API_URL=https://gator-api.up.railway.app
   NODE_ENV=production
   ```

5. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy your app
   - You'll get a URL like `https://gator.vercel.app`

### Option B: Using Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   cd frontend
   vercel --prod
   ```

## Step 3: Configure Environment Variables

In your Vercel project dashboard, go to Settings → Environment Variables and add:

### Required Variables
```bash
NEXT_PUBLIC_API_URL=https://gator-api.up.railway.app
NODE_ENV=production
```

### Optional Variables
```bash
NEXT_PUBLIC_APP_NAME=Gator
NEXT_PUBLIC_APP_VERSION=1.0.0
```

## Step 4: Configure Build Settings

### Vercel Configuration
Your `vercel.json` should look like this:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://gator-api.up.railway.app/$1"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://gator-api.up.railway.app"
  },
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://gator-api.up.railway.app/$1"
    }
  ]
}
```

### Next.js Configuration
Your `next.config.js` should include:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['your-image-domain.com'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://gator-api.up.railway.app/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
```

## Step 5: Test Your Deployment

1. **Check Homepage**
   - Visit your Vercel URL (e.g., `https://gator.vercel.app`)
   - Should load the Gator dashboard

2. **Test API Integration**
   - Check browser console for API errors
   - Verify that API calls are going to your Railway backend
   - Test user registration and login

3. **Check Build Logs**
   - Go to Vercel dashboard → Deployments
   - Check for any build errors or warnings

## Step 6: Set Up Automatic Deployments

1. **Connect GitHub Repository**
   - Vercel automatically connects to your GitHub repo
   - Any push to the main branch will trigger a deployment

2. **Configure Branch**
   - Go to Settings → Git
   - Set "Production Branch" to `main`

3. **Set Up Preview Deployments** (Optional)
   - Enable preview deployments for pull requests
   - Go to Settings → Git → Enable "Preview Deployment"

## Step 7: Configure Custom Domain (Optional)

1. **Add Custom Domain**
   - Go to Settings → Domains
   - Add your custom domain (e.g., `gator-app.com`)

2. **Configure DNS**
   - Add the provided DNS records to your domain provider
   - Wait for DNS propagation (can take up to 48 hours)

3. **Update Environment Variables**
   - Update `CORS_ORIGINS` in your Railway backend to include your custom domain

## Step 8: Monitor Your Deployment

### Vercel Dashboard
- **Deployments**: View deployment history and status
- **Analytics**: Page views, performance metrics
- **Functions**: Serverless function logs
- **Settings**: Environment variables, domains, etc.

### Useful Commands
```bash
# View deployment status
vercel ls

# View logs
vercel logs

# Open in browser
vercel open

# View environment variables
vercel env ls
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check that all dependencies are in `package.json`
   - Ensure Node.js version is compatible
   - Check build logs for specific errors

2. **API Connection Errors**
   - Verify `NEXT_PUBLIC_API_URL` is set correctly
   - Check that your Railway backend is running
   - Ensure CORS is configured properly

3. **Environment Variables**
   - Make sure all required variables are set
   - Check that variable names are correct
   - Redeploy after adding new variables

4. **Image Loading Issues**
   - Configure image domains in `next.config.js`
   - Use Next.js Image component properly
   - Check image URLs and formats

### Debug Commands
```bash
# View deployment logs
vercel logs

# Check environment variables
vercel env ls

# Redeploy
vercel --prod
```

## Performance Optimization

### Vercel Optimizations
- **Edge Functions**: Use for global performance
- **Image Optimization**: Next.js automatic image optimization
- **CDN**: Vercel's global CDN for static assets
- **Caching**: Configure caching headers

### Application Optimization
- **Code Splitting**: Next.js automatic code splitting
- **Lazy Loading**: Implement lazy loading for components
- **Bundle Analysis**: Use `@next/bundle-analyzer`
- **Image Optimization**: Use Next.js Image component

## Security Considerations

1. **Environment Variables**
   - Never expose secrets in client-side code
   - Use `NEXT_PUBLIC_` prefix only for public variables
   - Keep sensitive data server-side

2. **API Security**
   - Use HTTPS for all API calls
   - Implement proper authentication
   - Validate all user inputs

3. **Content Security Policy**
   - Configure CSP headers
   - Sanitize user-generated content
   - Use HTTPS for all resources

## Cost Management

### Vercel Pricing
- **Hobby Plan**: Free tier with limitations
- **Pro Plan**: $20/month for more features
- **Enterprise**: Custom pricing

### Optimization Tips
- Monitor bandwidth usage
- Optimize images and assets
- Use appropriate caching strategies
- Minimize bundle size

## Advanced Configuration

### Edge Functions
Create `frontend/app/api/edge/route.js`:
```javascript
export const runtime = 'edge';

export async function GET() {
  return new Response('Hello from Edge!');
}
```

### Middleware
Create `frontend/middleware.js`:
```javascript
import { NextResponse } from 'next/server';

export function middleware(request) {
  // Add custom middleware logic
  return NextResponse.next();
}
```

### Custom Headers
Add to `next.config.js`:
```javascript
async headers() {
  return [
    {
      source: '/(.*)',
      headers: [
        {
          key: 'X-Frame-Options',
          value: 'DENY',
        },
      ],
    },
  ];
},
```

## Monitoring and Analytics

### Vercel Analytics
- **Web Analytics**: Built-in analytics dashboard
- **Core Web Vitals**: Performance metrics
- **Real User Monitoring**: User experience data

### Custom Monitoring
- **Error Tracking**: Integrate with Sentry or similar
- **Performance Monitoring**: Use tools like New Relic
- **User Analytics**: Google Analytics or similar

## Next Steps

After successful deployment:

1. **Test all features** thoroughly
2. **Set up monitoring** and error tracking
3. **Configure analytics** to track user behavior
4. **Set up CI/CD** for automated testing
5. **Plan for scaling** as your user base grows

## Support Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [Vercel Discord](https://discord.gg/vercel)
- [Vercel Community](https://github.com/vercel/vercel/discussions)

---

Your Vercel deployment should now be live and automatically updating with every push to your main branch! 