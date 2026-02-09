import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

const isDevelopment = import.meta.env.DEV;

// Global error handler - 仅在开发环境显示详细错误
if (isDevelopment) {
window.addEventListener('error', (e) => {
  const errorDiv = document.createElement('div');
    errorDiv.style.cssText = 'color:red; padding:20px; border:1px solid red; margin:20px; background:white; position:fixed; top:0; left:0; z-index:9999; max-width:90vw; overflow:auto;';
  errorDiv.innerHTML = `<h3>Global Error:</h3><pre>${e.message}</pre><pre>${e.filename}:${e.lineno}:${e.colno}</pre>`;
  document.body.appendChild(errorDiv);
});

window.addEventListener('unhandledrejection', (e) => {
  const errorDiv = document.createElement('div');
    errorDiv.style.cssText = 'color:red; padding:20px; border:1px solid red; margin:20px; background:white; position:fixed; top:100px; left:0; z-index:9999; max-width:90vw; overflow:auto;';
  errorDiv.innerHTML = `<h3>Unhandled Promise Rejection:</h3><pre>${e.reason}</pre>`;
  document.body.appendChild(errorDiv);
});
} else {
  // 生产环境：静默处理错误，可以上报到监控平台
  window.addEventListener('error', (e) => {
    console.error('Global error:', e.message);
    // TODO: 上报到错误监控平台（如 Sentry）
    // reportErrorToMonitoring(e);
  });

  window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
    // TODO: 上报到错误监控平台
    // reportErrorToMonitoring(e);
  });
}

try {
  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <App />
    </StrictMode>,
  )
} catch (e) {
  console.error('Render error:', e);
  if (isDevelopment) {
  const errorDiv = document.createElement('div');
    errorDiv.style.cssText = 'color:red; padding:20px; border:1px solid red; margin:20px; background:white; position:fixed; top:200px; left:0; z-index:9999; max-width:90vw; overflow:auto;';
  errorDiv.innerHTML = `<h3>Render Error:</h3><pre>${e}</pre>`;
  document.body.appendChild(errorDiv);
  }
}
