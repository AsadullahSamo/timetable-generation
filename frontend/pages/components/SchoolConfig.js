import React, { useState } from "react";
import { useRouter } from "next/router";
import Navbar from "./Navbar";
import Link from "next/link";
import api from "../utils/api";

const SchoolConfig = () => {
  const router = useRouter();
  const [schoolName, setSchoolName] = useState("");
  const [numPeriods, setNumPeriods] = useState(0);
  const [startTime, setStartTime] = useState("08:00");
  const [days] = useState(["Mon", "Tue", "Wed", "Thu", "Fri"]);
  const [lessonDuration, setLessonDuration] = useState(60);
  const [periods, setPeriods] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Time formatting helpers
  const formatTime = (timeString) => {
    const [hours, minutes] = timeString.split(":").map(Number);
    const period = hours >= 12 ? "PM" : "AM";
    const formattedHours = hours % 12 || 12;
    return `${formattedHours}:${String(minutes).padStart(2, "0")} ${period}`;
  };

  const incrementTime = (time, duration) => {
    let [hours, minutes] = time.split(":").map(Number);
    minutes += duration;
    hours += Math.floor(minutes / 60);
    minutes %= 60;
    hours %= 24;
    return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
  };

  const generatePeriods = () => {
    if (!numPeriods || !startTime || !lessonDuration) {
      setError("Please fill all required fields before generating periods.");
      return;
    }

    const newPeriods = {};
    let currentTime = startTime;

    days.forEach(day => {
      newPeriods[day] = [];
      let dayTime = startTime;
      for (let i = 0; i < numPeriods; i++) {
        newPeriods[day].push(formatTime(dayTime));
        dayTime = incrementTime(dayTime, lessonDuration);
      }
    });

    setPeriods(newPeriods);
    setError(null); // Clear any previous errors
  };

  const addPeriod = (day) => {
    const lastPeriod = periods[day][periods[day].length - 1];
    const [time, period] = lastPeriod.split(" ");
    let [hours, minutes] = time.split(":").map(Number);

    if (period === "PM" && hours !== 12) hours += 12;
    if (period === "AM" && hours === 12) hours = 0;

    const newTime = incrementTime(`${hours}:${minutes}`, lessonDuration);

    setPeriods(prev => ({
      ...prev,
      [day]: [...prev[day], formatTime(newTime)]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (Object.keys(periods).length === 0) {
      setError("Please generate periods before saving.");
      setLoading(false);
      return;
    }

    try {
      // Convert startTime to HH:mm:ss format
      const formattedStartTime = `${startTime}:00`;

      const response = await api.post("/api/timetable/configs/", {
        name: schoolName,
        days,
        periods: numPeriods,
        start_time: formattedStartTime,
        lesson_duration: lessonDuration,
        generated_periods: periods
      });

      if (response.status === 201) {
        router.push("/components/ClassesConfig");
      }
    } catch (error) {
      if (error.response) {
        setError(`Error: ${error.response.data.detail || "Failed to save configuration"}`);
      } else if (error.request) {
        setError("No response from server. Please check your connection.");
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
      console.error("Submission error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-900 text-gray-100 font-sans">
      <Navbar number={1} />

      <form onSubmit={handleSubmit} className="flex-1 p-8 max-w-7xl">
        <h2 className="text-3xl text-gray-50 mb-8">School Configuration</h2>

        {error && (
          <div className="bg-red-900/50 text-red-200 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        <section className="bg-gray-800 rounded-lg p-6 mb-8 border border-gray-700">
          <h3 className="text-xl text-purple-400 mb-4">School Name</h3>
          <input
            type="text"
            value={schoolName}
            onChange={(e) => setSchoolName(e.target.value)}
            className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 disabled:opacity-50"
            placeholder="Enter school name"
            required
            disabled={loading}
          />
        </section>

        <section className="bg-gray-800 rounded-lg p-6 mb-8 border border-gray-700">
          <h3 className="text-xl text-purple-400 mb-4">Period Configuration</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <div className="flex flex-col gap-2">
              <label className="text-gray-400 text-sm">Number of Periods</label>
              <input
                type="number"
                value={numPeriods}
                onChange={(e) => setNumPeriods(Number(e.target.value))}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 disabled:opacity-50"
                min="1"
                required
                disabled={loading}
              />
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-gray-400 text-sm">Starting Time</label>
              <input
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 disabled:opacity-50"
                required
                disabled={loading}
              />
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-gray-400 text-sm">Lesson Duration (minutes)</label>
              <input
                type="number"
                value={lessonDuration}
                onChange={(e) => setLessonDuration(Number(e.target.value))}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 disabled:opacity-50"
                min="1"
                required
                disabled={loading}
              />
            </div>

            <div className="flex items-end">
              <button
                type="button"
                onClick={generatePeriods}
                className="w-full px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={loading || !numPeriods || !startTime || !lessonDuration}
              >
                {loading ? "Generating..." : "Generate Periods"}
              </button>
            </div>
          </div>

          {Object.keys(periods).length > 0 && (
            <div className="mt-6">
              <div className="flex gap-4">
                {days.map((day) => (
                  <div key={day} className="flex-1 bg-gray-900 rounded-lg p-4 border border-gray-700">
                    <div className="text-purple-400 font-semibold mb-4">{day}</div>
                    {periods[day].map((time, i) => (
                      <div
                        key={i}
                        className="px-3 py-2 mb-2 bg-gray-800 rounded text-sm"
                      >
                        {time}
                      </div>
                    ))}
                    <button
                      type="button"
                      className="w-full py-2 border-2 border-dashed border-gray-600 text-gray-400 rounded hover:border-purple-500 hover:text-purple-400 transition-colors disabled:opacity-50"
                      onClick={() => addPeriod(day)}
                      disabled={loading}
                    >
                      +
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        <div className="flex justify-between mt-8">
          <Link
            href="/"
            className="px-6 py-3 border border-gray-700 text-gray-400 rounded-lg hover:border-purple-500 hover:text-purple-400 transition-colors"
          >
            ← Back
          </Link>

          <button
            type="submit"
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={loading || Object.keys(periods).length === 0}
          >
            {loading ? "Saving..." : "Save Configuration"}
          </button>

          <Link
            href="/components/ClassesConfig"
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Next →
          </Link>
        </div>
      </form>
    </div>
  );
};

export default SchoolConfig;