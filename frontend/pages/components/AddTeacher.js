import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import api from "../utils/api";

const AddTeacher = () => {
  const router = useRouter();
  const { id } = router.query;
  
  // Form states
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [subjects, setSubjects] = useState([]);
  const [allSubjects, setAllSubjects] = useState([]);
  const [maxLessons, setMaxLessons] = useState(4);
  // Internal availability state: { day: { periodIndex: mode } }
  const [availabilityState, setAvailabilityState] = useState({});
  const [timetableConfig, setTimetableConfig] = useState(null);
  
  // Separate loading states:
  const [configLoading, setConfigLoading] = useState(true);
  const [teacherLoading, setTeacherLoading] = useState(false);
  const [error, setError] = useState("");
  
  // Active mode selector: "preferable" or "mandatory"
  const [activeMode, setActiveMode] = useState("preferable");

  // Fetch configuration and subjects once on mount.
  useEffect(() => {
    const fetchConfigAndSubjects = async () => {
      try {
        const configRes = await api.get("/api/timetable/configs/");
        if (configRes.data.length > 0) {
          setTimetableConfig(configRes.data[0]);
        }
        const subjectsRes = await api.get("/api/timetable/subjects/");
        setAllSubjects(subjectsRes.data);
      } catch (err) {
        setError("Failed to load configuration or subjects.");
      } finally {
        setConfigLoading(false);
      }
    };
    fetchConfigAndSubjects();
  }, []);

  // Fetch teacher data if editing
  useEffect(() => {
    const fetchTeacher = async () => {
      if (!id) return;
      try {
        const { data } = await api.get(`/api/timetable/teachers/${id}/`);
        setName(data.name);
        setEmail(data.email);
        setSubjects(data.subjects || []);
        setMaxLessons(data.max_lessons_per_day);
        // Convert availability data to internal state
        const newState = {};
        if (data.unavailable_periods) {
          // Handle both mandatory and preferable slots
          for (const mode of ['mandatory', 'preferable']) {
            const dayData = data.unavailable_periods[mode] || {};
            for (const [day, times] of Object.entries(dayData)) {
              if (!newState[day]) newState[day] = {};
              times.forEach(time => {
                const periodIndex = timetableConfig?.generated_periods[day]?.findIndex(p => p === time);
                if (periodIndex !== -1) {
                  newState[day][periodIndex] = mode;
                }
              });
            }
          }
        }
        setAvailabilityState(newState);
      } catch (err) {
        setError("Failed to load teacher data.");
      }
    };
    fetchTeacher();
  }, [id, timetableConfig]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setTeacherLoading(true);

    try {
      const availability = convertAvailability();
      const teacherData = {
        name,
        email,
        subjects,
        max_lessons_per_day: maxLessons,
        unavailable_periods: availability
      };
      
      console.log('Sending teacher data:', teacherData);
      console.log('Availability structure:', JSON.stringify(availability, null, 2));

      if (id) {
        const response = await api.put(`/api/timetable/teachers/${id}/`, teacherData);
        console.log('Update response:', response.data);
      } else {
        const response = await api.post("/api/timetable/teachers/", teacherData);
        console.log('Create response:', response.data);
      }
      router.push("/components/TeachersConfig");
    } catch (err) {
      console.error('Error response:', err.response?.data);
      setError(err.response?.data?.detail || "Failed to save teacher.");
    } finally {
      setTeacherLoading(false);
    }
  };

  // Combine loading states for rendering:
  const isLoading = configLoading || teacherLoading;

  const handleSubjectChange = (subjectId) => {
    setSubjects(prev =>
      prev.includes(subjectId)
        ? prev.filter((id) => id !== subjectId)
        : [...prev, subjectId]
    );
  };

  // Toggle the state for a given day and period index.
  const toggleTimeSlot = (day, periodIndex) => {
    setAvailabilityState(prev => {
      const newState = { ...prev };
      const dayState = newState[day] ? { ...newState[day] } : {};
      if (dayState[periodIndex] === activeMode) {
        // If cell is already set to active mode, remove it.
        delete dayState[periodIndex];
      } else {
        // Otherwise, set cell to active mode.
        dayState[periodIndex] = activeMode;
      }
      newState[day] = dayState;
      return newState;
    });
  };

  // Convert internal availabilityState into final JSON format:
  // { mandatory: { day: [time, ...], ... }, preferable: { day: [time, ...], ... } }
  const convertAvailability = () => {
    const result = { mandatory: {}, preferable: {} };
    if (!timetableConfig || !timetableConfig.generated_periods) return result;
    
    // Then populate the times
    for (const [day, periodsObj] of Object.entries(availabilityState)) {
      for (const [periodIndexStr, cellMode] of Object.entries(periodsObj)) {
        const periodIndex = parseInt(periodIndexStr, 10);
        const dayPeriods = timetableConfig.generated_periods[day] || [];
        const time = dayPeriods[periodIndex];
        if (time) {
          if (!result[cellMode][day]) {
            result[cellMode][day] = [];
          }
          result[cellMode][day].push(time);
        }
      }
    }

    return result;
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen bg-gray-900 text-gray-100 font-sans">
        <div className="flex-1 p-8 max-w-7xl mx-auto">
          <div className="flex justify-center items-center h-full">
            <div className="text-center text-purple-400 italic">
              <i className="fas fa-spinner fa-spin text-4xl mb-4"></i>
              <p>Loading...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gray-900 text-gray-100 font-sans">
      <div className="flex-1 p-8 max-w-7xl mx-auto">
        <h2 className="text-3xl text-gray-50 mb-8">
          {id ? "Edit Teacher" : "Add New Teacher"}
        </h2>

        {error && (
          <div className="bg-red-900/50 text-red-200 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-8">
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-xl text-purple-400 mb-4">Basic Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-gray-400 text-sm mb-2">Name*</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                  required
                />
              </div>
              <div>
                <label className="block text-gray-400 text-sm mb-2">Email*</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                  required
                />
              </div>
              <div>
                <label className="block text-gray-400 text-sm mb-2">Max Lessons per Day*</label>
                <input
                  type="number"
                  value={maxLessons}
                  onChange={(e) => setMaxLessons(Math.max(1, parseInt(e.target.value) || 1))}
                  min="1"
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                  required
                />
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-xl text-purple-400 mb-4">Assigned Subjects</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {allSubjects.map((subject) => (
                <div
                  key={subject.id}
                  onClick={() => handleSubjectChange(subject.id)}
                  className={`p-4 text-center rounded-lg border cursor-pointer transition-colors ${
                    subjects.includes(subject.id)
                      ? "bg-purple-600 text-white border-purple-500"
                      : "bg-gray-900 border-gray-700 hover:border-purple-500"
                  }`}
                >
                  {subject.name}
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-xl text-purple-400 mb-4">Availability</h3>
            
            <div className="flex gap-4 mb-6">
              <button
                type="button"
                onClick={() => setActiveMode("preferable")}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  activeMode === "preferable"
                    ? "bg-purple-600 text-white"
                    : "bg-gray-900 text-gray-400 hover:text-purple-400"
                }`}
              >
                Preferable
              </button>
              <button
                type="button"
                onClick={() => setActiveMode("mandatory")}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  activeMode === "mandatory"
                    ? "bg-purple-600 text-white"
                    : "bg-gray-900 text-gray-400 hover:text-purple-400"
                }`}
              >
                Mandatory
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="bg-gray-900">
                    <th className="px-4 py-3 text-left border border-gray-700">Time</th>
                    {timetableConfig?.days.map((day) => (
                      <th key={day} className="px-4 py-3 text-left border border-gray-700">
                        {day}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {timetableConfig?.generated_periods[timetableConfig?.days[0]]?.map((period, periodIndex) => (
                    <tr key={periodIndex} className="hover:bg-gray-700/50">
                      <td className="px-4 py-3 border border-gray-700">{period}</td>
                      {timetableConfig.days.map((day) => (
                        <td
                          key={day}
                          className="px-4 py-3 border border-gray-700 cursor-pointer"
                          onClick={() => toggleTimeSlot(day, periodIndex)}
                        >
                          <div
                            className={`w-6 h-6 rounded-full ${
                              availabilityState[day]?.[periodIndex] === activeMode
                                ? "bg-purple-600"
                                : "bg-gray-700"
                            }`}
                          ></div>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="flex justify-between">
            <button
              type="button"
              onClick={() => router.push("/components/TeachersConfig")}
              className="px-6 py-3 border border-gray-700 text-gray-400 rounded-lg hover:border-purple-500 hover:text-purple-400 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={teacherLoading}
            >
              {teacherLoading ? "Saving..." : id ? "Update Teacher" : "Add Teacher"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddTeacher;


