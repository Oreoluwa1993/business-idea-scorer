import React, { useState } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  Grid, 
  Button, 
  CircularProgress,
  AppBar,
  Toolbar,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  CloudUpload as CloudUploadIcon,
  BarChart as BarChartIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import FileUploadComponent from '../components/FileUploadComponent';
import IdeaScoresGrid from '../components/IdeaScoresGrid';

const HomePage: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [uploadedFileId, setUploadedFileId] = useState<string | null>(null);

  const handleDrawerOpen = () => {
    setOpen(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };

  const handleFileUploaded = (fileId: string) => {
    setUploadedFileId(fileId);
    setActiveTab('scores');
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'upload':
        return (
          <FileUploadComponent 
            onFileUploaded={handleFileUploaded}
            setLoading={setLoading}
          />
        );
      case 'scores':
        return uploadedFileId ? (
          <IdeaScoresGrid fileId={uploadedFileId} />
        ) : (
          <Box sx={{ textAlign: 'center', py: 5 }}>
            <Typography variant="h6" color="text.secondary">
              Please upload a file to view scores
            </Typography>
            <Button 
              variant="contained" 
              color="primary" 
              onClick={() => setActiveTab('upload')}
              sx={{ mt: 2 }}
            >
              Upload File
            </Button>
          </Box>
        );
      case 'dashboard':
      default:
        return (
          <Box>
            <Typography variant="h5" gutterBottom>
              Welcome to Business Idea Scorer
            </Typography>
            <Typography paragraph>
              This tool helps you analyze and rank business ideas based on custom criteria.
            </Typography>
            <Grid container spacing={3} sx={{ mt: 2 }}>
              <Grid item xs={12} sm={6} md={4}>
                <Paper 
                  sx={{ 
                    p: 3, 
                    display: 'flex', 
                    flexDirection: 'column', 
                    alignItems: 'center',
                    cursor: 'pointer',
                    '&:hover': {
                      bgcolor: 'action.hover',
                    },
                  }}
                  onClick={() => setActiveTab('upload')}
                >
                  <CloudUploadIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                  <Typography variant="h6">Upload Data</Typography>
                  <Typography variant="body2" color="text.secondary" align="center">
                    Upload Excel/CSV files with business ideas
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Paper 
                  sx={{ 
                    p: 3, 
                    display: 'flex', 
                    flexDirection: 'column', 
                    alignItems: 'center',
                    cursor: 'pointer',
                    '&:hover': {
                      bgcolor: 'action.hover',
                    },
                  }}
                  onClick={() => setActiveTab('scores')}
                >
                  <BarChartIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                  <Typography variant="h6">View Scores</Typography>
                  <Typography variant="body2" color="text.secondary" align="center">
                    Analyze and compare business idea scores
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Paper 
                  sx={{ 
                    p: 3, 
                    display: 'flex', 
                    flexDirection: 'column', 
                    alignItems: 'center',
                    cursor: 'pointer',
                    '&:hover': {
                      bgcolor: 'action.hover',
                    },
                  }}
                >
                  <SettingsIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                  <Typography variant="h6">Settings</Typography>
                  <Typography variant="body2" color="text.secondary" align="center">
                    Customize scoring weights and criteria
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          </Box>
        );
    }
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* App bar */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerOpen}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Business Idea Scorer
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Drawer
        variant="permanent"
        sx={{
          width: 240,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { width: 240, boxSizing: 'border-box' },
          display: { xs: 'none', sm: 'block' },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            <ListItem 
              button 
              selected={activeTab === 'dashboard'}
              onClick={() => setActiveTab('dashboard')}
            >
              <ListItemIcon>
                <DashboardIcon />
              </ListItemIcon>
              <ListItemText primary="Dashboard" />
            </ListItem>
            <ListItem 
              button 
              selected={activeTab === 'upload'}
              onClick={() => setActiveTab('upload')}
            >
              <ListItemIcon>
                <CloudUploadIcon />
              </ListItemIcon>
              <ListItemText primary="Upload Data" />
            </ListItem>
            <ListItem 
              button 
              selected={activeTab === 'scores'}
              onClick={() => setActiveTab('scores')}
            >
              <ListItemIcon>
                <BarChartIcon />
              </ListItemIcon>
              <ListItemText primary="View Scores" />
            </ListItem>
          </List>
          <Divider />
          <List>
            <ListItem button>
              <ListItemIcon>
                <SettingsIcon />
              </ListItemIcon>
              <ListItemText primary="Settings" />
            </ListItem>
          </List>
        </Box>
      </Drawer>

      {/* Mobile drawer */}
      <Drawer
        variant="temporary"
        open={open}
        onClose={handleDrawerClose}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 240 },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            <ListItem 
              button 
              selected={activeTab === 'dashboard'}
              onClick={() => {
                setActiveTab('dashboard');
                handleDrawerClose();
              }}
            >
              <ListItemIcon>
                <DashboardIcon />
              </ListItemIcon>
              <ListItemText primary="Dashboard" />
            </ListItem>
            <ListItem 
              button 
              selected={activeTab === 'upload'}
              onClick={() => {
                setActiveTab('upload');
                handleDrawerClose();
              }}
            >
              <ListItemIcon>
                <CloudUploadIcon />
              </ListItemIcon>
              <ListItemText primary="Upload Data" />
            </ListItem>
            <ListItem 
              button 
              selected={activeTab === 'scores'}
              onClick={() => {
                setActiveTab('scores');
                handleDrawerClose();
              }}
            >
              <ListItemIcon>
                <BarChartIcon />
              </ListItemIcon>
              <ListItemText primary="View Scores" />
            </ListItem>
          </List>
          <Divider />
          <List>
            <ListItem button onClick={handleDrawerClose}>
              <ListItemIcon>
                <SettingsIcon />
              </ListItemIcon>
              <ListItemText primary="Settings" />
            </ListItem>
          </List>
        </Box>
      </Drawer>

      {/* Main content */}
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
            <CircularProgress />
          </Box>
        ) : (
          <Container maxWidth="lg">
            {renderContent()}
          </Container>
        )}
      </Box>
    </Box>
  );
};

export default HomePage;
