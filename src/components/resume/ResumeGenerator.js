import React from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Grid,
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  GetApp as GetAppIcon,
} from '@mui/icons-material';
import useResumeGenerator from '../../hooks/useResumeGenerator';
import ResumePreview from './ResumePreview';
import SkillsDisplay from './SkillsDisplay';
import { generatePdfResume, generateWordResume } from '../../services/resume/documentGenerationService';

const ResumeGenerator = () => {
  const {
    jobDescription,
    setJobDescription,
    resume,
    setResume,
    extractedSkills,
    generatedResume,
    matchScore,
    loading,
    error,
    backendStatus,
    handleAnalyze,
    handleReset
  } = useResumeGenerator();

  return (
    <Box sx={{ width: '100%', mb: 4 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {backendStatus === 'disconnected' && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          The AI resume backend is not connected. Please make sure the Python backend is running.
        </Alert>
      )}

      <Paper sx={{ p: 3 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            AI Resume Generator
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Tailor your resume to job descriptions using AI and NLP
          </Typography>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              multiline
              rows={10}
              label="Job Description"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the job description here..."
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              multiline
              rows={10}
              label="Your Resume"
              value={resume}
              onChange={(e) => setResume(e.target.value)}
              placeholder="Paste your current resume here..."
            />
          </Grid>
        </Grid>

        <Box sx={{ display: 'flex', justifyContent: 'center', my: 3, gap: 2 }}>
          <Button 
            variant="contained" 
            color="primary" 
            size="large"
            onClick={handleAnalyze}
            disabled={loading || backendStatus === 'disconnected'}
            startIcon={loading ? <CircularProgress size={24} color="inherit" /> : <AnalyticsIcon />}
          >
            {loading ? 'Analyzing...' : 'Analyze & Generate Resume'}
          </Button>
          <Button 
            variant="outlined" 
            color="secondary" 
            size="large"
            onClick={handleReset}
            disabled={loading}
          >
            Reset
          </Button>
        </Box>

        {extractedSkills.length > 0 && (
          <SkillsDisplay 
            skills={extractedSkills} 
            title="Key Skills Extracted from Job Description" 
          />
        )}

        {generatedResume && (
          <>
            <ResumePreview generatedResume={generatedResume} matchScore={matchScore} />
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3, gap: 2 }}>
              <Button 
                variant="contained" 
                color="primary" 
                onClick={() => generatePdfResume(generatedResume)}
                startIcon={<GetAppIcon />}
              >
                Download PDF
              </Button>
              <Button 
                variant="outlined" 
                color="primary" 
                onClick={() => generateWordResume(generatedResume)}
                startIcon={<GetAppIcon />}
              >
                Download Word
              </Button>
            </Box>
          </>
        )}
      </Paper>
    </Box>
  );
};

export default ResumeGenerator;
