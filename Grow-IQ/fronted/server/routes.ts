import type { Express, Request, Response } from "express";
import { createServer, type Server } from "http";
// @ts-ignore - types may not be present in dev
import { createProxyMiddleware } from "http-proxy-middleware";
import path from "path";

export async function registerRoutes(app: Express): Promise<Server> {
  // Backend target (FastAPI). Configure via env BACKEND_URL or auto-detect
  // In production (Render), use RENDER_EXTERNAL_URL or current origin
  const getBackendUrl = (): string => {
    if (process.env.BACKEND_URL) {
      return process.env.BACKEND_URL;
    }
    // Render automatically sets RENDER_EXTERNAL_URL
    if (process.env.RENDER_EXTERNAL_URL) {
      return process.env.RENDER_EXTERNAL_URL;
    }
    // Auto-detect from request in production, fallback to localhost for dev
    if (process.env.NODE_ENV === 'production') {
      // In production, backend should be on same origin or use BASE_URL
      return process.env.BASE_URL || '';
    }
    return "http://localhost:8000";
  };
  
  const backendUrl = getBackendUrl();

  // Reverse proxy API and auth to backend
  // Ensure these are registered BEFORE the Vite middleware catch-all
  app.use(
    "/api",
    createProxyMiddleware({
      target: backendUrl,
      changeOrigin: true,
      xfwd: true,
      ws: true,
      cookieDomainRewrite: "localhost",
      onProxyReq(proxyReq: any, req: Request) {
        // forward cookies for auth sessions
        const cookie = (req as Request).headers["cookie"];
        if (cookie) proxyReq.setHeader("cookie", cookie);
      },
    }),
  );

  app.use(
    "/auth",
    createProxyMiddleware({
      target: backendUrl,
      changeOrigin: true,
      xfwd: true,
      ws: true,
      cookieDomainRewrite: "localhost",
      onProxyReq(proxyReq: any, req: Request) {
        const cookie = req.headers["cookie"];
        if (cookie) proxyReq.setHeader("cookie", cookie);
      },
    }),
  );

  // Proxy social features (posts, comments, likes)
  app.use(
    "/social",
    createProxyMiddleware({
      target: backendUrl,
      changeOrigin: true,
      xfwd: true,
      ws: true,
      cookieDomainRewrite: "localhost",
      onProxyReq(proxyReq: any, req: Request) {
        const cookie = req.headers["cookie"];
        if (cookie) proxyReq.setHeader("cookie", cookie);
      },
    }),
  );

  // Optional: proxy message websocket paths if needed
  app.use(
    ["/messages", "/messages/ws"],
    createProxyMiddleware({ target: backendUrl, changeOrigin: true, ws: true }),
  );

  // Proxy resume-tester routes
  app.use(
    "/resume-tester",
    createProxyMiddleware({
      target: backendUrl,
      changeOrigin: true,
      xfwd: true,
      ws: true,
      cookieDomainRewrite: "localhost",
      onProxyReq(proxyReq: any, req: Request) {
        const cookie = req.headers["cookie"];
        if (cookie) proxyReq.setHeader("cookie", cookie);
      },
    }),
  );

  // Login route: serve SPA entry. In dev, vite catch-all handles this.
  // In prod, serveStatic() will fall through to index.html already.
  app.get("/login", (_req: Request, res: Response) => {
    res.sendFile(
      path.resolve(import.meta.dirname, "..", "client", "index.html"),
    );
  });

  // Ensure SPA home routes are served directly
  app.get(["/", "/home"], (_req: Request, res: Response) => {
    res.sendFile(
      path.resolve(import.meta.dirname, "..", "client", "index.html"),
    );
  });

  const httpServer = createServer(app);

  return httpServer;
}
