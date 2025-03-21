import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Stepper,
  Step,
  StepLabel,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Divider,
} from '@mui/material';
import {
  Description as DescriptionIcon,
  Person as PersonIcon,
  Style as StyleIcon,
  GetApp as GetAppIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  CloudUpload as CloudUploadIcon,
  LinkedIn as LinkedInIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { generateFinalResume } from '../../services/resumeGenerationService';

const steps = ['Job Description', 'Your Profile', 'Customize', 'Generate & Download'];

const ResumeGenerator = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [candidateProfile, setCandidateProfile] = useState({
    personalInfo: {
      name: '',
      email: '',
      phone: '',
      location: '',
    },
    experience: [],
    education: [],
    skills: [],
  });
  const [preferences, setPreferences] = useState({
    template: 'modern',
    tone: 'professional',
    format: 'chronological',
  });
  const [generatedResume, setGeneratedResume] = useState(null);

  const handleNext = async () => {
    if (activeStep === steps.length - 1) {
      try {
        setLoading(true);
        setError(null);

        const result = await generateFinalResume(
          jobDescription,
          candidateProfile,
          preferences,
          preferences.template
        );

        setGeneratedResume(result);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    } else {
      setActiveStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleImportLinkedIn = () => {
    // Mock LinkedIn import
    setCandidateProfile({
      personalInfo: {
        name: 'John Doe',
        email: 'john@example.com',
        phone: '123-456-7890',
        location: 'New York, NY',
      },
      experience: [
        {
          title: 'Senior Software Engineer',
          company: 'Tech Corp',
          duration: '2020 - Present',
          description: 'Led development of cloud applications',
        },
      ],
      education: [
        {
          degree: 'BS Computer Science',
          school: 'Tech University',
          year: '2018',
        },
      ],
      skills: ['JavaScript', 'React', 'Node.js', 'AWS'],
    });
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              multiline
              rows={6}
              label="Job Description"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the job description here..."
            />
          </Box>
        );

      case 1:
        return (
          <Box sx={{ mt: 2 }}>
            <Button
              variant="outlined"
              startIcon={<LinkedInIcon />}
              onClick={handleImportLinkedIn}
              sx={{ mb: 2 }}
            >
              Import from LinkedIn
            </Button>
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Full Name"
                  value={candidateProfile.personalInfo.name}
                  onChange={(e) =>
                    setCandidateProfile({
                      ...candidateProfile,
                      personalInfo: {
                        ...candidateProfile.personalInfo,
                        name: e.target.value,
                      },
                    })
                  }
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Email"
                  value={candidateProfile.personalInfo.email}
                  onChange={(e) =>
                    setCandidateProfile({
                      ...candidateProfile,
                      personalInfo: {
                        ...candidateProfile.personalInfo,
                        email: e.target.value,
                      },
                    })
                  }
                />
              </Grid>
            </Grid>
          </Box>
        );

      case 2:
        return (
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth>
                  <InputLabel>Template</InputLabel>
                  <Select
                    value={preferences.template}
                    label="Template"
                    onChange={(e) =>
                      setPreferences({ ...preferences, template: e.target.value })
                    }
                  >
                    <MenuItem value="modern">Modern</MenuItem>
                    <MenuItem value="classic">Classic</MenuItem>
                    <MenuItem value="creative">Creative</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth>
                  <InputLabel>Tone</InputLabel>
                  <Select
                    value={preferences.tone}
                    label="Tone"
                    onChange={(e) =>
                      setPreferences({ ...preferences, tone: e.target.value })
                    }
                  >
                    <MenuItem value="professional">Professional</MenuItem>
                    <MenuItem value="casual">Casual</MenuItem>
                    <MenuItem value="confident">Confident</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth>
                  <InputLabel>Format</InputLabel>
                  <Select
                    value={preferences.format}
                    label="Format"
                    onChange={(e) =>
                      setPreferences({ ...preferences, format: e.target.value })
                    }
                  >
                    <MenuItem value="chronological">Chronological</MenuItem>
                    <MenuItem value="functional">Functional</MenuItem>
                    <MenuItem value="hybrid">Hybrid</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Box>
        );

      case 3:
        return (
          <Box sx={{ mt: 2 }}>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                <CircularProgress />
              </Box>
            ) : generatedResume ? (
              <Box>
                <Alert severity="success" sx={{ mb: 2 }}>
                  Resume generated successfully! ATS Score: {generatedResume.atsCheck.score}
                </Alert>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={8}>
                    <Paper sx={{ p: 2 }}>
                      <Typography variant="h6" gutterBottom>
                        {candidateProfile.personalInfo.name}
                      </Typography>
                      <Typography color="textSecondary" gutterBottom>
                        {candidateProfile.personalInfo.email} |{' '}
                        {candidateProfile.personalInfo.location}
                      </Typography>
                      <Divider sx={{ my: 2 }} />
                      {/* Display generated resume content here */}
                    </Paper>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          ATS Analysis
                        </Typography>
                        {generatedResume.atsCheck.suggestions.map((suggestion, index) => (
                          <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                            • {suggestion}
                          </Typography>
                        ))}
                      </CardContent>
                    </Card>
                    <Box sx={{ mt: 2 }}>
                      <Button
                        fullWidth
                        variant="contained"
                        startIcon={<GetAppIcon />}
                        onClick={() => {
                          // Handle download
                        }}
                      >
                        Download PDF
                      </Button>
                    </Box>
                  </Grid>
                </Grid>
              </Box>
            ) : error ? (
              <Alert severity="error">{error}</Alert>
            ) : null}
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        AI Resume Generator
      </Typography>
      <Stepper activeStep={activeStep} sx={{ my: 3 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      {renderStepContent(activeStep)}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
        {activeStep > 0 && (
          <Button onClick={handleBack} sx={{ mr: 1 }}>
            Back
          </Button>
        )}
        <Button
          variant="contained"
          onClick={handleNext}
          disabled={loading}
        >
          {activeStep === steps.length - 1 ? 'Generate Resume' : 'Next'}
        </Button>
      </Box>
    </Paper>
  );
};

export default ResumeGenerator;
