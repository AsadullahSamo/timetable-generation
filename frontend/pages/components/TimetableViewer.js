import React from "react";
import dynamic from "next/dynamic";
import ErrorBoundary from "./ErrorBoundary";

// Dynamically import Timetable component to prevent SSR issues
const Timetable = dynamic(() => import("./Timetable"), {
  ssr: false,
  loading: () => (
    <div className="flex min-h-screen bg-background text-primary font-sans">
      <div className="flex-1 p-8 max-w-7xl">
        <div className="flex justify-center items-center h-96">
          <div className="text-center">
            <div className="h-12 w-12 border-4 border-accent-cyan/30 border-t-accent-cyan rounded-full animate-spin mx-auto mb-4"></div>
            <h2 className="text-xl text-accent-cyan mb-2">Loading Timetable</h2>
            <p className="text-secondary">Preparing application...</p>
          </div>
        </div>
      </div>
    </div>
  )
});

/**
 * TimetableViewer Component
 * 
 * A wrapper component that provides error boundaries and loading states
 * for the main Timetable component. This component handles:
 * - Error boundary protection
 * - SSR prevention with dynamic imports
 * - Loading states during component initialization
 * - Hydration mismatch prevention
 */
const TimetableViewer = () => {
  return (
    <ErrorBoundary>
      <div suppressHydrationWarning>
        <Timetable />
      </div>
    </ErrorBoundary>
  );
};

export default TimetableViewer;
