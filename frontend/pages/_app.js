import "@/styles/globals.css";
import { useEffect } from "react";

export default function App({ Component, pageProps }) {
  useEffect(() => {
    // Global error handling for unhandled promise rejections
    const handleUnhandledRejection = (event) => {
      console.error('Unhandled promise rejection:', event.reason);
      
      // Check if it's an Axios error
      if (event.reason?.isAxiosError) {
        console.error('Axios error caught globally:', {
          status: event.reason.response?.status,
          data: event.reason.response?.data,
          message: event.reason.message
        });
        
        // Prevent the default behavior (which would crash the app)
        event.preventDefault();
      }
    };

    // Global error handling for uncaught exceptions
    const handleError = (event) => {
      console.error('Uncaught error:', event.error);
      
      // If it's an Axios error, prevent crash
      if (event.error?.isAxiosError) {
        console.error('Axios error caught globally:', event.error);
        event.preventDefault();
      }
    };

    // Add event listeners
    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    window.addEventListener('error', handleError);

    // Cleanup event listeners on unmount
    return () => {
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
      window.removeEventListener('error', handleError);
    };
  }, []);

  return <Component {...pageProps} />;
}
