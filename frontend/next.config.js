/** @type {import('next').NextConfig} */
const nextConfig = {
  // Turns off the /_next/image optimizer: unused here, and Next 14 has an
  // unauthenticated RCE in it (GHSA-2xp9-vwfh-vxw4) that is only fixed in 15.5.24+.
  images: { unoptimized: true },
  output: 'standalone',
}

module.exports = nextConfig
