/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
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