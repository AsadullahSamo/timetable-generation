import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import dynamic from 'next/dynamic';
import Navbar from './Navbar';
import BackButton from './BackButton';
import api from "../utils/api";
import { generateTimetablePDF } from "../utils/pdfGenerator";
import { 
  Calendar, 
  Clock, 
  AlertTriangle, 
  RefreshCw, 
  Download, 
  Settings, 
  CheckCircle2,
  AlertCircle,
  Loader2,
  Building2,
  BookOpen,
  Users,
  Trash2,
  Shield
} from 'lucide-react';

const Timetable = () => {
  console.log("Timetable component rendering"); // Debug log
  
  // SSR state to prevent hydration mismatch
  const [mounted, setMounted] = useState(false);
  
  // Initialize state with safe defaults
  const router = useRouter();
  const [timetableData, setTimetableData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedClassGroup, setSelectedClassGroup] = useState("");
  const [regenerating, setRegenerating] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [draggingEntry, setDraggingEntry] = useState(null);
  const [message, setMessage] = useState(null);
  const [moveUIForEntry, setMoveUIForEntry] = useState(null);
  const [moveDay, setMoveDay] = useState('');
  const [movePeriod, setMovePeriod] = useState('');
  const [safeSlotsByEntry, setSafeSlotsByEntry] = useState({});
  const [safeSlotsLoadingFor, setSafeSlotsLoadingFor] = useState(null);
  const [safeSlotsErrorFor, setSafeSlotsErrorFor] = useState(null);
  const [downloadingPDF, setDownloadingPDF] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const [showDeleteTimetableConfirm, setShowDeleteTimetableConfirm] = useState(false);
  const [deleteTimetableLoading, setDeleteTimetableLoading] = useState(false);

  // Handle client-side mounting
  useEffect(() => {
    setMounted(true);
  }, []);

  // Retry function for failed requests
  const retryFetch = () => {
    setRetryCount(prev => prev + 1);
    setError("");
    setLoading(true);
  };

  // Fetch timetable data effect
  useEffect(() => {
    // Don't fetch on server side or before component is mounted
    if (!mounted) return;

    const fetchTimetable = async () => {
      try {
        setLoading(true);
        setError(""); // Clear any previous errors
        
        const params = new URLSearchParams();
        if (selectedClassGroup) {
          params.append('class_group', selectedClassGroup);
        }

        const response = await api.get(`/api/timetable/latest/?${params}`);
        const data = response.data;
        
        console.log("Raw API response:", data); // Debug log
        
        if (!data || !data.entries || !Array.isArray(data.entries)) {
          throw new Error("Invalid timetable data received");
        }
        
        // Validate required fields
        if (!data.days || !data.timeSlots) {
          throw new Error("Missing required timetable structure (days or timeSlots)");
        }
        
        console.log("Received timetable data:", data); // Debug log
        console.log("Days:", data.days); // Debug log
        console.log("Time slots:", data.timeSlots); // Debug log
        console.log("Entries count:", data.entries.length); // Debug log
        
        setTimetableData(data);
        setError("");
      } catch (err) {
        console.error("Timetable fetch error:", err);
        console.error("Error details:", {
          isAxiosError: err?.isAxiosError,
          status: err?.response?.status,
          data: err?.response?.data,
          message: err?.message,
          stack: err?.stack
        });
        
        // Handle Axios errors more robustly
        let errorMessage = "Failed to load timetable. Please try again.";
        
        if (err.response) {
          // The request was made and the server responded with a status code
          const status = err.response.status;
          const responseData = err.response.data;
          const backendError = responseData?.error || responseData?.detail || responseData?.message || "";
          
          switch (status) {
            case 400:
              if (backendError.includes("No valid schedule configuration") || 
                  backendError.includes("No schedule configuration") ||
                  backendError.includes("schedule configuration")) {
                errorMessage = "No schedule configuration found. Please set up Department Configuration first.";
              } else {
                errorMessage = "Configuration error. Please check your Department Configuration settings.";
              }
              break;
            case 404:
              errorMessage = "No schedule configuration found. Please set up Department Configuration first.";
              break;
            case 500:
              errorMessage = "Server error occurred while loading timetable. Please try again later.";
              break;
            default:
              errorMessage = `Server returned error ${status}. Please try again.`;
          }
        } else if (err.request) {
          // The request was made but no response was received
          errorMessage = "Network error. Please check your connection and try again.";
        } else if (err.message) {
          // Something happened in setting up the request or processing response
          if (err.message.includes("Invalid timetable data") || err.message.includes("Missing required")) {
            errorMessage = err.message;
          } else {
            errorMessage = "An unexpected error occurred. Please try again.";
          }
        }
        
        setError(errorMessage);
        setTimetableData(null); // Clear any existing data
      } finally {
        setLoading(false);
      }
    };

    // Call the async function and handle any uncaught errors
    fetchTimetable().catch((err) => {
      console.error("Uncaught error in fetchTimetable:", err);
      setError("An unexpected error occurred while loading the timetable.");
      setLoading(false);
    });
  }, [selectedClassGroup, retryCount, mounted]);

  // Early error boundary check - AFTER all hooks are defined
  if (!mounted) {
    // SSR or initial client render - show loading
    return (
      <div className="flex min-h-screen bg-background text-primary font-sans" suppressHydrationWarning>
        <Navbar number={8} />
        <div className="flex-1 p-8 max-w-7xl">
          <div className="flex justify-center items-center h-96">
            <div className="text-center">
              <Loader2 className="h-12 w-12 animate-spin text-accent-cyan mx-auto mb-4" />
              <h2 className="text-xl text-accent-cyan mb-2">Loading Timetable</h2>
              <p className="text-secondary">Initializing application...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const handleRegenerateTimetable = async () => {
    setRegenerating(true);
    setError(""); // Clear any previous errors
    
    try {
      await api.post('/api/timetable/regenerate/');
      setTimetableData(null); // Clear existing data
      setLoading(true); // Set loading state
      
      // Manually fetch new timetable data
      const params = new URLSearchParams();
      if (selectedClassGroup) {
        params.append('class_group', selectedClassGroup);
      }
      
      const response = await api.get(`/api/timetable/latest/?${params}`);
      const data = response.data;
      
      if (!data || !data.entries || !Array.isArray(data.entries)) {
        throw new Error("Invalid timetable data received after regeneration");
      }
      
      console.log("Received new timetable data after regeneration:", data);
      setTimetableData(data);
      setLoading(false); // Clear loading state
    } catch (err) {
      console.error("Regenerate timetable error:", err);
      
      // Handle Axios errors more robustly for regeneration
      let errorMessage = "Failed to regenerate timetable. Please try again.";
      
      if (err.response) {
        const status = err.response.status;
        const responseData = err.response.data;
        const backendError = responseData?.error || responseData?.detail || responseData?.message || "";
        
        switch (status) {
          case 400:
            if (backendError.includes("No valid schedule configuration") || 
                backendError.includes("No schedule configuration") ||
                backendError.includes("schedule configuration")) {
              errorMessage = "Cannot regenerate: No schedule configuration found. Please set up Department Configuration first.";
            } else {
              errorMessage = "Cannot regenerate: Configuration error. Please check your Department Configuration settings.";
            }
            break;
          case 404:
            errorMessage = "Cannot regenerate: No schedule configuration found. Please set up Department Configuration first.";
            break;
          case 500:
            errorMessage = "Server error occurred during timetable generation. Please try again later.";
            break;
          default:
            errorMessage = `Regeneration failed with error ${status}. Please try again.`;
        }
      } else if (err.request) {
        errorMessage = "Network error during regeneration. Please check your connection and try again.";
      } else if (err.message) {
        if (err.message.includes("Invalid timetable data")) {
          errorMessage = err.message;
        } else {
          errorMessage = "An unexpected error occurred during regeneration. Please try again.";
        }
      }
      
      setError(errorMessage);
      setLoading(false); // Clear loading state on error
    } finally {
      setRegenerating(false);
    }
  };

  const handleDeleteTimetable = async () => {
    try {
      setDeleteTimetableLoading(true);
      const response = await api.delete('/api/timetable/data-management/timetable/');
      
      if (response.data.success) {
        setTimetableData({ entries: [], days: timetableData?.days || [], timeSlots: timetableData?.timeSlots || [], pagination: timetableData?.pagination });
        setError("");
        setShowDeleteTimetableConfirm(false);
        setMessage({ type: 'success', text: `Successfully deleted ${response.data.deleted_count} timetable entries.` });
        setTimeout(() => setMessage(null), 5000);
        // Refetch latest to sync empty state cleanly
        try {
          const params = new URLSearchParams();
          if (selectedClassGroup) params.append('class_group', selectedClassGroup);
          const latest = await api.get(`/api/timetable/latest/?${params}`);
          // If backend returns empty after delete, ensure UI shows empty template not blank screen
          const data = latest.data;
          if (!data || !Array.isArray(data.entries)) {
            setTimetableData({ entries: [], days: timetableData?.days || [], timeSlots: timetableData?.timeSlots || [], pagination: timetableData?.pagination });
          } else {
            setTimetableData(data);
          }
        } catch (_) {
          // Ignore refetch errors; UI already shows cleared timetable
        }
      } else {
        setError("Failed to delete timetable");
      }
    } catch (err) {
      setError("Failed to delete timetable");
      console.error("Delete timetable error:", err);
    } finally {
      setDeleteTimetableLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-background text-primary font-sans" suppressHydrationWarning>
        <Navbar number={8} />
        <div className="flex-1 p-8 max-w-7xl">
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-8">Generated Timetable</h1>
          <div className="flex justify-center items-center h-96">
            <div className="text-center">
              <Loader2 className="h-12 w-12 animate-spin text-accent-cyan mx-auto mb-4" />
              <h2 className="text-xl text-accent-cyan mb-2">Loading Timetable</h2>
              <p className="text-secondary">
                {selectedClassGroup 
                  ? `Fetching timetable for ${selectedClassGroup}...` 
                  : "Fetching your generated timetable..."}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    const isNoConfig = error.includes("No schedule configuration found") || error.includes("Department Configuration");
    
    return (
      <div className="flex min-h-screen bg-background text-primary font-sans" suppressHydrationWarning>
        <Navbar number={8} />
        <div className="flex-1 p-8 max-w-7xl">
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-8">Generated Timetable</h1>
          
          {isNoConfig ? (
            <div className="max-w-2xl mx-auto text-center">
              {/* No Configuration State */}
              <div className="bg-surface/95 backdrop-blur-sm rounded-2xl border border-border p-8 mb-6">
                <Calendar className="h-16 w-16 text-secondary/50 mx-auto mb-4" />
                <h2 className="text-2xl font-semibold text-primary mb-4">
                  No Timetable Configuration Found
                </h2>
                <p className="text-secondary mb-6 leading-relaxed">
                  To generate a timetable, you need to set up your department configuration first. 
                  This includes defining your schedule settings, subjects, teachers, and classroom assignments.
                </p>
                
                <div className="bg-accent-cyan/10 border border-accent-cyan/20 rounded-xl p-4 mb-6">
                  <h3 className="text-lg font-medium text-accent-cyan mb-2 flex items-center justify-center gap-2">
                    <Settings className="h-5 w-5" />
                    What you need to set up:
                  </h3>
                  <ul className="text-sm text-primary text-left space-y-1">
                    <li>• Schedule Configuration (days, time slots, periods)</li>
                    <li>• Subjects and their details</li>
                    <li>• Teachers and their subject assignments</li>
                    <li>• Classrooms and their capacities</li>
                    <li>• Class groups and batch information</li>
                  </ul>
                </div>
                
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <BackButton 
                    href="/components/DepartmentConfig" 
                    label="Setup Department Config"
                    className="px-6 py-3 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white rounded-xl font-medium transition-all duration-300 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30"
                  />
                  <button
                    onClick={() => window.location.reload()}
                    className="px-6 py-3 bg-surface border border-border text-secondary rounded-xl font-medium transition-all duration-200 hover:border-accent-cyan/30 hover:text-primary flex items-center gap-2"
                  >
                    <RefreshCw className="h-4 w-4" />
                    Refresh Page
                  </button>
                </div>
              </div>
            </div>
          ) : (
            /* General Error State */
            <div className="max-w-2xl mx-auto">
              <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6 mb-6">
                <div className="flex items-center mb-3">
                  <AlertTriangle className="h-5 w-5 text-red-500 mr-3" />
                  <h3 className="text-lg font-semibold text-red-500">Error Loading Timetable</h3>
                </div>
                <p className="text-red-400 mb-4">{error}</p>
                <div className="flex gap-3">
                  <button
                    onClick={retryFetch}
                    className="px-4 py-2 bg-red-500/20 border border-red-500/30 hover:bg-red-500/30 text-red-400 rounded-xl font-medium transition-all duration-200 flex items-center gap-2"
                    disabled={loading}
                  >
                    {loading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <RefreshCw className="h-4 w-4" />
                    )}
                    {loading ? 'Retrying...' : 'Try Again'}
                  </button>
                  <button
                    onClick={() => window.location.reload()}
                    className="px-4 py-2 bg-surface border border-border text-secondary rounded-xl font-medium transition-all duration-200 hover:border-accent-cyan/30 hover:text-primary flex items-center gap-2"
                  >
                    <RefreshCw className="h-4 w-4" />
                    Full Refresh
                  </button>
                  <BackButton 
                    href="/components/DepartmentConfig" 
                    label="Department Config"
                    className="px-4 py-2 bg-accent-cyan/20 border border-accent-cyan/30 text-accent-cyan rounded-xl font-medium transition-all duration-200 hover:bg-accent-cyan/30"
                  />
                </div>
              </div>
            </div>
          )}
          
          {/* Download Button (disabled when no data) */}
          <div className="mt-8 flex justify-end">
            <button
              disabled={true}
              className="px-6 py-3 bg-surface/50 text-secondary/50 rounded-xl cursor-not-allowed flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Download PDF (No Data)
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!timetableData) return null;

  // Safety check for required properties
  if (!timetableData.days || !timetableData.timeSlots || !timetableData.entries) {
    console.error("Missing required timetable data:", timetableData);
    return (
      <div className="flex min-h-screen bg-background text-primary font-sans" suppressHydrationWarning>
        <Navbar number={8} />
        <div className="flex-1 p-8 max-w-7xl">
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-8">Generated Timetable</h1>
          
          <div className="max-w-2xl mx-auto text-center">
            <div className="bg-surface/95 backdrop-blur-sm rounded-2xl border border-border p-8 mb-6">
              <AlertTriangle className="h-16 w-16 text-accent-pink mx-auto mb-4" />
              <h2 className="text-2xl font-semibold text-primary mb-4">
                Incomplete Timetable Data
              </h2>
              <p className="text-secondary mb-6 leading-relaxed">
                The timetable data received is incomplete or corrupted. This might happen if the 
                department configuration is partially set up or if there was an issue during timetable generation.
              </p>
              
              <div className="bg-accent-pink/10 border border-accent-pink/20 rounded-xl p-4 mb-6">
                <h3 className="text-lg font-medium text-accent-pink mb-2 flex items-center justify-center gap-2">
                  <Settings className="h-5 w-5" />
                  Possible Solutions:
                </h3>
                <ul className="text-sm text-primary text-left space-y-1">
                  <li>• Check your Department Configuration is complete</li>
                  <li>• Try regenerating the timetable</li>
                  <li>• Refresh the page to reload data</li>
                  <li>• Contact support if the issue persists</li>
                </ul>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => window.location.reload()}
                  className="px-6 py-3 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white rounded-xl font-medium transition-all duration-300 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 flex items-center gap-2"
                >
                  <RefreshCw className="h-4 w-4" />
                  Refresh Page
                </button>
                <BackButton 
                  href="/components/DepartmentConfig" 
                  label="Check Configuration"
                  className="px-6 py-3 bg-surface border border-border text-secondary rounded-xl font-medium transition-all duration-200 hover:border-accent-cyan/30 hover:text-primary"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Check for empty timetable (no entries)
  if (timetableData.entries && Array.isArray(timetableData.entries) && timetableData.entries.length === 0) {
    return (
      <div className="flex min-h-screen bg-background text-primary font-sans" suppressHydrationWarning>
        <Navbar number={8} />
        <div className="flex-1 p-8 max-w-7xl">
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-8">Generated Timetable</h1>
          
          <div className="max-w-2xl mx-auto text-center">
            <div className="bg-surface/95 backdrop-blur-sm rounded-2xl border border-border p-8 mb-6">
              <BookOpen className="h-16 w-16 text-secondary/50 mx-auto mb-4" />
              <h2 className="text-2xl font-semibold text-primary mb-4">
                No Timetable Entries Found
              </h2>
              <p className="text-secondary mb-6 leading-relaxed">
                Your timetable configuration is set up, but there are no scheduled classes yet. 
                This might happen if no subjects have been assigned to teachers or class groups, 
                or if the timetable generation hasn't been completed.
              </p>
              
              <div className="bg-accent-cyan/10 border border-accent-cyan/20 rounded-xl p-4 mb-6">
                <h3 className="text-lg font-medium text-accent-cyan mb-2 flex items-center justify-center gap-2">
                  <Settings className="h-5 w-5" />
                  Next Steps:
                </h3>
                <ul className="text-sm text-primary text-left space-y-1">
                  <li>• Ensure subjects are assigned to teachers</li>
                  <li>• Verify class groups and batches are configured</li>
                  <li>• Check teacher-subject assignments</li>
                  <li>• Try generating a new timetable</li>
                </ul>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={handleRegenerateTimetable}
                  disabled={regenerating}
                  className={`px-6 py-3 rounded-xl font-medium transition-all duration-300 flex items-center gap-2 ${
                    regenerating
                      ? 'bg-surface/50 text-secondary/50 cursor-not-allowed'
                      : 'bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30'
                  }`}
                >
                  {regenerating ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Calendar className="h-4 w-4" />
                      Generate Timetable
                    </>
                  )}
                </button>
                <BackButton 
                  href="/components/DepartmentConfig" 
                  label="Review Configuration"
                  className="px-6 py-3 bg-surface border border-border text-secondary rounded-xl font-medium transition-all duration-200 hover:border-accent-cyan/30 hover:text-primary"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-background text-primary font-sans" suppressHydrationWarning>
      <Navbar number={8} />

      <div className="flex-1 p-8 max-w-7xl">
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-2">Generated Timetable</h1>
            <p className="text-secondary">
              View and manage your generated class schedules. Use the filter to view specific sections.
            </p>
          </div>
          
          {/* Controls */}
          <div className="flex flex-col items-end gap-3">
            <div className="flex items-center gap-3">
              <label className="text-sm text-secondary">Edit Mode</label>
              <button
                onClick={() => setEditMode(!editMode)}
                className={`px-4 py-2 rounded-xl ${editMode ? 'bg-accent-pink/20 border border-accent-pink/30 text-accent-pink' : 'bg-surface border border-border text-secondary'} transition-all duration-200 hover:border-accent-cyan/30`}
              >
                {editMode ? 'On' : 'Off'}
              </button>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowDeleteTimetableConfirm(true)}
                className="px-4 py-3 bg-red-500 text-white font-medium rounded-xl hover:bg-red-600 hover:shadow-lg transition-all duration-300 flex items-center gap-2"
              >
                <Trash2 className="h-4 w-4" />
                Delete Timetable
              </button>
            <button
              onClick={handleRegenerateTimetable}
              disabled={regenerating}
              className={`px-6 py-3 rounded-xl font-medium transition-all duration-300 flex items-center gap-2 ${
                regenerating
                  ? 'bg-surface/50 text-secondary/50 cursor-not-allowed'
                  : 'bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30'
              }`}
            >
              {regenerating ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Regenerating...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4" />
                  Regenerate Timetable
                </>
              )}
            </button>
            </div>
            <p className="text-xs text-secondary/70 text-right max-w-xs">
              Wipes existing data and generates<br/>a completely new timetable
            </p>
          </div>
        </div>

        {message && (
          <div className={`mb-4 p-4 rounded-xl border ${message.type === 'error' ? 'bg-red-500/10 border-red-500/20 text-red-400' : 'bg-green-500/10 border-green-500/20 text-green-400'}`}>
            {message.text}
          </div>
        )}

        {/* Section Filter */}
        {timetableData.pagination && (
          <div className="mb-6 bg-gray-800 rounded-lg border border-gray-700 p-4">
            <div className="flex items-center gap-3">
              <label className="text-sm text-gray-300">Filter by Section:</label>
              <select
                value={selectedClassGroup}
                onChange={(e) => setSelectedClassGroup(e.target.value)}
                className="bg-gray-700 border border-gray-600 text-gray-100 px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                {[...new Set(timetableData.pagination.class_groups || [])]
                  .sort((a, b) => {
                    // Sort sections properly (21SW-I, 21SW-II, 21SW-III, 22SW-I, etc.)
                    const [batchA, sectionA] = a.split('-');
                    const [batchB, sectionB] = b.split('-');
                    if (batchA !== batchB) return batchA.localeCompare(batchB);
                    return (sectionA || '').localeCompare(sectionB || '');
                  })
                  .map(group => (
                  <option key={group} value={group}>
                    {group.includes('-') ? `${group.split('-')[0]} Section ${group.split('-')[1]}` : group}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-x-auto">
          <div className="grid grid-cols-[120px_repeat(5,1fr)] gap-[1px] bg-gray-700 min-w-[1000px]">
            <div className="bg-gray-800 p-4 text-center sticky left-0 z-10"></div>
            {(timetableData.days || []).map(day => (
              <div key={day} className="bg-gray-800 p-4 text-center font-semibold border-b-2 border-purple-500">
                {day}
              </div>
            ))}

            {(timetableData.timeSlots || []).map((timeSlot, index) => (
              <React.Fragment key={index}>
                <div className="bg-gray-800 p-4 text-center sticky left-0 z-10">
                  {timeSlot}
                </div>
                {(timetableData.days || []).map(day => {
                  // Normalize day names for matching
                  const normalizeDay = (dayName) => {
                    if (typeof dayName === 'string') {
                      return dayName.toUpperCase().substring(0, 3);
                    }
                    return dayName;
                  };

                  const entry = (timetableData.entries || []).find(
                    e => normalizeDay(e.day) === normalizeDay(day) && e.period === (index + 1)
                  );
                  console.log(`Looking for entry: day=${day} (normalized: ${normalizeDay(day)}), period=${index + 1}, found:`, entry); // Debug log
                  return (
                    <div
                      key={`${day}-${index}`}
                      className={`p-4 min-h-[80px] flex flex-col justify-center gap-1 ${
                        index % 2 === 0 ? 'bg-gray-800' : 'bg-gray-900'
                      } ${editMode ? 'outline outline-1 outline-gray-700' : ''}`}
                      onDragOver={(e) => {
                        if (!editMode) return;
                        e.preventDefault();
                      }}
                      onDrop={async (e) => {
                        if (!editMode || !draggingEntry) return;
                        e.preventDefault();
                        try {
                          const res = await api.post(`/api/timetable/slots/${draggingEntry.id}/move/`, {
                            day: day,
                            period: index + 1,
                          });
                          // Optimistically update UI to clear old slot
                          setTimetableData(prev => {
                            if (!prev) return prev;
                            const updated = { ...prev, entries: [...(prev.entries || [])] };
                            const idx = updated.entries.findIndex(en => en.id === draggingEntry.id);
                            if (idx !== -1) {
                              updated.entries[idx] = { ...updated.entries[idx], day, period: index + 1 };
                            }
                            return updated;
                          });
                          // Refresh entries to keep labels in sync
                          const params = new URLSearchParams();
                          if (selectedClassGroup) params.append('class_group', selectedClassGroup);
                          const latest = await api.get(`/api/timetable/latest/?${params}`);
                          setTimetableData(latest.data);
                          setMessage({ type: 'success', text: 'Slot moved successfully' });
                        } catch (err) {
                          const msg = err.response?.data?.detail || 'Move failed due to constraints';
                          setMessage({ type: 'error', text: msg });
                        } finally {
                          setDraggingEntry(null);
                          setTimeout(() => setMessage(null), 2500);
                        }
                      }}
                    >
                      {entry && (
                        <>
                          <div
                            className={`font-medium text-purple-400 ${editMode ? 'cursor-move' : ''}`}
                            draggable={editMode}
                            onDragStart={() => setDraggingEntry(entry)}
                          >
                            {entry.subject_short_name || entry.subject_code || entry.subject}
                          </div>
                          <div className="text-sm text-blue-400">{entry.teacher}</div>
                          <div className="text-xs text-emerald-400">{entry.classroom}</div>
                          <div className="text-xs text-gray-400">
                            {entry.class_group.includes('-') ?
                              `${entry.class_group.split('-')[0]} Sec ${entry.class_group.split('-')[1]}` :
                              entry.class_group
                            }
                          </div>
                          {editMode && (
                            <div className="mt-2 flex gap-2 items-center">
                              {/* Shift arrows removed as requested */}
                              <button
                                className="text-xs px-2 py-1 bg-blue-700 rounded"
                                onClick={async () => {
                                  const open = moveUIForEntry === entry.id
                                  setMoveUIForEntry(open ? null : entry.id)
                                  setSafeSlotsErrorFor(null)
                                  if (!open) {
                                    setMoveDay(entry.day)
                                    setMovePeriod(entry.period)
                                    setSafeSlotsLoadingFor(entry.id || `${entry.day}-${entry.period}`)
                                    try {
                                      let entryId = entry.id
                                      if (!entryId) {
                                        const params = new URLSearchParams();
                                        if (selectedClassGroup) params.append('class_group', selectedClassGroup);
                                        const latest = await api.get(`/api/timetable/latest/?${params}`)
                                        setTimetableData(latest.data)
                                        const refreshed = (latest.data.entries || []).find(
                                          e => (e.day?.toUpperCase().substring(0,3) === (entry.day?.toUpperCase().substring(0,3))) && e.period === entry.period
                                        )
                                        entryId = refreshed?.id
                                      }
                                      if (!entryId) throw new Error('Missing entry id')
                                      const res = await api.get(`/api/timetable/slots/${entryId}/safe-moves/`)
                                      const safe = res.data?.safe_slots || []
                                      setSafeSlotsByEntry(prev => ({ ...prev, [entryId]: safe }))
                                    } catch (err) {
                                      setSafeSlotsErrorFor(entry.id || `${entry.day}-${entry.period}`)
                                      setMessage({ type: 'error', text: 'Failed to fetch safe slots' })
                                      setTimeout(() => setMessage(null), 2200)
                                    } finally {
                                      setSafeSlotsLoadingFor(null)
                                    }
                                  }
                                }}
                              >Move…</button>
                              <button
                                className="text-xs px-2 py-1 bg-red-700 rounded"
                                onClick={async () => {
                                  if (!confirm('Delete this slot?')) return
                                  try {
                                    await api.delete(`/api/timetable/slots/${entry.id}/`)
                                    setTimetableData(prev => ({
                                      ...prev,
                                      entries: prev.entries.filter(en => en.id !== entry.id)
                                    }))
                                    setMessage({ type: 'success', text: 'Slot deleted' })
                                  } catch (err) {
                                    const msg = err.response?.data?.detail || 'Delete failed'
                                    setMessage({ type: 'error', text: msg })
                                  } finally {
                                    setTimeout(() => setMessage(null), 2000)
                                  }
                                }}
                              >Delete</button>
                            </div>
                          )}
                          {editMode && moveUIForEntry === entry.id && (
                            <div className="mt-2 p-2 bg-gray-800 rounded border border-gray-700 flex flex-wrap gap-2 items-center">
                              {safeSlotsLoadingFor === entry.id && (
                                <span className="text-xs text-gray-400">Loading safe slots…</span>
                              )}
                              {safeSlotsErrorFor === entry.id && (
                                <span className="text-xs text-red-300">Failed to load safe slots</span>
                              )}
                              {!!safeSlotsByEntry[entry.id]?.length && (
                                <div className="w-full flex flex-wrap gap-2 mt-1">
                                  {safeSlotsByEntry[entry.id].map((s) => (
                                    <button
                                      key={`${s.day}-${s.period}`}
                                      className={`text-xs px-2 py-1 rounded border ${moveDay===s.day && movePeriod===s.period ? 'bg-green-700 border-green-500' : 'bg-gray-700 border-gray-600'}`}
                                onClick={async () => {
                                        // Directly move to the chosen safe slot for a smoother UX
                                        setMoveDay(s.day);
                                        setMovePeriod(s.period);
                                        try {
                                          setMessage({ type: 'info', text: `Moving to ${s.day} · P${s.period}...` })
                                          let entryId = entry.id
                                          if (!entryId) {
                                            const params = new URLSearchParams();
                                            if (selectedClassGroup) params.append('class_group', selectedClassGroup);
                                            const latest = await api.get(`/api/timetable/latest/?${params}`)
                                            setTimetableData(latest.data)
                                            const refreshed = (latest.data.entries || []).find(
                                              e => (e.day?.toUpperCase().substring(0,3) === (entry.day?.toUpperCase().substring(0,3))) && e.period === entry.period
                                            )
                                            entryId = refreshed?.id
                                          }
                                          if (!entryId) throw new Error('Missing entry id')
                                          await api.post(`/api/timetable/slots/${entryId}/move/`, { day: s.day, period: s.period })
                                          // Optimistically update UI to clear old slot and show new
                                          setTimetableData(prev => {
                                            if (!prev) return prev;
                                            const updated = { ...prev, entries: [...(prev.entries || [])] };
                                            const idx = updated.entries.findIndex(en => en.id === entryId);
                                            if (idx !== -1) {
                                              updated.entries[idx] = { ...updated.entries[idx], day: s.day, period: s.period };
                                            }
                                            return updated;
                                          });
                                    const params = new URLSearchParams();
                                    if (selectedClassGroup) params.append('class_group', selectedClassGroup);
                                    const latest = await api.get(`/api/timetable/latest/?${params}`);
                                    setTimetableData(latest.data);
                                    setMoveUIForEntry(null)
                                          setMessage({ type: 'success', text: `Moved to ${s.day}, period ${s.period}` })
                                  } catch (err) {
                                          const msg = err.response?.data?.detail || err.message || 'Move failed'
                                    setMessage({ type: 'error', text: msg })
                                  } finally {
                                    setTimeout(() => setMessage(null), 2200)
                                  }
                                }}
                                    >{s.day} · P{s.period}</button>
                                  ))}
                                </div>
                              )}
                              <button
                                className="text-xs px-2 py-1 bg-gray-700 rounded"
                                onClick={() => setMoveUIForEntry(null)}
                              >Cancel</button>
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  );
                })}
              </React.Fragment>
            ))}
          </div>
        </div>

        <div className="mt-8 flex justify-between items-center">
          <BackButton href="/components/DepartmentConfig" label="Back: Department Config" />
          
          {/* Bottom Download Button */}
          <button
            onClick={async () => {
              try {
                setDownloadingPDF(true);
                await generateTimetablePDF(timetableData, selectedClassGroup);
              } catch (error) {
                console.error('Failed to generate PDF:', error);
                // You can add a user notification here if needed
              } finally {
                setDownloadingPDF(false);
              }
            }}
            disabled={downloadingPDF}
            className={`px-6 py-3 rounded-xl font-medium transition-all duration-300 flex items-center gap-2 ${
              downloadingPDF 
                ? 'bg-surface/50 text-secondary/50 cursor-not-allowed' 
                : 'bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30'
            }`}
          >
            {downloadingPDF ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Generating PDF...
              </>
            ) : (
              <>
                <Download className="h-4 w-4" />
                Download Timetable PDF
              </>
            )}
          </button>
        </div>

        {/* Delete Timetable Confirmation Modal */}
        {showDeleteTimetableConfirm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-surface border border-border rounded-xl p-6 max-w-md mx-4">
              <div className="flex items-center gap-3 mb-4">
                <Shield className="h-6 w-6 text-red-500" />
                <h3 className="text-lg font-semibold text-primary">Confirm Delete Timetable</h3>
              </div>
              
              <div className="mb-4 p-3 border bg-red-800 border-yellow-200 rounded-lg">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-yellow-600" />
                  <span className="text-sm text-white">
                    This will delete ALL timetable entries and related data. This action cannot be undone!
                  </span>
                </div>
              </div>
              
              <p className="text-secondary mb-6">
                Are you sure you want to proceed? This will permanently delete all timetable data.
              </p>
              
              <div className="flex gap-3">
                <button
                  onClick={() => setShowDeleteTimetableConfirm(false)}
                  className="flex-1 py-2 px-4 border border-border rounded-lg text-secondary hover:bg-background transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteTimetable}
                  disabled={deleteTimetableLoading}
                  className="flex-1 py-2 px-4 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors disabled:opacity-50"
                >
                  {deleteTimetableLoading ? (
                    <div className="flex items-center justify-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Deleting...
                    </div>
                  ) : (
                    "Confirm Delete"
                  )}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Timetable;
