const isProd = process.env.NODE_ENV === "production";

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  images: { unoptimized: true },
  trailingSlash: true,
  basePath: isProd ? "/UofTBookingBot" : "",
  assetPrefix: isProd ? "/UofTBookingBot/" : "",
};

export default nextConfig;
