import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiProxyTarget = process.env.VITE_API_PROXY_TARGET || env.VITE_API_PROXY_TARGET || 'http://localhost:8080'
  console.log('API Proxy Target:', apiProxyTarget)
  return {
    plugins: [react()],
    build: {
      rollupOptions: {
        output: {
          manualChunks(id: string) {
            if (!id.includes('node_modules')) {
              return undefined;
            }
            if (id.includes('framer-motion')) {
              return 'framer-motion';
            }
            if (id.includes('react-router')) {
              return 'router';
            }
            if (id.includes('axios')) {
              return 'axios';
            }
            if (id.includes('i18next') || id.includes('react-i18next')) {
              return 'i18n';
            }
            if (
              id.includes('node_modules/react-dom') ||
              id.includes('node_modules/react/') ||
              id.includes('node_modules\\react\\') ||
              id.includes('node_modules\\react-dom') ||
              id.includes('node_modules/scheduler/')
            ) {
              return 'react-core';
            }
            return 'vendor';
          },
        },
      },
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@components': path.resolve(__dirname, './src/components'),
        '@pages': path.resolve(__dirname, './src/pages'),
        '@lib': path.resolve(__dirname, './src/lib'),
        '@api': path.resolve(__dirname, './src/api'),
        '@hooks': path.resolve(__dirname, './src/hooks'),
        '@store': path.resolve(__dirname, './src/store'),
        '@types': path.resolve(__dirname, './src/types'),
      },
    },
    server: {
      host: '0.0.0.0',
      port: 5173,
      allowedHosts: ['web', 'localhost', '8.148.26.166', '.8.148.26.166', 'dd.twjob.cn', '.twjob.cn'],
      proxy: {
        '/api': {
          target: apiProxyTarget,
          changeOrigin: true,
        }
      },
      watch: {
        usePolling: true,
      }
    }
  }
})
