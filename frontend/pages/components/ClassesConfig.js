import React, { useState, useEffect } from "react";
import styles from "./ClassesConfig.module.css";
import Head from "next/head";
import Navbar from "./Navbar";
import Link from "next/link";
import api from "../utils/api";

const ClassesConfig = () => {
  const [configurations, setConfigurations] = useState([]);
  const [classData, setClassData] = useState({
    start_time: "08:00",
    end_time: "13:00",
    latest_start_time: "08:00",
    min_lessons: 0,
    max_lessons: 5,
    class_groups: []
  });
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchConfigurations = async () => {
      try {
        const response = await api.get('/timetable/class-groups/');
        setConfigurations(response.data);
      } catch (error) {
        setError('Failed to load configurations');
      }
    };
    fetchConfigurations();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setClassData(prev => ({
      ...prev,
      [name]: name.endsWith('_lessons') ? Number(value) : value
    }));
  };

  const handleAddOrUpdateConfiguration = async () => {
    if (classData.class_groups.length === 0) {
      alert("Please select at least one class.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload = {
        ...classData,
        start_time: `${classData.start_time}:00`,
        end_time: `${classData.end_time}:00`,
        latest_start_time: `${classData.latest_start_time}:00`
      };

      let response;
      if (editingId) {
        response = await api.put(`/timetable/class-groups/${editingId}/`, payload);
        setConfigurations(configurations.map(config => 
          config.id === editingId ? response.data : config
        ));
      } else {
        response = await api.post('/timetable/class-groups/', payload);
        setConfigurations([...configurations, response.data]);
      }

      setClassData({
        start_time: "08:00",
        end_time: "13:00",
        latest_start_time: "08:00",
        min_lessons: 0,
        max_lessons: 5,
        class_groups: []
      });
      setEditingId(null);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to save configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleEditConfiguration = (id) => {
    const configToEdit = configurations.find(config => config.id === id);
    setClassData({
      ...configToEdit,
      start_time: configToEdit.start_time.slice(0, 5),
      end_time: configToEdit.end_time.slice(0, 5),
      latest_start_time: configToEdit.latest_start_time.slice(0, 5)
    });
    setEditingId(id);
  };

  const handleDeleteConfiguration = async (id) => {
    try {
      await api.delete(`/timetable/class-groups/${id}/`);
      setConfigurations(configurations.filter(config => config.id !== id));
    } catch (error) {
      setError('Failed to delete configuration');
    }
  };

  return (
    <>
      <Head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" />
      </Head>

      <div className={styles.container}>
        <Navbar number={2}/>

        <div className={styles.mainContent}>
          <h1 className={styles.mainHeading}>Classes Configuration</h1>
          
          {error && <div className={styles.error}>{error}</div>}

          <div className={styles.section}>
            <h2 className={styles.sectionHeading}>Class Settings</h2>
            <div className={styles.periodControls}>
              {/* Time Inputs */}
              <div className={styles.controlGroup}>
                <label className={styles.label}>Starting hour:</label>
                <input
                  type="time"
                  name="start_time"
                  value={classData.start_time}
                  onChange={handleInputChange}
                  className={styles.input}
                  required
                />
              </div>

              <div className={styles.controlGroup}>
                <label className={styles.label}>Ending hour:</label>
                <input
                  type="time"
                  name="end_time"
                  value={classData.end_time}
                  onChange={handleInputChange}
                  className={styles.input}
                  required
                />
              </div>

              <div className={styles.controlGroup}>
                <label className={styles.label}>Latest start time:</label>
                <input
                  type="time"
                  name="latest_start_time"
                  value={classData.latest_start_time}
                  onChange={handleInputChange}
                  className={styles.input}
                  required
                />
              </div>

              {/* Lessons Inputs */}
              <div className={styles.controlGroup}>
                <label className={styles.label}>Min. lessons/day:</label>
                <input
                  type="number"
                  name="min_lessons"
                  value={classData.min_lessons}
                  onChange={handleInputChange}
                  className={styles.input}
                  min="0"
                  required
                />
              </div>

              <div className={styles.controlGroup}>
                <label className={styles.label}>Max. lessons/day:</label>
                <input
                  type="number"
                  name="max_lessons"
                  value={classData.max_lessons}
                  onChange={handleInputChange}
                  className={styles.input}
                  min="1"
                  required
                />
              </div>

              {/* Class Groups */}
              <div className={styles.controlGroup}>
                <label className={styles.label}>Class Groups:</label>
                <input
                  type="text"
                  name="class_groups"
                  placeholder="Enter classes (e.g., A, B, C)"
                  value={classData.class_groups.join(", ")}
                  onChange={(e) =>
                    setClassData({
                      ...classData,
                      class_groups: e.target.value.split(",").map(c => c.trim())
                    })
                  }
                  className={styles.input}
                  required
                />
              </div>
            </div>

            <button 
              onClick={handleAddOrUpdateConfiguration}
              className={styles.primaryButton}
              disabled={loading}
            >
              {loading ? "Saving..." : editingId ? "Update" : "Add"} Configuration
            </button>
          </div>

          {/* Configured Classes Table */}
          <div className={styles.section}>
            <h2 className={styles.sectionHeading}>Configured Classes</h2>
            <div className={styles.gridContainer}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>Classes</th>
                    <th>Start Time</th>
                    <th>End Time</th>
                    <th>Latest Start</th>
                    <th>Min Lessons</th>
                    <th>Max Lessons</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {configurations.map((config) => (
                    <tr key={config.id}>
                      <td>{config.class_groups.join(", ")}</td>
                      <td>{config.start_time.slice(0, 5)}</td>
                      <td>{config.end_time.slice(0, 5)}</td>
                      <td>{config.latest_start_time.slice(0, 5)}</td>
                      <td>{config.min_lessons}</td>
                      <td>{config.max_lessons}</td>
                      <td>
                        <button
                          onClick={() => handleEditConfiguration(config.id)}
                          className={styles.iconButton}
                        >
                          <i className="fas fa-edit"></i>
                        </button>
                        <button
                          onClick={() => handleDeleteConfiguration(config.id)}
                          className={styles.iconButton}
                        >
                          <i className="fas fa-trash"></i>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className={styles.navigation}>
            <Link href="/components/SchoolConfig" className={styles.primaryButton}>
              ← Back
            </Link>
            <Link href="/components/SubjectConfig" className={styles.primaryButton}>
              Next →
            </Link>
          </div>
        </div>
      </div>
    </>
  );
};

export default ClassesConfig;