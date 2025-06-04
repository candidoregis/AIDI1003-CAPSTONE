import { jsPDF } from 'jspdf';
import { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType } from 'docx';
import { saveAs } from 'file-saver';

/**
 * Generates a PDF resume from the provided resume data
 * @param {Object} resumeData - The resume data to generate a PDF from
 */
export const generatePdfResume = (resumeData) => {
  if (!resumeData) return;
  
  const doc = new jsPDF();
  const margin = 15;
  let y = margin;
  
  // Set font styles
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(18);
  
  // Check if contact and name exist before accessing
  const contactName = resumeData.contact && resumeData.contact.name ? 
    resumeData.contact.name : 'Resume';
  doc.text(contactName, margin, y);
  y += 8;
  
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(12);
  
  // Check if contact properties exist before accessing
  const contactEmail = resumeData.contact && resumeData.contact.email ? 
    resumeData.contact.email : '';
  const contactPhone = resumeData.contact && resumeData.contact.phone ? 
    resumeData.contact.phone : '';
  const contactLocation = resumeData.contact && resumeData.contact.location ? 
    resumeData.contact.location : '';
  
  doc.text(`${contactEmail} | ${contactPhone} | ${contactLocation}`, margin, y);
  y += 10;
  
  // Add summary
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(14);
  doc.text('Professional Summary', margin, y);
  y += 6;
  
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(12);
  
  // Split summary into multiple lines if needed
  const summaryText = typeof resumeData.summary === 'object' ? 
    JSON.stringify(resumeData.summary) : 
    (resumeData.summary || 'No summary available');
  const summaryLines = doc.splitTextToSize(summaryText, doc.internal.pageSize.width - 2 * margin);
  doc.text(summaryLines, margin, y);
  y += summaryLines.length * 6 + 6;
  
  // Add skills
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(14);
  doc.text('Skills', margin, y);
  y += 6;
  
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(12);
  const skillsText = Array.isArray(resumeData.skills) 
    ? resumeData.skills.map(skill => 
        typeof skill === 'object' 
          ? (skill.skill || skill.name || JSON.stringify(skill)) 
          : skill
      ).join(', ') 
    : (typeof resumeData.skills === 'object' 
        ? JSON.stringify(resumeData.skills) 
        : String(resumeData.skills || ''));
  doc.text(skillsText, margin, y);
  y += 10;
  
  // Add experience
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(14);
  doc.text('Experience', margin, y);
  y += 6;
  
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(12);
  
  if (Array.isArray(resumeData.experience)) {
    resumeData.experience.forEach(exp => {
      const expText = typeof exp === 'object' ? JSON.stringify(exp) : exp;
      const expLines = doc.splitTextToSize(expText, doc.internal.pageSize.width - 2 * margin);
      doc.text(expLines, margin, y);
      y += expLines.length * 6 + 4;
      
      // Add a new page if we're running out of space
      if (y > doc.internal.pageSize.height - 30) {
        doc.addPage();
        y = margin;
      }
    });
  } else if (resumeData.experience) {
    const expText = typeof resumeData.experience === 'object' ? 
      JSON.stringify(resumeData.experience) : 
      String(resumeData.experience);
    const expLines = doc.splitTextToSize(expText, doc.internal.pageSize.width - 2 * margin);
    doc.text(expLines, margin, y);
    y += expLines.length * 6 + 4;
  }
  
  // Add education
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(14);
  doc.text('Education', margin, y);
  y += 6;
  
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(12);
  
  if (Array.isArray(resumeData.education)) {
    resumeData.education.forEach(edu => {
      const eduText = typeof edu === 'object' ? JSON.stringify(edu) : edu;
      const eduLines = doc.splitTextToSize(eduText, doc.internal.pageSize.width - 2 * margin);
      doc.text(eduLines, margin, y);
      y += eduLines.length * 6 + 4;
    });
  } else if (resumeData.education) {
    const eduText = typeof resumeData.education === 'object' ? 
      JSON.stringify(resumeData.education) : 
      String(resumeData.education);
    const eduLines = doc.splitTextToSize(eduText, doc.internal.pageSize.width - 2 * margin);
    doc.text(eduLines, margin, y);
    y += eduLines.length * 6 + 4;
  }
  
  // Save the PDF
  doc.save('tailored-resume.pdf');
};

/**
 * Generates a Word document resume from the provided resume data
 * @param {Object} resumeData - The resume data to generate a Word document from
 */
export const generateWordResume = async (resumeData) => {
  if (!resumeData) return;
  
  // Check if contact properties exist before accessing
  const contactName = resumeData.contact && resumeData.contact.name ? 
    resumeData.contact.name : 'Resume';
  const contactEmail = resumeData.contact && resumeData.contact.email ? 
    resumeData.contact.email : '';
  const contactPhone = resumeData.contact && resumeData.contact.phone ? 
    resumeData.contact.phone : '';
  const contactLocation = resumeData.contact && resumeData.contact.location ? 
    resumeData.contact.location : '';
  
  // Create document
  const doc = new Document({
    sections: [
      {
        properties: {},
        children: [
          // Contact information
          new Paragraph({
            text: contactName,
            heading: HeadingLevel.TITLE,
            alignment: AlignmentType.CENTER,
          }),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun(`${contactEmail} | ${contactPhone} | ${contactLocation}`),
            ],
          }),
          new Paragraph({}),
          
          // Summary
          new Paragraph({
            text: 'Professional Summary',
            heading: HeadingLevel.HEADING_1,
          }),
          new Paragraph({
            text: typeof resumeData.summary === 'object' 
              ? JSON.stringify(resumeData.summary) 
              : (resumeData.summary || 'No summary available'),
          }),
          new Paragraph({}),
          
          // Skills
          new Paragraph({
            text: 'Skills',
            heading: HeadingLevel.HEADING_1,
          }),
          new Paragraph({
            text: Array.isArray(resumeData.skills) 
              ? resumeData.skills.map(skill => 
                  typeof skill === 'object' 
                    ? (skill.skill || skill.name || JSON.stringify(skill)) 
                    : skill
                ).join(', ') 
              : (typeof resumeData.skills === 'object' 
                  ? JSON.stringify(resumeData.skills) 
                  : String(resumeData.skills || '')),
          }),
          new Paragraph({}),
          
          // Experience
          new Paragraph({
            text: 'Experience',
            heading: HeadingLevel.HEADING_1,
          }),
          ...(Array.isArray(resumeData.experience) 
            ? resumeData.experience.map(exp => 
                new Paragraph({
                  text: typeof exp === 'object' ? JSON.stringify(exp) : exp,
                })
              )
            : [new Paragraph({ 
                text: typeof resumeData.experience === 'object' 
                  ? JSON.stringify(resumeData.experience) 
                  : String(resumeData.experience || '') 
              })]
          ),
          new Paragraph({}),
          
          // Education
          new Paragraph({
            text: 'Education',
            heading: HeadingLevel.HEADING_1,
          }),
          ...(Array.isArray(resumeData.education) 
            ? resumeData.education.map(edu => 
                new Paragraph({
                  text: typeof edu === 'object' ? JSON.stringify(edu) : edu,
                })
              )
            : [new Paragraph({ 
                text: typeof resumeData.education === 'object' 
                  ? JSON.stringify(resumeData.education) 
                  : String(resumeData.education || '') 
              })]
          ),
        ],
      },
    ],
  });
  
  // Generate and save document - use blob directly instead of buffer
  Packer.toBlob(doc).then(blob => {
    saveAs(blob, 'tailored-resume.docx');
  });
};
