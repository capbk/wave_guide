const state = {
  // set default modes
  sourceMode: "song",
  destinationMode: "mood",
  sourceTrackId: null,
  destinationTrackId: null,
  sourceMood: null,
  destinationMood: null,
  getSourceMode() {
    return this.sourceMode;
  },
  setSourceMode(mode) {
    this.sourceMode = mode;
  },
  getDestinationMode() {
    return this.destinationMode;
  },
  setDestinationMode(mode) {
    this.destinationMode = mode;
  },

  getSourceTrackId() {
    return this.sourceTrackId;
  },
  setSourceTrackId(trackId) {
    this.sourceTrackId = trackId;
  },
  getDestinationTrackId() {
    return this.destinationTrackId;
  },
  setDestinationTrackId(trackId) {
    this.destinationTrackId = trackId;
  },

  getSourceMood() {
    return this.sourceMood;
  },
  setSourceMood(mood) {
    this.sourceMood = mood;
  },
  getDestinationMood() {
    return this.destinationMood;
  },
  setDestinationMood(mood) {
    this.destinationMood = mood;
  },
};

export default state;
