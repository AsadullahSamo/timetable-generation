import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Navbar from "./Navbar";
import api from "../utils/api";
import { 
  Users, 
  Share2, 
  Eye, 
  MessageSquare, 
  Edit3, 
  Trash2, 
  Plus, 
  Search, 
  Building2, 
  UserPlus, 
  AlertCircle,
  CheckCircle,
  Clock,
  X,
  Info
} from 'lucide-react';

const SharedAccess = () => {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState("");
  
  // Data states
  const [departments, setDepartments] = useState([]);
  const [users, setUsers] = useState([]);
  const [sharedAccess, setSharedAccess] = useState([]);
  const [mySharedAccess, setMySharedAccess] = useState([]);
  
  // Form states
  const [showShareForm, setShowShareForm] = useState(false);
  const [shareForm, setShareForm] = useState({
    shared_with: "",
    department: "",
    access_level: "VIEW",
    notes: "",
    share_subjects: true,
    share_teachers: true,
    share_classrooms: true,
    share_batches: true,
    share_constraints: true,
    share_timetable: true
  });
  
  // Search and filter states
  const [searchTerm, setSearchTerm] = useState("");
  const [filterDepartment, setFilterDepartment] = useState("");
  const [filterAccessLevel, setFilterAccessLevel] = useState("");

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user');
    
    if (!token || !user) {
      router.push('/components/Login');
      return;
    }
    
    // Verify token is still valid by making a test request
    const verifyAuth = async () => {
      try {
        await api.get('/api/auth/profile/');
        fetchData();
      } catch (error) {
        if (error.response?.status === 401) {
          // Token is invalid, clear storage and redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          router.push('/components/Login');
        } else {
          // Other error, still try to fetch data
          fetchData();
        }
      }
    };
    
    verifyAuth();
  }, [router]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Check if we have a valid token
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No access token found');
      }
      
      console.log('Fetching data with token:', token.substring(0, 20) + '...');
      
      const [deptsRes, usersRes, sharedRes] = await Promise.all([
        api.get('/api/timetable/departments/'),
        api.get('/api/auth/'), // Get users list endpoint
        api.get('/api/timetable/shared-access/')
      ]);
      
      setDepartments(deptsRes.data);
      setUsers(usersRes.data);
      setSharedAccess(sharedRes.data);
      
      // Separate shared access by user's role
      const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
      setMySharedAccess(sharedRes.data.filter(access => access.owner === currentUser.id));
      
    } catch (error) {
      console.error('Error fetching data:', error);
      
      if (error.response?.status === 401) {
        // Authentication failed, redirect to login
        console.log('Authentication failed, redirecting to login');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        router.push('/components/Login');
        return;
      }
      
      // Show more specific error messages
      let errorMessage = 'Failed to load data';
      if (error.message === 'No access token found') {
        errorMessage = 'Authentication required. Please log in.';
      } else if (error.response?.status === 403) {
        errorMessage = 'Access denied. You do not have permission to view this data.';
      } else if (error.response?.status >= 500) {
        errorMessage = 'Server error. Please try again later.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleShareFormChange = (field, value) => {
    setShareForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleShareSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      // Get current user info
      const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
      
      // Check if user is trying to share with themselves
      if (parseInt(shareForm.shared_with) === currentUser.id) {
        setError('You cannot share access with yourself.');
        setLoading(false);
        return;
      }
      
      // Validate required fields
      if (!shareForm.shared_with || !shareForm.department) {
        setError('Please select both a user and a department.');
        setLoading(false);
        return;
      }
      
      // Prepare the data to send
      const shareData = {
        ...shareForm,
        // Ensure required fields are present
        shared_with: parseInt(shareForm.shared_with),
        department: parseInt(shareForm.department)
      };
      
      console.log('Current user:', currentUser);
      console.log('Share form data:', shareForm);
      console.log('Sharing access with data:', shareData);
      
      const response = await api.post('/api/timetable/shared-access/', shareData);
      
      setSuccess('Access shared successfully!');
      setShowShareForm(false);
          setShareForm({
      shared_with: "",
      department: "",
      access_level: "VIEW",
      notes: "",
      share_subjects: true,
      share_teachers: true,
      share_classrooms: true,
      share_batches: true,
      share_constraints: true,
      share_timetable: true
    });
      
      // Refresh data
      fetchData();
      
    } catch (error) {
      console.error('Error sharing access:', error);
      console.error('Error response data:', error.response?.data);
      console.error('Error response status:', error.response?.status);
      
      // Show more specific error messages
      let errorMessage = 'Failed to share access';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.shared_with) {
        errorMessage = `User: ${error.response.data.shared_with[0]}`;
      } else if (error.response?.data?.department) {
        errorMessage = `Department: ${error.response.data.department[0]}`;
      } else if (error.response?.data?.non_field_errors) {
        errorMessage = error.response.data.non_field_errors[0];
      } else if (error.response?.status === 400) {
        errorMessage = 'Invalid data provided. Please check your selections.';
      } else if (error.response?.status === 403) {
        errorMessage = 'You do not have permission to share access.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleRevokeAccess = async (accessId) => {
    if (!confirm('Are you sure you want to revoke this access?')) return;
    
    try {
      setLoading(true);
      await api.delete(`/api/timetable/shared-access/${accessId}/`);
      setSuccess('Access revoked successfully!');
      fetchData();
    } catch (error) {
      console.error('Error revoking access:', error);
      setError('Failed to revoke access');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateAccess = async (accessId, updates) => {
    try {
      setLoading(true);
      await api.patch(`/api/timetable/shared-access/${accessId}/`, updates);
      setSuccess('Access updated successfully!');
      fetchData();
    } catch (error) {
      console.error('Error updating access:', error);
      setError('Failed to update access');
    } finally {
      setLoading(false);
    }
  };

  const getAccessLevelIcon = (level) => {
    switch (level) {
      case 'VIEW': return <Eye className="w-4 h-4 text-accent-cyan" />;
      case 'COMMENT': return <MessageSquare className="w-4 h-4 text-accent-pink" />;
      case 'EDIT': return <Edit3 className="w-4 h-4 text-accent-green" />;
      default: return <Eye className="w-4 h-4 text-secondary" />;
    }
  };

  const getAccessLevelColor = (level) => {
    switch (level) {
      case 'VIEW': return 'bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20';
      case 'COMMENT': return 'bg-accent-pink/10 text-accent-pink border border-accent-pink/20';
      case 'EDIT': return 'bg-accent-green/10 text-accent-green border border-accent-green/20';
      default: return 'bg-secondary/10 text-secondary border border-secondary/20';
    }
  };

  const filteredSharedAccess = sharedAccess.filter(access => {
    const matchesSearch = 
      access.shared_with_username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      access.department_name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesDepartment = !filterDepartment || access.department === filterDepartment;
    const matchesAccessLevel = !filterAccessLevel || access.access_level === filterAccessLevel;
    
    return matchesSearch && matchesDepartment && matchesAccessLevel;
  });

  if (loading) {
    return (
      <div className="flex min-h-screen bg-background text-primary font-sans">
        <Navbar />
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-accent-cyan"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-background text-primary font-sans">
      <Navbar />
      
      <div className="flex-1 p-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-2 flex items-center gap-3">
                <Share2 className="w-8 h-8 text-accent-cyan" />
                Shared Access Management
              </h1>
              <p className="text-secondary/90">
                Manage who can access your timetable data and control their permissions
              </p>
            </div>
            <button
              onClick={() => setShowShareForm(true)}
              className="bg-gradient-to-r from-gradient-cyan-start to-gradient-cyan-end hover:from-gradient-cyan-end hover:to-gradient-cyan-start text-white px-6 py-3 rounded-xl font-medium flex items-center gap-2 transition-all duration-300 shadow-lg hover:shadow-xl"
            >
              <UserPlus className="w-5 h-5" />
              Share Access
            </button>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-6 bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <span className="text-red-500">{error}</span>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-400 hover:text-red-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}

        {success && (
          <div className="mb-6 bg-accent-green/10 border border-accent-green/20 rounded-xl p-4 flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-accent-green" />
            <span className="text-accent-green">{success}</span>
            <button
              onClick={() => setSuccess(null)}
              className="ml-auto text-accent-green/60 hover:text-accent-green"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}

        {/* Filters and Search */}
        <div className="bg-surface rounded-xl shadow-sm border border-border p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-primary mb-2">
                Search
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search users or departments..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-accent-cyan focus:border-transparent text-primary placeholder-secondary"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-primary mb-2">
                Department
              </label>
              <select
                value={filterDepartment}
                onChange={(e) => setFilterDepartment(e.target.value)}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-accent-cyan focus:border-transparent text-primary"
              >
                <option value="">All Departments</option>
                {departments.map(dept => (
                  <option key={dept.id} value={dept.id}>
                    {dept.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-primary mb-2">
                Access Level
              </label>
              <select
                value={filterAccessLevel}
                onChange={(e) => setFilterAccessLevel(e.target.value)}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-accent-cyan focus:border-transparent text-primary"
              >
                <option value="">All Levels</option>
                <option value="VIEW">View Only</option>
                <option value="COMMENT">Comment</option>
                <option value="EDIT">Edit</option>
              </select>
            </div>
            
            <div className="flex items-end">
              <button
                onClick={() => {
                  setSearchTerm("");
                  setFilterDepartment("");
                  setFilterAccessLevel("");
                }}
                className="w-full bg-secondary/10 hover:bg-secondary/20 text-secondary px-4 py-2 rounded-lg font-medium transition-colors border border-secondary/20"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Shared Access List */}
        <div className="bg-surface rounded-xl shadow-sm border border-border overflow-hidden">
          <div className="px-6 py-4 border-b border-border">
            <h2 className="text-lg font-semibold text-primary">
              Shared Access ({filteredSharedAccess.length})
            </h2>
          </div>
          
          {filteredSharedAccess.length === 0 ? (
            <div className="p-8 text-center">
              <Share2 className="w-16 h-16 text-secondary mx-auto mb-4" />
              <h3 className="text-lg font-medium text-primary mb-2">No shared access found</h3>
              <p className="text-secondary">
                {searchTerm || filterDepartment || filterAccessLevel 
                  ? "Try adjusting your filters" 
                  : "Start sharing your timetable data with other users"}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-border">
                <thead className="bg-background/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Department
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Access Level
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Shared Data
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Shared Date
                    </th>

                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-surface divide-y divide-border">
                  {filteredSharedAccess.map((access) => (
                    <tr key={access.id} className="hover:bg-background/30 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-accent-cyan/10 flex items-center justify-center border border-accent-cyan/20">
                              <Users className="w-5 h-5 text-accent-cyan" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-primary">
                              {access.shared_with_username}
                            </div>
                            <div className="text-sm text-secondary">
                              {access.shared_with_email}
                            </div>
                          </div>
                        </div>
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Building2 className="w-4 h-4 text-secondary mr-2" />
                          <span className="text-sm text-primary">
                            {access.department_name}
                          </span>
                        </div>
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getAccessLevelColor(access.access_level)}`}>
                          {getAccessLevelIcon(access.access_level)}
                          <span className="ml-1">{access.access_level}</span>
                        </span>
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex flex-wrap gap-1">
                          {access.share_subjects && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20">
                              Subjects
                            </span>
                          )}
                          {access.share_teachers && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-accent-green/10 text-accent-green border border-accent-green/20">
                              Teachers
                            </span>
                          )}
                          {access.share_classrooms && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gradient-purple-start/10 text-gradient-purple-start border border-gradient-purple-start/20">
                              Classrooms
                            </span>
                          )}
                          {access.share_batches && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-accent-pink/10 text-accent-pink border border-accent-pink/20">
                              Batches
                            </span>
                          )}
                          {access.share_constraints && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gradient-purple-end/10 text-gradient-purple-end border border-gradient-purple-end/20">
                              Constraints
                            </span>
                          )}
                          {access.share_timetable && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gradient-pink-start/10 text-gradient-pink-start border border-gradient-pink-start/20">
                              Timetable
                            </span>
                          )}
                        </div>
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-primary">
                        {new Date(access.shared_at).toLocaleDateString()}
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap">
                        {access.is_valid ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-accent-green/10 text-accent-green border border-accent-green/20">
                            <CheckCircle className="w-4 h-4 mr-1" />
                            Active
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-500/10 text-red-500 border border-red-500/20">
                            <Clock className="w-4 h-4 mr-1" />
                            Expired
                          </span>
                        )}
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          {access.owner === JSON.parse(localStorage.getItem('user') || '{}').id && (
                            <>
                              <button
                                onClick={() => handleRevokeAccess(access.id)}
                                className="text-red-500 hover:text-red-400 transition-colors"
                                title="Revoke Access"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => {
                                  // Handle edit access
                                }}
                                className="text-accent-cyan hover:text-accent-cyan/80 transition-colors"
                                title="Edit Access"
                              >
                                <Edit3 className="w-4 h-4" />
                              </button>
                            </>
                          )}
                          <button
                            onClick={() => {
                              // Show access details
                            }}
                            className="text-secondary hover:text-primary transition-colors"
                            title="View Details"
                          >
                            <Info className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Share Access Modal */}
      {showShareForm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="w-[600px] max-h-[90vh] bg-surface border border-border shadow-2xl rounded-xl flex flex-col">
            <div className="flex items-center justify-between p-6 border-b border-border">
              <h3 className="text-lg font-medium text-primary">Share Access</h3>
              <button
                onClick={() => setShowShareForm(false)}
                className="text-secondary hover:text-primary transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6">
              <form id="share-form" onSubmit={handleShareSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    User to Share With
                  </label>
                  <select
                    required
                    value={shareForm.shared_with}
                    onChange={(e) => handleShareFormChange('shared_with', e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-accent-cyan focus:border-transparent text-primary"
                  >
                    <option value="">Select User</option>
                    {users.map(user => (
                      <option key={user.id} value={user.id}>
                        {user.username} - {user.email}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Department
                  </label>
                  <select
                    required
                    value={shareForm.department}
                    onChange={(e) => handleShareFormChange('department', e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-accent-cyan focus:border-transparent text-primary"
                  >
                    <option value="">Select Department</option>
                    {departments.map(dept => (
                      <option key={dept.id} value={dept.id}>
                        {dept.name} ({dept.code})
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Access Level
                  </label>
                  <select
                    required
                    value={shareForm.access_level}
                    onChange={(e) => handleShareFormChange('access_level', e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-accent-cyan focus:border-transparent text-primary opacity-60 cursor-not-allowed"
                    disabled
                  >
                    <option value="VIEW">View Only</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    What to Share
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={shareForm.share_subjects}
                        onChange={(e) => handleShareFormChange('share_subjects', e.target.checked)}
                        className="rounded border-border text-accent-cyan focus:ring-accent-cyan bg-background"
                      />
                      <span className="text-sm text-primary">Subjects</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={shareForm.share_teachers}
                        onChange={(e) => handleShareFormChange('share_teachers', e.target.checked)}
                        className="rounded border-border text-accent-cyan focus:ring-accent-cyan bg-background"
                      />
                      <span className="text-sm text-primary">Teachers</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={shareForm.share_classrooms}
                        onChange={(e) => handleShareFormChange('share_classrooms', e.target.checked)}
                        className="rounded border-border text-accent-cyan focus:ring-accent-cyan bg-background"
                      />
                      <span className="text-sm text-primary">Classrooms</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={shareForm.share_batches}
                        onChange={(e) => handleShareFormChange('share_batches', e.target.checked)}
                        className="rounded border-border text-accent-cyan focus:ring-accent-cyan bg-background"
                      />
                      <span className="text-sm text-primary">Batches</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={shareForm.share_constraints}
                        onChange={(e) => handleShareFormChange('share_constraints', e.target.checked)}
                        className="rounded border-border text-accent-cyan focus:ring-accent-cyan bg-background"
                      />
                      <span className="text-sm text-primary">Constraints</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={shareForm.share_timetable}
                        onChange={(e) => handleShareFormChange('share_timetable', e.target.checked)}
                        className="rounded border-border text-accent-cyan focus:ring-accent-cyan bg-background"
                      />
                      <span className="text-sm text-primary">Timetable</span>
                    </label>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Notes (Optional)
                  </label>
                  <textarea
                    value={shareForm.notes}
                    onChange={(e) => handleShareFormChange('notes', e.target.value)}
                    rows="3"
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-accent-cyan focus:border-transparent text-primary placeholder-secondary"
                    placeholder="Add any notes about this shared access..."
                  />
                </div>
                

              </form>
            </div>
            
            {/* Fixed footer for buttons */}
            <div className="p-6 border-t border-border bg-surface">
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowShareForm(false)}
                  className="px-4 py-2 border border-border rounded-lg text-secondary hover:bg-background transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  form="share-form"
                  disabled={loading}
                  className="px-4 py-2 bg-gradient-to-r from-gradient-cyan-start to-gradient-cyan-end text-white rounded-lg hover:from-gradient-cyan-end hover:to-gradient-cyan-start disabled:opacity-50 transition-all duration-300"
                >
                  {loading ? 'Sharing...' : 'Share Access'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SharedAccess;
