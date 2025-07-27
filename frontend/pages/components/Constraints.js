import { useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import Navbar from './Navbar';
import api from "../utils/api";
import { 
  Sliders, 
  ArrowLeft, 
  ArrowRight, 
  Info, 
  AlertCircle, 
  Loader2,
  CheckCircle2,
  XCircle,
  ChevronDown,
  Filter,
  Clock,
  Calendar,
  Users,
  Building2,
  CalendarClock,
  BookOpen,
  Check,
  AlertTriangle,
  GraduationCap,
  Briefcase,
  Timer,
  CalendarDays
} from 'lucide-react';

const Constraints = () => {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [constraints, setConstraints] = useState([
    // Credit Hour Rules
    { 
      id: 1, 
      name: '3 Credit Theory Subjects', 
      importance: 'Very Important', 
      active: true, 
      description: '4-5 classes per week for 3 credit theory subjects',
      category: 'credit'
    },
    { 
      id: 2, 
      name: '2 Credit Theory Subjects', 
      importance: 'Very Important', 
      active: true, 
      description: '3-4 classes per week for 2 credit theory subjects',
      category: 'credit'
    },
    { 
      id: 3, 
      name: '1 Credit Practical Subjects', 
      importance: 'Very Important', 
      active: true, 
      description: 'One 3-hour practical per week for 1 credit practical subjects',
      category: 'credit'
    },
    { 
      id: 4, 
      name: '2 Credit Practical Subjects', 
      importance: 'Very Important', 
      active: true, 
      description: '1-2 three-hour practicals per week for 2 credit practical subjects',
      category: 'credit'
    },

    // Teacher Scheduling Rules
    { 
      id: 5, 
      name: 'No Teacher Overlap', 
      importance: 'Very Important', 
      active: true, 
      description: 'Teachers cannot be assigned to multiple classes at the same time',
      category: 'teacher'
    },
    { 
      id: 6, 
      name: 'Teacher Gap After Consecutive Classes', 
      importance: 'Important', 
      active: true, 
      description: 'Teachers must have a gap after two consecutive classes',
      category: 'teacher'
    },
    { 
      id: 7, 
      name: 'Teacher Day Preferences', 
      importance: 'Important', 
      active: true, 
      description: 'Respect teacher preferences for specific days',
      category: 'teacher'
    },

    // General Constraints
    { 
      id: 8, 
      name: 'Commute Time', 
      importance: 'Important', 
      active: true, 
      description: 'Consider teacher commute time between buildings',
      category: 'general'
    },
    { 
      id: 9, 
      name: 'Minimize Working Days', 
      importance: 'Important', 
      active: true, 
      description: 'Try to schedule teachers for fewer days',
      category: 'general'
    },
    { 
      id: 10, 
      name: 'Lessons Grouped by Building', 
      importance: 'Less Important', 
      active: true, 
      description: 'Group lessons in the same building together',
      category: 'general'
    },
    { 
      id: 11, 
      name: 'Uniform Distribution', 
      importance: 'Very Important', 
      active: true, 
      description: 'Spread lessons evenly across the week',
      category: 'general'
    },
    { 
      id: 12, 
      name: 'Minimize Gaps', 
      importance: 'Important', 
      active: true, 
      description: 'Reduce gaps between teacher lessons',
      category: 'general'
    },
    { 
      id: 13, 
      name: 'Early Important Lessons', 
      importance: 'Very Important', 
      active: true, 
      description: 'Schedule important lessons earlier in the day',
      category: 'general'
    },
    { 
      id: 14, 
      name: 'Consecutive Identical Lessons', 
      importance: 'Important', 
      active: true, 
      description: 'Allow same subject lessons in consecutive periods',
      category: 'general'
    },
    { 
      id: 15, 
      name: 'No 3 Identical Lessons', 
      importance: 'Very Important', 
      active: true, 
      description: 'Limit same subject to 2 lessons per day',
      category: 'general'
    },
    { 
      id: 16, 
      name: 'Appropriate Distribution', 
      importance: 'Important', 
      active: true, 
      description: 'Ensure lessons are spread across appropriate days',
      category: 'general'
    }
  ]);
  // const [loading, setLoading] = useState(false);
  const [showTooltip, setShowTooltip] = useState("");
  const [selectedCategory, setSelectedCategory] = useState('all');

  const toggleConstraint = (id) => {
    setConstraints(prev =>
      prev.map(constraint =>
        constraint.id === id
          ? { ...constraint, active: !constraint.active }
          : constraint
      )
    );
  };

  const updateImportance = (id, newImportance) => {
    setConstraints(prev =>
      prev.map(constraint =>
        constraint.id === id
          ? { ...constraint, importance: newImportance }
          : constraint
      )
    );
  };

  const validatePrerequisites = async () => {
    try {
      // Check if basic data exists
      const [configRes, subjectsRes, teachersRes, classroomsRes, classesRes] = await Promise.all([
        api.get('/api/timetable/configs/'),
        api.get('/api/timetable/subjects/'),
        api.get('/api/timetable/teachers/'),
        api.get('/api/timetable/classrooms/'),
        api.get('/api/timetable/class-groups/')
      ]);

      const issues = [];

      // Check department configuration
      if (!configRes.data.length || !configRes.data[0].start_time) {
        issues.push('⚙️ Department Configuration: Set up working days, periods, and times');
      }

      // Check subjects
      if (!subjectsRes.data.length) {
        issues.push('📚 Subjects: Add at least one subject');
      } else {
        const subjectsWithoutBatch = subjectsRes.data.filter(s => !s.batch);
        if (subjectsWithoutBatch.length > 0) {
          issues.push(`📚 Subjects: ${subjectsWithoutBatch.length} subjects need batch assignment`);
        }
      }

      // Check teachers
      if (!teachersRes.data.length) {
        issues.push('👨‍🏫 Teachers: Add at least one teacher');
      }

      // Check classrooms
      if (!classroomsRes.data.length) {
        issues.push('🏫 Classrooms: Add at least one classroom');
      }

      // Check classes
      if (!classesRes.data.length) {
        issues.push('👥 Classes: Add at least one class group');
      }

      return issues;
    } catch (error) {
      console.error('Validation error:', error);
      return ['❌ Unable to validate prerequisites. Please check your connection.'];
    }
  };

  const handleCheckPrerequisites = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    const issues = await validatePrerequisites();

    if (issues.length === 0) {
      setSuccess('✅ All prerequisites are met! You can now generate the timetable.');
    } else {
      const issuesList = issues.map(issue => `• ${issue}`).join('\n');
      setError(`⚠️ Please fix the following issues before generating timetables:\n\n${issuesList}`);
    }

    setLoading(false);
  };

  const handleGenerateTimetable = async () => {
    try {
      setLoading(true);
      setError('');
      setSuccess('');

      console.log('🔍 Validating prerequisites...');
      const validationIssues = await validatePrerequisites();

      if (validationIssues.length > 0) {
        const issuesList = validationIssues.map(issue => `• ${issue}`).join('\n');
        setError(`⚠️ Please fix the following issues before generating timetables:\n\n${issuesList}`);
        return;
      }

      console.log('🚀 Starting timetable generation...');
      console.log('Active constraints:', constraints.filter(c => c.active));

      const response = await api.post('/api/timetable/generate-timetable/', {
        constraints: constraints.filter(c => c.active)
      });

      console.log('✅ API Response:', response.data);

      if (response.data.message === 'Timetable generated successfully') {
        console.log('🎉 Timetable generated successfully! Navigating to timetable page...');
        const entriesCount = response.data.entries_count || 'multiple';
        setSuccess(`🎉 Timetable generated successfully! Created ${entriesCount} schedule entries. Redirecting to view timetable...`);

        // Wait a moment to show success message, then navigate
        setTimeout(() => {
          router.push('/components/Timetable');
        }, 2000);
      } else {
        throw new Error('Failed to generate timetable');
      }
    } catch (error) {
      console.error('❌ Timetable generation error:', error);
      console.error('Error response:', error.response?.data);

      // Enhanced error handling with specific user-friendly messages
      let errorMessage = 'Timetable generation failed. ';

      if (error.response?.data?.error) {
        const apiError = error.response.data.error;

        // Parse common error types and provide actionable solutions
        if (apiError.includes('No valid schedule configuration found')) {
          errorMessage = '⚠️ Missing Department Configuration: Please go to Department Config and set up your schedule (working days, periods, times) before generating timetables.';
        } else if (apiError.includes('Teacher') && apiError.includes('returned more than one')) {
          errorMessage = '⚠️ Duplicate Teacher Found: There are duplicate teachers in your database. Please check Teachers section and remove duplicates.';
        } else if (apiError.includes('Subject') && apiError.includes('returned more than one')) {
          errorMessage = '⚠️ Duplicate Subject Found: There are duplicate subjects in your database. Please check Subjects section and remove duplicates.';
        } else if (apiError.includes('Classroom') && apiError.includes('returned more than one')) {
          errorMessage = '⚠️ Duplicate Classroom Found: There are duplicate classrooms in your database. Please check Classrooms section and remove duplicates.';
        } else if (apiError.includes('No subjects found')) {
          errorMessage = '⚠️ No Subjects Added: Please add subjects in the Subjects section before generating timetables.';
        } else if (apiError.includes('No teachers found')) {
          errorMessage = '⚠️ No Teachers Added: Please add teachers in the Teachers section before generating timetables.';
        } else if (apiError.includes('No classrooms found')) {
          errorMessage = '⚠️ No Classrooms Added: Please add classrooms in the Classrooms section before generating timetables.';
        } else if (apiError.includes('No class groups found')) {
          errorMessage = '⚠️ No Classes Added: Please add class groups in the Classes section before generating timetables.';
        } else if (apiError.includes('batch')) {
          errorMessage = '⚠️ Batch Assignment Issue: Some subjects may not be assigned to batches. Please check Subjects section and assign all subjects to appropriate batches.';
        } else if (apiError.includes('constraint')) {
          errorMessage = '⚠️ Constraint Conflict: The selected constraints cannot be satisfied. Try adjusting or disabling some constraints.';
        } else if (apiError.includes('schedule')) {
          errorMessage = '⚠️ Scheduling Conflict: Unable to create a valid schedule with current data. Check for conflicts in teacher availability, classroom capacity, or time slots.';
        } else {
          // Show the raw error for unknown issues
          errorMessage = `⚠️ Generation Error: ${apiError}`;
        }
      } else if (error.code === 'NETWORK_ERROR' || error.message.includes('Network Error')) {
        errorMessage = '🌐 Network Error: Cannot connect to the server. Please check if the backend is running.';
      } else {
        errorMessage = `⚠️ Unexpected Error: ${error.message}`;
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
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

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'credit':
        return <GraduationCap className="h-4 w-4 text-accent-cyan" />;
      case 'teacher':
        return <Users className="h-4 w-4 text-accent-cyan" />;
      case 'general':
        return <Sliders className="h-4 w-4 text-accent-cyan" />;
      default:
        return null;
    }
  };

  const filteredConstraints = selectedCategory === 'all' 
    ? constraints 
    : constraints.filter(c => c.category === selectedCategory);

  return (
    <>
      <Head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" />
      </Head>

      <div className="flex min-h-screen bg-background text-primary font-sans">
        <Navbar number={7} />
        <div className="flex-1 p-8 max-w-[60rem] mx-auto">
          <div className="mb-8">
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-2">
              Timetable Constraints
            </h1>
            <p className="text-secondary/90">Configure and prioritize scheduling rules for timetable generation</p>
          </div>

          {success && (
            <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-xl mb-6">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h3 className="text-green-500 font-semibold text-sm mb-2">Success!</h3>
                  <div className="text-green-500 text-sm">{success}</div>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl mb-6">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h3 className="text-red-500 font-semibold text-sm mb-2">Timetable Generation Failed</h3>
                  <div className="text-red-500 text-sm whitespace-pre-line">{error}</div>
                </div>
              </div>
            </div>
          )}

          <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-primary flex items-center gap-2">
                <Sliders className="h-5 w-5 text-accent-cyan" />
                Configure Constraints
              </h2>
              <div className="relative">
                <button
                  type="button"
                  className="text-secondary hover:text-primary transition-colors"
                  onMouseEnter={() => setShowTooltip("constraints")}
                  onMouseLeave={() => setShowTooltip("")}
                >
                  <Info className="h-5 w-5" />
                </button>
                {showTooltip === "constraints" && (
                  <div className="absolute right-0 top-full mt-2 p-3 bg-surface border border-border rounded-xl shadow-lg text-sm text-secondary w-64 z-50">
                    Set the importance level for each constraint and enable/disable them. These rules will guide the timetable generation process.
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center gap-4 mb-6">
              <div className="relative">
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="appearance-none pl-3 pr-8 py-1.5 bg-surface border border-border rounded-lg text-sm text-primary focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                >
                  <option value="all">All Constraints</option>
                  <option value="credit">Credit Hour Rules</option>
                  <option value="teacher">Teacher Rules</option>
                  <option value="general">General Rules</option>
                </select>
                <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70 pointer-events-none" />
              </div>
            </div>
            
            <div className="space-y-4">
              {filteredConstraints.map((constraint) => (
                <div 
                  key={constraint.id} 
                  className="group p-4 bg-background/95 rounded-xl border border-border hover:border-accent-cyan/30 transition-all duration-300"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center gap-2">
                        <div className="flex items-center gap-2">
                          {getCategoryIcon(constraint.category)}
                          <span className="font-medium text-primary">{constraint.name}</span>
                        </div>
                        <span className="text-sm text-secondary/70">{constraint.description}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="relative">
                          <select
                            value={constraint.importance}
                            onChange={(e) => updateImportance(constraint.id, e.target.value)}
                            className="appearance-none pl-3 pr-8 py-1.5 bg-surface border border-border rounded-lg text-sm text-primary focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                          >
                            <option value="Very Important">Very Important</option>
                            <option value="Important">Important</option>
                            <option value="Less Important">Less Important</option>
                          </select>
                          <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70 pointer-events-none" />
                        </div>
                        {getImportanceIcon(constraint.importance)}
                      </div>
                    </div>
                    <button
                      onClick={() => toggleConstraint(constraint.id)}
                      className={`p-2 rounded-lg transition-all duration-300 ${
                        constraint.active
                          ? 'bg-accent-cyan/10 text-accent-cyan hover:bg-accent-cyan/20'
                          : 'bg-surface text-secondary hover:text-primary'
                      }`}
                    >
                      {constraint.active ? (
                        <Check className="h-5 w-5" />
                      ) : (
                        <XCircle className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-between items-center mt-8">
            <Link
              href="/components/Teachers"
              className="px-6 py-3 border border-border text-secondary rounded-xl hover:text-primary hover:border-accent-cyan/30 transition-colors flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </Link>

            <div className="flex gap-3">
              <button
                className="px-6 py-3 border border-accent-cyan/30 text-accent-cyan rounded-xl hover:bg-accent-cyan/10 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={handleCheckPrerequisites}
                disabled={loading}
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <CheckCircle2 className="h-4 w-4" />
                )}
                Check Prerequisites
              </button>

              <button
                className="px-6 py-3 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center gap-2 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={handleGenerateTimetable}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    Generate Timetable
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Constraints;