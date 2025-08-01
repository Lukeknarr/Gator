/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://gator.up.railway.app/:path*',
      },
    ];
  },
};

module.exports = nextConfig; 