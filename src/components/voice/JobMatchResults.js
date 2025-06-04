import React from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Grid,
} from '@mui/material';
import VoiceJobCard from './VoiceJobCard';

/**
 * Component to display job matches from voice search
 */
const JobMatchResults = ({ 
  voiceQuery, 
  matchingJobs, 
  loading, 
  error, 
  onApply 
}) => {
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!voiceQuery) {
    return null;
  }

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h6" gutterBottom>
        Job Matches for: "{voiceQuery}"
      </Typography>
      
      {matchingJobs.length > 0 ? (
        <Grid container spacing={2}>
          {matchingJobs.map((job) => (
            <Grid item xs={12} md={6} key={job.id}>
              <VoiceJobCard job={job} onApply={onApply} />
            </Grid>
          ))}
        </Grid>
      ) : (
        <Alert severity="info">
          No matching jobs found. Try a different search query.
        </Alert>
      )}
    </Box>
  );
};

export default JobMatchResults;
