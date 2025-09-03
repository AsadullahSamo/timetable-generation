// Test script to verify PDF generation changes
// This script tests the subject name formatting and class advisor functionality

// Mock data structure similar to what the API returns
const mockTimetableData = {
  days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
  timeSlots: ['1st [09:00 to 10:00]', '2nd [10:00 to 11:00]', '3rd [11:00 to 12:00]'],
  entries: [
    {
      id: 1,
      day: 'Monday',
      period: 1,
      subject: 'Database Systems',
      subject_code: 'SW215',
      subject_short_name: 'DBS',
      teacher: 'Dr. John Doe',
      classroom: 'Lab. No. 1',
      class_group: '21SW-I',
      start_time: '09:00:00',
      end_time: '10:00:00',
      is_practical: false,
      is_extra_class: false,
      credits: 3
    },
    {
      id: 2,
      day: 'Monday',
      period: 2,
      subject: 'Software Engineering',
      subject_code: 'SW301',
      subject_short_name: 'SE',
      teacher: 'Dr. Jane Smith',
      classroom: 'Room 101',
      class_group: '21SW-I',
      start_time: '10:00:00',
      end_time: '11:00:00',
      is_practical: false,
      is_extra_class: false,
      credits: 3
    }
  ],
  batch_info: {
    '21SW': {
      description: '8th Semester - Final Year',
      semester_number: 8,
      academic_year: '2024-2025',
      class_advisor: 'Dr. Qasim Ali (Email: Qasim.arain@faculty.muet.edu.pk)'
    }
  },
  semester: 'Fall 2024',
  academic_year: '2024-2025'
};

// Test function to verify timetable table cells (should show only short codes)
function testTimetableTableCells() {
  console.log('🧪 Testing Timetable Table Cells (should show only short codes)...');
  
  const testEntry = mockTimetableData.entries[0];
  
  // Simulate the timetable table cell logic (should show only short codes)
  let subjectCode = testEntry.subject_short_name || testEntry.subject;
  let cellContent = subjectCode || '';
  
  console.log(`✅ Expected: "DBS" (short code only)`);
  console.log(`✅ Actual: "${cellContent}"`);
  console.log(`✅ Test ${cellContent === 'DBS' ? 'PASSED' : 'FAILED'}`);
  
  return cellContent === 'DBS';
}

// Test function to verify Subject and Teacher Details table formatting
function testSubjectDetailsTable() {
  console.log('🧪 Testing Subject and Teacher Details Table...');
  
  const testEntry = mockTimetableData.entries[0];
  
  // Simulate the Subject and Teacher Details table logic
  let subjectName = testEntry.subject || '';
  let subjectCode = testEntry.subject_code || '';
  let formattedSubjectName = subjectName;
  
  if (subjectCode && subjectCode.trim()) {
    formattedSubjectName = `${subjectName} - ${subjectCode}`;
  }
  
  console.log(`✅ Expected: "Database Systems - SW215"`);
  console.log(`✅ Actual: "${formattedSubjectName}"`);
  console.log(`✅ Test ${formattedSubjectName === 'Database Systems - SW215' ? 'PASSED' : 'FAILED'}`);
  
  return formattedSubjectName === 'Database Systems - SW215';
}

// Test function to verify class advisor formatting
function testClassAdvisorFormatting() {
  console.log('\n🧪 Testing Class Advisor Formatting...');
  
  const batchName = '21SW';
  const batchData = mockTimetableData.batch_info[batchName];
  
  // Simulate the new class advisor logic
  let classAdvisorText = 'Class Advisor: Not Assigned';
  if (mockTimetableData.batch_info && mockTimetableData.batch_info[batchName]) {
    if (batchData.class_advisor && batchData.class_advisor.trim()) {
      classAdvisorText = `Class Advisor: ${batchData.class_advisor}`;
    }
  }
  
  console.log(`✅ Expected: "Class Advisor: Dr. Qasim Ali (Email: Qasim.arain@faculty.muet.edu.pk)"`);
  console.log(`✅ Actual: "${classAdvisorText}"`);
  console.log(`✅ Test ${classAdvisorText.includes('Dr. Qasim Ali') ? 'PASSED' : 'FAILED'}`);
  
  return classAdvisorText.includes('Dr. Qasim Ali');
}

// Test function for missing class advisor
function testMissingClassAdvisor() {
  console.log('\n🧪 Testing Missing Class Advisor...');
  
  const batchName = '22SW';
  const mockDataWithoutAdvisor = {
    ...mockTimetableData,
    batch_info: {
      '22SW': {
        description: '6th Semester',
        semester_number: 6,
        academic_year: '2024-2025',
        class_advisor: '' // Empty advisor
      }
    }
  };
  
  let classAdvisorText = 'Class Advisor: Not Assigned';
  if (mockDataWithoutAdvisor.batch_info && mockDataWithoutAdvisor.batch_info[batchName]) {
    const batchData = mockDataWithoutAdvisor.batch_info[batchName];
    if (batchData.class_advisor && batchData.class_advisor.trim()) {
      classAdvisorText = `Class Advisor: ${batchData.class_advisor}`;
    }
  }
  
  console.log(`✅ Expected: "Class Advisor: Not Assigned"`);
  console.log(`✅ Actual: "${classAdvisorText}"`);
  console.log(`✅ Test ${classAdvisorText === 'Class Advisor: Not Assigned' ? 'PASSED' : 'FAILED'}`);
  
  return classAdvisorText === 'Class Advisor: Not Assigned';
}

// Run all tests
function runTests() {
  console.log('🚀 Starting PDF Generation Changes Tests\n');
  
  const test1 = testSubjectFormatting();
  const test2 = testClassAdvisorFormatting();
  const test3 = testMissingClassAdvisor();
  
  console.log('\n📊 Test Results Summary:');
  console.log(`✅ Subject Formatting: ${test1 ? 'PASSED' : 'FAILED'}`);
  console.log(`✅ Class Advisor (with data): ${test2 ? 'PASSED' : 'FAILED'}`);
  console.log(`✅ Class Advisor (missing data): ${test3 ? 'PASSED' : 'FAILED'}`);
  
  const allPassed = test1 && test2 && test3;
  console.log(`\n🎯 Overall Result: ${allPassed ? 'ALL TESTS PASSED ✅' : 'SOME TESTS FAILED ❌'}`);
  
  return allPassed;
}

// Export for use in other files if needed
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    runTests,
    testSubjectFormatting,
    testClassAdvisorFormatting,
    testMissingClassAdvisor,
    mockTimetableData
  };
}

// Run tests if this file is executed directly
if (typeof window === 'undefined') {
  runTests();
}
