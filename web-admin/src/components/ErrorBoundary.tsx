import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // 在生产环境中，可以将错误上报到监控平台
    if (process.env.NODE_ENV === 'production') {
      // TODO: 集成错误监控服务（如 Sentry）
      // reportErrorToService(error, errorInfo);
    }
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          padding: '20px',
          textAlign: 'center',
          background: '#f9fafb',
        }}>
          <div style={{
            maxWidth: '500px',
            padding: '40px',
            background: 'white',
            borderRadius: '12px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
          }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>😵</div>
            <h2 style={{ fontSize: '24px', marginBottom: '12px', color: '#1f2937' }}>
              出错了
            </h2>
            <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '24px' }}>
              {process.env.NODE_ENV === 'development' 
                ? this.state.error?.message 
                : '应用遇到了一个错误，请刷新页面重试'}
            </p>
            <button
              onClick={() => window.location.reload()}
              style={{
                padding: '12px 24px',
                background: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                marginRight: '12px',
              }}
            >
              刷新页面
            </button>
            <button
              onClick={this.handleReset}
              style={{
                padding: '12px 24px',
                background: '#f3f4f6',
                color: '#1f2937',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
              }}
            >
              重试
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
