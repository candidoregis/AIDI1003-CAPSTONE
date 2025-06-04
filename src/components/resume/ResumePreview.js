import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Divider,
  Chip,
} from '@mui/material';

/**
 * ResumePreview component to display the generated resume
 */
const ResumePreview = ({ generatedResume, matchScore }) => {
  if (!generatedResume) return null;
  
  // Check if generatedResume is a string (plain text resume)
  const isPlainText = typeof generatedResume === 'string';
  
  // If it's a plain text resume, display it as is with line breaks preserved
  if (isPlainText) {
    return (
      <Box sx={{ mt: 4 }}>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Job Match Score: {(matchScore * 100).toFixed(1)}%
        </Typography>
        
        <Paper sx={{ p: 3 }}>
          <Typography variant="body1" component="pre" sx={{ 
            whiteSpace: 'pre-wrap',
            fontFamily: 'inherit',
            fontSize: 'inherit'
          }}>
            {generatedResume}
          </Typography>
        </Paper>
      </Box>
    );
  }
  
  // Otherwise, use the structured resume display
  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        Job Match Score: {(matchScore * 100).toFixed(1)}%
      </Typography>
      
      <Paper sx={{ p: 3 }}>
        {/* Contact Information */}
        <Typography variant="h5" align="center" gutterBottom>
          {generatedResume.contact?.name || 'Resume'}
        </Typography>
        <Typography variant="body2" align="center" gutterBottom>
          {generatedResume.contact?.email || ''} | {generatedResume.contact?.phone || ''} | {generatedResume.contact?.location || ''}
        </Typography>
        
        <Divider sx={{ my: 2 }} />
        
        {/* Summary */}
        <Typography variant="h6" gutterBottom>
          Professional Summary
        </Typography>
        <Typography variant="body1" paragraph>
          {typeof generatedResume.summary === 'object' 
            ? JSON.stringify(generatedResume.summary) 
            : (generatedResume.summary || 'No summary available')}
        </Typography>
        
        {/* Skills */}
        <Typography variant="h6" gutterBottom>
          Skills
        </Typography>
        <Box sx={{ mb: 2 }}>
          {Array.isArray(generatedResume.skills) ? 
            generatedResume.skills.map((skill, index) => (
              <Chip 
                key={index} 
                label={typeof skill === 'object' ? (skill.skill || skill.name || JSON.stringify(skill)) : skill} 
                sx={{ m: 0.5 }} 
              />
            )) : 
            <Typography variant="body1">
              {typeof generatedResume.skills === 'object' ? 
                JSON.stringify(generatedResume.skills) : 
                (generatedResume.skills || 'No skills data available')}
            </Typography>
          }
        </Box>
        
        {/* Experience */}
        <Typography variant="h6" gutterBottom>
          Experience
        </Typography>
        {Array.isArray(generatedResume.experience) ? 
          generatedResume.experience.map((exp, index) => (
            <Box key={index} sx={{ mb: 2 }}>
              <Typography variant="body1">
                {typeof exp === 'object' ? JSON.stringify(exp) : exp}
              </Typography>
            </Box>
          )) : 
          <Typography variant="body1">
            {typeof generatedResume.experience === 'object' ? 
              JSON.stringify(generatedResume.experience) : 
              (generatedResume.experience || 'No experience data available')}
          </Typography>
        }
        
        {/* Education */}
        <Typography variant="h6" gutterBottom>
          Education
        </Typography>
        {Array.isArray(generatedResume.education) ? 
          generatedResume.education.map((edu, index) => (
            <Box key={index} sx={{ mb: 1 }}>
              <Typography variant="body1">
                {typeof edu === 'object' ? JSON.stringify(edu) : edu}
              </Typography>
            </Box>
          )) :
          <Typography variant="body1">
            {typeof generatedResume.education === 'object' ? 
              JSON.stringify(generatedResume.education) : 
              (generatedResume.education || 'No education data available')}
          </Typography>
        }
      </Paper>
    </Box>
  );
};

export default ResumePreview;
