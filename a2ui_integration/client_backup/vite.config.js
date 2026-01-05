import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: process.env.API_TARGET || 'http://localhost:8005',
        changeOrigin: true,
      },
      '/ws': {
        target: process.env.API_TARGET ? process.env.API_TARGET.replace('http', 'ws') : 'ws://localhost:8005',
        ws: true,
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    minify: 'terser',
    sourcemap: false, // Disable source maps for production to reduce bundle size
    target: 'es2018', // Modern browsers
    cssTarget: 'chrome61', // Optimize for modern browsers
    lib: {
      entry: resolve(__dirname, 'main.js'),
      formats: ['es']
    },
    rollupOptions: {
      input: {
        main: 'index.html'
      },
      output: {
        manualChunks: (id) => {
          // Create smarter chunks based on module paths
          if (id.includes('node_modules')) {
            if (id.includes('@a2ui')) {
              return 'vendor-a2ui'
            }
            if (id.includes('@a2a-js')) {
              return 'vendor-a2a'
            }
            if (id.includes('lit')) {
              return 'vendor-lit'
            }
            if (id.includes('markdown-it')) {
              return 'vendor-markdown'
            }
            return 'vendor'
          }
        },
        // Optimize chunk naming
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    },
    // Enable tree shaking and code splitting
    modulePreload: {
      polyfill: true
    },
    // Optimize chunk size
    chunkSizeWarningLimit: 500, // Warn if chunk is larger than 500KB
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log statements
        drop_debugger: true, // Remove debugger statements
        pure_funcs: ['console.log', 'console.info', 'console.debug', 'console.warn'], // Remove specific console functions
        passes: 3, // Run compression multiple times for better optimization
        hoist_funs: true, // Hoist function declarations
        hoist_vars: true, // Hoist var declarations
        if_return: true, // Optimize if/return and if/continue
        join_vars: true, // Join var declarations
        sequences: true, // Use comma operator instead of semicolon
        side_effects: true, // Drop side-effect-free statements
        unused: true, // Drop unused variables/functions
      },
      mangle: {
        toplevel: true, // Mangle top-level variables
        properties: {
          regex: /^_/ // Mangle private properties starting with _
        }
      },
      format: {
        comments: false, // Remove all comments
        safari10: false // Don't cater to Safari 10 bugs
      }
    }
  },
  // Optimize dependencies
  optimizeDeps: {
    include: [
      'lit',
      '@lit/reactive-element',
      '@lit/context',
      '@a2ui/lit',
      '@a2a-js/sdk',
      'markdown-it',
      'signal-utils'
    ],
    exclude: [
      // Exclude any large dependencies that aren't needed immediately
    ],
    // Force pre-bundling of these dependencies
    force: true
  },
  // Enable production optimizations
  esbuild: {
    drop: ['console', 'debugger'], // Drop console and debugger in production
    pure: ['console.log', 'console.info', 'console.debug'], // Mark console functions as pure for better tree shaking
    legalComments: 'none' // Remove legal comments
  },
  // Performance optimizations
  resolve: {
    alias: {
      // Create aliases for faster resolution
      '@': resolve(__dirname, './src'),
      '@components': resolve(__dirname, './src/components'),
      '@utils': resolve(__dirname, './src/utils')
    }
  }
})