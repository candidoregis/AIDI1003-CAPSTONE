import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import WorkIcon from '@mui/icons-material/Work';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import CloseIcon from '@mui/icons-material/Close';
import IntelligentChatbot from '../components/chatbot/IntelligentChatbot';
import ResumeGenerator from '../components/resume/ResumeGenerator';
import VoiceJobSearch from '../components/voice/VoiceJobSearch';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`dashboard-tabpanel-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function Dashboard() {
  const [tabValue, setTabValue] = useState(0);
  const [showChatbot, setShowChatbot] = useState(false);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Container maxWidth="xl">
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab icon={<DashboardIcon />} label="Overview" />
            <Tab icon={<WorkIcon />} label="Jobs" />
            <Tab icon={<SmartToyIcon />} label="AI Tools" />
          </Tabs>
        </Box>

        {/* Overview Tab */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Active Jobs
                </Typography>
                <Typography variant="h3">24</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Total Candidates
                </Typography>
                <Typography variant="h3">156</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Upcoming Interviews
                </Typography>
                <Typography variant="h3">12</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Recent Activity
                </Typography>
                {/* Add activity feed here */}
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Jobs Tab */}
        <TabPanel value={tabValue} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <VoiceJobSearch />
            </Grid>
          </Grid>
        </TabPanel>

        {/* AI Tools Tab */}
        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3}>
            {/* Resume Generation */}
            <Grid item xs={12}>
              <ResumeGenerator />
            </Grid>
          </Grid>
        </TabPanel>

        {/* Chatbot Dialog */}
        {showChatbot && (
          <Paper
            sx={{
              position: 'fixed',
              right: 20,
              bottom: 80,
              width: 400,
              height: 600,
              zIndex: 1000,
              borderRadius: 2,
              boxShadow: 3,
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <Box
              sx={{
                p: 2,
                bgcolor: 'primary.main',
                color: 'white',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <Typography variant="h6">
                AI Assistant
              </Typography>
              <IconButton
                onClick={() => setShowChatbot(false)}
                sx={{ color: 'white' }}
              >
                <CloseIcon />
              </IconButton>
            </Box>
            <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
              <IntelligentChatbot />
            </Box>
          </Paper>
        )}

        {/* AI Assistant Button */}
        <Box sx={{ position: 'fixed', right: 20, bottom: 20, display: 'flex', gap: 2 }}>
          <Tooltip title="AI Assistant">
            <IconButton
              onClick={() => setShowChatbot(true)}
              sx={{
                bgcolor: 'secondary.main',
                color: 'white',
                '&:hover': {
                  bgcolor: 'secondary.dark',
                },
              }}
            >
              <SmartToyIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Container>
    </Box>
  );
}

export default Dashboard;
