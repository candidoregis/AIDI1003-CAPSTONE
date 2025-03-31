import React, { useState, useEffect } from 'react';
import { Box, IconButton, Typography, CircularProgress, Fade, Alert, Paper } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import CloseIcon from '@mui/icons-material/Close';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

const VoiceSearch = ({ onSearchComplete, onClose, processing = false }) => {
  const [isListening, setIsListening] = useState(false);
  const [processingAudio, setProcessingAudio] = useState(false);
  const [error, setError] = useState(null);
  
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
    isMicrophoneAvailable
  } = useSpeechRecognition();

  useEffect(() => {
    setIsListening(listening);
  }, [listening]);

  // Set processingAudio based on external processing prop
  useEffect(() => {
    if (processing) {
      setProcessingAudio(true);
    }
  }, [processing]);

  const startListening = async () => {
    try {
      setError(null);
      resetTranscript();
      
      // Check if microphone permission is granted
      const permissionResult = await navigator.mediaDevices.getUserMedia({ audio: true });
      if (!permissionResult) {
        throw new Error("Microphone permission denied");
      }
      
      SpeechRecognition.startListening({ continuous: true });
    } catch (err) {
      setError("Please allow microphone access to use voice search");
      console.error('Microphone error:', err);
    }
  };

  const stopListening = async () => {
    SpeechRecognition.stopListening();
    setProcessingAudio(true);
    
    try {
      if (onSearchComplete && transcript) {
        await onSearchComplete(transcript);
      } else if (!transcript) {
        setError("No speech was detected. Please try again.");
        setProcessingAudio(false);
      }
    } catch (err) {
      setError("Sorry, there was an error processing your voice search. Please try again.");
      console.error('Voice search error:', err);
      setProcessingAudio(false);
    }
  };

  if (!browserSupportsSpeechRecognition) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Voice search is only supported in Chrome browser.
      </Alert>
    );
  }

  if (!isMicrophoneAvailable) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Please allow microphone access to use voice search.
      </Alert>
    );
  }

  return (
    <Paper sx={{ p: 3, position: 'relative' }}>
      {/* Close Button */}
      <IconButton
        onClick={onClose}
        sx={{
          position: 'absolute',
          right: 8,
          top: 8,
          color: 'text.secondary'
        }}
      >
        <CloseIcon />
      </IconButton>

      <Box sx={{ 
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 3,
        pt: 2
      }}>
        <Typography variant="body1" color="text.secondary" align="center">
          {isListening 
            ? "I'm listening... Click stop when you're done."
            : "Click the microphone and describe the job you're looking for"
          }
        </Typography>
        
        <Typography variant="body2" color="text.secondary" align="center" sx={{ fontStyle: 'italic' }}>
          Try saying: "I'm looking for a senior software engineer position in New York with 5 years of experience in React and Node.js"
        </Typography>

        {error && (
          <Alert 
            severity="error" 
            onClose={() => setError(null)}
            sx={{ width: '100%' }}
          >
            {error}
          </Alert>
        )}

        <IconButton
          onClick={isListening ? stopListening : startListening}
          disabled={processingAudio}
          sx={{
            width: 80,
            height: 80,
            bgcolor: isListening ? 'error.main' : 'primary.main',
            color: 'white',
            '&:hover': {
              bgcolor: isListening ? 'error.dark' : 'primary.dark',
            },
            '&.Mui-disabled': {
              bgcolor: 'grey.400',
              color: 'white'
            },
            transition: 'all 0.3s ease',
            ...(isListening && {
              animation: 'pulse 1.5s infinite',
              '@keyframes pulse': {
                '0%': {
                  transform: 'scale(1)',
                  boxShadow: '0 0 0 0 rgba(244, 67, 54, 0.4)'
                },
                '70%': {
                  transform: 'scale(1.1)',
                  boxShadow: '0 0 0 15px rgba(244, 67, 54, 0)'
                },
                '100%': {
                  transform: 'scale(1)',
                  boxShadow: '0 0 0 0 rgba(244, 67, 54, 0)'
                }
              }
            })
          }}
        >
          {processingAudio ? (
            <CircularProgress size={36} color="inherit" />
          ) : isListening ? (
            <StopIcon sx={{ fontSize: 36 }} />
          ) : (
            <MicIcon sx={{ fontSize: 36 }} />
          )}
        </IconButton>

        {transcript && (
          <Fade in={true}>
            <Box sx={{ 
              width: '100%',
              p: 2,
              bgcolor: 'background.paper',
              borderRadius: 1,
              boxShadow: 1
            }}>
              <Typography 
                variant="body1" 
                color="text.primary"
                sx={{ 
                  fontStyle: 'italic',
                  lineHeight: 1.6
                }}
              >
                "{transcript}"
              </Typography>
            </Box>
          </Fade>
        )}

        {processingAudio && (
          <Typography 
            variant="body2" 
            color="text.secondary"
            sx={{ 
              display: 'flex',
              alignItems: 'center',
              gap: 1
            }}
          >
            <CircularProgress size={16} />
            Processing your job search...
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default VoiceSearch;
