import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
  Button,
  Stack,
  LinearProgress,
  Tooltip
} from '@mui/material';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import WorkIcon from '@mui/icons-material/Work';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

const VoiceJobCard = ({ job, onApply }) => {
  const confidencePercent = Math.round(job.confidenceScore * 100);

  return (
    <Card 
      sx={{ 
        mb: 2,
        transition: 'transform 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4
        }
      }}
    >
      <CardContent>
        <Typography variant="h6" component="div" gutterBottom>
          {job.title}
        </Typography>
        
        <Typography color="text.secondary" gutterBottom>
          {job.company}
        </Typography>

        <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <LocationOnIcon fontSize="small" />
            <Typography variant="body2">{job.location}</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <WorkIcon fontSize="small" />
            <Typography variant="body2">{job.experience}</Typography>
          </Box>
        </Stack>

        <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
          {job.skills.map((skill) => (
            <Chip 
              key={skill} 
              label={skill} 
              size="small"
              sx={{ 
                bgcolor: 'primary.light',
                color: 'primary.contrastText'
              }} 
            />
          ))}
        </Stack>

        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <TrendingUpIcon color="primary" fontSize="small" />
            <Typography variant="body2">Match Confidence</Typography>
          </Box>
          <Tooltip title={`${confidencePercent}% match based on your voice search`}>
            <Box sx={{ width: '100%' }}>
              <LinearProgress 
                variant="determinate" 
                value={confidencePercent}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  bgcolor: 'grey.200',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 4
                  }
                }}
              />
            </Box>
          </Tooltip>
        </Box>

        <Button 
          variant="contained" 
          fullWidth
          onClick={() => onApply(job)}
          sx={{
            borderRadius: '20px',
            textTransform: 'none',
            py: 1
          }}
        >
          Apply Now
        </Button>
      </CardContent>
    </Card>
  );
};

export default VoiceJobCard;
