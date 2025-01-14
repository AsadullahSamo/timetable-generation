import React, { useState } from "react";
import styles from "./ClassesConfig.module.css"; 
import Head from "next/head";

const ClassesConfig = () => {
  const [configurations, setConfigurations] = useState([]);
  const [classData, setClassData] = useState({
    startTime: "08:00 AM",
    endTime: "01:00 PM",
    latestStartTime: "08:00 AM",
    minLessons: 0,
    maxLessons: 5,
    classes: [],
  });
  const [editingIndex, setEditingIndex] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setClassData({ ...classData, [name]: value });
  };

  const handleAddOrUpdateConfiguration = () => {
    if (classData.classes.length === 0) {
      alert("Please select at least one class.");
      return;
    }

    if (editingIndex !== null) {      
      const updatedConfigurations = [...configurations];
      updatedConfigurations[editingIndex] = { ...classData };
      setConfigurations(updatedConfigurations);
      setEditingIndex(null); 
    } else {
      setConfigurations([...configurations, { ...classData }]);
    }

    setClassData({
      startTime: "08:00 AM",
      endTime: "01:00 PM",
      latestStartTime: "08:00 AM",
      minLessons: 0,
      maxLessons: 5,
      classes: [],
    });
  };

  const handleEditConfiguration = (index) => {
    const configToEdit = configurations[index];
    setClassData(configToEdit);
    setEditingIndex(index);
  };

  const handleDeleteConfiguration = (index) => {
    setConfigurations(configurations.filter((_, i) => i !== index));
  };

  return (
    <>
      <Head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" />
      </Head>

      <div className={styles.classesConfigContainer}>
        <h2 className={styles.header}>Classes</h2>
        <div className={styles.inputContainer}>
          <label className={styles.label}>
            Starting hour:
            <input
              type="time"
              name="startTime"
              value={classData.startTime}
              onChange={handleInputChange}
              className={styles.input}
            />
          </label>
          <label className={styles.label}>
            Ending hour:
            <input
              type="time"
              name="endTime"
              value={classData.endTime}
              onChange={handleInputChange}
              className={styles.input}
            />
          </label>
          <label className={styles.label}>
            Latest start time:
            <input
              type="time"
              name="latestStartTime"
              value={classData.latestStartTime}
              onChange={handleInputChange}
              className={styles.input}
            />
          </label>
          <label className={styles.label}>
            Min. number of lessons/day:
            <input
              type="number"
              name="minLessons"
              value={classData.minLessons}
              onChange={handleInputChange}
              className={styles.input}
            />
          </label>
          <label className={styles.label}>
            Max. number of lessons/day:
            <input
              type="number"
              name="maxLessons"
              value={classData.maxLessons}
              onChange={handleInputChange}
              className={styles.input}
            />
          </label>
          <label className={styles.label}>
            Classes:
            <input
              type="text"
              name="classes"
              placeholder="Enter classes (e.g., A, B, C)"
              value={classData.classes.join(", ")}
              onChange={(e) =>
                setClassData({
                  ...classData,
                  classes: e.target.value.split(",").map((c) => c.trim()),
                })
              }
              className={styles.input}
            />
          </label>
          <button onClick={handleAddOrUpdateConfiguration} className={styles.addButton}>
            {editingIndex !== null ? "Update Configuration" : "Add Configuration"}
          </button>
        </div>

        <div className={styles.outputContainer}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Classes</th>
                <th>Start Time</th>
                <th>Ending Time</th>
                <th>Latest Start Time</th>
                <th>Min. Lessons/Day</th>
                <th>Max. Lessons/Day</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {configurations.map((config, index) => (
                <tr key={index}>
                  <td>{config.classes.join(", ")}</td>
                  <td>{config.startTime}</td>
                  <td>{config.endTime}</td>
                  <td>{config.latestStartTime}</td>
                  <td>{config.minLessons}</td>
                  <td>{config.maxLessons}</td>
                  <td>
                    <button
                      onClick={() => handleEditConfiguration(index)}
                      className={styles.iconButton}
                    >
                      <i className="fas fa-edit"></i>
                    </button>
                    <button
                      onClick={() => handleDeleteConfiguration(index)}
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
    </>
  );
};

export default ClassesConfig;
