import React, { useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

interface FileUploadComponentProps {
  onFileUploaded: (fileId: string) => void;
  setLoading: (loading: boolean) => void;
}

interface UploadResponse {
  filename: string;
  saved_as: string;
  size_bytes: number;
  record_count: number;
  columns: string[];
  status: string;
  message: string;
}

const FileUploadComponent: React.FC<FileUploadComponentProps> = ({ onFileUploaded, setLoading }) => {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<UploadResponse | null>(null);
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    // Reset states
    setError(null);
    setSuccess(null);
    
    // Check if there are files
    if (acceptedFiles.length === 0) {
      return;
    }
    
    const selectedFile = acceptedFiles[0];
    
    // Validate file type
    const validFileTypes = [
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'text/csv'
    ];
    
    if (!validFileTypes.includes(selectedFile.type)) {
      setError('Please upload a valid Excel (.xlsx, .xls) or CSV (.csv) file');
      return;
    }
    
    // Validate file size (10MB limit)
    const maxSize = 10 * 1024 * 1024;
    if (selectedFile.size > maxSize) {
      setError('File size exceeds 10MB limit');
      return;
    }
    
    // Set the file
    setFile(selectedFile);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: {
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/csv': ['.csv']
    },
    maxFiles: 1
  });

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }
    
    try {
      setUploading(true);
      setLoading(true);
      setError(null);
      
      // Create form data
      const formData = new FormData();
      formData.append('file', file);
      
      // Upload file to API
      const response = await axios.post<UploadResponse>(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/uploads`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      // Set success response
      setSuccess(response.data);
      
      // Notify parent component
      onFileUploaded(response.data.saved_as);
      
    } catch (error) {
      console.error('Error uploading file:', error);
      
      if (axios.isAxiosError(error) && error.response) {
        setError(error.response.data.detail || 'Failed to upload file');
      } else {
        setError('Failed to upload file. Please try again.');
      }
      
    } finally {
      setUploading(false);
      setLoading(false);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setError(null);
    setSuccess(null);
  };

  return (
    <Box sx={{ py: 3 }}>
      <Typography variant="h5" gutterBottom>
        Upload Business Ideas
      </Typography>
      <Typography paragraph>
        Upload an Excel (.xlsx, .xls) or CSV (.csv) file containing your business ideas.
        The file should include columns for name, description, industry, and other relevant data.
      </Typography>

      {/* Error message */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Success message */}
      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          File uploaded successfully! {success.record_count} records processed.
        </Alert>
      )}

      {/* Dropzone */}
      {!file && (
        <Paper
          {...getRootProps()}
          sx={{
            p: 5,
            border: '2px dashed',
            borderColor: isDragActive ? 'primary.main' : 'grey.400',
            borderRadius: 2,
            bgcolor: isDragActive ? 'action.hover' : 'background.paper',
            textAlign: 'center',
            cursor: 'pointer',
            mb: 3
          }}
        >
          <input {...getInputProps()} />
          <Typography variant="h6" gutterBottom>
            {isDragActive ? 'Drop the file here' : 'Drag & drop your file here'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            or click to select a file
          </Typography>
          <Typography variant="caption" display="block" sx={{ mt: 1 }}>
            Supported formats: Excel (.xlsx, .xls) and CSV (.csv)
          </Typography>
        </Paper>
      )}

      {/* Selected file */}
      {file && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Selected File:
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="body1" fontWeight="medium">
                {file.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </Typography>
            </Box>
            <Button 
              variant="outlined" 
              color="error" 
              onClick={handleRemoveFile}
              disabled={uploading}
            >
              Remove
            </Button>
          </Box>
          <Button
            variant="contained"
            color="primary"
            fullWidth
            onClick={handleUpload}
            disabled={uploading}
            startIcon={uploading && <CircularProgress size={20} color="inherit" />}
          >
            {uploading ? 'Uploading...' : 'Upload File'}
          </Button>
        </Paper>
      )}

      {/* File details if upload successful */}
      {success && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            File Details:
          </Typography>
          <List>
            <ListItem>
              <ListItemText 
                primary="Filename" 
                secondary={success.filename} 
              />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemText 
                primary="Records Processed" 
                secondary={success.record_count} 
              />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemText 
                primary="File Size" 
                secondary={`${(success.size_bytes / 1024 / 1024).toFixed(2)} MB`} 
              />
            </ListItem>
            <Divider />
            <ListItem sx={{ flexDirection: 'column', alignItems: 'flex-start' }}>
              <ListItemText 
                primary="Columns Detected" 
                sx={{ mb: 1 }}
              />
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {success.columns.map((column, index) => (
                  <Chip key={index} label={column} size="small" />
                ))}
              </Box>
            </ListItem>
          </List>
          <Button
            variant="contained"
            color="primary"
            fullWidth
            onClick={() => onFileUploaded(success.saved_as)}
            sx={{ mt: 2 }}
          >
            View Scores
          </Button>
        </Paper>
      )}
    </Box>
  );
};

export default FileUploadComponent;
