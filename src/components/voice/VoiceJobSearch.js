import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  Container,
  Fade,
} from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import CloseIcon from '@mui/icons-material/Close';
import useVoiceJobSearch from '../../hooks/useVoiceJobSearch';
import VoiceSearch from './VoiceSearch';
import JobMatchResults from './JobMatchResults';

/**
 * VoiceJobSearch component integrates voice recognition with job search functionality
 */
const VoiceJobSearch = () => {
  const [showVoiceSearch, setShowVoiceSearch] = useState(false);
  const {
    voiceQuery,
    matchingJobs,
    loading,
    error,
    backendStatus,
    handleVoiceQuery,
    resetSearch
  } = useVoiceJobSearch();

  const handleVoiceSearchComplete = async (transcript) => {
    await handleVoiceQuery(transcript);
    setShowVoiceSearch(false);
  };

  const handleVoiceSearchClose = () => {
    setShowVoiceSearch(false);
  };

  const handleApplyJob = (job) => {
    console.log('Applying for job:', job);
    // Implement job application logic here
    alert(`Applied for ${job.title} at ${job.company}`);
  };

  const handleStartNewSearch = () => {
    resetSearch();
    setShowVoiceSearch(true);
  };

  return (
    <Container maxWidth="lg">
      <Paper sx={{ p: 4, my: 4 }}>
        <Typography variant="h4" gutterBottom>
          Voice Job Search
        </Typography>
        
        <Typography variant="body1" paragraph>
          Use your voice to search for jobs by describing what you're looking for.
          Our AI will analyze your requirements and find the best matches.
        </Typography>
        
        {backendStatus === 'disconnected' && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            The AI job search backend is not connected. Please make sure the Python backend is running.
          </Alert>
        )}
        
        {error && !loading && !showVoiceSearch && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        
        {!showVoiceSearch && !voiceQuery && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              startIcon={<MicIcon />}
              onClick={() => setShowVoiceSearch(true)}
              disabled={backendStatus === 'disconnected'}
              sx={{ py: 1.5, px: 3, borderRadius: 2 }}
            >
              Start Voice Search
            </Button>
          </Box>
        )}
        
        {showVoiceSearch && (
          <Fade in={showVoiceSearch}>
            <Box sx={{ my: 3 }}>
              <VoiceSearch
                onSearchComplete={handleVoiceSearchComplete}
                onClose={handleVoiceSearchClose}
                processing={loading}
              />
            </Box>
          </Fade>
        )}
        
        {voiceQuery && !showVoiceSearch && (
          <Fade in={!showVoiceSearch}>
            <Box>
              <JobMatchResults
                voiceQuery={voiceQuery}
                matchingJobs={matchingJobs}
                loading={loading}
                error={error}
                onApply={handleApplyJob}
              />
              
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <Button
                  variant="outlined"
                  color="primary"
                  startIcon={<MicIcon />}
                  onClick={handleStartNewSearch}
                  disabled={backendStatus === 'disconnected'}
                >
                  New Voice Search
                </Button>
              </Box>
            </Box>
          </Fade>
        )}
      </Paper>
    </Container>
  );
};

export default VoiceJobSearch;
