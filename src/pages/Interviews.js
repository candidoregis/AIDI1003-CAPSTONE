import React from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Avatar,
  Chip,
  Button,
  Divider,
} from '@mui/material';
import {
  EventNote as EventNoteIcon,
  Videocam as VideocamIcon,
  Person as PersonIcon,
} from '@mui/icons-material';

const InterviewCard = ({ candidate, position, date, time, type, interviewer }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Avatar sx={{ mr: 2 }}>{candidate[0]}</Avatar>
          <Box>
            <Typography variant="h6">{candidate}</Typography>
            <Typography variant="body2" color="text.secondary">
              {position}
            </Typography>
          </Box>
        </Box>
        <Chip
          label={type}
          color={type === 'Technical' ? 'primary' : 'secondary'}
          size="small"
        />
      </Box>

      <Divider sx={{ my: 2 }} />

      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <EventNoteIcon sx={{ mr: 1, fontSize: 20 }} />
        <Typography variant="body2">
          {date} at {time}
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <PersonIcon sx={{ mr: 1, fontSize: 20 }} />
        <Typography variant="body2">
          Interviewer: {interviewer}
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', gap: 1 }}>
        <Button
          variant="contained"
          startIcon={<VideocamIcon />}
          fullWidth
        >
          Join Meeting
        </Button>
      </Box>
    </CardContent>
  </Card>
);

const Interviews = () => {
  const interviews = [
    {
      candidate: 'John Smith',
      position: 'Senior Software Engineer',
      date: 'Feb 26, 2025',
      time: '10:00 AM',
      type: 'Technical',
      interviewer: 'David Wilson',
    },
    {
      candidate: 'Sarah Johnson',
      position: 'Product Manager',
      date: 'Feb 26, 2025',
      time: '2:00 PM',
      type: 'HR',
      interviewer: 'Lisa Anderson',
    },
    {
      candidate: 'Michael Brown',
      position: 'UX Designer',
      date: 'Feb 27, 2025',
      time: '11:30 AM',
      type: 'Technical',
      interviewer: 'James Taylor',
    },
    {
      candidate: 'Emily Davis',
      position: 'Marketing Manager',
      date: 'Feb 27, 2025',
      time: '3:30 PM',
      type: 'HR',
      interviewer: 'Robert Martin',
    },
  ];

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Upcoming Interviews
      </Typography>

      <Grid container spacing={3}>
        {interviews.map((interview, index) => (
          <Grid item xs={12} md={6} key={index}>
            <InterviewCard {...interview} />
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default Interviews;
