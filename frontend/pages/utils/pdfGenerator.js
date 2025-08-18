import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

export const generateTimetablePDF = (timetableData, selectedClassGroup = null) => {
  const doc = new jsPDF('p', 'mm', 'a4');
  
  // Set font
  doc.setFont('helvetica');
  
  // Page dimensions
  const pageWidth = doc.internal.pageSize.width;
  const pageHeight = doc.internal.pageSize.height;
  const margin = 20;
  const contentWidth = pageWidth - (2 * margin);
  
  // Header
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.text('MEHRAN UNIVERSITY OF ENGINEERING AND TECHNOLOGY, JAMSHORO', pageWidth / 2, 30, { align: 'center' });
  
  doc.setFontSize(16);
  doc.text('DEPARTMENT OF SOFTWARE ENGINEERING', pageWidth / 2, 40, { align: 'center' });
  
  // Get class groups to process
  let classGroupsToProcess = [];
  if (selectedClassGroup) {
    classGroupsToProcess = [selectedClassGroup];
  } else if (timetableData.pagination && timetableData.pagination.class_groups) {
    classGroupsToProcess = timetableData.pagination.class_groups;
  }
  
  let currentY = 60;
  
  // Process each class group
  for (const classGroup of classGroupsToProcess) {
    // Check if we need a new page
    if (currentY > pageHeight - 100) {
      doc.addPage();
      currentY = 30;
    }
    
    // Class group header
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    const batchName = classGroup.split('-')[0] || classGroup;
    const sectionName = classGroup.split('-')[1] || '';
    const sectionText = sectionName ? `SECTION-${sectionName}` : '';
    const semesterText = '1st Semester Final YEAR'; // You can make this dynamic if needed
    
    doc.text(`TIMETABLE OF ${batchName}-BATCH ${sectionText} (${semesterText})`, pageWidth / 2, currentY, { align: 'center' });
    currentY += 10;
    
    // Effective date
    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    const today = new Date();
    const dateString = today.toLocaleDateString('en-GB').split('/').join('-');
    doc.text(`w.e.f ${dateString}`, pageWidth / 2, currentY, { align: 'center' });
    currentY += 15;
    
    // Filter entries for this class group
    const classGroupEntries = timetableData.entries.filter(entry => entry.class_group === classGroup);
    
    // Create timetable table
    const tableData = [];
    
    // Add header row with days
    const headerRow = ['Periods'];
    timetableData.days.forEach(day => {
      headerRow.push(day);
    });
    tableData.push(headerRow);
    
    // Add lab/room numbers row
    const roomRow = ['Lab. No.'];
    // For now, we'll use default room numbers - you can make this dynamic
    const defaultRooms = ['Lab. No. 01', 'Lab. No. 02', 'Lab. No. 03', 'Lab. No. 01', 'Lab. No. 02'];
    timetableData.days.forEach((day, index) => {
      roomRow.push(defaultRooms[index] || 'Lab. No. 01');
    });
    tableData.push(roomRow);
    
    // Add time slots and subjects
    // Note: timeSlots are fetched dynamically from the database
    // This handles different period durations and start times automatically
    timetableData.timeSlots.forEach((timeSlot, index) => {
      // Format time slot to ensure it's on a single line
      // Convert "8:00 AM to 9:00 AM" to "8:00 - 9:00 AM"
      let formattedTimeSlot = timeSlot;
      if (timeSlot.includes(' to ')) {
        formattedTimeSlot = timeSlot.replace(' to ', ' - ');
      }
      
      // Ensure no line breaks by removing any newlines or extra spaces
      formattedTimeSlot = formattedTimeSlot.replace(/\s+/g, ' ').trim();
      
      const row = [formattedTimeSlot];
      
      timetableData.days.forEach(day => {
        // Try to find entry by day and period
        let entry = classGroupEntries.find(e => 
          e.day === day && e.period === (index + 1)
        );
        
        // If not found, try to find by normalized day names
        if (!entry) {
          const normalizeDay = (dayName) => {
            if (typeof dayName === 'string') {
              return dayName.toUpperCase().substring(0, 3);
            }
            return dayName;
          };
          
          entry = classGroupEntries.find(e => 
            normalizeDay(e.day) === normalizeDay(day) && e.period === (index + 1)
          );
        }
        
        if (entry) {
          // Use the actual subject code from the database
          // The backend now provides subject_code field with codes like "WE", "MC", "FMSE", etc.
          let subjectCode = entry.subject_code || entry.subject;
          
          // Add room information if different from default
          let cellContent = subjectCode || '';
          if (entry.classroom && !entry.classroom.includes('Lab. No.')) {
            cellContent += ` [${entry.classroom}]`;
          }
          
          row.push(cellContent);
        } else {
          row.push('');
        }
      });
      
      tableData.push(row);
    });
    
    // Generate the table
    autoTable(doc, {
      head: [tableData[0], tableData[1]], // First two rows as headers
      body: tableData.slice(2), // Rest as body
      startY: currentY,
      margin: { left: margin, right: margin },
      tableWidth: contentWidth,
      styles: {
        fontSize: 10,
        cellPadding: 3,
        lineWidth: 0.1,
        lineColor: [100, 100, 100],
        textColor: [50, 50, 50],
        fillColor: [255, 255, 255],
        overflow: 'linebreak', // Prevent text overflow
        halign: 'center', // Center align all cells by default
      },
      headStyles: {
        fillColor: [70, 70, 70],
        textColor: [255, 255, 255],
        fontSize: 11,
        fontStyle: 'bold',
        halign: 'center',
      },
      columnStyles: {
        0: { cellWidth: 35, halign: 'center', cellPadding: 2, fontSize: 9 }, // Periods column - compact padding, smaller font
      },
      didDrawPage: function (data) {
        // Add page number
        doc.setFontSize(10);
        doc.text(`Page ${doc.internal.getNumberOfPages()}`, pageWidth - margin, pageHeight - 10);
      }
    });
    
    currentY = doc.lastAutoTable.finalY + 15;
    
    // Add teachers information
    if (currentY > pageHeight - 80) {
      doc.addPage();
      currentY = 30;
    }
    
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.text('Subject and Teacher Details:', margin, currentY);
    currentY += 10;
    
    // Create teachers table
    const teacherData = [];
    const uniqueSubjects = [...new Set(classGroupEntries.map(e => e.subject))];
    
    uniqueSubjects.forEach((subject, index) => {
      const entry = classGroupEntries.find(e => e.subject === subject);
      if (entry) {
        // Use the actual subject code from the database
        // The backend now provides subject_code field with codes like "WE", "MC", "FMSE", etc.
        let subjectCode = entry.subject_code || subject;
        
        // Get teacher name
        const teacherName = entry.teacher || '--';
        
        // Determine credit hours (you can make this dynamic based on your data)
        const creditHours = subject.includes('(PR)') ? '0+3' : '3+0';
        
        // Use subject code as the main identifier
        teacherData.push([
          index + 1,
          subjectCode || '',
          creditHours,
          teacherName
        ]);
      }
    });
    
    // Add teachers table
    autoTable(doc, {
      head: [['S.', 'SUBJECT CODE', 'C.H', 'TEACHER']],
      body: teacherData,
      startY: currentY,
      margin: { left: margin, right: margin },
      tableWidth: contentWidth,
      styles: {
        fontSize: 9,
        cellPadding: 3,
        lineWidth: 0.1,
        lineColor: [100, 100, 100],
        textColor: [50, 50, 50],
        fillColor: [255, 255, 255],
      },
      headStyles: {
        fillColor: [70, 70, 70],
        textColor: [255, 255, 255],
        fontSize: 10,
        fontStyle: 'bold',
        halign: 'center',
      },
      columnStyles: {
        0: { cellWidth: 15, halign: 'center' }, // Serial number
        1: { cellWidth: 40, halign: 'center' }, // Subject code (smaller since it's just codes)
        2: { cellWidth: 25, halign: 'center' }, // Credit hours
        3: { cellWidth: 100 }, // Teacher (wider for names)
      }
    });
    
    currentY = doc.lastAutoTable.finalY + 20;
    
    // Add additional information
    if (currentY > pageHeight - 60) {
      doc.addPage();
      currentY = 30;
    }
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text('Class Advisor: Dr. Qasim Ali (Email: Qasim.arain@faculty.muet.edu.pk)', margin, currentY);
    currentY += 15;
    
    // Signature line
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.text('Chairman', pageWidth - margin - 30, currentY);
    
    // Add some space before next section
    currentY += 30;
  }
  
  // Save the PDF
  const fileName = selectedClassGroup 
    ? `timetable_${selectedClassGroup}_${new Date().toISOString().split('T')[0]}.pdf`
    : `timetable_all_sections_${new Date().toISOString().split('T')[0]}.pdf`;
  
  doc.save(fileName);
};
