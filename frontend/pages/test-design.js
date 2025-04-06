import { useState, useEffect } from 'react';
import {
  Clock, Settings, Search, Calendar, ChevronRight,
  LineChart, Target
} from 'lucide-react';

export default function TestDesign() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <div className="min-h-screen bg-[#09090B] text-[#F8FAFC] overflow-hidden font-sans">
      {/* Background Glow Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-1/3 left-1/4 w-[700px] h-[700px] bg-[#22D3EE]/10 rounded-full blur-[200px] animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-[700px] h-[700px] bg-[#F471B5]/10 rounded-full blur-[200px] animate-pulse animation-delay-3000"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-6 py-14">
        {/* Header */}
        <header className="flex items-center justify-between mb-16">
          <div className="flex items-center space-x-5">
            <div className="relative h-12 w-12">
              <div className="absolute inset-0 bg-gradient-to-br from-[#22D3EE] to-[#F471B5] rounded-full blur-lg opacity-30"></div>
              <div className="relative bg-[#18181B] h-full w-full rounded-full flex items-center justify-center border border-[#27272A]">
                <Clock className="h-6 w-6 text-[#22D3EE]" />
              </div>
            </div>
            <h1 className="text-2xl font-semibold text-white tracking-tight">Timetable Generator</h1>
          </div>
          <div className="flex items-center space-x-3">
            {[Search, Settings].map((Icon, i) => (
              <button key={i} className="p-2 rounded-full bg-[#18181B] hover:bg-[#27272A] transition-all duration-300">
                <Icon className="h-5 w-5 text-[#A1A1AA]" />
              </button>
            ))}
          </div>
        </header>

        {/* Central Stat Circle */}
        <div className="mb-20 flex justify-center">
          <div className="relative group hover:scale-105 transition duration-500">
            <div className="absolute inset-0 bg-gradient-to-br from-[#22D3EE] to-[#F471B5] rounded-full blur-2xl opacity-30"></div>
            <div className="relative w-[280px] h-[280px] bg-[#18181B] rounded-full border border-[#27272A] flex flex-col items-center justify-center p-8 shadow-inner shadow-[#22D3EE]/10">
              <div className="text-5xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-[#22D3EE] to-[#F471B5]">
                84%
              </div>
              <p className="text-[#A1A1AA] mt-2 text-sm">Schedule Optimization</p>
              <div className="mt-4 flex space-x-2">
                <div className="h-2 w-2 rounded-full bg-[#22D3EE]"></div>
                <div className="h-2 w-2 rounded-full bg-[#F471B5]"></div>
                <div className="h-2 w-2 rounded-full bg-[#A1A1AA]"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-20">
          {[
            {
              icon: <Calendar className="h-6 w-6 text-[#22D3EE]" />,
              title: "Schedule",
              value: "23:45",
              change: "+2.5%"
            },
            {
              icon: <Target className="h-6 w-6 text-[#F471B5]" />,
              title: "Efficiency",
              value: "92.8%",
              change: "+4.3%"
            },
            {
              icon: <LineChart className="h-6 w-6 text-[#A78BFA]" />,
              title: "Progress",
              value: "89.2%",
              change: "+1.2%"
            }
          ].map((item, i) => (
            <div key={i} className="relative group hover:-translate-y-1 transition-transform duration-300">
              <div className="absolute -inset-1 bg-gradient-to-r from-[#22D3EE]/10 to-[#F471B5]/10 blur-xl opacity-20 rounded-2xl"></div>
              <div className="relative bg-[#18181B] p-6 rounded-2xl border border-[#27272A] shadow-md hover:shadow-[#22D3EE]/10">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-2 rounded-full bg-[#27272A]">
                    {item.icon}
                  </div>
                  <span className="text-[#4ADE80] text-sm font-semibold">{item.change}</span>
                </div>
                <h3 className="text-[#A1A1AA] text-sm mb-1 tracking-wide">{item.title}</h3>
                <div className="text-2xl font-bold text-white">{item.value}</div>
              </div>
            </div>
          ))}
        </div>

        {/* CTA Card */}
        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#22D3EE]/10 to-[#F471B5]/10 rounded-2xl blur opacity-30 transition-all duration-1000 group-hover:opacity-50"></div>
          <div className="relative bg-[#18181B] p-6 rounded-2xl border border-[#27272A] flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold mb-1">Generate New Schedule</h2>
              <p className="text-[#A1A1AA] text-sm">Optimize your timetable with AI</p>
            </div>
            <button className="p-3 rounded-full bg-gradient-to-r from-[#22D3EE] to-[#F471B5] text-white shadow-md hover:scale-105 transition-all duration-300">
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
