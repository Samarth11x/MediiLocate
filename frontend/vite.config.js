import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'icons/*.png', 'icons/*.svg', 'offline.html'],
      manifest: {
        id: '/',
        name: 'MediLocate',
        short_name: 'MediLocate',
        description: 'Find Your Medicine. Right Around You.',
        theme_color: '#0F766E',
        background_color: '#F8FAFC',
        display: 'standalone',
        orientation: 'portrait-primary',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: '/icons/icon-192x192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: '/icons/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: '/icons/maskable-icon-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,ico,woff2}'],
        // CRITICAL SAFETY RULE: Never cache medicine API endpoints offline.
        // /api/v1/* calls must strictly be NetworkOnly.
        runtimeCaching: [
          {
            urlPattern: ({ url }) => url.pathname.startsWith('/api/'),
            handler: 'NetworkOnly',
            options: {
              backgroundSync: {
                name: 'medilocate-api-queue',
                options: {
                  maxRetentionTime: 0
                }
              }
            }
          },
          {
            urlPattern: ({ request }) => request.mode === 'navigate',
            handler: 'NetworkFirst',
            options: {
              cacheName: 'medilocate-pages',
              networkTimeoutSeconds: 3,
            }
          }
        ],
        navigateFallback: '/offline.html',
        navigateFallbackDenylist: [/^\/api\//]
      }
    })
  ],
  server: {
    port: 5173,
    open: false,
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/tests/setup.js',
    css: true,
  },
});
