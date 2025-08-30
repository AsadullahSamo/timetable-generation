import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      // Custom error UI
      return (
        <div className="flex min-h-screen bg-gray-900 text-gray-100 font-sans">
          <div className="flex-1 p-8 max-w-4xl mx-auto">
            <div className="max-w-2xl mx-auto text-center">
              <div className="bg-gray-800 rounded-lg border border-red-500/30 p-8 mb-6">
                <div className="text-6xl text-red-500 mb-4">
                  <i className="fas fa-exclamation-triangle"></i>
                </div>
                <h1 className="text-3xl font-semibold text-gray-100 mb-4">
                  Something went wrong
                </h1>
                <p className="text-gray-400 mb-6 leading-relaxed">
                  An unexpected error occurred while loading the timetable page. 
                  This might be due to a configuration issue or network problem.
                </p>
                
                <div className="bg-red-900/30 border border-red-600/50 rounded-lg p-4 mb-6 text-left">
                  <h3 className="text-lg font-medium text-red-300 mb-2">
                    <i className="fas fa-bug mr-2"></i>
                    Error Details:
                  </h3>
                  {this.state.error && (
                    <div className="text-sm text-red-200 font-mono bg-red-900/50 p-3 rounded mb-3">
                      {this.state.error.toString()}
                    </div>
                  )}
                  <ul className="text-sm text-red-200 space-y-1">
                    <li>• Try refreshing the page</li>
                    <li>• Check your internet connection</li>
                    <li>• Ensure Department Configuration is set up</li>
                    <li>• Contact support if the issue persists</li>
                  </ul>
                </div>
                
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <button
                    onClick={() => window.location.reload()}
                    className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-all duration-200"
                  >
                    <i className="fas fa-refresh mr-2"></i>
                    Refresh Page
                  </button>
                  <button
                    onClick={() => window.history.back()}
                    className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-gray-200 rounded-lg font-medium transition-all duration-200"
                  >
                    <i className="fas fa-arrow-left mr-2"></i>
                    Go Back
                  </button>
                </div>
                
                {/* Show stack trace in development */}
                {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                  <details className="mt-6 text-left">
                    <summary className="text-gray-400 cursor-pointer mb-2">
                      Show technical details (Development only)
                    </summary>
                    <div className="bg-gray-900 p-4 rounded border text-xs font-mono text-gray-300 overflow-auto max-h-48">
                      {this.state.error && this.state.error.stack}
                      <br />
                      {this.state.errorInfo.componentStack}
                    </div>
                  </details>
                )}
              </div>
            </div>
          </div>
        </div>
      );
    }

    // Normally, just render children
    return this.props.children;
  }
}

export default ErrorBoundary;
