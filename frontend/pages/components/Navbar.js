import React from 'react'

export default function Navbar({number}) {
  return (
    <div className="w-[280px] bg-gray-800 p-8 border-r border-gray-700">
      <div className="flex flex-col gap-2">
        {[1, 2, 3, 4, 5, 6, 7].map((num) => (
          <div
            key={num}
            className={`px-4 py-3 rounded-md cursor-pointer transition-all duration-200 ${
              num === number 
                ? 'bg-purple-700 text-white' 
                : 'text-gray-400 hover:bg-gray-700'
            }`}
          >
            {["School Config", "Classes", "Subjects", "Teachers", "Lessons", "Constraints", "Timetable"][num - 1]}
          </div>
        ))}
      </div>
    </div>
  )
}
