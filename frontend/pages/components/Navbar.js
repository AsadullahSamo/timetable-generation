import React from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import {
  Settings,
  Users,
  BookOpen,
  User,
  Layout,
  Sliders,
  Calendar,
  LogOut
} from 'lucide-react';

const menuItems = [
  { name: "School Config", icon: Settings, path: "/components/SchoolConfig" },
  { name: "Classes", icon: Users, path: "/components/Classes" },
  { name: "Subjects", icon: BookOpen, path: "/components/Subjects" },
  { name: "Teachers", icon: User, path: "/components/Teachers" },
  { name: "Lessons", icon: Layout, path: "/components/Lessons" },
  { name: "Constraints", icon: Sliders, path: "/components/Constraints" },
  { name: "Timetable", icon: Calendar, path: "/components/Timetable" }
];

export default function Navbar() {
  const router = useRouter();
  const currentPath = router.pathname;

  const handleLogout = () => {
    // Add logout logic here
    router.push('/components/Login');
  };

  return (
    <div className="w-[280px] bg-surface border-r border-border flex flex-col h-screen sticky top-0">
      <div className="p-6 flex-1">
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

        <nav className="space-y-2">
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

      {/* Logout Button */}
      <div className="p-4 border-t border-border">
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
