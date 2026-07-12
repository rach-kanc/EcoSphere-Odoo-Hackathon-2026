export interface Badge {
  id: number;
  name: string;
  description: string | null;
  icon_url: string | null;
  rarity: "common" | "rare" | "epic" | "legendary";
  created_at: string;
}

export interface UserBadge {
  id: number;
  user_id: number;
  badge_id: number;
  earned_at: string;
  badge: Badge;
}

export interface Challenge {
  id: number;
  title: string;
  description: string | null;
  xp_reward: number;
  difficulty: "easy" | "medium" | "hard" | "expert";
  deadline: string | null;
  evidence_required: boolean;
  status: "draft" | "active" | "under_review" | "completed" | "archived";
  created_at: string;
  participation_count: number;
}

export interface Participation {
  id: number;
  challenge_id: number;
  employee_id: number;
  progress: number;
  proof_url: string | null;
  status: "in_progress" | "submitted" | "approved" | "rejected";
  xp_awarded: number;
  submitted_at: string | null;
  created_at: string;
  challenge: Challenge;
}

export interface Reward {
  id: number;
  name: string;
  description: string | null;
  icon_url: string | null;
  points_required: number;
  stock: number;
  status: "available" | "out_of_stock" | "discontinued";
  created_at: string;
}

export interface Redemption {
  id: number;
  reward_id: number;
  employee_id: number;
  xp_spent: number;
  status: "pending" | "fulfilled" | "cancelled";
  redeemed_at: string;
  reward: Reward;
}

export interface LeaderboardEntry {
  user_id: number;
  full_name: string;
  department_name: string | null;
  level: number;
  xp_points: number;
  rank: number;
}
