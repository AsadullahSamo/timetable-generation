import React, { useState } from "react";
import styles from "./SubjectConfig.module.css";
import Head from "next/head";
import Navbar from "./Navbar";
import Link from "next/link";

const SubjectConfig = () => {
  const [subjects, setSubjects] = useState([]);
  const [subjectData, setSubjectData] = useState({
    subjectName: "",
  });
  const [searchQuery, setSearchQuery] = useState("");
  const [editingIndex, setEditingIndex] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSubjectData({ ...subjectData, [name]: value });
  };

  const handleAddOrUpdateSubject = () => {
    if (subjectData.subjectName.trim() === "") {
      console.error("Please enter a subject name.");
      return;
    }

    if (editingIndex !== null) {
      const updatedSubjects = [...subjects];
      updatedSubjects[editingIndex] = subjectData.subjectName;
      setSubjects(updatedSubjects);
      setEditingIndex(null);
    } else {
      setSubjects([...subjects, subjectData.subjectName]);
    }

    setSubjectData({ subjectName: "" });
  };

  const handleDeleteSubject = (index) => {
    setSubjects(subjects.filter((_, i) => i !== index));
  };

  const handleEditSubject = (index) => {
    setSubjectData({ subjectName: subjects[index] });
    setEditingIndex(index);
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const filteredSubjects = subjects.filter((subject) =>
    subject.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <>
      <Head>
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
        />
      </Head>

      <div className={styles.container}>
        <Navbar number={4} />

        <div className={styles.mainContent}>
          <h2 className={styles.mainHeading}>Subject Configuration</h2>

          <div className={styles.searchBox}>
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder="Search Subject Name"
              className={styles.inputSearch}
            />
            <button className={styles.btnSearch}>
              <i className="fas fa-search"></i>
            </button>
          </div>

          <div className={styles.inputContainer}>
            <input
              type="text"
              name="subjectName"
              value={subjectData.subjectName}
              onChange={handleInputChange}
              placeholder="Enter Subject Name"
              className={styles.input}
            />
            <button onClick={handleAddOrUpdateSubject} className={styles.primaryButton}>
              {editingIndex !== null ? "Update Subject" : "Add Subject"}
            </button>
          </div>

          <div className={styles.outputContainer}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Subject Name</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredSubjects.map((subject, index) => (
                  <tr key={index}>
                    <td>{subject}</td>
                    <td>
                      <button
                        onClick={() => handleEditSubject(index)}
                        className={styles.iconButton}
                      >
                        <i className="fas fa-edit"></i>
                      </button>
                      <button
                        onClick={() => handleDeleteSubject(index)}
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

          <div className={styles.navigation}>
            <Link href="/components/ClassesConfig" className={styles.primaryButton}>
              ← Back
            </Link>
            <Link href="/components/TeachersConfig" type="submit" className={styles.primaryButton}>
              Next →
            </Link>
          </div>


        </div>
      </div>
    </>
  );
};

export default SubjectConfig;