import type { NextConfig } from "next";

const isExport = process.env.BUILD_STANDALONE !== "true";
const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

const nextConfig: NextConfig = {
  output: isExport ? "export" : undefined,
  basePath: basePath || undefined,
  images: {
    unoptimized: true,
  },
  ...(isExport
    ? {}
    : {
        allowedDevOrigins: ["169.254.83.107"],
        async rewrites() {
          const backendUrl = (
            process.env.AQUAMIND_BACKEND_URL ?? "http://127.0.0.1:8000"
          ).replace(/\/$/, "");
          return [
            {
              source: "/backend-api/:path*",
              destination: `${backendUrl}/:path*`,
            },
          ];
        },
      }),
};

export default nextConfig;
