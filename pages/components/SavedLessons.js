import React, { useState, useEffect } from "react";
import styles from "./SavedLessons.module.css";
import { useRouter } from "next/router";
import Head from "next/head";

const SavedLessons = () => {
  const [lessons, setLessons] = useState([]);
  const router = useRouter();

  useEffect(() => {
    const savedLessons = JSON.parse(localStorage.getItem("lessons")) || [];
    setLessons(savedLessons);
  }, []);

  const handleDelete = (index) => {
    const updatedLessons = [...lessons];
    updatedLessons.splice(index, 1);
    setLessons(updatedLessons);
    localStorage.setItem("lessons", JSON.stringify(updatedLessons));
  };

  const handleEdit = (lessonIndex) => {
    const lessonToEdit = lessons[lessonIndex];
    router.push({
      pathname: "/components/AddLessonDetails",
      query: { lesson: JSON.stringify(lessonToEdit), index: lessonIndex },
    });
  };

  const handleAddLesson = () => {
    router.push("/components/AddLessonDetails"); // Navigate to AddLessonDetails page
  };

  return (
    <>
      <Head>
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
        />
      </Head>

      <div className={styles.container}>
        <h1 className={styles.heading}>Saved Lessons</h1>

        {/* Add New Lesson Button */}
        <div className={styles.addLessonButton}>
          <button onClick={handleAddLesson} className={styles.addLessonBtn}>
            <i className="fas fa-plus-circle"></i> Add New Lesson
          </button>
        </div>
        
        <div className={styles.listContainer}>
          {lessons.length === 0 ? (
            <p className={styles.noLessons}>No lessons saved yet.</p>
          ) : (
            lessons.map((lesson, index) => (
              <div key={index} className={styles.lessonCard}>
                <div className={styles.lessonDetails}>
                  <span className={styles.lessonInfo}>
                    Teacher: {lesson.teacher}, Subject: {lesson.subject}
                  </span>
                  <span className={styles.lessonImportance}>
                    Importance: {lesson.importance}
                  </span>
                </div>
                <div className={styles.actionButtons}>
                  <button
                    className={styles.editButton}
                    onClick={() => handleEdit(index)}
                  >
                    <i className="fas fa-pencil-alt"></i>
                  </button>
                  <button
                    className={styles.deleteButton}
                    onClick={() => handleDelete(index)}
                  >
                    <i className="fas fa-trash-alt"></i>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
};

export default SavedLessons;
