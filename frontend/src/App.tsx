// @ts-nocheck
import React, { useEffect, useState } from "react";
import {
  LayoutDashboard,
  Leaf,
  Users,
  Scale,
  Trophy,
  TrendingUp,
  Plus,
  Award,
  ShieldAlert,
  CheckCircle2,
  MapPin,
  Calendar,
  Building2,
  AlertTriangle,
  FileText,
  Sparkles,
  Check,
  DollarSign,
  Briefcase,
  FileCheck,
  Zap,
  ArrowUpRight,
  Cpu
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
  PieChart,
  Pie
} from "recharts";

import GamificationTab from "./components/GamificationTab";
import GovernanceTab from "./components/GovernanceTab";
import EmissionFactorsTab from "./components/EmissionFactorsTab";
import AutomationTab from "./components/AutomationTab";
import ManualCarbonEntryModal from "./components/ManualCarbonEntryModal";
import { carbonTransactionsApi } from "./api/carbonTransactions";
import AuthScreen from "./features/auth/AuthScreen";
// TypeScript types from local types file
import {
  User,
  Department,
  CarbonTransaction,
  CSRActivity,
  ESGPolicy,
  ComplianceIssue,
  Challenge,
  SourceType
} from "./types";

// --- MOCK DATA ---
const MOCK_USER: User = {
  id: 1,
  email: "dev.saxena@ecosphere.com",
  full_name: "Dev Saxena",
  role: "esg_manager",
  department_id: 1,
  is_active: true,
  xp_points: 2450,
  level: 5
};

const MOCK_DEPARTMENTS: Department[] = [
  { id: 1, name: "Engineering & Dev", code: "ENG", employee_count: 120, status: "active", head_id: 1 },
  { id: 2, name: "Operations & Logistics", code: "OPS", employee_count: 250, status: "active" },
  { id: 3, name: "Sales & Marketing", code: "SAL", employee_count: 85, status: "active" },
  { id: 4, name: "Human Resources", code: "HR", employee_count: 30, status: "active" }
];

const MOCK_CARBON_DATA = [
  { month: "Jan", emissions: 4500, target: 4800 },
  { month: "Feb", emissions: 4200, target: 4700 },
  { month: "Mar", emissions: 3900, target: 4600 },
  { month: "Apr", emissions: 4100, target: 4500 },
  { month: "May", emissions: 3600, target: 4400 },
  { month: "Jun", emissions: 3200, target: 4300 }
];

const SOURCE_COLORS = {
  fleet: "#3b82f6",          // Blue
  manufacturing: "#10b981",  // Emerald
  purchase: "#a855f7",       // Purple
  expense: "#f59e0b"         // Amber
};

const MOCK_PIE_DATA = [
  { name: "Fleet Vehicles", value: 1250, color: SOURCE_COLORS.fleet },
  { name: "Manufacturing", value: 2400, color: SOURCE_COLORS.manufacturing },
  { name: "Purchase Energy", value: 950, color: SOURCE_COLORS.purchase },
  { name: "Logistical Expenses", value: 600, color: SOURCE_COLORS.expense }
];

const MOCK_CSR_ACTIVITIES: CSRActivity[] = [
  {
    id: 1,
    title: "City Tree Plantation Drive",
    description: "Plant 500 native trees in the local park with community volunteers.",
    category_id: 1,
    location: "Cubbon Park, Bengaluru",
    max_participants: 50,
    points_per_participation: 150,
    evidence_required: true,
    status: "Completed",
    is_open_for_participation: false,
    start_date: "2026-06-20",
    end_date: "2026-06-20"
  },
  {
    id: 2,
    title: "E-Waste Recycling Camp",
    description: "Dispose of corporate and personal electronics safely at our tech centers.",
    category_id: 1,
    location: "Corporate HQ, Tower B",
    max_participants: 100,
    points_per_participation: 100,
    evidence_required: false,
    status: "Active",
    is_open_for_participation: true,
    start_date: "2026-07-15",
    end_date: "2026-07-17"
  },
  {
    id: 3,
    title: "Sustain-a-thon Workshop",
    description: "Ideating operational workflows to eliminate single-use plastics.",
    category_id: 2,
    location: "Hybrid / Conference Room 4",
    max_participants: 30,
    points_per_participation: 200,
    evidence_required: true,
    status: "Active",
    is_open_for_participation: true,
    start_date: "2026-07-28",
    end_date: "2026-07-29"
  }
];

