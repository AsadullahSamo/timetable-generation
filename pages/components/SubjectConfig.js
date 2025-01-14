import React, { useState } from "react";
import styles from "./SubjectConfig.module.css"; // Assuming this is the .module.css file for styling
import Head from "next/head";

const SubjectConfig = () => {
  const [subjects, setSubjects] = useState([]);
  const [subjectData, setSubjectData] = useState({
    subjectName: "",
  });
  const [editingIndex, setEditingIndex] = useState(null); // Track which subject is being edited

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSubjectData({ ...subjectData, [name]: value });
  };

  const handleAddOrUpdateSubject = () => {
    if (subjectData.subjectName.trim() === "") {
      alert("Please enter a subject name.");
      return;
    }

    if (editingIndex !== null) {
      // Update the subject
      const updatedSubjects = [...subjects];
      updatedSubjects[editingIndex] = subjectData.subjectName;
      setSubjects(updatedSubjects);
      setEditingIndex(null); // Reset editing mode
    } else {
      // Add a new subject
      setSubjects([...subjects, subjectData.subjectName]);
    }

    // Reset the subjectData to clear the input field
    setSubjectData({ subjectName: "" });
  };

  const handleDeleteSubject = (index) => {
    setSubjects(subjects.filter((_, i) => i !== index));
  };

  const handleEditSubject = (index) => {
    setSubjectData({ subjectName: subjects[index] });
    setEditingIndex(index); // Set the index for editing mode
  };

  return (
    <>
    <Head>
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" />
    </Head>

    <div className={styles.subjectConfigContainer}>
      <h2 className={styles.header}>Subject Configuration</h2>
      {/* Input Section */}
      <div className={styles.inputContainer}>
        <label className={styles.label}>
          Subject Name:
          <input
            type="text"
            name="subjectName"
            value={subjectData.subjectName}
            onChange={handleInputChange}
            placeholder="Enter Subject Name"
            className={styles.input}
          />
        </label>
        <button onClick={handleAddOrUpdateSubject} className={styles.addButton}>
          {editingIndex !== null ? "Update Subject" : "Add Subject"}
        </button>
      </div>

      {/* Output Section */}
      <div className={styles.outputContainer}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Subject Name</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {subjects.map((subject, index) => (
              <tr key={index}>
                <td>{subject}</td>
                <td>
                  <button
                    onClick={() => handleEditSubject(index)}
                    className={styles.iconButton}
                  >
                    <i className="fas fa-edit"></i> {/* Edit Icon */}
                  </button>
                  <button
                    onClick={() => handleDeleteSubject(index)}
                    className={styles.iconButton}
                  >
                    <i className="fas fa-trash"></i> {/* Trash Icon */}
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

export default SubjectConfig;
