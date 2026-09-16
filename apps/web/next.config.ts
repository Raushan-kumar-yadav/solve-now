import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Required for the multi-stage Docker build — produces a standalone server.js
  output: "standalone",

  // Disable telemetry in CI/production
  experimental: {
    // Add any experimental flags here
  },

  // Disable X-Powered-By header
  poweredByHeader: false,

  // Compression is handled by the reverse proxy (nginx / Cloudflare)
  compress: false,

  images: {
    // Allow images from S3 bucket and the API origin
    remotePatterns: [
      {
        protocol: "https",
        hostname: "*.s3.amazonaws.com",
      },
      {
        protocol: "https",
        hostname: "*.r2.cloudflarestorage.com",
      },
    ],
  },

  // Never expose source maps in production
  productionBrowserSourceMaps: false,
};

export default nextConfig;