const MOCK_POLICIES: ESGPolicy[] = [
  {
    id: 1,
    title: "Sustainable Travel & Aviation Guidelines",
    type: "environmental",
    content: "Our target is to reduce aviation emissions by 25% by requiring trains for distances under 500km and economy booking class.",
    version: "2.1",
    effective_date: "2026-01-01",
    status: "active",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z"
  },
  {
    id: 2,
    title: "Corporate Anti-Bribery & Whistleblower Directive",
    type: "anti_bribery",
    content: "EcoSphere enforces zero tolerance for bribery, providing secure hotlines and dynamic protection for reporters.",
    version: "4.0",
    effective_date: "2026-03-15",
    status: "active",
    created_at: "2026-03-15T00:00:00Z",
    updated_at: "2026-03-15T00:00:00Z"
  },
  {
    id: 3,
    title: "General Data Governance & Privacy Standard",
    type: "data_privacy",
    content: "Mandatory protocols for customer data handling, matching standard regulatory frameworks.",
    version: "1.2",
    effective_date: "2026-06-01",
    status: "active",
    created_at: "2026-06-01T00:00:00Z",
    updated_at: "2026-06-01T00:00:00Z"
  }
];


const MOCK_ISSUES: ComplianceIssue[] = [
  {
    id: 1,
    audit_id: 101,
    title: "Missing fleet trip logs for logistics unit B",
    severity: "high",
    status: "in_progress",
    due_date: "2026-07-25"
  },
  {
    id: 2,
    audit_id: 102,
    title: "Improper disposal tracking of decommissioned servers",
    severity: "critical",
    status: "open",
    due_date: "2026-07-18"
  },
  {
    id: 3,
    audit_id: 103,
    title: "Incomplete policy sign-offs for sales team",
    severity: "low",
    status: "resolved",
    due_date: "2026-06-30"
  }
];

