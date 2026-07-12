import React, { useState } from "react";
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
  FileCheck
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

const MOCK_TRANSACTIONS: CarbonTransaction[] = [
  {
    id: 1,
    source_type: "fleet",
    quantity: 120,
    co2e: 324.5,
    factor_value: 2.7,
    transaction_date: "2026-07-10",
    created_by: "auto",
    status: "confirmed",
    source_reference: "FLEET/TRIP/1042",
    notes: "Delivery trip Mumbai-Pune"
  },
  {
    id: 2,
    source_type: "manufacturing",
    quantity: 500,
    co2e: 1250.0,
    factor_value: 2.5,
    transaction_date: "2026-07-09",
    created_by: "auto",
    status: "confirmed",
    source_reference: "MFG/BATCH/304",
    notes: "Assembly line A shift"
  },
  {
    id: 3,
    source_type: "purchase",
    quantity: 4500,
    co2e: 3825.0,
    factor_value: 0.85,
    transaction_date: "2026-07-01",
    created_by: "auto",
    status: "confirmed",
    source_reference: "UTIL/ELEC/Q2",
    notes: "Grid electricity Q2 main facility"
  },
  {
    id: 4,
    source_type: "expense",
    quantity: 45,
    co2e: 98.4,
    factor_value: 2.18,
    transaction_date: "2026-07-08",
    created_by: "manual",
    status: "confirmed",
    notes: "Flights expense audit"
  }
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
    status: "active"
  },
  {
    id: 2,
    title: "Corporate Anti-Bribery & Whistleblower Directive",
    type: "anti_bribery",
    content: "EcoSphere enforces zero tolerance for bribery, providing secure hotlines and dynamic protection for reporters.",
    version: "4.0",
    effective_date: "2026-03-15",
    status: "active"
  },
  {
    id: 3,
    title: "General Data Governance & Privacy Standard",
    type: "data_privacy",
    content: "Mandatory protocols for customer data handling, matching standard regulatory frameworks.",
    version: "1.2",
    effective_date: "2026-06-01",
    status: "active"
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

const MOCK_CHALLENGES: Challenge[] = [
  {
    id: 1,
    title: "Zero Waste Coffee Cup Week",
    description: "Bring your own reusable flask or cup for all office hot drinks.",
    xp_reward: 100,
    difficulty: "easy",
    deadline: "2026-07-20",
    evidence_required: false,
    status: "active"
  },
  {
    id: 2,
    title: "Carbon Footprint Audit Challenge",
    description: "Track and log every business expense category carbon rating.",
    xp_reward: 350,
    difficulty: "hard",
    deadline: "2026-08-05",
    evidence_required: true,
    status: "active"
  }
];

export default function App() {
  const [activeTab, setActiveTab] = useState<"summary" | "environmental" | "social" | "governance" | "gamification">("summary");
  const [user, setUser] = useState<User>(MOCK_USER);
  const [transactions, setTransactions] = useState<CarbonTransaction[]>(MOCK_TRANSACTIONS);
  const [csrActivities, setCsrActivities] = useState<CSRActivity[]>(MOCK_CSR_ACTIVITIES);
  const [policies, setPolicies] = useState<ESGPolicy[]>(MOCK_POLICIES);
  const [issues, setIssues] = useState<ComplianceIssue[]>(MOCK_ISSUES);
  
  // States for interactive modals / logging
  const [showLogModal, setShowLogModal] = useState(false);
  const [logType, setLogType] = useState<SourceType>("fleet");
  const [logQuantity, setLogQuantity] = useState("");
  const [logNotes, setLogNotes] = useState("");
  
  const [acknowledgedPolicies, setAcknowledgedPolicies] = useState<Record<number, boolean>>({
    1: true
  });

  const handleLogEmissions = (e: React.FormEvent) => {
    e.preventDefault();
    if (!logQuantity || isNaN(Number(logQuantity))) return;

    const quantity = Number(logQuantity);
    let factor = 1.0;
    if (logType === "fleet") factor = 2.7;
    else if (logType === "manufacturing") factor = 2.5;
    else if (logType === "purchase") factor = 0.85;
    else factor = 2.18;

    const co2e = Number((quantity * factor).toFixed(2));

    const newTxn: CarbonTransaction = {
      id: transactions.length + 1,
      source_type: logType,
      quantity,
      co2e,
      factor_value: factor,
      transaction_date: new Date().toISOString().split("T")[0],
      created_by: "manual",
      status: "confirmed",
      notes: logNotes
    };

    setTransactions([newTxn, ...transactions]);
    
    // Add XP to user for manual reporting
    setUser({
      ...user,
      xp_points: user.xp_points + 50
    });

    // Reset Form
    setLogQuantity("");
    setLogNotes("");
    setShowLogModal(false);
  };

  const togglePolicyAck = (id: number) => {
    const isAck = !acknowledgedPolicies[id];
    setAcknowledgedPolicies({
      ...acknowledgedPolicies,
      [id]: isAck
    });

    if (isAck) {
      setUser({
        ...user,
        xp_points: user.xp_points + 100
      });
    }
  };

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
            <div className="w-10 h-10 rounded-xl bg-gradient-emerald flex items-center justify-center font-bold text-white shadow-lg">
              DS
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
              {activeTab === "summary" ? "Overall Scorecard" : activeTab}
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
                  <p className="text-4xl font-extrabold mt-4 text-white">90.0<span className="text-lg text-gray-500">/100</span></p>
                  <p className="text-xs text-gray-400 mt-4">3/3 active policies acknowledged</p>
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
            <div className="space-y-8 animate-fade-in">
              <div>
                <h2 className="text-2xl font-bold tracking-tight">Corporate Governance & Audits</h2>
                <p className="text-gray-400 text-sm mt-0.5">Policy compliance tracking, mandatory sign-offs, and audit resolution ledgers.</p>
              </div>

              {/* Grid of Policies & Audits */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Active policies list */}
                <div className="space-y-6 lg:col-span-2">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Awaiting Sign-Offs</h3>
                  <div className="space-y-4">
                    {policies.map((p) => {
                      const isAcked = acknowledgedPolicies[p.id];
                      return (
                        <div key={p.id} className="glass-card p-6 rounded-2xl flex justify-between items-start gap-4">
                          <div className="space-y-3">
                            <div className="flex items-center gap-2.5">
                              <span className="text-[10px] bg-slate-800 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded-full font-bold">
                                Version {p.version}
                              </span>
                              <span className="text-xs text-gray-500 font-medium">Effective: {p.effective_date}</span>
                            </div>
                            <h4 className="font-bold text-base">{p.title}</h4>
                            <p className="text-sm text-gray-400 leading-relaxed">{p.content}</p>
                          </div>

                          <button
                            onClick={() => togglePolicyAck(p.id)}
                            className={`shrink-0 flex items-center gap-1.5 px-4.5 py-2.5 rounded-xl border text-sm font-semibold transition-all duration-300 ${
                              isAcked
                                ? "bg-emerald-950/40 text-emerald-400 border-emerald-500/30"
                                : "bg-gradient-indigo text-white border-transparent shadow-md hover:shadow-indigo-950/20 hover:-translate-y-0.5 active:translate-y-0"
                            }`}
                          >
                            {isAcked ? (
                              <>
                                <Check className="w-4 h-4" />
                                <span>Signed Off</span>
                              </>
                            ) : (
                              <>
                                <FileCheck className="w-4 h-4" />
                                <span>Sign Policy</span>
                              </>
                            )}
                          </button>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Audit issue tracking */}
                <div className="glass-card p-6 rounded-2xl space-y-6 h-fit">
                  <div className="flex justify-between items-center">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Compliance Audits</h3>
                    <ShieldAlert className="w-5 h-5 text-indigo-400" />
                  </div>
                  
                  <div className="space-y-4 divide-y divide-brand-border">
                    {issues.map((issue) => (
                      <div key={issue.id} className="pt-4 first:pt-0 space-y-2">
                        <div className="flex justify-between items-center text-xs">
                          <span className={`px-2 py-0.5 rounded-full font-bold text-[9px] uppercase border ${
                            issue.severity === "critical"
                              ? "bg-rose-950/40 text-rose-400 border-rose-500/20 animate-pulse"
                              : issue.severity === "high"
                              ? "bg-amber-950/40 text-amber-400 border-amber-500/20"
                              : "bg-slate-800 text-gray-400 border-brand-border"
                          }`}>
                            {issue.severity}
                          </span>
                          <span className="text-gray-500 font-semibold">Due: {issue.due_date}</span>
                        </div>
                        <h4 className="font-semibold text-sm leading-snug">{issue.title}</h4>
                        <div className="flex justify-between items-center pt-1 text-[10px]">
                          <span className="text-gray-500">ID: {issue.audit_id}</span>
                          <span className={`font-bold capitalize ${
                            issue.status === "resolved"
                              ? "text-emerald-400"
                              : issue.status === "in_progress"
                              ? "text-amber-400"
                              : "text-rose-400"
                          }`}>
                            {issue.status.replace("_", " ")}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "gamification" && (
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
                      <div className="h-full bg-gradient-emerald rounded-full" style={{ width: `${(user.xp_points % 1000) / 10}%` }}></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Active Challenges & Badges Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Active challenges */}
                <div className="space-y-6 lg:col-span-2">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Active ESG Challenges</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {MOCK_CHALLENGES.map((ch) => (
                      <div key={ch.id} className="glass-card p-6 rounded-2xl flex flex-col justify-between group hover:border-emerald-500/20 hover:shadow-emerald-950/5 hover:shadow-lg transition-all duration-300">
                        <div className="space-y-3">
                          <div className="flex justify-between items-center">
                            <span className={`text-[9px] px-2 py-0.5 rounded-full font-bold uppercase border ${
                              ch.difficulty === "hard"
                                ? "bg-rose-950/40 text-rose-400 border-rose-500/20"
                                : "bg-emerald-950/40 text-emerald-400 border-emerald-500/20"
                            }`}>
                              {ch.difficulty}
                            </span>
                            <span className="text-[10px] text-gray-500 font-semibold">Till: {ch.deadline}</span>
                          </div>
                          <h4 className="font-bold text-base leading-snug group-hover:text-emerald-400 transition-colors">{ch.title}</h4>
                          <p className="text-sm text-gray-400">{ch.description}</p>
                        </div>

                        <div className="flex justify-between items-center mt-6 pt-4 border-t border-brand-border">
                          <span className="text-xs font-semibold text-gray-500">Reward</span>
                          <span className="text-sm font-extrabold text-amber-400">+{ch.xp_reward} XP</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Badges Locker */}
                <div className="glass-card p-6 rounded-2xl space-y-6">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Your Badges Locker</h3>
                  <div className="grid grid-cols-3 gap-4">
                    {[
                      { icon: Leaf, label: "Eco Pioneer", unlocked: true, color: "text-emerald-400 bg-emerald-950/40 border-emerald-500/20" },
                      { icon: Award, label: "CSR Champion", unlocked: true, color: "text-teal-400 bg-teal-950/40 border-teal-500/20" },
                      { icon: Scale, label: "Comply Guard", unlocked: true, color: "text-indigo-400 bg-indigo-950/40 border-indigo-500/20" },
                      { icon: Trophy, label: "Top Ranker", unlocked: false, color: "text-gray-500 bg-slate-900 border-brand-border opacity-40" }
                    ].map((badge, idx) => {
                      const Icon = badge.icon;
                      return (
                        <div key={idx} className="flex flex-col items-center gap-1.5 text-center group">
                          <div className={`w-14 h-14 rounded-2xl border flex items-center justify-center shadow-md transition-all duration-300 group-hover:scale-105 ${badge.color}`}>
                            <Icon className="w-7 h-7" />
                          </div>
                          <span className="text-[10px] font-semibold text-gray-400 mt-1 truncate w-full">{badge.label}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* --- CARBON LOGGER MODAL --- */}
      {showLogModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-card w-full max-w-md rounded-2xl overflow-hidden shadow-2xl animate-scale-up">
            <div className="p-6 border-b border-brand-border flex justify-between items-center bg-slate-950/60">
              <h3 className="font-bold text-lg flex items-center gap-2">
                <Leaf className="w-5 h-5 text-emerald-400" />
                <span>Log Carbon Transaction</span>
              </h3>
              <button onClick={() => setShowLogModal(false)} className="text-gray-400 hover:text-white text-lg font-bold">
                &times;
              </button>
            </div>

            <form onSubmit={handleLogEmissions} className="p-6 space-y-4">
              {/* Source Type Selector */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Source Type</label>
                <select
                  value={logType}
                  onChange={(e) => setLogType(e.target.value as any)}
                  className="w-full bg-slate-900 border border-brand-border px-3.5 py-2.5 rounded-xl text-sm focus:outline-none focus:border-emerald-500/50"
                >
                  <option value="fleet">Fleet Vehicles (liters)</option>
                  <option value="manufacturing">Manufacturing (kW/h)</option>
                  <option value="purchase">Grid Electricity (MW/h)</option>
                  <option value="expense">Corporate Expense (USD)</option>
                </select>
              </div>

              {/* Quantity */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Quantity</label>
                <input
                  type="number"
                  placeholder="e.g. 150"
                  value={logQuantity}
                  onChange={(e) => setLogQuantity(e.target.value)}
                  className="w-full bg-slate-900 border border-brand-border px-3.5 py-2.5 rounded-xl text-sm focus:outline-none focus:border-emerald-500/50"
                  required
                />
              </div>

              {/* Notes */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Notes / Reference</label>
                <textarea
                  placeholder="e.g. Fleet logistics record code or description"
                  value={logNotes}
                  onChange={(e) => setLogNotes(e.target.value)}
                  rows={3}
                  className="w-full bg-slate-900 border border-brand-border px-3.5 py-2.5 rounded-xl text-sm focus:outline-none focus:border-emerald-500/50 resize-none"
                />
              </div>

              <div className="pt-4 flex gap-4">
                <button
                  type="button"
                  onClick={() => setShowLogModal(false)}
                  className="flex-1 bg-slate-900 border border-brand-border text-gray-400 py-2.5 rounded-xl text-sm font-semibold hover:text-white hover:bg-slate-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-gradient-emerald text-white py-2.5 rounded-xl text-sm font-semibold hover:shadow-emerald-950/20 hover:shadow-lg transition-all"
                >
                  Submit Log
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
