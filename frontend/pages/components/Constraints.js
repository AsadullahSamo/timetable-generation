import { useState } from 'react';
import { useRouter } from 'next/router';
import { FaArrowUp, FaArrowDown } from 'react-icons/fa';
import Navbar from './Navbar';
import api from "../utils/api";

const Constraints = () => {
  const router = useRouter();
  const [constraints, setConstraints] = useState([
    { id: 1, name: 'Commute time', importance: 'Very Important', active: true },
    { id: 2, name: 'Minimize working days for teachers', importance: 'Important', active: true },
    { id: 3, name: 'Lessons grouped by building', importance: 'Less Important', active: true },
    { id: 4, name: 'Uniform distribution of lessons across days', importance: 'Very Important', active: true },
    { id: 5, name: 'Minimize teachers gaps', importance: 'Important', active: true },
    { id: 6, name: 'Early placement of important lessons', importance: 'Very Important', active: true },
    { id: 7, name: 'Consecutive identical lessons', importance: 'Important', active: true },
    { id: 8, name: 'No 3 identical lessons in the same day', importance: 'Very Important', active: true },
    { id: 9, name: 'Appropriate number of days for lesson distribution', importance: 'Important', active: true },
  ]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

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
      
      const response = await api.post('/api/timetable/generate/', {
        constraints: constraints.filter(c => c.active)
      });
      
      if (response.data.task_id) {
        // Poll for task completion
        const pollResult = async () => {
          const task = await api.get(`/api/timetable/tasks/${response.data.task_id}/`);
          if (task.data.status === 'SUCCESS') {
            router.push('/components/TimetableDisplay');
          } else if (task.data.status === 'FAILURE') {
            throw new Error('Generation failed');
          } else {
            setTimeout(pollResult, 1000);
          }
        };
        await pollResult();
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
        return <><FaArrowUp className="text-purple-500" /><FaArrowUp className="text-purple-500" /></>;
      case 'Important':
        return <FaArrowUp className="text-blue-500" />;
      case 'Less Important':
        return <FaArrowDown className="text-red-500" />;
      default:
        return null;
    }
  };

  const getImportanceClass = (importance) => {
    switch (importance) {
      case 'Very Important':
        return 'border-purple-500';
      case 'Important':
        return 'border-blue-500';
      case 'Less Important':
        return 'border-red-500';
      default:
        return 'border-gray-700';
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-900 text-gray-100 font-sans">
      <Navbar number={6}/>

      <div className="flex-1 p-8 max-w-7xl">
        <h1 className="text-3xl text-gray-50 mb-8">Timetable Constraints</h1>

        {error && (
          <div className="bg-red-900/50 text-red-200 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        <div className="bg-gray-800 rounded-lg p-6 mb-8 border border-gray-700">
          <h2 className="text-xl text-purple-400 mb-4">Configure Constraints</h2>
          
          <div className="space-y-4">
            {constraints.map((constraint) => (
              <div key={constraint.id} className="flex justify-between items-center p-4 bg-gray-900 rounded-lg border border-gray-700">
                <div className="space-y-2">
                  <span className="font-medium">{constraint.name}</span>
                  <div className="flex items-center gap-2">
                    <select
                      value={constraint.importance}
                      onChange={(e) => updateImportance(constraint.id, e.target.value)}
                      className={`px-3 py-1 rounded-md bg-gray-800 text-sm transition-colors ${getImportanceClass(constraint.importance)}`}
                    >
                      <option value="Very Important">Very Important</option>
                      <option value="Important">Important</option>
                      <option value="Less Important">Less Important</option>
                    </select>
                    <div className="flex items-center gap-1">
                      {getImportanceIcon(constraint.importance)}
                    </div>
                  </div>
                </div>
                <button
                  className={`px-4 py-2 rounded-md transition-colors ${
                    constraint.active
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-800 text-gray-400 hover:text-purple-400'
                  }`}
                  onClick={() => toggleConstraint(constraint.id)}
                >
                  {constraint.active ? '✓' : '✗'}
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-between">
          <button 
            className="px-6 py-3 border border-gray-700 text-gray-400 rounded-lg hover:border-purple-500 hover:text-purple-400 transition-colors"
            onClick={() => router.back()}
          >
            Previous Step
          </button>
          <button
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={handleGenerateTimetable}
            disabled={loading}
          >
            {loading ? 'Generating...' : 'Generate Timetable'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Constraints;