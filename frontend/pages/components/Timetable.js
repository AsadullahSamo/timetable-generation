import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Navbar from './Navbar';
import api from "../utils/api";

const Timetable = () => {
  const router = useRouter();
  const [timetableData, setTimetableData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedClassGroup, setSelectedClassGroup] = useState("");
  const [constraintFilter, setConstraintFilter] = useState(null);
  const [constraintData, setConstraintData] = useState(null);
  const [filteredEntries, setFilteredEntries] = useState([]);
  const [resolving, setResolving] = useState(false);
  const [resolutionResult, setResolutionResult] = useState(null);

  useEffect(() => {
    const fetchTimetable = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams();

        if (selectedClassGroup) {
          params.append('class_group', selectedClassGroup);
        }

        const { data } = await api.get(`/api/timetable/latest/?${params}`);
        if (!data || !data.entries || !Array.isArray(data.entries)) {
          throw new Error("Invalid timetable data received");
        }
        console.log("Received timetable data:", data); // Debug log
        setTimetableData(data);
        setError("");
      } catch (err) {
        // Handle specific case when no configuration exists (400 error)
        if (err.response?.status === 400) {
          setError("No schedule configuration found. Please set up Department Configuration first.");
        } else {
          setError("Failed to load timetable. Please try again.");
        }
        console.error("Timetable fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchTimetable();
  }, [selectedClassGroup]);

  // Constraint filter definitions
  const constraintFilters = [
    {
      id: 'subject_frequency',
      name: 'Credit Hours',
      description: 'Show subjects with their credit hours, assigned teachers, sections, and timings',
      icon: '📊',
      color: 'bg-blue-500'
    },
    {
      id: 'cross_semester_conflicts',
      name: 'Cross-Semester',
      description: 'Show teachers and their assignments across different semesters',
      icon: '🔄',
      color: 'bg-red-500'
    },
    {
      id: 'practical_blocks',
      name: 'Practical Blocks',
      description: 'Show 3-hour practical blocks with consecutive timings',
      icon: '🔬',
      color: 'bg-purple-500'
    },
    {
      id: 'teacher_conflicts',
      name: 'Teacher Conflicts',
      description: 'Show teachers and their time slot assignments',
      icon: '👨‍🏫',
      color: 'bg-yellow-500'
    },
    {
      id: 'room_conflicts',
      name: 'Room Usage',
      description: 'Show classroom assignments and usage patterns',
      icon: '🏫',
      color: 'bg-green-500'
    },
    {
      id: 'friday_time_limits',
      name: 'Friday Limits',
      description: 'Show Friday classes and time restrictions',
      icon: '📅',
      color: 'bg-indigo-500'
    },
    {
      id: 'thesis_day_constraint',
      name: 'Thesis Day',
      description: 'Show Wednesday thesis assignments for final year students',
      icon: '📝',
      color: 'bg-pink-500'
    },
    {
      id: 'senior_batch_lab_assignment',
      name: 'Senior Lab Priority',
      description: 'Show senior batches assigned to labs (even for theory)',
      icon: '🎓',
      color: 'bg-amber-500'
    }
  ];

  const fetchConstraintData = async (constraintType, forceRefresh = false) => {
    try {
      setLoading(true);

      // Clear resolution result when switching to different constraint
      if (constraintFilter !== constraintType) {
        setResolutionResult(null);
      }

      // Add timestamp to force fresh data after resolution
      const requestData = {
        constraint_type: constraintType
      };

      if (forceRefresh) {
        requestData.timestamp = Date.now();
      }

      const response = await api.post('/api/timetable/constraint-testing/', requestData);

      console.log('Constraint data received:', response.data.analysis);
      console.log('Constraint type:', constraintType);
      console.log('Force refresh:', forceRefresh);

      setConstraintData(response.data.analysis);
      setConstraintFilter(constraintType);

      // Filter timetable entries based on constraint
      filterEntriesByConstraint(constraintType, response.data.analysis);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch constraint data');
      console.error('Constraint data error:', err);
    } finally {
      setLoading(false);
    }
  };

  const filterEntriesByConstraint = (constraintType, analysisData) => {
    if (!timetableData || !timetableData.entries) return;

    let filtered = [];

    switch (constraintType) {
      case 'subject_frequency':
        // Show ONLY entries that have subject frequency violations
        const subjectFrequencyData = analysisData?.violations || [];

        if (subjectFrequencyData.length === 0) {
          // No violations, show empty array
          filtered = [];
        } else {
          // Get subjects and class groups that have violations
          const violatedSubjectGroups = subjectFrequencyData.map(item => ({
            subject_code: item.subject_code,
            class_group: item.class_group
          }));

          // Filter entries to show only those with violations
          filtered = timetableData.entries.filter(entry => {
            return violatedSubjectGroups.some(violation =>
              violation.subject_code === entry.subject &&
              violation.class_group === entry.class_group
            );
          }).map(entry => {
            const violationData = subjectFrequencyData.find(item =>
              item.subject_code === entry.subject && item.class_group === entry.class_group
            );

            return {
              ...entry,
              constraintInfo: {
                type: 'Credit Hours Violation',
                details: violationData ?
                  `Expected: ${violationData.expected_count}, Actual: ${violationData.actual_count} classes/week` :
                  `Frequency violation`,
                status: 'warning'
              }
            };
          });
        }
        break;

      case 'cross_semester_conflicts':
        // Show ALL entries (not filtered) to see complete teacher assignments across all sections
        filtered = timetableData.entries.map(entry => {
          const conflictData = analysisData?.conflicts || [];
          const hasConflict = conflictData.some(c =>
            c.teacher === entry.teacher && c.day === entry.day && c.period === entry.period
          );
          return {
            ...entry,
            constraintInfo: {
              type: 'Cross-Semester',
              details: hasConflict ? 'Potential Conflict' : 'No Conflict',
              status: hasConflict ? 'warning' : 'success'
            }
          };
        });
        break;

      case 'practical_blocks':
        // Filter by practical subjects only
        const practicalData = analysisData?.violations || [];
        const compliantBlocks = analysisData?.compliant_blocks || [];
        const allPracticalData = [...practicalData, ...compliantBlocks];
        const practicalSubjects = [...new Set(allPracticalData.map(item => item.subject_code || item.subject_name))];

        filtered = timetableData.entries.filter(entry =>
          entry.subject && (
            practicalSubjects.includes(entry.subject) ||
            entry.subject.toLowerCase().includes('lab') ||
            entry.subject.toLowerCase().includes('practical')
          )
        ).map(entry => {
          const blockData = allPracticalData.find(item =>
            (item.subject_code === entry.subject || item.subject_name === entry.subject) &&
            item.class_group === entry.class_group
          );
          return {
            ...entry,
            constraintInfo: {
              type: 'Practical Block',
              details: blockData ?
                `${blockData.block_length || 3}-hour block` :
                `Practical subject`,
              status: blockData?.violation_type ? 'warning' : 'success'
            }
          };
        });
        break;

      case 'teacher_conflicts':
        // Show ONLY entries with teacher conflicts
        const teacherConflicts = analysisData?.conflicts || [];

        if (teacherConflicts.length === 0) {
          filtered = [];
        } else {
          const conflictTeachers = [...new Set(teacherConflicts.map(c => c.teacher_name))];

          filtered = timetableData.entries.filter(entry =>
            conflictTeachers.includes(entry.teacher)
          ).map(entry => {
            const conflictInfo = teacherConflicts.find(c => c.teacher_name === entry.teacher);
            return {
              ...entry,
              constraintInfo: {
                type: 'Teacher Conflict',
                details: conflictInfo ?
                  `Conflict at ${conflictInfo.day} P${conflictInfo.period} (${conflictInfo.conflict_count} overlaps)` :
                  `Teacher scheduling conflict`,
                status: 'warning'
              }
            };
          });
        }
        break;

      case 'room_conflicts':
        // Filter by rooms that have conflicts
        const roomConflicts = analysisData?.conflicts || [];
        const conflictRooms = [...new Set(roomConflicts.map(c => c.classroom_name))];

        filtered = timetableData.entries.filter(entry =>
          conflictRooms.length === 0 || conflictRooms.includes(entry.classroom)
        ).map(entry => {
          const hasConflict = roomConflicts.some(c => c.classroom_name === entry.classroom);
          return {
            ...entry,
            constraintInfo: {
              type: 'Room Conflict',
              details: `${entry.classroom} - ${entry.day} P${entry.period}`,
              status: hasConflict ? 'warning' : 'success'
            }
          };
        });
        break;

      case 'friday_time_limits':
        // Filter by Friday entries only
        filtered = timetableData.entries.filter(entry =>
          entry.day.toUpperCase() === 'FRIDAY'
        ).map(entry => {
          const violationData = analysisData?.violations?.find(v =>
            v.class_group === entry.class_group && v.period === entry.period
          );
          return {
            ...entry,
            constraintInfo: {
              type: 'Friday Limit',
              details: `Period ${entry.period} - ${entry.start_time}`,
              status: violationData ? 'warning' : 'success'
            }
          };
        });
        break;

      case 'thesis_day_constraint':
        // Filter by Wednesday entries only
        filtered = timetableData.entries.filter(entry =>
          entry.day.toUpperCase() === 'WEDNESDAY'
        ).map(entry => {
          const isThesis = entry.subject && entry.subject.toLowerCase().includes('thesis');
          const violationData = analysisData?.violations?.find(v =>
            v.class_group === entry.class_group && !isThesis
          );
          return {
            ...entry,
            constraintInfo: {
              type: 'Thesis Day',
              details: isThesis ? 'Thesis Subject' : 'Non-Thesis Subject',
              status: violationData ? 'warning' : 'success'
            }
          };
        });
        break;

      case 'senior_batch_lab_assignment':
        // Show ONLY entries that violate senior batch lab assignment
        const seniorLabViolations = analysisData?.violations || [];

        console.log('Senior lab violations:', seniorLabViolations);
        console.log('Total violations:', seniorLabViolations.length);

        if (seniorLabViolations.length === 0) {
          filtered = [];
        } else {
          // Filter timetable entries to match violations
          // Since we have violations, let's show all senior batch entries that are NOT in labs
          filtered = timetableData.entries.filter(entry => {
            if (!entry.class_group || !entry.classroom) return false;

            // Extract batch from class_group (e.g., "21SW-I" -> "21SW")
            const batch_name = entry.class_group.split('-')[0];

            try {
              const batch_year = parseInt(batch_name.substring(0, 2));
              const is_senior_batch = batch_year <= 22; // 21SW, 22SW are senior

              if (is_senior_batch) {
                // Check if this senior batch entry is in a regular room (not lab)
                const classroom_name = entry.classroom.name.toLowerCase();
                const is_lab_room = classroom_name.includes('lab') || classroom_name.includes('laboratory');

                if (!is_lab_room) {
                  console.log('Found senior batch violation:', {
                    batch: batch_name,
                    class_group: entry.class_group,
                    subject: entry.subject?.name,
                    classroom: entry.classroom.name,
                    day: entry.day,
                    period: entry.period
                  });
                  return true; // This is a violation
                }
              }
            } catch (e) {
              console.log('Error parsing batch:', batch_name, e);
            }

            return false;
          }).map(entry => {
            const batch_name = entry.class_group.split('-')[0];

            return {
              ...entry,
              constraintInfo: {
                type: 'Senior Lab Priority Violation',
                details: `${batch_name} (senior) should be in lab, currently in ${entry.classroom.name}`,
                status: 'warning'
              }
            };
          });
        }

        console.log('Filtered entries for senior lab:', filtered.length);
        break;

      default:
        filtered = timetableData.entries;
    }

    setFilteredEntries(filtered);
  };

  const clearConstraintFilter = () => {
    setConstraintFilter(null);
    setConstraintData(null);
    setFilteredEntries([]);
    setResolutionResult(null);
  };

  const attemptToResolveConstraint = async () => {
    if (!constraintFilter) return;

    setResolving(true);
    setResolutionResult(null);

    try {
      const response = await api.post('/api/timetable/resolve-constraint/', {
        constraint_type: constraintFilter,
        max_attempts: 5
      });

      setResolutionResult(response.data);

      // Always refresh data after resolution attempt (successful or not)
      try {
        // Refresh timetable data
        const timetableResponse = await api.get(`/api/timetable/latest/?${selectedClassGroup ? `class_group=${selectedClassGroup}` : ''}`);
        setTimetableData(timetableResponse.data);

        // Clear resolution result temporarily to avoid showing stale data
        setResolutionResult(null);

        // Wait longer for database to update, then refresh constraint analysis with force refresh
        setTimeout(async () => {
          try {
            await fetchConstraintData(constraintFilter, true); // Force refresh
            // Restore resolution result after fresh data is loaded
            setResolutionResult(response.data);
          } catch (refreshError) {
            console.error('Failed to refresh constraint data:', refreshError);
            // Still show resolution result even if refresh fails
            setResolutionResult(response.data);
          }
        }, 2000); // Increased timeout to 2 seconds for database consistency
      } catch (refreshError) {
        console.error('Failed to refresh timetable data:', refreshError);
        // Still show resolution result
        setResolutionResult(response.data);
      }

    } catch (err) {
      setResolutionResult({
        success: false,
        message: err.response?.data?.error || 'Failed to resolve constraint',
        error: true
      });
      console.error('Constraint resolution error:', err);
    } finally {
      setResolving(false);
    }
  };

  const getConstraintStatusColor = (status) => {
    switch (status) {
      case 'success': return 'text-green-400';
      case 'warning': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      default: return 'text-blue-400';
    }
  };

  const renderConstraintIssue = (constraintType, issue) => {
    switch (constraintType) {
      case 'subject_frequency':
        return (
          <div>
            <div className="font-medium">{issue.subject_name} ({issue.subject_code})</div>
            <div>Class: {issue.class_group}</div>
            <div>Expected: {issue.expected_count} classes/week, Actual: {issue.actual_count}</div>
            <div>Type: {issue.is_practical ? 'Practical' : 'Theory'}</div>
          </div>
        );
      case 'cross_semester_conflicts':
        return (
          <div>
            <div className="font-medium">Teacher: {issue.teacher}</div>
            <div>Subject: {issue.subject}</div>
            <div>Time: {issue.day} Period {issue.period} ({issue.time})</div>
            <div>Class: {issue.class_group}</div>
          </div>
        );
      case 'teacher_conflicts':
      case 'room_conflicts':
        return (
          <div>
            <div className="font-medium">{issue.teacher_name || issue.classroom_name}</div>
            <div>Time: {issue.day} Period {issue.period}</div>
            <div>Conflicts: {issue.conflict_count} assignments</div>
          </div>
        );
      case 'practical_blocks':
        return (
          <div>
            <div className="font-medium">{issue.subject_name}</div>
            <div>Class: {issue.class_group}</div>
            <div>Day: {issue.day}</div>
            <div>Issue: {issue.violation_type}</div>
            <div>Periods: {issue.periods?.join(', ')}</div>
          </div>
        );
      default:
        return JSON.stringify(issue).substring(0, 100) + '...';
    }
  };

  const renderCompliantItem = (constraintType, item) => {
    switch (constraintType) {
      case 'subject_frequency':
        return `${item.subject_name} - ${item.class_group} (${item.actual_count}/${item.expected_count} classes)`;
      case 'teacher_assignments':
        return `${item.teacher} → ${item.subject} (${item.class_group})`;
      case 'practical_blocks':
        return `${item.subject_name} - ${item.class_group} (${item.day})`;
      case 'cross_semester_conflicts':
        return `${item.teacher} - No conflicts`;
      default:
        return JSON.stringify(item).substring(0, 50) + '...';
    }
  };

  const renderTeacherBasedCrossSemesterData = () => {
    if (!filteredEntries.length) return null;

    // Group entries by teacher
    const groupedByTeacher = {};

    filteredEntries.forEach(entry => {
      if (!groupedByTeacher[entry.teacher]) {
        groupedByTeacher[entry.teacher] = [];
      }
      groupedByTeacher[entry.teacher].push(entry);
    });

    return Object.entries(groupedByTeacher).map(([teacher, entries], index) => {
      // Sort entries by day and period for better readability
      const sortedEntries = entries.sort((a, b) => {
        const dayOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
        const dayDiff = dayOrder.indexOf(a.day) - dayOrder.indexOf(b.day);
        if (dayDiff !== 0) return dayDiff;
        return a.period - b.period;
      });

      // Get unique subjects for this teacher
      const subjects = [...new Set(sortedEntries.map(entry => entry.subject))].join(', ');

      // Create detailed schedule showing day, period, time, subject, section, room
      const completeSchedule = sortedEntries.map(entry => {
        const section = entry.class_group.includes('-') ?
          `${entry.class_group.split('-')[0]} Sec ${entry.class_group.split('-')[1]}` :
          entry.class_group;
        return `${entry.day} P${entry.period} (${entry.start_time}-${entry.end_time}): ${entry.subject} [${section}] @${entry.classroom}`;
      }).join(' | ');

      // Get all sections this teacher teaches
      const sections = [...new Set(sortedEntries.map(entry => {
        return entry.class_group.includes('-') ?
          `${entry.class_group.split('-')[0]} Sec ${entry.class_group.split('-')[1]}` :
          entry.class_group;
      }))].join(', ');

      // Get all rooms this teacher uses
      const rooms = [...new Set(sortedEntries.map(entry => entry.classroom))].join(', ');

      // Check for conflicts (same teacher, same time slot)
      const timeSlots = {};
      let hasConflict = false;

      sortedEntries.forEach(entry => {
        const timeKey = `${entry.day}-P${entry.period}`;
        if (timeSlots[timeKey]) {
          hasConflict = true;
        } else {
          timeSlots[timeKey] = entry;
        }
      });

      // Also check if this teacher has conflicts from analysis data
      const analysisConflict = sortedEntries.some(entry =>
        entry.constraintInfo?.status === 'warning' || entry.constraintInfo?.status === 'error'
      );

      const finalStatus = hasConflict || analysisConflict ? 'warning' : 'success';

      return (
        <tr key={`teacher-${teacher}-${index}`} className="border-b border-gray-700 hover:bg-gray-700/50">
          <td className="p-3 text-blue-400 font-medium">{teacher}</td>
          <td className="p-3 text-purple-400">{subjects}</td>
          <td className="p-3 text-gray-300 text-xs max-w-md">
            <div className="max-h-20 overflow-y-auto">
              {completeSchedule}
            </div>
          </td>
          <td className="p-3 text-emerald-400">{sections}</td>
          <td className="p-3 text-emerald-400">{rooms}</td>
          <td className="p-3">
            <span className={`px-2 py-1 rounded text-xs ${
              finalStatus === 'success' ? 'bg-green-900/50 text-green-300' :
              'bg-yellow-900/50 text-yellow-300'
            }`}>
              {hasConflict ? 'Time Conflict!' : analysisConflict ? 'Cross-Semester Issue' : 'No Conflicts'}
            </span>
          </td>
        </tr>
      );
    });
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-gray-900 text-gray-100 font-sans" suppressHydrationWarning>
        <Navbar number={8} />
        <div className="flex-1 p-8 max-w-7xl">
          <div className="flex justify-center items-center h-full">
            <div className="text-center text-purple-400 italic">
              <i className="fas fa-spinner fa-spin text-4xl mb-4"></i>
              <p>Loading timetable...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen bg-gray-900 text-gray-100 font-sans" suppressHydrationWarning>
        <Navbar number={8} />
        <div className="flex-1 p-8 max-w-7xl">
          <h1 className="text-3xl text-gray-50 mb-8">Generated Timetable</h1>
          <div className="bg-red-900/50 text-red-200 p-4 rounded-lg mb-6">
            {error}
          </div>
          <div className="mt-8">
            <button 
              className="px-6 py-3 border border-gray-700 text-gray-400 rounded-lg hover:border-purple-500 hover:text-purple-400 transition-colors"
              onClick={() => router.back()}
            >
              ← Back to Constraints
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!timetableData) return null;

  return (
    <div className="flex min-h-screen bg-gray-900 text-gray-100 font-sans" suppressHydrationWarning>
      <Navbar number={8} />
      
      <div className="flex-1 p-8 max-w-7xl">
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-3xl text-gray-50 mb-2">Generated Timetable</h1>
            <p className="text-gray-400">
              View and manage your generated class schedules. Use the filter to view specific sections.
            </p>
          </div>

        </div>

        {/* Constraint Filter Buttons */}
        <div className="mb-6 bg-gray-800 rounded-lg border border-gray-700 p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-100">Constraint Filters</h3>
            {constraintFilter && (
              <div className="flex gap-2">
                <button
                  onClick={() => fetchConstraintData(constraintFilter, true)}
                  disabled={loading}
                  className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-500 transition-colors disabled:opacity-50"
                >
                  {loading ? 'Refreshing...' : 'Refresh'}
                </button>
                <button
                  onClick={clearConstraintFilter}
                  className="px-3 py-1 text-sm bg-gray-600 text-gray-300 rounded hover:bg-gray-500 transition-colors"
                >
                  Clear Filter
                </button>
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
            {constraintFilters.map((filter) => (
              <button
                key={filter.id}
                onClick={() => fetchConstraintData(filter.id)}
                disabled={loading}
                className={`p-3 rounded-lg border transition-all duration-300 flex flex-col items-center gap-2 text-sm ${
                  constraintFilter === filter.id
                    ? `${filter.color} text-white border-transparent shadow-lg`
                    : 'bg-gray-700 border-gray-600 text-gray-300 hover:border-purple-500 hover:text-purple-400'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                <div className="text-xl">{filter.icon}</div>
                <div className="font-medium text-center leading-tight">{filter.name}</div>
              </button>
            ))}
          </div>

          {constraintFilter && (
            <div className="mt-4 p-3 bg-gray-900 rounded-lg">
              <div className="flex justify-between items-start">
                <div className="text-sm text-gray-300">
                  <strong>Active Filter:</strong> {constraintFilters.find(f => f.id === constraintFilter)?.description}
                  {constraintData && (
                    <div className="mt-2 text-xs text-gray-400">
                      Status: {constraintData.status} |
                      Issues: {constraintData.total_violations || constraintData.total_conflicts || 0} |
                      Showing: {filteredEntries.length} entries
                    </div>
                  )}
                </div>

                {/* Attempt to Resolve Button - Only show if there are actual violations */}
                {constraintData && filteredEntries.length > 0 && (constraintData.total_violations > 0 || constraintData.total_conflicts > 0) && (
                  <button
                    onClick={attemptToResolveConstraint}
                    disabled={resolving}
                    className="px-4 py-2 bg-gradient-to-r from-orange-600 to-red-600 text-white rounded-lg hover:from-orange-700 hover:to-red-700 transition-all duration-300 flex items-center gap-2 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {resolving ? (
                      <>
                        <i className="fas fa-spinner fa-spin"></i>
                        Resolving...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-tools"></i>
                        Attempt to Resolve
                      </>
                    )}
                  </button>
                )}
              </div>

              {/* Resolution Result */}
              {resolutionResult && (
                <div className={`mt-3 p-3 rounded-lg border ${
                  resolutionResult.success
                    ? 'bg-green-900/20 border-green-700 text-green-300'
                    : 'bg-red-900/20 border-red-700 text-red-300'
                }`}>
                  <div className="font-medium mb-2">
                    {resolutionResult.success ? '✅ Resolution Result' : '❌ Resolution Failed'}
                  </div>
                  <div className="text-sm">
                    <div>{resolutionResult.message}</div>
                    {resolutionResult.attempts_made && (
                      <div className="mt-1">
                        Attempts: {resolutionResult.attempts_made} |
                        Violations Before: {resolutionResult.violations_before} → After: {resolutionResult.violations_after}
                        {resolutionResult.other_constraints_affected !== undefined && (
                          <span> | Other Constraints Affected: {resolutionResult.other_constraints_affected}</span>
                        )}
                      </div>
                    )}
                    {resolutionResult.violations_after === 0 && (
                      <div className="mt-2 text-green-400 text-xs">
                        ✅ Data is being refreshed to reflect the changes...
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

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
                {[...new Set(timetableData.pagination.class_groups)]
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
            {timetableData.days.map(day => (
              <div key={day} className="bg-gray-800 p-4 text-center font-semibold border-b-2 border-purple-500">
                {day}
              </div>
            ))}

            {timetableData.timeSlots.map((timeSlot, index) => (
              <React.Fragment key={index}>
                <div className="bg-gray-800 p-4 text-center sticky left-0 z-10">
                  {timeSlot}
                </div>
                {timetableData.days.map(day => {
                  // Normalize day names for matching
                  const normalizeDay = (dayName) => {
                    if (typeof dayName === 'string') {
                      return dayName.toUpperCase().substring(0, 3);
                    }
                    return dayName;
                  };

                  // Use filtered entries if constraint filter is active, otherwise use all entries
                  const entriesToSearch = constraintFilter && filteredEntries.length > 0 ? filteredEntries : timetableData.entries;
                  const entry = entriesToSearch.find(
                    e => normalizeDay(e.day) === normalizeDay(day) && e.period === (index + 1)
                  );
                  console.log(`Looking for entry: day=${day} (normalized: ${normalizeDay(day)}), period=${index + 1}, found:`, entry); // Debug log
                  return (
                    <div 
                      key={`${day}-${index}`} 
                      className={`p-4 min-h-[80px] flex flex-col justify-center gap-1 ${
                        index % 2 === 0 ? 'bg-gray-800' : 'bg-gray-900'
                      }`}
                    >
                      {entry && (
                        <>
                          <div className="font-medium text-purple-400">{entry.subject}</div>
                          <div className="text-sm text-blue-400">{entry.teacher}</div>
                          <div className="text-xs text-emerald-400">{entry.classroom}</div>
                          <div className="text-xs text-gray-400">
                            {entry.class_group.includes('-') ?
                              `${entry.class_group.split('-')[0]} Sec ${entry.class_group.split('-')[1]}` :
                              entry.class_group
                            }
                          </div>

                          {/* Show constraint information if filter is active */}
                          {constraintFilter && entry.constraintInfo && (
                            <div className={`text-xs mt-1 px-2 py-1 rounded ${
                              entry.constraintInfo.status === 'success' ? 'bg-green-900/50 text-green-300' :
                              entry.constraintInfo.status === 'warning' ? 'bg-yellow-900/50 text-yellow-300' :
                              entry.constraintInfo.status === 'error' ? 'bg-red-900/50 text-red-300' :
                              'bg-blue-900/50 text-blue-300'
                            }`}>
                              <div className="font-medium">{entry.constraintInfo.type}</div>
                              <div className="text-xs opacity-90">{entry.constraintInfo.details}</div>
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

        {/* No Violations Message */}
        {constraintFilter && filteredEntries.length === 0 && (
          <div className="mt-8 bg-green-900/20 border border-green-700 rounded-lg p-6">
            <h3 className="text-xl font-semibold text-green-400 mb-2">
              ✅ No Violations Found
            </h3>
            <p className="text-green-300">
              All entries for "{constraintFilters.find(f => f.id === constraintFilter)?.name}" constraint are compliant.
              No issues need to be resolved.
            </p>
          </div>
        )}

        {/* Filtered Data Table */}
        {constraintFilter && filteredEntries.length > 0 && (
          <div className="mt-8 bg-gray-800 rounded-lg border border-gray-700 p-6">
            <h3 className="text-xl font-semibold text-gray-100 mb-4">
              {constraintFilters.find(f => f.id === constraintFilter)?.name} - Filtered Data
            </h3>

            {constraintFilter === 'cross_semester_conflicts' ? (
              // Special teacher-based display for cross-semester
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-600">
                      <th className="text-left p-3 text-gray-300">Teacher</th>
                      <th className="text-left p-3 text-gray-300">Subjects</th>
                      <th className="text-left p-3 text-gray-300">Complete Schedule</th>
                      <th className="text-left p-3 text-gray-300">Sections</th>
                      <th className="text-left p-3 text-gray-300">Rooms</th>
                      <th className="text-left p-3 text-gray-300">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {renderTeacherBasedCrossSemesterData()}
                  </tbody>
                </table>
              </div>
            ) : (
              // Standard display for other constraints
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-600">
                      <th className="text-left p-3 text-gray-300">Subject</th>
                      <th className="text-left p-3 text-gray-300">Teacher</th>
                      <th className="text-left p-3 text-gray-300">Section</th>
                      <th className="text-left p-3 text-gray-300">Day</th>
                      <th className="text-left p-3 text-gray-300">Period</th>
                      <th className="text-left p-3 text-gray-300">Time</th>
                      <th className="text-left p-3 text-gray-300">Room</th>
                      <th className="text-left p-3 text-gray-300">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredEntries.map((entry, index) => (
                      <tr key={index} className="border-b border-gray-700 hover:bg-gray-700/50">
                        <td className="p-3 text-purple-400 font-medium">{entry.subject}</td>
                        <td className="p-3 text-blue-400">{entry.teacher}</td>
                        <td className="p-3 text-gray-300">
                          {entry.class_group.includes('-') ?
                            `${entry.class_group.split('-')[0]} Sec ${entry.class_group.split('-')[1]}` :
                            entry.class_group
                          }
                        </td>
                        <td className="p-3 text-gray-300">{entry.day}</td>
                        <td className="p-3 text-gray-300">{entry.period}</td>
                        <td className="p-3 text-emerald-400">{entry.start_time} - {entry.end_time}</td>
                        <td className="p-3 text-emerald-400">{entry.classroom}</td>
                        <td className="p-3">
                          <span className={`px-2 py-1 rounded text-xs ${
                            entry.constraintInfo?.status === 'success' ? 'bg-green-900/50 text-green-300' :
                            entry.constraintInfo?.status === 'warning' ? 'bg-yellow-900/50 text-yellow-300' :
                            entry.constraintInfo?.status === 'error' ? 'bg-red-900/50 text-red-300' :
                            'bg-blue-900/50 text-blue-300'
                          }`}>
                            {entry.constraintInfo?.details || 'OK'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Constraint Details Panel */}
        {constraintFilter && constraintData && (
          <div className="mt-8 bg-gray-800 rounded-lg border border-gray-700 p-6">
            <h3 className="text-xl font-semibold text-gray-100 mb-4">
              {constraintFilters.find(f => f.id === constraintFilter)?.name} - Analysis Summary
            </h3>

            {constraintFilter === 'cross_semester_conflicts' ? (
              // Special summary for cross-semester conflicts
              <div className="space-y-6">
                {/* Overview Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-gray-900 rounded-lg p-4">
                    <div className={`text-2xl font-bold ${constraintData.status === 'PASS' ? 'text-green-400' : 'text-red-400'}`}>
                      {constraintData.status === 'PASS' ? '✅' : '❌'} {constraintData.status}
                    </div>
                    <div className="text-sm text-gray-400">Overall Status</div>
                  </div>
                  <div className="bg-gray-900 rounded-lg p-4">
                    <div className={`text-2xl font-bold ${(constraintData.total_conflicts || 0) === 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {constraintData.total_conflicts || 0}
                    </div>
                    <div className="text-sm text-gray-400">Time Conflicts</div>
                  </div>
                  <div className="bg-gray-900 rounded-lg p-4">
                    <div className="text-2xl font-bold text-blue-400">
                      {constraintData.total_teachers || 0}
                    </div>
                    <div className="text-sm text-gray-400">Total Teachers</div>
                  </div>
                  <div className="bg-gray-900 rounded-lg p-4">
                    <div className="text-2xl font-bold text-purple-400">
                      {filteredEntries.length}
                    </div>
                    <div className="text-sm text-gray-400">Schedule Entries</div>
                  </div>
                </div>

                {/* Teacher Summary */}
                {constraintData.teacher_schedules && (
                  <div className="bg-gray-900 rounded-lg p-4">
                    <h4 className="text-lg font-semibold text-gray-100 mb-3">Teacher Workload Summary</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-64 overflow-y-auto">
                      {Object.entries(constraintData.teacher_schedules).map(([teacherName, data]) => (
                        <div key={teacherName} className={`p-3 rounded-lg border ${
                          data.conflicts && data.conflicts.length > 0
                            ? 'bg-red-900/20 border-red-700'
                            : 'bg-green-900/20 border-green-700'
                        }`}>
                          <div className="font-medium text-gray-100">{teacherName}</div>
                          <div className="text-xs text-gray-400 mt-1">
                            <div>Subjects: {data.subjects?.length || 0}</div>
                            <div>Sections: {data.sections?.length || 0}</div>
                            <div>Classes: {data.schedule?.length || 0}</div>
                            <div>Semesters: {data.semesters?.join(', ') || 'N/A'}</div>
                            {data.conflicts && data.conflicts.length > 0 && (
                              <div className="text-red-300 font-medium">⚠️ {data.conflicts.length} conflicts</div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Conflict Details */}
                {constraintData.conflicts && constraintData.conflicts.length > 0 && (
                  <div className="bg-red-900/20 border border-red-700 rounded-lg p-4">
                    <h4 className="text-lg font-semibold text-red-400 mb-3">
                      🚨 Cross-Semester Conflicts ({constraintData.conflicts.length})
                    </h4>
                    <div className="space-y-3 max-h-64 overflow-y-auto">
                      {constraintData.conflicts.map((conflict, index) => (
                        <div key={index} className="bg-gray-800 rounded-lg p-3 border border-red-600">
                          <div className="font-medium text-red-300">
                            {conflict.teacher} - {conflict.subject}
                          </div>
                          <div className="text-sm text-gray-300 mt-1">
                            <div>Time: {conflict.day} Period {conflict.period} ({conflict.time})</div>
                            <div>Section: {conflict.class_group}</div>
                            <div>Room: {conflict.room}</div>
                            <div className="text-red-400 text-xs mt-1">
                              Conflicts: {conflict.conflicts?.join(', ')}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* No Conflicts Message */}
                {(!constraintData.conflicts || constraintData.conflicts.length === 0) && (
                  <div className="bg-green-900/20 border border-green-700 rounded-lg p-4">
                    <h4 className="text-lg font-semibold text-green-400 mb-2">
                      ✅ No Cross-Semester Conflicts Found
                    </h4>
                    <p className="text-green-300 text-sm">
                      All teachers have clean schedules with no overlapping assignments across semesters.
                    </p>
                  </div>
                )}
              </div>
            ) : (
              // Standard summary for other constraints
              <div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-gray-900 rounded-lg p-4">
                    <div className={`text-2xl font-bold ${constraintData.status === 'PASS' ? 'text-green-400' : 'text-red-400'}`}>
                      {constraintData.status === 'PASS' ? '✅' : '❌'} {constraintData.status}
                    </div>
                    <div className="text-sm text-gray-400">Overall Status</div>
                  </div>
                  <div className="bg-gray-900 rounded-lg p-4">
                    <div className={`text-2xl font-bold ${(constraintData.total_violations || constraintData.total_conflicts || 0) === 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {constraintData.total_violations || constraintData.total_conflicts || 0}
                    </div>
                    <div className="text-sm text-gray-400">Issues Found</div>
                  </div>
                  <div className="bg-gray-900 rounded-lg p-4">
                    <div className="text-2xl font-bold text-blue-400">
                      {filteredEntries.length}
                    </div>
                    <div className="text-sm text-gray-400">Filtered Entries</div>
                  </div>
                </div>
              </div>
            )}

            {/* Show violations if any */}
            {(constraintData.violations || constraintData.conflicts) &&
             (constraintData.violations?.length > 0 || constraintData.conflicts?.length > 0) && (
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-red-400 mb-3">Issues Found:</h4>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {(constraintData.violations || constraintData.conflicts || []).slice(0, 10).map((issue, index) => (
                    <div key={index} className="bg-red-900/20 border border-red-700 rounded-lg p-3">
                      <div className="text-sm text-red-300">
                        {renderConstraintIssue(constraintFilter, issue)}
                      </div>
                    </div>
                  ))}
                  {(constraintData.violations || constraintData.conflicts || []).length > 10 && (
                    <div className="text-sm text-gray-400 text-center">
                      ... and {(constraintData.violations || constraintData.conflicts || []).length - 10} more issues
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Show compliant items */}
            {(constraintData.compliant_subjects || constraintData.compliant_assignments ||
              constraintData.compliant_entries || constraintData.compliant_blocks ||
              constraintData.compliant_schedules || constraintData.compliant_days || []).length > 0 && (
              <div>
                <h4 className="text-lg font-semibold text-green-400 mb-3">Working Correctly:</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-48 overflow-y-auto">
                  {(constraintData.compliant_subjects || constraintData.compliant_assignments ||
                    constraintData.compliant_entries || constraintData.compliant_blocks ||
                    constraintData.compliant_schedules || constraintData.compliant_days || []).slice(0, 12).map((item, index) => (
                    <div key={index} className="bg-green-900/20 border border-green-700 rounded-lg p-3">
                      <div className="text-sm text-green-300">
                        {renderCompliantItem(constraintFilter, item)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="mt-8">
          <button
            className="px-6 py-3 border border-gray-700 text-gray-400 rounded-lg hover:border-purple-500 hover:text-purple-400 transition-colors"
            onClick={() => router.back()}
          >
            ← Back to Constraints
          </button>
        </div>
      </div>
    </div>
  );
};

export default Timetable;