import { useState, useEffect } from 'react';
import { FaArrowUp, FaArrowDown } from 'react-icons/fa';
import Navbar from './Navbar';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { 
    X,
  BookOpen, 
  Building2, 
  Clock, 
  Users, 
  ArrowLeft, 
  ArrowRight, 
  Info, 
  AlertCircle,
  Plus,
  Edit2,
  Trash2,
  CheckCircle2,
  Calendar,
  Filter,
  ChevronDown,
  Check
} from 'lucide-react';

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
    roomSelection: 'default'
  });

  const [page, setPage] = useState(1);
  const itemsPerPage = 10;
  const [showTooltip, setShowTooltip] = useState("");
  const [error, setError] = useState("");

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
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'Important':
        return <CheckCircle2 className="h-4 w-4 text-blue-500" />;
      case 'Less Important':
        return <CheckCircle2 className="h-4 w-4 text-yellow-500" />;
      default:
        return null;
    }
  };

  return (
    <>
      <Head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" />
      </Head>

      <div className="flex min-h-screen bg-background text-primary font-sans">
        <Navbar number={5} />
        <div className="flex-1 p-8 max-w-[60rem] mx-auto">
          <div className="mb-8">
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-2">
              Lessons Configuration
            </h1>
            <p className="text-secondary/90">Configure lessons, their schedules, and room assignments</p>
          </div>

          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl mb-6 flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <p className="text-red-500 text-sm font-medium">{error}</p>
            </div>
          )}

          <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-primary flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-accent-cyan" />
                {editingIndex > -1 ? 'Edit Lesson' : 'Add New Lesson'}
              </h2>
              <div className="relative">
                <button
                  type="button"
                  className="text-secondary hover:text-primary transition-colors"
                  onMouseEnter={() => setShowTooltip("form")}
                  onMouseLeave={() => setShowTooltip("")}
                >
                  <Info className="h-5 w-5" />
                </button>
                {showTooltip === "form" && (
                  <div className="absolute right-0 top-full mt-2 p-3 bg-surface border border-border rounded-xl shadow-lg text-sm text-secondary w-64 z-50">
                    Fill in the lesson details. Required fields are marked with an asterisk (*).
                  </div>
                )}
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-secondary">Teacher*</label>
                  <div className="relative">
                    <Users className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                    <input
                      type="text"
                      name="teacher"
                      value={formData.teacher}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-secondary">Subject*</label>
                  <div className="relative">
                    <BookOpen className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                    <input
                      type="text"
                      name="subject"
                      value={formData.subject}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-secondary">Classes*</label>
                  <div className="relative">
                    <Users className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                    <input
                      type="text"
                      name="classes"
                      value={formData.classes.join(', ')}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        classes: e.target.value.split(',').map(c => c.trim())
                      }))}
                      className="w-full pl-10 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-secondary">Building*</label>
                  <div className="relative">
                    <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                    <select
                      name="building"
                      value={formData.building}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-10 py-3 bg-background/95 border border-border rounded-xl text-primary focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30 appearance-none"
                    >
                      <option value="School">School</option>
                      <option value="Online">Online</option>
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70 pointer-events-none" />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-secondary">Lessons per Week*</label>
                  <div className="relative">
                    <Clock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                    <input
                      type="number"
                      name="lessonsPerWeek"
                      value={formData.lessonsPerWeek}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-secondary">Importance*</label>
                  <div className="relative">
                    <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                    <select
                      name="importance"
                      value={formData.importance}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-10 py-3 bg-background/95 border border-border rounded-xl text-primary focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30 appearance-none"
                    >
                      <option value="Very Important">Very Important</option>
                      <option value="Important">Important</option>
                      <option value="Less Important">Less Important</option>
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70 pointer-events-none" />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-secondary">Min. Days/Week</label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                    <input
                      type="number"
                      name="minDays"
                      value={formData.minDays}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-secondary">Max. Days/Week</label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                    <input
                      type="number"
                      name="maxDays"
                      value={formData.maxDays}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-secondary">Max. Lessons/Day</label>
                  <div className="relative">
                    <Clock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                    <input
                      type="number"
                      name="maxLessonsPerDay"
                      value={formData.maxLessonsPerDay}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                    />
                  </div>
                </div>

                <div className="space-y-2 col-span-1 md:col-span-2 lg:col-span-3">
                  <label className="text-sm font-medium text-secondary">Room Configuration</label>
                  <div className="flex flex-col sm:flex-row gap-4">
                    <label className="flex items-center gap-2 text-gray-400 cursor-pointer group h-[52px] whitespace-nowrap">
                      <div className="relative">
                        <input
                          type="radio"
                          name="roomSelection"
                          checked={formData.roomSelection === 'default'}
                          onChange={() => handleRoomSelection('default')}
                          className="sr-only peer"
                        />
                        <div className="w-5 h-5 border-2 border-border rounded-full peer-checked:border-accent-cyan peer-checked:bg-accent-cyan/10 transition-colors group-hover:border-accent-cyan/50">
                          <div className="absolute inset-0 flex items-center justify-center">
                            <div className="w-2 h-2 bg-accent-cyan rounded-full scale-0 peer-checked:scale-100 transition-transform"></div>
                          </div>
                        </div>
                      </div>
                      Use Default Rooms
                    </label>
                    <label className="flex items-center gap-2 text-gray-400 cursor-pointer group h-[52px] whitespace-nowrap">
                      <div className="relative">
                        <input
                          type="radio"
                          name="roomSelection"
                          checked={formData.roomSelection === 'custom'}
                          onChange={() => handleRoomSelection('custom')}
                          className="sr-only peer"
                        />
                        <div className="w-5 h-5 border-2 border-border rounded-full peer-checked:border-accent-cyan peer-checked:bg-accent-cyan/10 transition-colors group-hover:border-accent-cyan/50">
                          <div className="absolute inset-0 flex items-center justify-center">
                            <div className="w-2 h-2 bg-accent-cyan rounded-full scale-0 peer-checked:scale-100 transition-transform"></div>
                          </div>
                        </div>
                      </div>
                      Custom Rooms
                    </label>
                  </div>
                  
                  {formData.roomSelection === 'custom' && (
                    <div className="relative mt-2">
                      <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                      <input
                        type="text"
                        value={formData.rooms.join(', ')}
                        onChange={(e) => setFormData(prev => ({
                          ...prev,
                          rooms: e.target.value.split(',').map(r => r.trim())
                        }))}
                        className="w-full pl-10 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                        placeholder="Enter rooms (comma separated)"
                      />
                    </div>
                  )}
                </div>
              </div>

              <div className="flex justify-end gap-4">
                <button
                  type="button"
                  className="px-6 py-3 border border-border text-secondary rounded-xl hover:text-primary hover:border-accent-cyan/30 transition-colors flex items-center gap-2"
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
                      roomSelection: 'default'
                    });
                  }}
                >
                  <X className="h-4 w-4" />
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="px-6 py-3 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center gap-2 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300"
                >
                  <Plus className="h-4 w-4" />
                  {editingIndex > -1 ? 'Update Lesson' : 'Add Lesson'}
                </button>
              </div>
            </form>
          </div>

          <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-primary flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-accent-cyan" />
                Existing Lessons
              </h2>
              <div className="relative">
                <button
                  type="button"
                  className="text-secondary hover:text-primary transition-colors"
                  onMouseEnter={() => setShowTooltip("table")}
                  onMouseLeave={() => setShowTooltip("")}
                >
                  <Info className="h-5 w-5" />
                </button>
                {showTooltip === "table" && (
                  <div className="absolute right-0 top-full mt-2 p-3 bg-surface border border-border rounded-xl shadow-lg text-sm text-secondary w-64 z-50">
                    View and manage your configured lessons. Click the edit or delete icons to modify entries.
                  </div>
                )}
              </div>
            </div>
            
            <div className="overflow-x-auto [&::-webkit-scrollbar]:h-2 [&::-webkit-scrollbar-track]:bg-surface/50 [&::-webkit-scrollbar-track]:rounded-full [&::-webkit-scrollbar-thumb]:bg-accent-cyan/30 [&::-webkit-scrollbar-thumb]:rounded-full hover:[&::-webkit-scrollbar-thumb]:bg-accent-cyan/50 [&::-webkit-scrollbar-thumb]:transition-colors [&::-webkit-scrollbar-thumb]:duration-300 [&::-webkit-scrollbar-thumb]:border-2 [&::-webkit-scrollbar-thumb]:border-surface/95">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="bg-surface/95">
                    <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Teacher</th>
                    <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Subject</th>
                    <th className="px-4 py-3 text-left border border-border text-secondary font-medium w-[200px]">Classes</th>
                    <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Building</th>
                    <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Lessons/Week</th>
                    <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Importance</th>
                    <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Rooms</th>
                    <th className="px-4 py-3 text-center border border-border text-secondary font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {lessons
                    .slice((page - 1) * itemsPerPage, page * itemsPerPage)
                    .map((lesson, index) => (
                      <tr key={index} className="hover:bg-surface/80 transition-colors">
                        <td className="px-4 py-3 border border-border">
                          <div className="flex items-center gap-2">
                            <Users className="h-4 w-4 text-accent-cyan" />
                            {lesson.teacher}
                          </div>
                        </td>
                        <td className="px-4 py-3 border border-border">
                          <div className="flex items-center gap-2">
                            <BookOpen className="h-4 w-4 text-secondary/70" />
                            {lesson.subject}
                          </div>
                        </td>
                        <td className="px-4 py-3 border border-border">
                          <div className="flex items-center gap-2">
                            <Users className="h-4 w-4 text-secondary/70" />
                            {Array.isArray(lesson.classes) ? lesson.classes.join(', ') : lesson.classes}
                          </div>
                        </td>
                        <td className="px-4 py-3 border border-border">
                          <div className="flex items-center gap-2">
                            <Building2 className="h-4 w-4 text-secondary/70" />
                            {lesson.building}
                          </div>
                        </td>
                        <td className="px-4 py-3 border border-border">
                          <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4 text-secondary/70" />
                            {lesson.lessonsPerWeek}
                          </div>
                        </td>
                        <td className="px-4 py-3 border border-border">
                          <div className="flex items-center gap-2">
                            {getImportanceIcon(lesson.importance)}
                            {lesson.importance}
                          </div>
                        </td>
                        <td className="px-4 py-3 border border-border">
                          <div className="flex items-center gap-2">
                            <Building2 className="h-4 w-4 text-secondary/70" />
                            {Array.isArray(lesson.rooms) ? lesson.rooms.join(', ') : lesson.rooms}
                          </div>
                        </td>
                        <td className="px-4 py-3 border border-border text-center">
                          <div className="flex items-center justify-center gap-2">
                            <button
                              onClick={() => handleEdit(index)}
                              className="text-secondary hover:text-accent-cyan transition-colors p-2"
                            >
                              <Edit2 className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(index)}
                              className="text-secondary hover:text-red-500 transition-colors p-2"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>

            <div className="flex justify-between items-center mt-4 p-4 bg-surface/95 rounded-xl border border-border">
              <Link
                href="/components/Teachers"
                className="px-6 py-3 border border-border text-secondary rounded-xl hover:text-primary hover:border-accent-cyan/30 transition-colors flex items-center gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Back
              </Link>
              <span className="text-secondary">
                Page {page} of {Math.ceil(lessons.length / itemsPerPage) || 1}
              </span>
              <Link
                href="/components/Constraints"
                className="px-6 py-3 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center gap-2 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300"
              >
                Next
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default LessonsConfig;