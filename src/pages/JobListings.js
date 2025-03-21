import React from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Box,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Search as SearchIcon,
  LocationOn as LocationIcon,
  Business as BusinessIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';

const JobCard = ({ title, department, location, type, postedDate }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <BusinessIcon sx={{ mr: 1, fontSize: 20 }} />
        <Typography variant="body2" color="text.secondary">
          {department}
        </Typography>
      </Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <LocationIcon sx={{ mr: 1, fontSize: 20 }} />
        <Typography variant="body2" color="text.secondary">
          {location}
        </Typography>
      </Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <ScheduleIcon sx={{ mr: 1, fontSize: 20 }} />
        <Typography variant="body2" color="text.secondary">
          Posted {postedDate}
        </Typography>
      </Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Chip label={type} color="primary" size="small" />
        <Button variant="contained" color="primary">
          View Details
        </Button>
      </Box>
    </CardContent>
  </Card>
);

const JobListings = () => {
  const jobs = [
    {
      title: 'Senior Software Engineer',
      department: 'Engineering',
      location: 'New York, NY',
      type: 'Full-time',
      postedDate: '2 days ago',
    },
    {
      title: 'Product Manager',
      department: 'Product',
      location: 'San Francisco, CA',
      type: 'Full-time',
      postedDate: '3 days ago',
    },
    {
      title: 'UX Designer',
      department: 'Design',
      location: 'Remote',
      type: 'Contract',
      postedDate: '1 week ago',
    },
    {
      title: 'Marketing Manager',
      department: 'Marketing',
      location: 'Chicago, IL',
      type: 'Full-time',
      postedDate: '5 days ago',
    },
  ];

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Job Listings
      </Typography>
      
      <Box sx={{ mb: 4 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search jobs..."
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      <Grid container spacing={3}>
        {jobs.map((job, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <JobCard {...job} />
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default JobListings;
