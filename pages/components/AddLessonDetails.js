import React, { useState, useEffect } from "react";
import styles from "./AddLessonDetails.module.css";
import Head from "next/head";
import { useRouter } from "next/router";

const AddLessonDetails = () => {
  const router = useRouter();
  const { lesson, index } = router.query; 

  const [formData, setFormData] = useState({
    teacher: "",
    subject: "",
    classes: "",
    lessonsPerWeek: "",
    importance: "Very Important",
    minDaysPerWeek: "",
    maxDaysPerWeek: "",
    maxLessonsPerDay: "",
    rooms: "",
  });

  useEffect(() => {
    if (lesson) {
      const parsedLesson = JSON.parse(lesson);
      setFormData(parsedLesson);
    }
  }, [lesson]);

  const handleSubmit = () => {
    let savedLessons = JSON.parse(localStorage.getItem("lessons")) || [];
    if (index !== undefined) {
      savedLessons[index] = formData;
    } else {
      savedLessons.push(formData);
    }

    localStorage.setItem("lessons", JSON.stringify(savedLessons));
    window.alert("Configuration Saved!");
    router.push("/components/SavedLessons");
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
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
        <h2 className={styles.heading}>{index !== undefined ? "Edit Lesson" : "Add Lesson"}</h2>
        <div className={styles.form}>
          <div className={styles.row}>
            <select
              name="teacher"
              value={formData.teacher}
              onChange={handleInputChange}
              className={styles.inputField}
            >
              <option value="" disabled>
                Select Teacher*
              </option>
              <option value="Teacher1">Teacher 1</option>
              <option value="Teacher2">Teacher 2</option>
            </select>
            <select
              name="subject"
              value={formData.subject}
              onChange={handleInputChange}
              className={styles.inputField}
            >
              <option value="" disabled>
                Select Subject*
              </option>
              <option value="Math">Math</option>
              <option value="Science">Science</option>
            </select>
          </div>

          <div className={styles.row}>
            <select
              name="classes"
              value={formData.classes}
              onChange={handleInputChange}
              className={styles.inputField}
            >
              <option value="" disabled>
                Select Class/Classes*
              </option>
              <option value="5A">5A</option>
              <option value="5B">5B</option>
              <option value="6A">6A</option>
              <option value="6B">6B</option>
            </select>
          </div>

          <div className={styles.row}>
            <input
              type="number"
              name="lessonsPerWeek"
              value={formData.lessonsPerWeek}
              onChange={handleInputChange}
              placeholder="Lessons/week*"
              className={styles.inputField}
            />
          </div>

          <div className={styles.row}>
            <select
              name="importance"
              value={formData.importance}
              onChange={handleInputChange}
              className={styles.inputField}
            >
              <option value="Very Important">Very Important</option>
              <option value="Important">Important</option>
              <option value="Less Important">Less Important</option>
            </select>
          </div>

          <div className={styles.row}>
            <input
              type="number"
              name="minDaysPerWeek"
              value={formData.minDaysPerWeek}
              onChange={handleInputChange}
              placeholder="Min Days/Week"
              className={styles.inputField}
            />
            <input
              type="number"
              name="maxDaysPerWeek"
              value={formData.maxDaysPerWeek}
              onChange={handleInputChange}
              placeholder="Max Days/Week"
              className={styles.inputField}
            />
          </div>

          <div className={styles.row}>
            <input
              type="number"
              name="maxLessonsPerDay"
              value={formData.maxLessonsPerDay}
              onChange={handleInputChange}
              placeholder="Max lessons/day*"
              className={styles.inputField}
            />
          </div>

          <div className={styles.row}>
            <select
              name="rooms"
              value={formData.rooms}
              onChange={handleInputChange}
              className={styles.inputField}
            >
              <option value="" disabled>
                Select Room*
              </option>
              <option value="Room1">Room 1</option>
              <option value="Room2">Room 2</option>
              <option value="Room3">Room 3</option>
            </select>
          </div>

          <div className={styles.buttonRow}>
            <button className={styles.saveButton} onClick={handleSubmit}>
              {index !== undefined ? "Update" : "Save"}
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default AddLessonDetails;
