import React from 'react';
import {
  Box,
  Typography,
  Chip,
} from '@mui/material';

/**
 * SkillsDisplay component to display extracted skills
 */
const SkillsDisplay = ({ skills, title = "Key Skills" }) => {
  if (!skills || skills.length === 0) return null;
  
  return (
    <Box sx={{ mt: 4, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {skills.map((skill, index) => {
          // Determine the label based on the skill structure
          let skillLabel = '';
          if (typeof skill === 'string') {
            skillLabel = skill;
          } else if (typeof skill === 'object') {
            if (skill.skill) skillLabel = skill.skill;
            else if (skill.name) skillLabel = skill.name;
            else skillLabel = JSON.stringify(skill);
          } else {
            skillLabel = String(skill);
          }
          
          return (
            <Chip 
              key={index} 
              label={skillLabel} 
              color={index < 5 ? "primary" : "default"}
              variant={index < 3 ? "filled" : "outlined"}
            />
          );
        })}
      </Box>
    </Box>
  );
};

export default SkillsDisplay;
