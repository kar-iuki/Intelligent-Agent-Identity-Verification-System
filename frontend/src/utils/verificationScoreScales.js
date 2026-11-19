// Thresholds use the API's native units. Face match is already a percentage.
export const verificationScoreScales = {
  ocrConfidenceScore: { max: 1, amberThreshold: 0.4, greenThreshold: 0.7 },
  faceMatchScore: { max: 100, amberThreshold: 50, greenThreshold: 80 },
  livenessScore: { max: 1, amberThreshold: 0.5, greenThreshold: 0.75 },
}
