/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    unoptimized: true,
  },
  redirects: async () => [
    {
      source: '/api/:path*',
      destination: 'http://localhost:3001/api/:path*',
      permanent: false,
    },
  ],
}

module.exports = nextConfig
