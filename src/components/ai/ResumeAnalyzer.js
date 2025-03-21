import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
} from '@mui/material';
import { analyzeResume, analyzeSkillGaps } from '../../services/mockAiService';

const ResumeAnalyzer = ({ resumeText, jobRequirements }) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyzeDocument = async () => {
    setLoading(true);
    setError(null);
    try {
      const resumeAnalysis = await analyzeResume(resumeText);
      const skillGaps = await analyzeSkillGaps(jobRequirements, resumeAnalysis.skills);
      
      setAnalysis({
        ...resumeAnalysis,
        skillGaps
      });
    } catch (err) {
      setError('Failed to analyze resume. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!analysis) {
    return null;
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          AI Resume Analysis
        </Typography>
        
        <Box mb={3}>
          <Typography variant="subtitle1" color="primary" gutterBottom>
            Key Skills
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1}>
            {analysis.skills.map((skill, index) => (
              <Chip 
                key={index}
                label={skill}
                color="primary"
                variant="outlined"
                size="small"
              />
            ))}
          </Box>
        </Box>

        <Box mb={3}>
          <Typography variant="subtitle1" color="primary" gutterBottom>
            Experience & Education
          </Typography>
          <List dense>
            <ListItem>
              <ListItemText 
                primary="Years of Experience"
                secondary={analysis.yearsOfExperience}
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="Education Level"
                secondary={analysis.educationLevel}
              />
            </ListItem>
          </List>
        </Box>

        <Box mb={3}>
          <Typography variant="subtitle1" color="primary" gutterBottom>
            Key Achievements
          </Typography>
          <List dense>
            {analysis.achievements.map((achievement, index) => (
              <ListItem key={index}>
                <ListItemText primary={achievement} />
              </ListItem>
            ))}
          </List>
        </Box>

        <Box mb={3}>
          <Typography variant="subtitle1" color="error" gutterBottom>
            Skill Gaps
          </Typography>
          <List dense>
            {analysis.skillGaps.missing.map((skill, index) => (
              <ListItem key={index}>
                <ListItemText 
                  primary={skill.name}
                  secondary={`Suggested Training: ${skill.training}`}
                />
              </ListItem>
            ))}
          </List>
        </Box>

        <Box>
          <Typography variant="subtitle1" color="primary" gutterBottom>
            Recommended Roles
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1}>
            {analysis.recommendedRoles.map((role, index) => (
              <Chip 
                key={index}
                label={role}
                color="success"
                variant="outlined"
                size="small"
              />
            ))}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ResumeAnalyzer;
