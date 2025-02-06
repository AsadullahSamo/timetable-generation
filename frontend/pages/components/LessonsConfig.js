import { useState, useEffect } from 'react';
import styles from './LessonsConfig.module.css';
import { FaArrowUp, FaArrowDown } from 'react-icons/fa';
import Navbar from './Navbar';
import Head from 'next/head';
import Link from 'next/link';

const LessonsConfig = () => {
  const [lessons, setLessons] = useState([]);
  const [editingIndex, setEditingIndex] = useState(-1);
  const [formData, setFormData] = useState({
    teacher: '',
    subject: '',
    classes: [],
    building: 'School',
    lessonsPerWeek: 9,
    importance: 'Normal',
    division: 'Whole class',
    minDays: '',
    maxDays: '',
    maxLessonsPerDay: '',
    rooms: ['Default'],
    twoWeeks: false,
    roomSelection: 'default'
  });

  const [page, setPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    const savedLessons = JSON.parse(localStorage.getItem('lessons')) || [];
    // Ensure classes and rooms are arrays
    const formattedLessons = savedLessons.map(lesson => ({
      ...lesson,
      classes: Array.isArray(lesson.classes) ? lesson.classes : [lesson.classes],
      rooms: Array.isArray(lesson.rooms) ? lesson.rooms : [lesson.rooms]
    }));
    setLessons(formattedLessons);
  }, []);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleRoomSelection = (type) => {
    setFormData(prev => ({
      ...prev,
      roomSelection: type,
      rooms: type === 'default' ? ['Default'] : []
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const newLessons = [...lessons];
    
    if (editingIndex > -1) {
      newLessons[editingIndex] = formData;
    } else {
      newLessons.push(formData);
    }
    
    localStorage.setItem('lessons', JSON.stringify(newLessons));
    setLessons(newLessons);
    setEditingIndex(-1);
    setFormData({
      teacher: '',
      subject: '',
      classes: [],
      building: 'School',
      lessonsPerWeek: 9,
      importance: 'Normal',
      division: 'Whole class',
      minDays: '',
      maxDays: '',
      maxLessonsPerDay: '',
      rooms: ['Default'],
      twoWeeks: false,
      roomSelection: 'default'
    });
  };

  const handleEdit = (index) => {
    setFormData(lessons[index]);
    setEditingIndex(index);
  };

  const handleDelete = (index) => {
    const newLessons = lessons.filter((_, i) => i !== index);
    localStorage.setItem('lessons', JSON.stringify(newLessons));
    setLessons(newLessons);
  };

  const getImportanceIcon = (importance) => {
    switch (importance) {
      case 'Very Important':
        return <><i style={{margin: 'auto'}} className="fas fa-angle-double-up"></i></>;
      case 'Important':
        return <FaArrowUp />;
      case 'Less Important':
        return <FaArrowDown style={{ color: '#ef4444' }} />;
      default:
        return null;
    }
  };

  return (
    <>
      <Head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" />
      </Head>

    <div className={styles.container}>
      
      <Navbar number={6} />

      <div className={styles.mainContent}>
        <h1 className={styles.mainHeading}>Lessons Configuration</h1>
        
        <div className={styles.section}>
          <h2 className={styles.sectionHeading}>
            {editingIndex > -1 ? 'Edit Lesson' : 'Add New Lesson'}
          </h2>
          
          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.formGrid}>
              <div className={styles.formGroup}>
                <label className={styles.label}>Teacher*</label>
                <input
                  type="text"
                  name="teacher"
                  value={formData.teacher}
                  onChange={handleInputChange}
                  className={styles.input}
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Subject*</label>
                <input
                  type="text"
                  name="subject"
                  value={formData.subject}
                  onChange={handleInputChange}
                  className={styles.input}
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Classes*</label>
                <input
                  type="text"
                  name="classes"
                  value={formData.classes.join(', ')}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    classes: e.target.value.split(',').map(c => c.trim())
                  }))}
                  className={styles.input}
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Building*</label>
                <select
                  name="building"
                  value={formData.building}
                  onChange={handleInputChange}
                  className={styles.input}
                >
                  <option value="School">School</option>
                  <option value="Online">Online</option>
                </select>
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Lessons/Week*</label>
                <input
                  type="number"
                  name="lessonsPerWeek"
                  value={formData.lessonsPerWeek}
                  onChange={handleInputChange}
                  className={styles.input}
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Importance*</label>
                <select
                  name="importance"
                  value={formData.importance}
                  onChange={handleInputChange}
                  className={styles.input}
                >
                  <option value="Very Important">Very Important</option>
                  <option value="Important">Important</option>
                  <option value="Less Important">Less Important</option>
                </select>
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Min. Days/Week</label>
                <input
                  type="number"
                  name="minDays"
                  value={formData.minDays}
                  onChange={handleInputChange}
                  className={styles.input}
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Max. Days/Week</label>
                <input
                  type="number"
                  name="maxDays"
                  value={formData.maxDays}
                  onChange={handleInputChange}
                  className={styles.input}
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Max. Lessons/Day</label>
                <input
                  type="number"
                  name="maxLessonsPerDay"
                  value={formData.maxLessonsPerDay}
                  onChange={handleInputChange}
                  className={styles.input}
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Room Configuration</label>
                <div className={styles.radioGroup}>
                  <label className={styles.radioLabel}>
                    <input
                      type="radio"
                      name="roomSelection"
                      checked={formData.roomSelection === 'default'}
                      onChange={() => handleRoomSelection('default')}
                    />
                    Use Default Rooms
                  </label>
                  <label className={styles.radioLabel}>
                    <input
                      type="radio"
                      name="roomSelection"
                      checked={formData.roomSelection === 'custom'}
                      onChange={() => handleRoomSelection('custom')}
                    />
                    Custom Rooms
                  </label>
                </div>
                
                {formData.roomSelection === 'custom' && (
                  <input
                    type="text"
                    value={formData.rooms.join(', ')}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      rooms: e.target.value.split(',').map(r => r.trim())
                    }))}
                    className={styles.input}
                    placeholder="Enter rooms (comma separated)"
                  />
                )}
              </div>

              <div className={styles.formGroup}>
                <label className={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    name="twoWeeks"
                    checked={formData.twoWeeks}
                    onChange={handleInputChange}
                  />
                  Once every two weeks
                </label>
              </div>
            </div>

            <div className={styles.buttonGroup}>
              <button
                type="button"
                className={styles.secondaryButton}
                onClick={() => {
                  setEditingIndex(-1);
                  setFormData({
                    teacher: '',
                    subject: '',
                    classes: [],
                    building: 'School',
                    lessonsPerWeek: 9,
                    importance: 'Normal',
                    division: 'Whole class',
                    minDays: '',
                    maxDays: '',
                    maxLessonsPerDay: '',
                    rooms: ['Default'],
                    twoWeeks: false,
                    roomSelection: 'default'
                  });
                }}
              >
                Cancel
              </button>
              <button type="submit" className={styles.primaryButton}>
                {editingIndex > -1 ? 'Update Lesson' : 'Add Lesson'}
              </button>
            </div>
          </form>
        </div>

        <div className={styles.section}>
          <h2 className={styles.sectionHeading}>Existing Lessons</h2>
          
          <div className={styles.tableContainer}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Teacher</th>
                  <th>Subject</th>
                  <th>Classes</th>
                  <th>Building</th>
                  <th>Lessons/Week</th>
                  <th>Importance</th>
                  <th>Rooms</th>
                  <th>Two Weeks</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {lessons
                  .slice((page - 1) * itemsPerPage, page * itemsPerPage)
                  .map((lesson, index) => (
                    <tr key={index}>
                      <td style={{textAlign: 'center'}}>{lesson.teacher}</td>
                      <td style={{textAlign: 'center'}}>{lesson.subject}</td>
                      <td style={{textAlign: 'center'}}>{Array.isArray(lesson.classes) ? lesson.classes.join(', ') : lesson.classes}</td>
                      <td>{lesson.building}</td>
                      <td style={{textAlign: 'center'}}>{lesson.lessonsPerWeek}</td>
                      <td style={{ textAlign: 'center' }}>
                        {getImportanceIcon(lesson.importance)}
                      </td>
                      <td>{Array.isArray(lesson.rooms) ? lesson.rooms.join(', ') : lesson.rooms}</td>
                      <td style={{textAlign: 'center'}}>{lesson.twoWeeks ? '✓' : '✗'}</td>
                      <td>
                        <button
                          onClick={() => handleEdit(index)}
                          className={styles.iconButton}
                        >
                          <i className="fas fa-edit"></i>
                        </button>
                        <button
                          onClick={() => handleDelete(index)}
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

          <div className={styles.pagination}>
            <Link
              href="/components/TeachersConfig"
              className={styles.primaryButton}
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Previous
            </Link>
            <span>Page {page} of {Math.ceil(lessons.length / itemsPerPage)}</span>
            <Link
              href="/components/Constraints"
              className={styles.primaryButton}
              onClick={() => setPage(p => 
                Math.min(p + 1, Math.ceil(lessons.length / itemsPerPage))
              )}
              disabled={page === Math.ceil(lessons.length / itemsPerPage)}
            >
              Next
            </Link>
          </div>
        </div>
      </div>
    </div>
    </>
  );
};

export default LessonsConfig;