import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  useTheme,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Work as WorkIcon,
  People as PeopleIcon,
  Event as EventIcon,
} from '@mui/icons-material';

const Navbar = () => {
  const theme = useTheme();
  
  const navItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Jobs', icon: <WorkIcon />, path: '/jobs' },
    { text: 'Candidates', icon: <PeopleIcon />, path: '/candidates' },
    { text: 'Interviews', icon: <EventIcon />, path: '/interviews' },
  ];

  return (
    <AppBar 
      position="static" 
      sx={{
        background: 'linear-gradient(135deg, #00BCD4 0%, #2196F3 100%)',
        boxShadow: '0 3px 5px 2px rgba(33, 150, 243, .3)',
      }}
    >
      <Container maxWidth="xl">
        <Toolbar>
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              flexGrow: 0, 
              mr: 4,
              background: 'white',
              borderRadius: '50%',
              padding: '8px',
              marginRight: '16px'
            }}
          >
            <img
              src="/images/syncruit-logo.png"
              alt="Syncruit Logo"
              style={{
                height: '40px',
                width: 'auto',
              }}
            />
          </Box>
          <Box>
            <Typography
              variant="h6"
              component={RouterLink}
              to="/"
              sx={{
                textDecoration: 'none',
                color: 'white',
                fontWeight: 700,
                letterSpacing: 1,
                lineHeight: 1,
                '&:hover': {
                  color: 'rgba(255, 255, 255, 0.9)',
                },
              }}
            >
              SYNCRUIT
            </Typography>
            <Typography
              variant="caption"
              sx={{
                color: 'rgba(255, 255, 255, 0.9)',
                display: 'block',
                letterSpacing: '0.5px',
                fontSize: '0.7rem',
                mt: 0.5,
              }}
            >
              WHERE TALENT MEETS ITS MATCH
            </Typography>
          </Box>
          <Box sx={{ 
            flexGrow: 1, 
            display: 'flex', 
            gap: 2,
            '& .MuiButton-root': {
              borderRadius: 2,
              transition: 'all 0.3s ease-in-out',
              '&:hover': {
                transform: 'translateY(-2px)',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
            },
          }}>
            {navItems.map((item) => (
              <Button
                key={item.text}
                component={RouterLink}
                to={item.path}
                color="inherit"
                startIcon={item.icon}
                sx={{
                  padding: '8px 16px',
                  '&.active': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  },
                }}
              >
                {item.text}
              </Button>
            ))}
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Navbar;
