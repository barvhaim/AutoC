import axios from "axios";

export interface FeedbackRequest {
  url: string;
  feedback_type: string;
  context: string;
  value: number;
}

export const postFeedback = (feedback: FeedbackRequest) => {
  return axios.post("/api/v1/feedback", feedback);
};
