import React from 'react';
import {
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Avatar,
  Chip,
  IconButton,
  Box,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Search as SearchIcon,
  MoreVert as MoreVertIcon,
} from '@mui/icons-material';

const CandidateRow = ({ name, email, role, status, experience }) => (
  <TableRow hover>
    <TableCell>
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <Avatar sx={{ mr: 2 }}>{name[0]}</Avatar>
        <Box>
          <Typography variant="subtitle2">{name}</Typography>
          <Typography variant="body2" color="text.secondary">
            {email}
          </Typography>
        </Box>
      </Box>
    </TableCell>
    <TableCell>{role}</TableCell>
    <TableCell>{experience} years</TableCell>
    <TableCell>
      <Chip
        label={status}
        color={
          status === 'Hired'
            ? 'success'
            : status === 'In Progress'
            ? 'warning'
            : 'default'
        }
        size="small"
      />
    </TableCell>
    <TableCell align="right">
      <IconButton size="small">
        <MoreVertIcon />
      </IconButton>
    </TableCell>
  </TableRow>
);

const Candidates = () => {
  const candidates = [
    {
      name: 'John Smith',
      email: 'john.smith@email.com',
      role: 'Software Engineer',
      experience: 5,
      status: 'In Progress',
    },
    {
      name: 'Sarah Johnson',
      email: 'sarah.j@email.com',
      role: 'Product Manager',
      experience: 8,
      status: 'Hired',
    },
    {
      name: 'Michael Brown',
      email: 'michael.b@email.com',
      role: 'UX Designer',
      experience: 4,
      status: 'New',
    },
    {
      name: 'Emily Davis',
      email: 'emily.d@email.com',
      role: 'Marketing Manager',
      experience: 6,
      status: 'In Progress',
    },
  ];

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Candidates
      </Typography>

      <Box sx={{ mb: 4 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search candidates..."
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Candidate</TableCell>
              <TableCell>Applied For</TableCell>
              <TableCell>Experience</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {candidates.map((candidate, index) => (
              <CandidateRow key={index} {...candidate} />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default Candidates;
