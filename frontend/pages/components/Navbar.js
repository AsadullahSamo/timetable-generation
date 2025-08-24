import React from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import {
  Settings,
  Users,
  BookOpen,
  User,
  Building2,
  Sliders,
  Calendar,
  LogOut,
  GraduationCap,
  Share2
} from 'lucide-react';

const menuItems = [
  { name: "Batches", icon: GraduationCap, path: "/components/Batches" },
  { name: "Subjects", icon: BookOpen, path: "/components/Subjects" },
  { name: "Teachers", icon: User, path: "/components/Teachers" },
  { name: "Classrooms", icon: Building2, path: "/components/Classrooms" },
  { name: "Teacher Assignments", icon: Users, path: "/components/TeacherAssignments" },
  { name: "Department Config", icon: Settings, path: "/components/DepartmentConfig" },
  { name: "Constraints", icon: Sliders, path: "/components/Constraints" },
  { name: "Timetable", icon: Calendar, path: "/components/Timetable" },
  { name: "Shared Access", icon: Share2, path: "/components/SharedAccess" }
];

export default function Navbar() {
  const router = useRouter();
  const currentPath = router.pathname;

  const handleLogout = () => {
    // Clear authentication tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    
    // Redirect to login
    router.push('/components/Login');
  };

  return (
    <div className="w-[280px] bg-surface border-r border-border flex flex-col h-screen sticky top-0">
      {/* Header Section - Fixed */}
      <div className="p-6 flex-shrink-0">
        <div className="mb-8">
          <div className="relative h-12 w-12 mb-4">
            <div className="absolute inset-0 bg-gradient-to-r from-accent-cyan to-accent-pink rounded-xl blur opacity-40"></div>
            <div className="relative bg-surface h-full w-full rounded-xl flex items-center justify-center border border-border">
              <Calendar className="h-6 w-6 text-accent-cyan" />
            </div>
          </div>
          <h1 className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end">
            Timetable Generator
          </h1>
          <p className="text-secondary/90 text-sm font-medium">AI-Powered Scheduling</p>
        </div>
      </div>

      {/* Navigation Section - Scrollable */}
      <div className="flex-1 overflow-y-auto px-6">
        <nav className="space-y-2 pb-4">
          {menuItems.map((item, index) => {
            const Icon = item.icon;
            const isActive = currentPath === item.path;
            
            return (
              <Link
                key={index}
                href={item.path}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer transition-all duration-300
                  ${isActive 
                    ? 'bg-gradient-to-r from-accent-cyan/10 to-accent-pink/10 text-primary border border-border' 
                    : 'text-secondary hover:text-primary hover:bg-surface/60'}
                `}
              >
                <Icon className={`h-5 w-5 ${isActive ? 'text-accent-cyan' : 'text-secondary'}`} />
                <span className="text-sm font-medium">{item.name}</span>
                {isActive && (
                  <div className="ml-auto h-2 w-2 rounded-full bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end"></div>
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Logout Button - Fixed at Bottom */}
      <div className="flex-shrink-0 p-4 border-t border-border bg-surface">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-secondary hover:text-primary hover:bg-surface/60 transition-all duration-300"
        >
          <LogOut className="h-5 w-5" />
          <span className="text-sm font-medium">Logout</span>
        </button>
      </div>
    </div>
  );
}
