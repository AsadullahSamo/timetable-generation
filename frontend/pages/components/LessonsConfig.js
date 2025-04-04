import { useState, useEffect } from 'react';
import { FaArrowUp, FaArrowDown } from 'react-icons/fa';
import Navbar from './Navbar';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';

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
        return <><i className="fas fa-angle-double-up mx-auto"></i></>;
      case 'Important':
        return <FaArrowUp />;
      case 'Less Important':
        return <FaArrowDown className="text-red-500" />;
      default:
        return null;
    }
  };

  return (
    <>
      <Head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" />
      </Head>

      <div className="flex min-h-screen bg-gray-900 text-gray-100 font-sans">
        <Navbar number={5} />
        <div className="flex-1 p-8 max-w-7xl mx-auto">
          <h1 className="text-3xl text-gray-50 mb-8">Lessons Configuration</h1>

          <div className="bg-gray-800 rounded-lg p-6 mb-8 border border-gray-700">
            <h2 className="text-xl text-purple-400 mb-4">
              {editingIndex > -1 ? 'Edit Lesson' : 'Add New Lesson'}
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="flex flex-col gap-2">
                  <label className="text-gray-400 text-sm">Teacher*</label>
                  <input
                    type="text"
                    name="teacher"
                    value={formData.teacher}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                    required
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-gray-400 text-sm">Subject*</label>
                  <input
                    type="text"
                    name="subject"
                    value={formData.subject}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                    required
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-gray-400 text-sm">Classes*</label>
                  <input
                    type="text"
                    name="classes"
                    value={formData.classes.join(', ')}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      classes: e.target.value.split(',').map(c => c.trim())
                    }))}
                    className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                    required
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-gray-400 text-sm">Building*</label>
                  <select
                    name="building"
                    value={formData.building}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                  >
                    <option value="School">School</option>
                    <option value="Online">Online</option>
                  </select>
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-gray-400 text-sm">Lessons per Week*</label>
                  <input
                    type="number"
                    name="lessonsPerWeek"
                    value={formData.lessonsPerWeek}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                    required
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-gray-400 text-sm">Importance*</label>
                  <select
                    name="importance"
                    value={formData.importance}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                  >
                    <option value="Very Important">Very Important</option>
                    <option value="Important">Important</option>
                    <option value="Less Important">Less Important</option>
                  </select>
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-gray-400 text-sm">Min. Days/Week</label>
                  <input
                    type="number"
                    name="minDays"
                    value={formData.minDays}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-gray-400 text-sm">Max. Days/Week</label>
                  <input
                    type="number"
                    name="maxDays"
                    value={formData.maxDays}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-gray-400 text-sm">Max. Lessons/Day</label>
                  <input
                    type="number"
                    name="maxLessonsPerDay"
                    value={formData.maxLessonsPerDay}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-gray-400 text-sm">Room Configuration</label>
                  <div className="flex flex-col gap-2">
                    <label className="flex items-center gap-2 text-gray-400">
                      <input
                        type="radio"
                        name="roomSelection"
                        checked={formData.roomSelection === 'default'}
                        onChange={() => handleRoomSelection('default')}
                        className="text-purple-600 focus:ring-purple-500"
                      />
                      Use Default Rooms
                    </label>
                    <label className="flex items-center gap-2 text-gray-400">
                      <input
                        type="radio"
                        name="roomSelection"
                        checked={formData.roomSelection === 'custom'}
                        onChange={() => handleRoomSelection('custom')}
                        className="text-purple-600 focus:ring-purple-500"
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
                      className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 mt-2"
                      placeholder="Enter rooms (comma separated)"
                    />
                  )}
                </div>

                <div className="flex flex-col gap-2">
                  <label className="flex items-center gap-2 text-gray-400">
                    <input
                      type="checkbox"
                      name="twoWeeks"
                      checked={formData.twoWeeks}
                      onChange={handleInputChange}
                      className="text-purple-600 focus:ring-purple-500 rounded"
                    />
                    Once every two weeks
                  </label>
                </div>
              </div>

              <div className="flex justify-end gap-4">
                <button
                  type="button"
                  className="px-6 py-3 border border-gray-700 text-gray-400 rounded-lg hover:border-purple-500 hover:text-purple-400 transition-colors"
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
                <button 
                  type="submit" 
                  className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  {editingIndex > -1 ? 'Update Lesson' : 'Add Lesson'}
                </button>
              </div>
            </form>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl text-purple-400 mb-4">Existing Lessons</h2>
            
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="bg-gray-900">
                    <th className="px-4 py-3 text-left border border-gray-700">Teacher</th>
                    <th className="px-4 py-3 text-left border border-gray-700">Subject</th>
                    <th className="px-4 py-3 text-left border border-gray-700">Classes</th>
                    <th className="px-4 py-3 text-left border border-gray-700">Building</th>
                    <th className="px-4 py-3 text-left border border-gray-700">Lessons/Week</th>
                    <th className="px-4 py-3 text-left border border-gray-700">Importance</th>
                    <th className="px-4 py-3 text-left border border-gray-700">Rooms</th>
                    <th className="px-4 py-3 text-left border border-gray-700">Two Weeks</th>
                    <th className="px-4 py-3 text-left border border-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {lessons
                    .slice((page - 1) * itemsPerPage, page * itemsPerPage)
                    .map((lesson, index) => (
                      <tr key={index} className="hover:bg-gray-700/50">
                        <td className="px-4 py-3 border border-gray-700 text-center">{lesson.teacher}</td>
                        <td className="px-4 py-3 border border-gray-700 text-center">{lesson.subject}</td>
                        <td className="px-4 py-3 border border-gray-700 text-center">
                          {Array.isArray(lesson.classes) ? lesson.classes.join(', ') : lesson.classes}
                        </td>
                        <td className="px-4 py-3 border border-gray-700 text-center">{lesson.building}</td>
                        <td className="px-4 py-3 border border-gray-700 text-center">{lesson.lessonsPerWeek}</td>
                        <td className="px-4 py-3 border border-gray-700 text-center">
                          {getImportanceIcon(lesson.importance)}
                        </td>
                        <td className="px-4 py-3 border border-gray-700 text-center">
                          {Array.isArray(lesson.rooms) ? lesson.rooms.join(', ') : lesson.rooms}
                        </td>
                        <td className="px-4 py-3 border border-gray-700 text-center">
                          {lesson.twoWeeks ? '✓' : '✗'}
                        </td>
                        <td className="px-4 py-3 border border-gray-700 text-center">
                          <button
                            onClick={() => handleEdit(index)}
                            className="text-gray-400 hover:text-purple-400 transition-colors p-2"
                          >
                            <i className="fas fa-edit"></i>
                          </button>
                          <button
                            onClick={() => handleDelete(index)}
                            className="text-gray-400 hover:text-red-400 transition-colors p-2"
                          >
                            <i className="fas fa-trash"></i>
                          </button>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>

            <div className="flex justify-between items-center mt-4 p-4 bg-gray-800 rounded-lg">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="text-gray-400">
                Page {page} of {Math.ceil(lessons.length / itemsPerPage) || 1}
              </span>
              <Link
                href="/components/Constraints"
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
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