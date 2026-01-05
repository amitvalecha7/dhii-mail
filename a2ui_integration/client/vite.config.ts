import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, '.', '');
    const kernelUrl = env.KERNEL_URL || 'http://127.0.0.1:8005';

    return {
      server: {
        port: 3001,
        host: '0.0.0.0',
        proxy: {
          '/api': {
            target: kernelUrl,
            changeOrigin: true,
            secure: false,
          },
          '/ws': {
            target: kernelUrl.replace('http', 'ws'),
            ws: true,
          }
        }
      },
      plugins: [react()],
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      }
    };
});
