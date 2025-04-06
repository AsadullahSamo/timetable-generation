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
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
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

  const handleGenerateTimetable = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await api.post('/api/timetable/generate-timetable/', {
        constraints: constraints.filter(c => c.active)
      });
      
      if (response.data.message === 'Timetable generated successfully') {
        // Navigate directly to the timetable page with correct component name
        router.push('/components/Timetable');
      } else {
        throw new Error('Failed to generate timetable');
      }
    } catch (error) {
      setError('Timetable generation failed: ' + error.message);
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
        <Navbar number={6} />
        <div className="flex-1 p-8 max-w-[60rem] mx-auto">
          <div className="mb-8">
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-2">
              Timetable Constraints
            </h1>
            <p className="text-secondary/90">Configure and prioritize scheduling rules for timetable generation</p>
          </div>

          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl mb-6 flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <p className="text-red-500 text-sm font-medium">{error}</p>
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
              href="/components/Lessons"
              className="px-6 py-3 border border-border text-secondary rounded-xl hover:text-primary hover:border-accent-cyan/30 transition-colors flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </Link>
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
    </>
  );
};

export default Constraints;