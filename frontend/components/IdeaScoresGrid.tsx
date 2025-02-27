import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  InputAdornment,
  Grid,
  Card,
  CardContent,
  Divider,
  LinearProgress
} from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridValueGetterParams,
  GridRenderCellParams,
  GridToolbar
} from '@mui/x-data-grid';
import SearchIcon from '@mui/icons-material/Search';
import InfoIcon from '@mui/icons-material/Info';
import ErrorIcon from '@mui/icons-material/Error';
import axios from 'axios';

interface IdeaScoresGridProps {
  fileId: string;
}

interface BusinessIdea {
  id: string;
  name: string;
  industry: string;
  business_model: string;
  score: number;
  risk_flags: string[];
  explanation: string;
  file_id: string;
  market_size_tam?: number;
  competition_level?: number;
  founding_team_experience?: number;
  created_at: string;
  updated_at: string;
}

const IdeaScoresGrid: React.FC<IdeaScoresGridProps> = ({ fileId }) => {
  const [ideas, setIdeas] = useState<BusinessIdea[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedIdea, setSelectedIdea] = useState<BusinessIdea | null>(null);
  const [detailsOpen, setDetailsOpen] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [filteredIdeas, setFilteredIdeas] = useState<BusinessIdea[]>([]);

  useEffect(() => {
    fetchIdeas();
  }, [fileId]);

  useEffect(() => {
    // Filter ideas based on search term
    if (searchTerm.trim() === '') {
      setFilteredIdeas(ideas);
    } else {
      const term = searchTerm.toLowerCase();
      const filtered = ideas.filter(idea => 
        idea.name.toLowerCase().includes(term) || 
        idea.industry.toLowerCase().includes(term) ||
        idea.business_model.toLowerCase().includes(term)
      );
      setFilteredIdeas(filtered);
    }
  }, [searchTerm, ideas]);

  const fetchIdeas = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.get<BusinessIdea[]>(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/ideas`,
        {
          params: {
            file_id: fileId
          }
        }
      );

      setIdeas(response.data);
      setFilteredIdeas(response.data);
    } catch (error) {
      console.error('Error fetching ideas:', error);
      setError('Failed to fetch business ideas. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDetails = (idea: BusinessIdea) => {
    setSelectedIdea(idea);
    setDetailsOpen(true);
  };

  const handleCloseDetails = () => {
    setDetailsOpen(false);
  };

  // Define the columns for the data grid
  const columns: GridColDef[] = [
    {
      field: 'name',
      headerName: 'Business Idea',
      minWidth: 200,
      flex: 1,
    },
    {
      field: 'industry',
      headerName: 'Industry',
      minWidth: 150,
      flex: 0.8,
    },
    {
      field: 'business_model',
      headerName: 'Business Model',
      minWidth: 150,
      flex: 0.8,
      valueGetter: (params: GridValueGetterParams<BusinessIdea>) => {
        // Format business_model to make it more readable
        const model = params.row.business_model;
        return model
          .replace('_', ' ')
          .split(' ')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
          .join(' ');
      },
    },
    {
      field: 'score',
      headerName: 'Score',
      type: 'number',
      minWidth: 100,
      flex: 0.5,
      renderCell: (params: GridRenderCellParams<BusinessIdea>) => {
        const score = params.row.score;
        let color = 'success.main';
        
        if (score < 50) {
          color = 'error.main';
        } else if (score < 75) {
          color = 'warning.main';
        }
        
        return (
          <Box sx={{ width: '100%' }}>
            <Typography 
              variant="body2" 
              fontWeight="bold" 
              color={color}
              align="center"
            >
              {score}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={score}
              sx={{ 
                height: 4, 
                borderRadius: 2,
                bgcolor: 'grey.200',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 2,
                  bgcolor: color
                }
              }}
            />
          </Box>
        );
      },
    },
    {
      field: 'risk_flags',
      headerName: 'Risk Flags',
      minWidth: 150,
      flex: 0.8,
      renderCell: (params: GridRenderCellParams<BusinessIdea>) => {
        const flags = params.row.risk_flags;
        if (!flags || flags.length === 0) {
          return <Typography variant="body2">None</Typography>;
        }
        
        return (
          <Box>
            {flags.length > 2 ? (
              <Chip 
                icon={<ErrorIcon />} 
                label={`${flags.length} Risks`} 
                color="error" 
                size="small"
              />
            ) : (
              flags.map((flag, index) => (
                <Chip 
                  key={index} 
                  label={flag} 
                  color="error" 
                  size="small" 
                  sx={{ mr: 0.5, mb: 0.5 }}
                />
              ))
            )}
          </Box>
        );
      },
    },
    {
      field: 'details',
      headerName: 'Details',
      sortable: false,
      filterable: false,
      minWidth: 100,
      flex: 0.5,
      renderCell: (params: GridRenderCellParams<BusinessIdea>) => (
        <Button
          variant="outlined"
          size="small"
          startIcon={<InfoIcon />}
          onClick={() => handleOpenDetails(params.row)}
        >
          View
        </Button>
      ),
    },
  ];

  return (
    <Box sx={{ py: 3 }}>
      <Typography variant="h5" gutterBottom>
        Business Idea Scores
      </Typography>
      
      {/* Error message */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {/* Search bar */}
      <TextField
        fullWidth
        placeholder="Search by name, industry, or business model..."
        variant="outlined"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        sx={{ mb: 3 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
      />
      
      {/* Data grid */}
      <Paper sx={{ height: 600, width: '100%' }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <CircularProgress />
          </Box>
        ) : (
          <DataGrid
            rows={filteredIdeas}
            columns={columns}
            pagination
            paginationMode="client"
            pageSizeOptions={[10, 25, 50, 100]}
            initialState={{
              pagination: {
                paginationModel: { page: 0, pageSize: 10 },
              },
              sorting: {
                sortModel: [{ field: 'score', sort: 'desc' }],
              },
            }}
            slots={{ toolbar: GridToolbar }}
            slotProps={{
              toolbar: {
                showQuickFilter: true,
                quickFilterProps: { debounceMs: 500 },
              },
            }}
            disableRowSelectionOnClick
            autoHeight={false}
          />
        )}
      </Paper>
      
      {/* Details dialog */}
      <Dialog 
        open={detailsOpen && selectedIdea !== null} 
        onClose={handleCloseDetails}
        maxWidth="md"
        fullWidth
      >
        {selectedIdea && (
          <>
            <DialogTitle>
              <Typography variant="h6">
                {selectedIdea.name}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Chip 
                  label={selectedIdea.industry} 
                  color="primary" 
                  size="small" 
                  sx={{ mr: 1 }}
                />
                <Chip 
                  label={selectedIdea.business_model.replace('_', ' ')} 
                  color="secondary" 
                  size="small" 
                />
                <Box sx={{ flexGrow: 1 }} />
                <Typography 
                  variant="h6" 
                  fontWeight="bold" 
                  color={
                    selectedIdea.score >= 75 ? 'success.main' : 
                    selectedIdea.score >= 50 ? 'warning.main' : 
                    'error.main'
                  }
                >
                  Score: {selectedIdea.score}/100
                </Typography>
              </Box>
            </DialogTitle>
            <DialogContent dividers>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom fontWeight="medium">
                    Analysis:
                  </Typography>
                  <Typography variant="body1">
                    {selectedIdea.explanation || 'No analysis available'}
                  </Typography>
                </Grid>
                
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                </Grid>
                
                {selectedIdea.risk_flags && selectedIdea.risk_flags.length > 0 && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle1" gutterBottom fontWeight="medium" color="error.main">
                      Risk Flags:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {selectedIdea.risk_flags.map((flag, index) => (
                        <Chip 
                          key={index} 
                          label={flag} 
                          color="error" 
                          size="small" 
                        />
                      ))}
                    </Box>
                  </Grid>
                )}
                
                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom fontWeight="medium">
                    Key Metrics:
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6} md={4}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="body2" color="text.secondary">
                            TAM
                          </Typography>
                          <Typography variant="h6">
                            {selectedIdea.market_size_tam ? 
                              `$${selectedIdea.market_size_tam}M` : 
                              'N/A'}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={6} md={4}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="body2" color="text.secondary">
                            Competition Level
                          </Typography>
                          <Typography variant="h6">
                            {selectedIdea.competition_level ? 
                              `${selectedIdea.competition_level}/10` : 
                              'N/A'}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={6} md={4}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="body2" color="text.secondary">
                            Team Experience
                          </Typography>
                          <Typography variant="h6">
                            {selectedIdea.founding_team_experience ? 
                              `${selectedIdea.founding_team_experience}/10` : 
                              'N/A'}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDetails}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default IdeaScoresGrid;
