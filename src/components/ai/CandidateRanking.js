import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Rating,
  Tooltip,
  IconButton,
  Alert,
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import { rankCandidates } from '../../services/mockAiService';
import { predictCandidateSuccess } from '../../services/aiServices';

const CandidateRanking = ({ jobDescription, candidates, historicalData }) => {
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const analyzeCandidates = async () => {
      setLoading(true);
      setError(null);
      try {
        const rankingResults = await rankCandidates(jobDescription, candidates);
        const rankedCandidates = [];

        // Get success predictions for each candidate
        for (const candidate of rankingResults) {
          const prediction = await predictCandidateSuccess(
            candidate,
            jobDescription,
            historicalData
          );
          rankedCandidates.push({
            ...candidate,
            prediction
          });
        }

        setRankings(rankedCandidates);
      } catch (err) {
        setError('Failed to rank candidates. Please try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (candidates.length > 0) {
      analyzeCandidates();
    }
  }, [jobDescription, candidates, historicalData]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          AI-Powered Candidate Ranking
        </Typography>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Rank</TableCell>
                <TableCell>Candidate</TableCell>
                <TableCell>Match Score</TableCell>
                <TableCell>Success Prediction</TableCell>
                <TableCell>Key Strengths</TableCell>
                <TableCell>Analysis</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rankings.map((candidate, index) => (
                <TableRow 
                  key={candidate.id}
                  sx={{ 
                    backgroundColor: index < 3 ? 'rgba(76, 175, 80, 0.1)' : 'inherit'
                  }}
                >
                  <TableCell>{index + 1}</TableCell>
                  <TableCell>
                    <Typography variant="subtitle2">
                      {candidate.name}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {candidate.currentRole}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Rating 
                        value={candidate.score / 20} 
                        readOnly 
                        precision={0.5}
                      />
                      <Typography variant="body2">
                        ({candidate.score}%)
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography
                        color={candidate.prediction.confidence > 70 ? 'success.main' : 'warning.main'}
                      >
                        {candidate.prediction.confidence}% Confidence
                      </Typography>
                      <Tooltip title={candidate.prediction.reasoning}>
                        <IconButton size="small">
                          <InfoIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" flexWrap="wrap" gap={0.5}>
                      {candidate.strengths.map((strength, i) => (
                        <Typography
                          key={i}
                          variant="body2"
                          sx={{
                            bgcolor: 'primary.light',
                            color: 'primary.contrastText',
                            px: 1,
                            py: 0.5,
                            borderRadius: 1,
                            fontSize: '0.75rem'
                          }}
                        >
                          {strength}
                        </Typography>
                      ))}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Tooltip title={candidate.analysis}>
                      <IconButton size="small">
                        <InfoIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
};

export default CandidateRanking;