function LandingPage({ onEnterDashboard }: { onEnterDashboard: () => void }) {
  const pillars = [
    {
      number: "1.",
      title: "carbon intelligence",
      codename: "/ live ledger /",
      body: "turns fleet, energy, expense, and manufacturing activity into a trusted emissions trail.",
      icon: Leaf
    },
    {
      number: "2.",
      title: "social momentum",
      codename: "/ participation graph /",
      body: "connects people to CSR work, evidence, points, and team-level accountability.",
      icon: Users
    },
    {
      number: "3.",
      title: "governance memory",
      codename: "/ policy mesh /",
      body: "keeps policies, acknowledgements, risk issues, and audit signals moving together.",
      icon: Scale
    }
  ];

  const proofPoints = [
    "5,497.9 kg co2e recorded",
    "3 active policies",
    "4 departments scored",
    "2 reduction goals"
  ];

  return (
    <div className="landing-paper min-h-screen overflow-hidden bg-[#ede8d7] text-[#11110f]">
      <header className="fixed left-0 right-0 top-6 z-50 px-4">
        <nav className="mx-auto flex max-w-5xl items-center justify-between rounded-full border border-black/15 bg-[#f3eedf]/80 px-4 py-2 shadow-[0_12px_40px_rgba(20,18,12,0.12)] backdrop-blur-xl">
          <a href="#top" className="flex items-center gap-2 rounded-full px-3 py-2 text-xl font-black tracking-tight">
            <Leaf className="h-6 w-6 fill-[#11110f] stroke-[#11110f]" />
            <span>ecosphere</span>
          </a>

          <div className="hidden items-center gap-7 text-sm font-medium lowercase md:flex">
            <a href="#system" className="hover:text-[#53652c]">system</a>
            <a href="#modules" className="hover:text-[#53652c]">modules</a>
            <a href="#impact" className="hover:text-[#53652c]">impact</a>
            <button onClick={onEnterDashboard} className="hover:text-[#53652c]">dashboard</button>
          </div>

          <button
            onClick={onEnterDashboard}
            className="inline-flex items-center gap-2 rounded-full bg-[#11110f] px-5 py-3 text-sm font-bold lowercase text-[#f6f0df] transition hover:bg-[#53652c]"
          >
            open app
            <ArrowUpRight className="h-4 w-4" />
          </button>
        </nav>
      </header>

      <main id="top">
        <section className="relative flex min-h-[92vh] items-end overflow-hidden px-4 pb-12 pt-32 md:pb-16">
          <video
            className="absolute inset-0 h-full w-full object-cover"
            src="/resources/ecosphere-hero.mp4"
            autoPlay
            loop
            muted
            playsInline
            aria-hidden="true"
          />
          <div className="absolute inset-0 bg-[#ede8d7]/35 mix-blend-screen" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(237,232,215,0.05),rgba(17,17,15,0.62))]" />

          <div className="relative z-10 mx-auto grid w-full max-w-6xl gap-10 text-[#f8f2df] lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
            <div>
              <p className="mb-5 max-w-xl text-sm font-semibold lowercase tracking-[0.24em] text-[#d7e2b6]">
                esg operating system for odoo
              </p>
              <h1 className="max-w-5xl text-[clamp(4rem,12vw,10.5rem)] font-black lowercase leading-[0.82] tracking-normal">
                ecosphere
              </h1>
              <p className="mt-8 max-w-2xl text-[clamp(1.25rem,2.4vw,2.35rem)] font-semibold lowercase leading-tight">
                turns environmental, social, and governance work into one living enterprise record.
              </p>
            </div>

            <div className="flex flex-col gap-5 lg:items-end">
              <div className="max-w-md text-base font-medium lowercase leading-relaxed text-[#f0ead7]">
                built for teams that need carbon accounting, policy acknowledgement, csr engagement, and reward loops without leaving their operational flow.
              </div>
              <div className="flex flex-wrap gap-3">
                {proofPoints.map((point) => (
                  <span key={point} className="rounded-full border border-[#f8f2df]/35 bg-[#11110f]/35 px-4 py-2 text-xs font-bold lowercase backdrop-blur-md">
                    {point}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section id="system" className="px-4 py-24 md:py-32">
          <div className="mx-auto max-w-6xl">
            <p className="mb-8 text-sm font-bold lowercase tracking-[0.28em] text-[#53652c]">
              we are building an esg command layer
            </p>
            <h2 className="max-w-5xl text-[clamp(3rem,8vw,8.5rem)] font-black lowercase leading-[0.88] tracking-normal">
              making sustainability data feel alive.
            </h2>
            <button
              onClick={onEnterDashboard}
              className="mt-10 inline-flex items-center gap-2 rounded-full border border-black/15 bg-[#11110f] px-6 py-4 text-sm font-black lowercase text-[#f6f0df] transition hover:bg-[#53652c]"
            >
              launch dashboard
              <ArrowUpRight className="h-4 w-4" />
            </button>
          </div>
        </section>

        <section id="modules" className="px-4 py-20">
          <div className="mx-auto max-w-6xl">
            <p className="mb-8 text-sm font-bold lowercase tracking-[0.28em] text-[#53652c]">
              this requires mastering 3 essentials:
            </p>
            <div className="grid gap-5 lg:grid-cols-3">
              {pillars.map((pillar) => {
                const Icon = pillar.icon;
                return (
                  <article key={pillar.title} className="min-h-[25rem] border-t border-black/20 py-8">
                    <div className="mb-12 flex items-center justify-between">
                      <span className="text-4xl font-black lowercase">{pillar.number}</span>
                      <span className="rounded-full border border-black/15 bg-[#f6f0df]/70 p-3">
                        <Icon className="h-6 w-6" />
                      </span>
                    </div>
                    <h3 className="text-4xl font-black lowercase leading-none">{pillar.title}</h3>
                    <p className="mt-3 text-sm font-bold lowercase text-[#53652c]">{pillar.codename}</p>
                    <p className="mt-8 text-xl font-semibold lowercase leading-snug text-[#2e3027]">{pillar.body}</p>
                  </article>
                );
              })}
            </div>
          </div>
        </section>

        <section id="impact" className="overflow-hidden py-24">
          <div className="landing-marquee flex min-w-max gap-5 text-[clamp(3rem,8vw,8rem)] font-black lowercase leading-none text-[#11110f]">
            <span>carbon ledger</span>
            <span>policy memory</span>
            <span>csr motion</span>
            <span>team rewards</span>
            <span>audit clarity</span>
          </div>
          <div className="mx-auto mt-20 grid max-w-6xl gap-10 px-4 lg:grid-cols-[0.9fr_1.1fr] lg:items-end">
            <h2 className="text-[clamp(2.7rem,7vw,7rem)] font-black lowercase leading-[0.9] tracking-normal">
              one place for proof, progress, and people.
            </h2>
            <div className="grid gap-4 sm:grid-cols-2">
              {[
                ["environmental", "automated emission factors, manual logs, and source distribution."],
                ["social", "csr activity registration, evidence requirements, and xp incentives."],
                ["governance", "policy acknowledgement, issue severity, and compliance score."],
                ["gamification", "levels, challenges, badges, and department scoreboards."]
              ].map(([title, body]) => (
                <div key={title} className="border-t border-black/20 pt-5">
                  <p className="text-lg font-black lowercase">{title}</p>
                  <p className="mt-3 text-sm font-semibold lowercase leading-relaxed text-[#444638]">{body}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <footer className="bg-[#10100e] px-4 py-14 text-[#f6f0df]">
          <div className="mx-auto flex max-w-6xl flex-col gap-10 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm font-bold lowercase tracking-[0.28em] text-[#b8c886]">ecosphere</p>
              <h2 className="mt-4 max-w-3xl text-5xl font-black lowercase leading-none md:text-7xl">
                open the operating view.
              </h2>
            </div>
            <button
              onClick={onEnterDashboard}
              className="inline-flex w-fit items-center gap-2 rounded-full bg-[#f6f0df] px-6 py-4 text-sm font-black lowercase text-[#10100e] transition hover:bg-[#b8c886]"
            >
              enter dashboard
              <ArrowUpRight className="h-4 w-4" />
            </button>
          </div>
        </footer>
      </main>
    </div>
  );
}


export default function App() {
  const [showLanding, setShowLanding] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!localStorage.getItem("ecosphere_token"));
  const [activeTab, setActiveTab] = useState<"summary" | "environmental" | "emission_factors" | "automation" | "social" | "governance" | "gamification">("summary");
  const [user, setUser] = useState<User>(MOCK_USER);
  const [transactions, setTransactions] = useState<CarbonTransaction[]>([]);
  const [csrActivities, setCsrActivities] = useState<CSRActivity[]>(MOCK_CSR_ACTIVITIES);
  const [policies, setPolicies] = useState<ESGPolicy[]>(MOCK_POLICIES);
  const [issues, setIssues] = useState<ComplianceIssue[]>(MOCK_ISSUES);

  // States for interactive modals / logging
  const [showLogModal, setShowLogModal] = useState(false);

  const [acknowledgedPolicies, setAcknowledgedPolicies] = useState<Record<number, boolean>>({});

  useEffect(() => {
    carbonTransactionsApi
      .list()
      .then(setTransactions)
      .catch((err) => console.error("Failed to load carbon transactions", err));
  }, []);

  const handlePolicyAck = (id: number) => {
    setAcknowledgedPolicies((prev) => ({ ...prev, [id]: true }));
  };

  const handleUserXpUpdate = (xp: number) => {
    setUser((prev) => ({ ...prev, xp_points: prev.xp_points + xp }));
  };

  const handleLogin = (token: string, loggedInUser: User) => {
    localStorage.setItem("ecosphere_token", token);
    setUser(loggedInUser);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem("ecosphere_token");
    setIsAuthenticated(false);
  };
  // --- Governance score (live) ---
  const activePolicies = policies.filter((p) => p.status === "active");
  const ackedCount = activePolicies.filter((p) => !!acknowledgedPolicies[p.id]).length;
  const activeCount = activePolicies.length;
  // Score = (acknowledged / total) * 100, capped at 100. Show 0 when no active policies.
  const gScore = activeCount > 0 ? Math.round((ackedCount / activeCount) * 1000) / 10 : 0;

  if (showLanding) {
    return <LandingPage onEnterDashboard={() => setShowLanding(false)} />;
  }

  if (!isAuthenticated) {
    return <AuthScreen onLogin={handleLogin} />;
  }

  return (
    <div className="flex min-h-screen bg-brand-dark">
      {/* --- SIDEBAR --- */}
      <aside className="w-64 bg-slate-950 border-r border-brand-border flex flex-col justify-between shrink-0">
        <div>
          {/* Logo */}
          <div className="p-6 border-b border-brand-border flex items-center gap-3">
            <div className="bg-emerald-950 p-2 rounded-lg border border-emerald-500/30">
              <Leaf className="text-emerald-400 w-6 h-6 animate-pulse" />
            </div>
            <div>
              <h1 className="font-extrabold text-lg text-glow-emerald text-emerald-400 leading-none">EcoSphere</h1>
              <span className="text-xs text-gray-500 font-semibold tracking-widest uppercase">Odoo ESG Stack</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1">
            {[
              { id: "summary", label: "ESG Summary", icon: LayoutDashboard, color: "text-emerald-400" },
              { id: "environmental", label: "Environmental", icon: Leaf, color: "text-emerald-400" },
              { id: "emission_factors", label: "Emission Factors", icon: Zap, color: "text-emerald-400" },
              { id: "automation", label: "Automation", icon: Cpu, color: "text-emerald-400" },
              { id: "social", label: "Social", icon: Users, color: "text-teal-400" },
              { id: "governance", label: "Governance", icon: Scale, color: "text-indigo-400" },
              { id: "gamification", label: "XP & Rewards", icon: Trophy, color: "text-amber-400" }
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group ${
                    isActive
                      ? "bg-slate-900 border border-brand-border text-white shadow-lg shadow-emerald-500/5"
                      : "text-gray-400 hover:text-white hover:bg-slate-900/50"
                  }`}
                >
                  <Icon className={`w-5 h-5 transition-transform duration-300 group-hover:scale-110 ${tab.color}`} />
                  <span className="font-medium text-sm">{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* User Mini Profile */}
        <div className="p-4 border-t border-brand-border bg-slate-950/70">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-emerald flex items-center justify-center font-bold text-white shadow-lg shrink-0">
              {user.full_name.substring(0, 2).toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold truncate">{user.full_name}</p>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="text-[10px] bg-slate-800 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.5 rounded-full font-bold">
                  Lvl {user.level}
                </span>
                <span className="text-[10px] text-gray-400 font-medium truncate">
                  {user.xp_points} XP
                </span>
              </div>
            </div>
            <button onClick={handleLogout} className="p-2 text-gray-500 hover:text-rose-400 transition-colors" title="Logout">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
            </button>
          </div>
        </div>
      </aside>

      {/* --- MAIN CONTENT AREA --- */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Top Navbar */}
        <header className="h-16 border-b border-brand-border bg-slate-950/40 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-20">
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 uppercase tracking-widest font-semibold">EcoSphere</span>
            <span className="text-gray-600">/</span>
            <span className="text-sm font-semibold capitalize text-gray-300">
              {activeTab === "summary"
                ? "Overall Scorecard"
                : activeTab === "emission_factors"
                ? "Emission Factors"
                : activeTab === "automation"
                ? "Automation"
                : activeTab}
            </span>
          </div>

          <div className="flex items-center gap-6">
            {/* Quick XP display */}
            <div className="flex items-center gap-2 bg-emerald-950/40 border border-emerald-500/20 px-3.5 py-1.5 rounded-full">
              <Sparkles className="w-4 h-4 text-emerald-400 animate-spin" style={{ animationDuration: '3s' }} />
              <span className="text-xs font-bold text-emerald-300">{user.xp_points} XP Available</span>
            </div>

            <button
              onClick={() => setShowLogModal(true)}
              className="bg-gradient-emerald hover:shadow-emerald-950/20 hover:shadow-lg transition-all px-4 py-2 rounded-xl text-sm font-semibold text-white flex items-center gap-2 shadow-md hover:-translate-y-0.5 active:translate-y-0 duration-300"
            >
              <Plus className="w-4 h-4" />
              <span>Log Carbon Event</span>
            </button>
          </div>
        </header>

        {/* Dynamic View Injection */}
        <div className="flex-1 p-8 overflow-y-auto">
          {activeTab === "summary" && (
            <div className="space-y-8 animate-fade-in">
              {/* Header Info */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-bold tracking-tight">EcoSphere ESG Dashboard</h2>
                  <p className="text-gray-400 text-sm mt-0.5">Real-time sustainability metrics derived from ERP operations.</p>
                </div>
                <div className="text-xs text-gray-500 bg-slate-900 border border-brand-border px-3 py-1.5 rounded-lg flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
                  <span>Direct ERP Connection Active</span>
                </div>
              </div>

              {/* ESG Score Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {/* Weighted ESG Score */}
                <div className="glass-card p-6 rounded-2xl relative overflow-hidden group">
                  <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl group-hover:scale-125 transition-transform duration-500"></div>
                  <div className="flex justify-between items-start">
                    <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest">Weighted ESG</span>
                    <span className="text-[10px] bg-emerald-950/40 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full font-bold">
                      Grade A
                    </span>
                  </div>
                  <p className="text-4xl font-extrabold mt-4 text-glow-emerald text-emerald-400">82.7<span className="text-lg text-emerald-500">/100</span></p>
                  <div className="flex items-center gap-1.5 text-xs text-gray-400 mt-4">
                    <TrendingUp className="w-4 h-4 text-emerald-400" />
                    <span>+2.4% vs previous month</span>
                  </div>
                </div>

                {/* E Pillar */}
                <div className="glass-card p-6 rounded-2xl relative overflow-hidden group">
                  <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl group-hover:scale-125 transition-transform duration-500"></div>
                  <div className="flex justify-between items-start">
                    <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest">Environmental (E)</span>
                    <Leaf className="w-5 h-5 text-emerald-400" />
                  </div>
                  <p className="text-4xl font-extrabold mt-4 text-white">82.0<span className="text-lg text-gray-500">/100</span></p>
                  <p className="text-xs text-gray-400 mt-4">Emissions reduced by 400kg CO2e</p>
                </div>

                {/* S Pillar */}
                <div className="glass-card p-6 rounded-2xl relative overflow-hidden group">
                  <div className="absolute top-0 right-0 w-24 h-24 bg-teal-500/10 rounded-full blur-2xl group-hover:scale-125 transition-transform duration-500"></div>
                  <div className="flex justify-between items-start">
                    <span className="text-xs font-bold text-teal-400 uppercase tracking-widest">Social (S)</span>
                    <Users className="w-5 h-5 text-teal-400" />
                  </div>
                  <p className="text-4xl font-extrabold mt-4 text-white">75.0<span className="text-lg text-gray-500">/100</span></p>
                  <p className="text-xs text-gray-400 mt-4">70% CSR participation achieved</p>
                </div>

                {/* G Pillar */}
                <div className="glass-card p-6 rounded-2xl relative overflow-hidden group">
                  <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/10 rounded-full blur-2xl group-hover:scale-125 transition-transform duration-500"></div>
                  <div className="flex justify-between items-start">
                    <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest">Governance (G)</span>
                    <Scale className="w-5 h-5 text-indigo-400" />
                  </div>
                  <p className="text-4xl font-extrabold mt-4 text-white">
                    {gScore.toFixed(1)}<span className="text-lg text-gray-500">/100</span>
                  </p>
                  <p className="text-xs text-gray-400 mt-4">
                    {ackedCount}/{activeCount} active {activeCount === 1 ? "policy" : "policies"} acknowledged
                  </p>
                </div>
              </div>

              {/* Main Visualizations */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Recharts Area Chart */}
                <div className="glass-card p-6 rounded-2xl lg:col-span-2">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400 mb-6">Emissions Trend vs Target (kg CO₂e)</h3>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={MOCK_CARBON_DATA}>
                        <defs>
                          <linearGradient id="emissionsGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                            <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                        <XAxis dataKey="month" stroke="#9ca3af" fontSize={12} />
                        <YAxis stroke="#9ca3af" fontSize={12} />
                        <Tooltip contentStyle={{ backgroundColor: "#0b0f19", border: "1px solid #1f2937", borderRadius: "12px", color: "white" }} />
                        <Area type="monotone" dataKey="emissions" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#emissionsGrad)" name="Current" />
                        <Area type="monotone" dataKey="target" stroke="#4f46e5" strokeWidth={1} strokeDasharray="5 5" fillOpacity={0} name="Target" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Score Breakdown Bar Chart */}
                <div className="glass-card p-6 rounded-2xl flex flex-col justify-between">
                  <div>
                    <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400 mb-6">ESG Pillar Ratios</h3>
                    <div className="h-56 flex items-center justify-center">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={MOCK_PIE_DATA}
                            cx="50%"
                            cy="50%"
                            innerRadius={50}
                            outerRadius={75}
                            paddingAngle={4}
                            dataKey="value"
                          >
                            {MOCK_PIE_DATA.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip contentStyle={{ backgroundColor: "#0b0f19", border: "1px solid #1f2937", borderRadius: "12px" }} />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                  
                  {/* Legend */}
                  <div className="grid grid-cols-2 gap-2 mt-4">
                    {MOCK_PIE_DATA.map((entry) => (
                      <div key={entry.name} className="flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: entry.color }}></span>
                        <span className="text-[10px] font-semibold text-gray-400 truncate">{entry.name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Departmental Rankings */}
              <div className="glass-card rounded-2xl overflow-hidden">
                <div className="p-6 border-b border-brand-border">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Department Performance Ranks</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-slate-950 text-gray-400 text-xs font-bold uppercase">
                      <tr>
                        <th className="p-4">Code</th>
                        <th className="p-4">Department</th>
                        <th className="p-4">Employees</th>
                        <th className="p-4 text-center">CSR Score</th>
                        <th className="p-4 text-center">Carbon Savings</th>
                        <th className="p-4 text-right">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-brand-border">
                      {[
                        { code: "ENG", name: "Engineering & Dev", size: 120, csr: "92%", savings: "840 kg", status: "Active" },
                        { code: "OPS", name: "Operations & Logistics", size: 250, csr: "74%", savings: "1,200 kg", status: "Active" },
                        { code: "SAL", name: "Sales & Marketing", size: 85, csr: "65%", savings: "410 kg", status: "Active" },
                        { code: "HR", name: "Human Resources", size: 30, csr: "95%", savings: "150 kg", status: "Active" }
                      ].map((d, index) => (
                        <tr key={d.code} className="hover:bg-slate-900/30 transition-colors">
                          <td className="p-4 font-bold text-emerald-400">{d.code}</td>
                          <td className="p-4 font-semibold">{d.name}</td>
                          <td className="p-4 text-gray-400">{d.size}</td>
                          <td className="p-4 text-center font-semibold text-teal-400">{d.csr}</td>
                          <td className="p-4 text-center font-semibold text-emerald-400">{d.savings}</td>
                          <td className="p-4 text-right">
                            <span className="text-xs bg-emerald-950 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full font-bold">
                              {d.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === "environmental" && (
            <div className="space-y-8 animate-fade-in">
              <div>
                <h2 className="text-2xl font-bold tracking-tight">Environmental Module</h2>
                <p className="text-gray-400 text-sm mt-0.5">Automated carbon accounting from logistics, fleets, and facility operations.</p>
              </div>

              {/* Grid with Logging & Pie */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Stats */}
                <div className="space-y-6 lg:col-span-2">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="glass-card p-6 rounded-2xl">
                      <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Total CO₂e Recorded</p>
                      <p className="text-3xl font-extrabold text-white mt-2">5,497.9 kg</p>
                    </div>
                    <div className="glass-card p-6 rounded-2xl">
                      <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Active Reduction Goals</p>
                      <p className="text-3xl font-extrabold text-white mt-2">2 Targets</p>
                    </div>
                  </div>

                  {/* Transactions Table */}
                  <div className="glass-card rounded-2xl overflow-hidden">
                    <div className="p-6 border-b border-brand-border flex justify-between items-center">
                      <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Recent Carbon Ledger</h3>
                      <button onClick={() => setShowLogModal(true)} className="text-xs bg-emerald-950 text-emerald-400 border border-emerald-500/20 px-3 py-1.5 rounded-lg font-bold hover:bg-emerald-900 transition-colors">
                        Add Log
                      </button>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-sm">
                        <thead className="bg-slate-950 text-gray-400 text-xs font-bold uppercase">
                          <tr>
                            <th className="p-4">Source Type</th>
                            <th className="p-4">Quantity</th>
                            <th className="p-4">CO2e Emissions</th>
                            <th className="p-4">Reference</th>
                            <th className="p-4">Date</th>
                            <th className="p-4 text-right">Method</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-brand-border">
                          {transactions.map((t) => (
                            <tr key={t.id} className="hover:bg-slate-900/30 transition-colors">
                              <td className="p-4 flex items-center gap-2">
                                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: SOURCE_COLORS[t.source_type] }}></span>
                                <span className="font-semibold capitalize">{t.source_type}</span>
                              </td>
                              <td className="p-4 font-medium">{t.quantity} units</td>
                              <td className="p-4 font-bold text-rose-400">{t.co2e} kg</td>
                              <td className="p-4 text-gray-400 text-xs">{t.source_reference || t.notes || "Manual Override"}</td>
                              <td className="p-4 text-gray-400">{t.transaction_date}</td>
                              <td className="p-4 text-right">
                                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${
                                  t.created_by === "auto"
                                    ? "bg-emerald-950/40 text-emerald-400 border-emerald-500/20"
                                    : "bg-amber-950/40 text-amber-400 border-amber-500/20"
                                }`}>
                                  {t.created_by.toUpperCase()}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>

                {/* Source Breakdowns */}
                <div className="glass-card p-6 rounded-2xl">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400 mb-6">Emissions Source Distribution</h3>
                  <div className="space-y-6">
                    {MOCK_PIE_DATA.map((entry) => {
                      const total = MOCK_PIE_DATA.reduce((sum, d) => sum + d.value, 0);
                      const percent = Math.round((entry.value / total) * 100);
                      return (
                        <div key={entry.name}>
                          <div className="flex justify-between items-center text-xs font-semibold mb-2">
                            <span className="text-gray-300">{entry.name}</span>
                            <span className="text-gray-400">{entry.value} kg ({percent}%)</span>
                          </div>
                          <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-brand-border">
                            <div className="h-full rounded-full" style={{ width: `${percent}%`, backgroundColor: entry.color }}></div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "emission_factors" && <EmissionFactorsTab />}

          {activeTab === "automation" && <AutomationTab />}

          {activeTab === "social" && (
            <div className="space-y-8 animate-fade-in">
              <div>
                <h2 className="text-2xl font-bold tracking-tight">Social & CSR Engagement</h2>
                <p className="text-gray-400 text-sm mt-0.5">Corporate social initiatives and employee volunteer coordination.</p>
              </div>

              {/* Feed of active/completed activities */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {csrActivities.map((act) => (
                  <div key={act.id} className="glass-card rounded-2xl flex flex-col justify-between overflow-hidden">
                    <div className="p-6 space-y-4">
                      <div className="flex justify-between items-center">
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${
                          act.status === "Active"
                            ? "bg-teal-950/40 text-teal-400 border-teal-500/20"
                            : "bg-slate-900 text-gray-400 border-brand-border"
                        }`}>
                          {act.status}
                        </span>
                        <div className="flex items-center gap-1 bg-amber-950/40 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded-full text-[10px] font-bold">
                          <Award className="w-3.5 h-3.5" />
                          <span>+{act.points_per_participation} XP</span>
                        </div>
                      </div>

                      <h3 className="font-bold text-lg leading-snug">{act.title}</h3>
                      <p className="text-gray-400 text-sm">{act.description}</p>
                    </div>

                    <div className="p-6 bg-slate-950/40 border-t border-brand-border space-y-4">
                      <div className="space-y-1.5 text-xs text-gray-400">
                        <div className="flex items-center gap-2">
                          <MapPin className="w-4 h-4 text-teal-400" />
                          <span>{act.location}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-teal-400" />
                          <span>{act.start_date}</span>
                        </div>
                      </div>

                      {act.status === "Active" ? (
                        <button
                          onClick={() => {
                            // Mock participation register
                            alert(`Registered for "${act.title}"! You will be awarded ${act.points_per_participation} XP upon admin validation.`);
                          }}
                          className="w-full bg-gradient-teal py-2 rounded-xl text-sm font-semibold text-white shadow-md hover:shadow-teal-950/20 transition-all duration-300"
                        >
                          Join Initiative
                        </button>
                      ) : (
                        <div className="text-center py-2 text-xs bg-slate-900 border border-brand-border rounded-xl text-gray-500 font-semibold flex items-center justify-center gap-2">
                          <Check className="w-4 h-4 text-teal-500" />
                          <span>Initiative Completed</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "governance" && (
            <GovernanceTab
              user={user}
              policies={policies}
              issues={issues}
              acknowledgedPolicies={acknowledgedPolicies}
              onPolicyAck={handlePolicyAck}
              onUserXpUpdate={handleUserXpUpdate}
            />
          )}

          {activeTab === "gamification" && (
            <GamificationTab user={user} setUser={setUser} />
          )}

        </div>
      </main>

      {/* --- CARBON LOGGER MODAL --- */}
      {showLogModal && (
        <ManualCarbonEntryModal
          onClose={() => setShowLogModal(false)}
          onCreated={(transaction) => setTransactions((prev) => [transaction, ...prev])}
        />
      )}
    </div>
  );
}
