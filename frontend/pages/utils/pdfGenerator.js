import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import api from './api';

export const generateTimetablePDF = async (timetableData, selectedClassGroup = null) => {
  try {
    console.log('Starting PDF generation...');
    console.log('Initial timetable data:', timetableData);
    
    // Always fetch fresh data for all sections when generating PDF
    let allSectionsData = null;
    
    try {
      console.log('Fetching complete timetable data for all sections...');
      // Request all sections by setting a very large page size to bypass pagination
      const response = await api.get('/api/timetable/latest/', {
        params: {
          page_size: 1000, // Large enough to get all sections
          page: 1
        }
      });
      
      if (response.data && response.data.entries && Array.isArray(response.data.entries)) {
        allSectionsData = response.data;
        console.log('✅ Successfully fetched complete data for PDF');
        console.log('Total entries found:', response.data.entries.length);
        console.log('Available class groups from API:', response.data.pagination?.class_groups);
        
        // Check if we got all sections or if pagination is still limiting us
        const totalClassGroups = response.data.pagination?.total_class_groups || 0;
        const currentClassGroups = response.data.pagination?.class_groups || [];
        const allClassGroupsFromAPI = response.data.pagination?.all_class_groups || [];
        
        console.log(`📊 Pagination info: total=${totalClassGroups}, current=${currentClassGroups.length}, all=${allClassGroupsFromAPI.length}`);
        
        // If we have all_class_groups, use that directly
        if (allClassGroupsFromAPI.length > 0 && allClassGroupsFromAPI.length >= totalClassGroups) {
          console.log(`✅ API returned all ${allClassGroupsFromAPI.length} sections in single request`);
          // Update the class_groups to include all sections
          response.data.pagination.class_groups = allClassGroupsFromAPI;
        }
        // Otherwise, check if pagination is still limiting us
        else if (totalClassGroups > currentClassGroups.length) {
          console.warn(`⚠️  Pagination still limiting results: got ${currentClassGroups.length} out of ${totalClassGroups} total sections`);
          console.log('Attempting to fetch all sections by making multiple requests...');
          
          // Try to fetch all sections by making multiple requests
          let allEntries = [...response.data.entries];
          let allClassGroups = [...currentClassGroups];
          let currentPage = 2;
          
          while (allClassGroups.length < totalClassGroups && currentPage <= 10) { // Safety limit
            try {
              const nextResponse = await api.get('/api/timetable/latest/', {
                params: {
                  page_size: 1000,
                  page: currentPage
                }
              });
              
              if (nextResponse.data?.entries && Array.isArray(nextResponse.data.entries)) {
                allEntries = [...allEntries, ...nextResponse.data.entries];
                const nextClassGroups = nextResponse.data.pagination?.class_groups || [];
                allClassGroups = [...new Set([...allClassGroups, ...nextClassGroups])];
                console.log(`📄 Fetched page ${currentPage}: ${nextResponse.data.entries.length} entries, total sections: ${allClassGroups.length}`);
              }
              
              currentPage++;
            } catch (pageError) {
              console.warn(`⚠️  Error fetching page ${currentPage}:`, pageError);
              break;
            }
          }
          
          // Update the data with all fetched entries
          allSectionsData.entries = allEntries;
          allSectionsData.pagination.class_groups = allClassGroups;
          console.log(`✅ Final data: ${allEntries.length} entries across ${allClassGroups.length} sections`);
        }
        
        // Verify we have all the necessary data
        if (!allSectionsData.days || !allSectionsData.timeSlots) {
          console.warn('⚠️  Missing days or timeSlots from API, using current data');
          allSectionsData.days = timetableData.days || allSectionsData.days;
          allSectionsData.timeSlots = timetableData.timeSlots || allSectionsData.timeSlots;
        }
      } else {
        console.warn('⚠️  API response missing entries, using current data');
        allSectionsData = timetableData;
      }
    } catch (error) {
      console.error('❌ Error fetching complete data:', error);
      console.warn('Using current timetable data instead');
      allSectionsData = timetableData;
    }
    
    // Ensure we have the basic structure
    if (!allSectionsData || !allSectionsData.entries) {
      throw new Error('No timetable data available for PDF generation');
    }
    
    // Final data consistency check
    console.log('\n🔍 Data Consistency Check:');
    console.log('- Total entries in data:', allSectionsData.entries.length);
    console.log('- Unique class groups in entries:', [...new Set(allSectionsData.entries.map(entry => entry.class_group))].length);
    console.log('- Class groups from pagination:', allSectionsData.pagination?.class_groups?.length || 0);
    console.log('- Total class groups reported:', allSectionsData.pagination?.total_class_groups || 0);
    
    // If there's a mismatch, log it for debugging
    const entriesClassGroups = [...new Set(allSectionsData.entries.map(entry => entry.class_group))];
    const paginationClassGroups = allSectionsData.pagination?.class_groups || [];
    const totalReported = allSectionsData.pagination?.total_class_groups || 0;
    
    if (entriesClassGroups.length !== paginationClassGroups.length) {
      console.warn(`⚠️  Mismatch: ${entriesClassGroups.length} class groups in entries vs ${paginationClassGroups.length} in pagination`);
    }
    
    if (totalReported > 0 && totalReported !== paginationClassGroups.length) {
      console.warn(`⚠️  Mismatch: ${paginationClassGroups.length} class groups in pagination vs ${totalReported} total reported`);
    }
    
    // Get ALL unique class groups from the entries data
    const allClassGroupsFromEntries = [...new Set(allSectionsData.entries.map(entry => entry.class_group))];
    console.log('Class groups found in entries:', allClassGroupsFromEntries);
    
    // Get class groups from pagination if available
    // Use all_class_groups for complete list, fallback to class_groups
    const classGroupsFromPagination = allSectionsData.pagination?.all_class_groups || 
                                    allSectionsData.pagination?.class_groups || [];
    console.log('Class groups from pagination:', classGroupsFromPagination);
    
    // Use the union of both sources to ensure we don't miss any sections
    const allClassGroups = [...new Set([...allClassGroupsFromEntries, ...classGroupsFromPagination])];
    
    // Sort class groups logically (batch first, then section)
    allClassGroups.sort((a, b) => {
      const [batchA, sectionA] = a.split('-');
      const [batchB, sectionB] = b.split('-');
      if (batchA !== batchB) return batchA.localeCompare(batchB);
      return (sectionA || '').localeCompare(sectionB || '');
    });
    
    console.log('Final sorted class groups to process:', allClassGroups);
    console.log('Total sections to include:', allClassGroups.length);
    
    // Verify each class group has data
    const classGroupsWithData = [];
    const classGroupsWithoutData = [];
    
    allClassGroups.forEach(classGroup => {
      const entries = allSectionsData.entries.filter(entry => entry.class_group === classGroup);
      if (entries.length > 0) {
        classGroupsWithData.push(classGroup);
        console.log(`✅ ${classGroup}: ${entries.length} entries`);
        
        // Debug: Show sample entries for this section
        const sampleEntries = entries.slice(0, 3).map(e => ({
          day: e.day,
          period: e.period,
          subject: e.subject,
          subject_code: e.subject_code,
          teacher: e.teacher
        }));
        console.log(`   Sample entries:`, sampleEntries);
      } else {
        classGroupsWithoutData.push(classGroup);
        console.log(`⚠️  ${classGroup}: NO DATA`);
      }
    });
    
    if (classGroupsWithoutData.length > 0) {
      console.warn(`⚠️  ${classGroupsWithoutData.length} class groups have no data:`, classGroupsWithoutData);
      console.warn('This might indicate a data issue or API filtering problem');
    }
    
    console.log(`📊 Summary: ${classGroupsWithData.length} sections with data, ${classGroupsWithoutData.length} without data`);
    
    // Additional verification: check if any sections from the original data are missing
    if (timetableData && timetableData.entries) {
      const originalClassGroups = [...new Set(timetableData.entries.map(entry => entry.class_group))];
      const missingFromOriginal = originalClassGroups.filter(group => !allClassGroups.includes(group));
      const extraInOriginal = allClassGroups.filter(group => !originalClassGroups.includes(group));
      
      if (missingFromOriginal.length > 0) {
        console.warn(`⚠️  Sections in original data but missing from API:`, missingFromOriginal);
      }
      if (extraInOriginal.length > 0) {
        console.log(`✅ Sections in API but not in original data:`, extraInOriginal);
      }
    }
    
    // Create PDF document
    const doc = new jsPDF('p', 'mm', 'a4');
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
    
    let currentY = 60;
    let processedCount = 0;
    const processedSections = new Set();
    
    // Process each class group that has data
    for (let i = 0; i < classGroupsWithData.length; i++) {
      const classGroup = classGroupsWithData[i];
      
      // Safety check: prevent duplicate processing
      if (processedSections.has(classGroup)) {
        console.log(`⚠️  Section ${classGroup} already processed, skipping...`);
        continue;
      }
      
      // Filter entries for this class group
      const classGroupEntries = allSectionsData.entries.filter(entry => entry.class_group === classGroup);
      
      if (classGroupEntries.length === 0) {
        console.log(`⚠️  No entries found for ${classGroup}, skipping...`);
        continue;
      }
      
      // Additional safety check: ensure we have valid data
      if (!classGroupEntries[0].day || !classGroupEntries[0].period) {
        console.warn(`⚠️  Section ${classGroup} has invalid entry data, skipping...`);
        continue;
      }
      
      // Mark this section as processed
      processedSections.add(classGroup);
      processedCount++;
      
      console.log(`📝 Processing section ${classGroup} (${processedCount}/${classGroupsWithData.length}) with ${classGroupEntries.length} entries`);
      
      // Start each section on a new page (except the first one)
      if (i > 0) {
        doc.addPage();
        currentY = 30;
        console.log(`📄 Added new page for section ${classGroup}`);
      }
      
      // Class group header
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      const batchName = classGroup.split('-')[0] || classGroup;
      const sectionName = classGroup.split('-')[1] || '';
      const sectionText = sectionName ? `SECTION-${sectionName}` : '';
      
      // Get batch description
      let batchDescription = 'Academic Year';
      if (allSectionsData.semester) {
        batchDescription = allSectionsData.semester;
      } else if (allSectionsData.academic_year) {
        batchDescription = `${allSectionsData.academic_year} Academic Year`;
      }
      
      doc.text(`TIMETABLE OF ${batchName}-BATCH ${sectionText} (${batchDescription})`, pageWidth / 2, currentY, { align: 'center' });
      currentY += 10;
      
      // Effective date
      doc.setFontSize(12);
      doc.setFont('helvetica', 'normal');
      const today = new Date();
      const dateString = today.toLocaleDateString('en-GB').split('/').join('-');
      doc.text(`w.e.f ${dateString}`, pageWidth / 2, currentY, { align: 'center' });
      currentY += 15;
      
      // Create timetable table
      const tableData = [];
      
      // Add header row with days
      const headerRow = ['Periods'];
      allSectionsData.days.forEach(day => {
        headerRow.push(day);
      });
      tableData.push(headerRow);
      
      // Add lab/room numbers row
      const roomRow = ['Lab. No.'];
      const defaultRooms = ['Lab. No. 01', 'Lab. No. 02', 'Lab. No. 03', 'Lab. No. 01', 'Lab. No. 02'];
      allSectionsData.days.forEach((day, index) => {
        roomRow.push(defaultRooms[index] || 'Lab. No. 01');
      });
      tableData.push(roomRow);
      
      // Add time slots and subjects
      allSectionsData.timeSlots.forEach((timeSlot, index) => {
        let formattedTimeSlot = timeSlot;
        if (timeSlot.includes(' to ')) {
          formattedTimeSlot = timeSlot.replace(' to ', ' - ');
        }
        formattedTimeSlot = formattedTimeSlot.replace(/\s+/g, ' ').trim();
        
        const row = [formattedTimeSlot];
        
        allSectionsData.days.forEach(day => {
          // Find entry by day and period
          let entry = classGroupEntries.find(e => 
            e.day === day && e.period === (index + 1)
          );
          
          // If not found, try normalized day names
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
            let subjectCode = entry.subject_code || entry.subject;
            let cellContent = subjectCode || '';
            
            // Add room information if different from default
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
      
      // Calculate column widths
      const numDays = allSectionsData.days.length;
      const periodColumnWidth = 35;
      const remainingWidth = contentWidth - periodColumnWidth;
      const dayColumnWidth = Math.max(remainingWidth / numDays, 30);
      
      // Generate the table
      console.log(`  📊 Creating table for ${classGroup} with ${tableData.length} rows`);
      autoTable(doc, {
        head: [tableData[0], tableData[1]],
        body: tableData.slice(2),
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
          overflow: 'linebreak',
          halign: 'center',
        },
        headStyles: {
          fillColor: [70, 70, 70],
          textColor: [255, 255, 255],
          fontSize: 11,
          fontStyle: 'bold',
          halign: 'center',
        },
        columnStyles: {
          0: { cellWidth: periodColumnWidth, halign: 'center', cellPadding: 2, fontSize: 9 },
          ...Array.from({ length: numDays }, (_, i) => i + 1).reduce((acc, colIndex) => {
            acc[colIndex] = { cellWidth: dayColumnWidth, halign: 'center' };
            return acc;
          }, {})
        },
        didDrawPage: function (data) {
          doc.setFontSize(10);
          doc.text(`Page ${doc.internal.getNumberOfPages()}`, pageWidth - margin, pageHeight - 10);
        }
      });
      
      console.log(`  ✅ Table created for ${classGroup}. Final Y: ${doc.lastAutoTable.finalY}`);
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
      const subjectGroups = {};
      
      // Group entries by subject
      classGroupEntries.forEach(entry => {
        const subjectName = entry.subject || '';
        const cleanSubjectName = subjectName.replace(' (PR)', '').trim();
        
        if (!subjectGroups[cleanSubjectName]) {
          subjectGroups[cleanSubjectName] = {
            theory: null,
            practical: null,
            subjectName: cleanSubjectName
          };
        }
        
        if (entry.is_practical) {
          subjectGroups[cleanSubjectName].practical = entry;
        } else {
          subjectGroups[cleanSubjectName].theory = entry;
        }
      });
      
      // Convert grouped data to table format
      Object.values(subjectGroups).forEach((group, index) => {
        const theoryEntry = group.theory;
        const practicalEntry = group.practical;
        
        // Determine credit hours
        let creditHours = '';
        if (theoryEntry && practicalEntry) {
          const theoryCredits = theoryEntry.credits || 3;
          creditHours = `${theoryCredits}+1`;
        } else if (theoryEntry) {
          const theoryCredits = theoryEntry.credits || 3;
          creditHours = `${theoryCredits}+0`;
        } else if (practicalEntry) {
          creditHours = `0+1`;
        }
        
        // Combine teacher names
        let teacherNames = '';
        if (theoryEntry && practicalEntry) {
          const theoryTeacher = theoryEntry.teacher || '--';
          const practicalTeacher = practicalEntry.teacher || '--';
          teacherNames = `${theoryTeacher} (Th)/${practicalTeacher}`;
        } else if (theoryEntry) {
          teacherNames = theoryEntry.teacher || '--';
        } else if (practicalEntry) {
          teacherNames = practicalEntry.teacher || '--';
        }
        
        teacherData.push([
          index + 1,
          group.subjectName,
          creditHours,
          teacherNames
        ]);
      });
      
      // Add teachers table
      console.log(`  👥 Creating teachers table for ${classGroup} with ${teacherData.length} subjects`);
      autoTable(doc, {
        head: [['S.', 'SUBJECT NAME', 'C.H', 'TEACHER']],
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
          0: { cellWidth: 15, halign: 'center' },
          1: { cellWidth: 60, halign: 'left' },
          2: { cellWidth: 25, halign: 'center' },
          3: { cellWidth: 80 },
        }
      });
      
      console.log(`  ✅ Teachers table created for ${classGroup}. Final Y: ${doc.lastAutoTable.finalY}`);
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
      
      currentY += 30;
      
      console.log(`✅ Completed processing section ${classGroup}`);
    }
    
    // Final verification
    console.log(`\n📋 PDF Generation Summary:`);
    console.log(`- Total sections available: ${allClassGroups.length}`);
    console.log(`- Sections with data: ${classGroupsWithData.length}`);
    console.log(`- Sections processed: ${processedCount}`);
    console.log(`- Total PDF pages: ${doc.internal.getNumberOfPages()}`);
    console.log(`- Processed sections:`, Array.from(processedSections));
    
    if (processedCount !== classGroupsWithData.length) {
      console.warn(`⚠️  Mismatch: processed ${processedCount} but expected ${classGroupsWithData.length}`);
      
      // Find which sections were not processed
      const unprocessedSections = classGroupsWithData.filter(group => !processedSections.has(group));
      if (unprocessedSections.length > 0) {
        console.error(`❌ Unprocessed sections:`, unprocessedSections);
        throw new Error(`Failed to process ${unprocessedSections.length} sections: ${unprocessedSections.join(', ')}`);
      }
    }
    
    if (classGroupsWithData.length === 0) {
      console.error(`❌ No sections with data found!`);
      throw new Error('No timetable data available for any sections');
    }
    
    // Verify that all sections with data were included
    const missingSections = classGroupsWithData.filter(group => !processedSections.has(group));
    if (missingSections.length > 0) {
      console.error(`❌ Critical error: ${missingSections.length} sections were not included in the PDF:`, missingSections);
      throw new Error(`PDF generation incomplete: ${missingSections.length} sections missing`);
    }
    
    console.log(`✅ All ${processedCount} sections successfully included in PDF`);
    
    // Save the PDF
    const fileName = `timetable_${processedCount}_sections_${new Date().toISOString().split('T')[0]}.pdf`;
    console.log(`💾 Saving PDF as: ${fileName}`);
    doc.save(fileName);
    
    console.log(`🎉 PDF generation completed successfully!`);
    
  } catch (error) {
    console.error('❌ Error generating PDF:', error);
    throw error;
  }
};
