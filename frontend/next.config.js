/** @type {import('next').NextConfig} */
const nextConfig = {
  serverExternalPackages: ["duckdb", "@mapbox/node-pre-gyp"],
};

module.exports = nextConfig;