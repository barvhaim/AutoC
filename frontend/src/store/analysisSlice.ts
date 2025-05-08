import { createSlice } from "@reduxjs/toolkit";

const analysisSlice = createSlice({
  name: "analysis",
  initialState: {
    url: null,
    keywords: [],
    qna: [],
    iocs: [],
    mitre_ttps: null,
  },
  reducers: {
    setAnalysisResults: (state, action) => {
      state.url = action.payload.url;
      state.keywords = action.payload.keywords;
      state.qna = action.payload.qna;
      state.iocs = action.payload.iocs;
      state.mitre_ttps = action.payload.mitre_ttps;
    },
    clearAnalysisResults: (state) => {
      state.url = null;
      state.keywords = [];
      state.qna = [];
      state.iocs = [];
      state.mitre_ttps = null;
    },
  },
});
export const { setAnalysisResults, clearAnalysisResults } =
  analysisSlice.actions;
export default analysisSlice.reducer;
