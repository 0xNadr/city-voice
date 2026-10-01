/** @type {import('next').NextConfig} */
const nextConfig = {
  // The app uses no next/image, so the /_next/image optimizer stays off
  // (it was the RCE surface of GHSA-2xp9-vwfh-vxw4, fixed in 15.5.24+).
  images: { unoptimized: true },
  output: 'standalone',
}

module.exports = nextConfig
