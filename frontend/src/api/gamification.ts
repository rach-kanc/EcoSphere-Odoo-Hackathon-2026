import {
  Challenge,
  Participation,
  Badge,
  UserBadge,
  Reward,
  Redemption,
  LeaderboardEntry,
} from "../types/gamification";

const API_BASE = "http://localhost:8000/api/v1/gamification";

// Helper for standard fetch calls
async function fetchApi<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "API request failed");
  }
  return response.json();
}

export const gamificationApi = {
  // Challenges
  getChallenges: () => fetchApi<Challenge[]>("/challenges"),
  joinChallenge: (challengeId: number) =>
    fetchApi<Participation>(`/challenges/${challengeId}/join`, {
      method: "POST",
    }),
  updateParticipation: (participationId: number, progress: number, proofUrl?: string, submitForReview: boolean = false) =>
    fetchApi<Participation>(`/participations/${participationId}`, {
      method: "PUT",
      body: JSON.stringify({
        progress,
        proof_url: proofUrl,
        submit_for_review: submitForReview,
      }),
    }),
  
  // Badges
  getBadges: () => fetchApi<Badge[]>("/badges"),
  getMyBadges: () => fetchApi<UserBadge[]>("/badges/me"),

  // Rewards
  getRewards: (onlyAvailable: boolean = true) =>
    fetchApi<Reward[]>(`/rewards?only_available=${onlyAvailable}`),
  redeemReward: (rewardId: number) =>
    fetchApi<Redemption>(`/rewards/${rewardId}/redeem`, {
      method: "POST",
    }),
  getMyRedemptions: () => fetchApi<Redemption[]>("/rewards/redemptions/me"),

  // Leaderboard
  getLeaderboard: (limit: number = 10) =>
    fetchApi<LeaderboardEntry[]>(`/leaderboard?limit=${limit}`),
};
