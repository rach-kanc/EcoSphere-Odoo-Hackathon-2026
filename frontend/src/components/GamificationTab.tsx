import React, { useEffect, useState } from "react";
import { Leaf, Award, Scale, Trophy, Gift, ArrowRight, Clock } from "lucide-react";
import { gamificationApi } from "../api/gamification";
import { Challenge, Badge, UserBadge, Reward, LeaderboardEntry } from "../types/gamification";

import { User } from "../types";

export default function GamificationTab({
  user,
  setUser,
}: {
  user: User;
  setUser: React.Dispatch<React.SetStateAction<User>>;
}) {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [badges, setBadges] = useState<Badge[]>([]);
  const [myBadges, setMyBadges] = useState<UserBadge[]>([]);
  const [rewards, setRewards] = useState<Reward[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  // Load all gamification data
  const loadData = async () => {
    try {
      const [chData, bData, myBData, rData, lbData] = await Promise.all([
        gamificationApi.getChallenges(),
        gamificationApi.getBadges(),
        gamificationApi.getMyBadges(),
        gamificationApi.getRewards(),
        gamificationApi.getLeaderboard(),
      ]);
      setChallenges(chData);
      setBadges(bData);
      setMyBadges(myBData);
      setRewards(rData);
      setLeaderboard(lbData);
      
      // Update local user state from leaderboard if possible
      const myEntry = lbData.find(e => e.user_id === user.id);
      if (myEntry) {
        setUser(prev => ({ ...prev, xp_points: myEntry.xp_points, level: myEntry.level }));
      }
    } catch (err) {
      console.error("Failed to load gamification data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleJoinChallenge = async (id: number) => {
    try {
      await gamificationApi.joinChallenge(id);
      alert("Successfully joined challenge!");
      loadData();
    } catch (err: any) {
      alert(`Error: ${err.message}`);
    }
  };

  const handleRedeemReward = async (id: number, points: number) => {
    if (user.xp_points < points) {
      alert("Not enough XP!");
      return;
    }
    if (!window.confirm("Redeem this reward?")) return;
    try {
      await gamificationApi.redeemReward(id);
      alert("Reward redeemed successfully!");
      loadData(); // This will update user XP via leaderboard refresh
    } catch (err: any) {
      alert(`Error: ${err.message}`);
    }
  };

  if (loading) {
    return <div className="text-gray-400 p-8 flex items-center justify-center animate-pulse">Loading Gamification Engine...</div>;
  }

  const myBadgeIds = new Set(myBadges.map((ub) => ub.badge_id));

  // A helper to map badge name to an icon, since the DB just stores names right now
  const getBadgeIcon = (name: string) => {
    if (name.toLowerCase().includes("eco")) return <Leaf className="w-7 h-7" />;
    if (name.toLowerCase().includes("comply")) return <Scale className="w-7 h-7" />;
    if (name.toLowerCase().includes("csr")) return <Award className="w-7 h-7" />;
    return <Trophy className="w-7 h-7" />;
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Level progress */}
      <div className="glass-card p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <h3 className="text-2xl font-bold tracking-tight">XP Rewards & Achievements</h3>
          <p className="text-gray-400 text-sm">Earn XP points for taking eco-friendly actions and claim rewards.</p>
        </div>
        
        {/* Level Ring */}
        <div className="flex items-center gap-4 bg-slate-950/40 border border-brand-border p-4 rounded-xl md:w-80">
          <div className="w-12 h-12 rounded-full bg-gradient-emerald flex items-center justify-center font-extrabold text-white text-lg shrink-0 shadow-lg">
            {user.level}
          </div>
          <div className="flex-1 space-y-1.5 min-w-0">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-gray-400">Level Progress</span>
              <span className="text-emerald-400">{user.xp_points % 1000} / 1000 XP</span>
            </div>
            <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-brand-border">
              <div className="h-full bg-gradient-emerald rounded-full transition-all duration-1000" style={{ width: `${(user.xp_points % 1000) / 10}%` }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Grid: Challenges, Badges, Rewards */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        
        {/* Left Col: Challenges & Rewards */}
        <div className="space-y-8 xl:col-span-2">
          {/* Active challenges */}
          <div className="space-y-6">
            <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Active ESG Challenges</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {challenges.length === 0 && <p className="text-sm text-gray-500">No active challenges available.</p>}
              {challenges.map((ch) => (
                <div key={ch.id} className="glass-card p-6 rounded-2xl flex flex-col justify-between group hover:border-emerald-500/20 hover:shadow-emerald-950/5 hover:shadow-lg transition-all duration-300">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className={`text-[9px] px-2 py-0.5 rounded-full font-bold uppercase border ${
                        ch.difficulty === "hard" || ch.difficulty === "expert"
                          ? "bg-rose-950/40 text-rose-400 border-rose-500/20"
                          : "bg-emerald-950/40 text-emerald-400 border-emerald-500/20"
                      }`}>
                        {ch.difficulty}
                      </span>
                      <span className="text-[10px] text-gray-500 font-semibold flex items-center gap-1">
                        <Clock className="w-3 h-3" /> Till: {ch.deadline || "Ongoing"}
                      </span>
                    </div>
                    <h4 className="font-bold text-base leading-snug group-hover:text-emerald-400 transition-colors">{ch.title}</h4>
                    <p className="text-sm text-gray-400">{ch.description}</p>
                  </div>

                  <div className="flex justify-between items-center mt-6 pt-4 border-t border-brand-border">
                    <span className="text-sm font-extrabold text-amber-400">+{ch.xp_reward} XP</span>
                    <button
                      onClick={() => handleJoinChallenge(ch.id)}
                      className="bg-slate-900 border border-brand-border hover:bg-slate-800 text-gray-300 text-xs px-3 py-1.5 rounded-lg font-semibold transition-colors"
                    >
                      Join Challenge
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Rewards Store */}
          <div className="space-y-6">
            <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Rewards Store</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {rewards.length === 0 && <p className="text-sm text-gray-500">No rewards available.</p>}
              {rewards.map((reward) => (
                <div key={reward.id} className="glass-card p-5 rounded-2xl flex items-center gap-4">
                  <div className="w-14 h-14 bg-gradient-emerald rounded-xl flex items-center justify-center shrink-0 shadow-lg shadow-emerald-900/20">
                    <Gift className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-bold text-sm truncate">{reward.name}</h4>
                    <p className="text-xs text-gray-400 truncate">{reward.stock} remaining</p>
                    <div className="mt-2 flex items-center gap-2">
                      <span className="text-xs font-bold text-amber-400">{reward.points_required} XP</span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleRedeemReward(reward.id, reward.points_required)}
                    disabled={user.xp_points < reward.points_required || reward.stock <= 0}
                    className="shrink-0 bg-slate-900 border border-brand-border hover:bg-slate-800 disabled:opacity-50 text-white w-10 h-10 rounded-lg flex items-center justify-center transition-all"
                  >
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Col: Badges & Leaderboard */}
        <div className="space-y-8">
          {/* Badges Locker */}
          <div className="glass-card p-6 rounded-2xl space-y-6">
            <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Your Badges Locker</h3>
            {badges.length === 0 ? (
              <p className="text-sm text-gray-500">No badges in the system.</p>
            ) : (
              <div className="grid grid-cols-3 gap-4">
                {badges.map((badge) => {
                  const unlocked = myBadgeIds.has(badge.id);
                  const colorClass = unlocked 
                    ? "text-emerald-400 bg-emerald-950/40 border-emerald-500/20" 
                    : "text-gray-500 bg-slate-900 border-brand-border opacity-40";
                  
                  return (
                    <div key={badge.id} className="flex flex-col items-center gap-1.5 text-center group relative cursor-help">
                      <div className={`w-14 h-14 rounded-2xl border flex items-center justify-center shadow-md transition-all duration-300 ${unlocked ? 'group-hover:scale-105' : ''} ${colorClass}`}>
                        {getBadgeIcon(badge.name)}
                      </div>
                      <span className="text-[10px] font-semibold text-gray-400 mt-1 truncate w-full" title={badge.name}>
                        {badge.name}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Leaderboard */}
          <div className="glass-card rounded-2xl overflow-hidden flex flex-col">
            <div className="p-6 border-b border-brand-border">
              <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Global Leaderboard</h3>
            </div>
            <div className="overflow-y-auto max-h-[400px]">
              <div className="divide-y divide-brand-border">
                {leaderboard.map((entry) => (
                  <div key={entry.user_id} className={`p-4 flex items-center gap-4 transition-colors ${entry.user_id === user.id ? 'bg-emerald-950/20' : 'hover:bg-slate-900/30'}`}>
                    <div className="w-6 text-center font-bold text-gray-500 text-sm">
                      #{entry.rank}
                    </div>
                    <div className="w-10 h-10 rounded-full bg-slate-800 border border-brand-border flex items-center justify-center font-bold text-white text-xs shrink-0">
                      {entry.full_name.substring(0, 2).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-semibold truncate ${entry.user_id === user.id ? 'text-emerald-400' : 'text-white'}`}>
                        {entry.full_name} {entry.user_id === user.id && "(You)"}
                      </p>
                      <p className="text-xs text-gray-400 truncate">{entry.department_name || "No Dept"}</p>
                    </div>
                    <div className="text-right shrink-0">
                      <p className="text-sm font-bold text-amber-400">{entry.xp_points} XP</p>
                      <p className="text-[10px] text-gray-500 font-semibold">Lvl {entry.level}</p>
                    </div>
                  </div>
                ))}
                {leaderboard.length === 0 && (
                  <div className="p-4 text-sm text-gray-500 text-center">No players yet.</div>
                )}
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
