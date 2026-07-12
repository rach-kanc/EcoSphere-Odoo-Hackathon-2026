export type UserRole = "system_admin" | "esg_manager" | "dept_manager" | "employee" | "auditor";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  department_id?: number;
  is_active: boolean;
  xp_points: number;
  level: number;
}

export type DeptStatus = "active" | "inactive";

export interface Department {
  id: number;
  name: string;
  code?: string;
  employee_count: number;
  status: DeptStatus;
  head_id?: number;
  head?: User;
}

export type CategoryType = "CSR_ACTIVITY" | "CHALLENGE";
export type CategoryStatus = "Active" | "Inactive";

export interface Category {
  id: number;
  name: string;
  type: CategoryType;
  status: CategoryStatus;
}

export type SourceType = "purchase" | "manufacturing" | "expense" | "fleet";
export type CreatedBy = "auto" | "manual";
export type TransactionStatus = "draft" | "confirmed" | "cancelled";

export interface CarbonTransaction {
  id: number;
  department_id?: number;
  department?: Department;
  emission_factor_id: number;
  source_type: SourceType;
  source_record_id?: number;
  source_reference?: string;
  co2e: number;
  quantity: number;
  factor_value: number;
  transaction_date: string;
  created_by: CreatedBy;
  status: TransactionStatus;
  notes?: string;
}

export type CSRActivityStatus = "Draft" | "Active" | "Completed" | "Archived";

export interface CSRActivity {
  id: number;
  title: string;
  description?: string;
  category_id: number;
  category?: Category;
  department_id?: number;
  department?: Department;
  start_date?: string;
  end_date?: string;
  location?: string;
  max_participants?: number;
  points_per_participation: number;
  evidence_required: boolean;
  status: CSRActivityStatus;
  is_open_for_participation: boolean;
}

export type PolicyType = "anti_bribery" | "data_privacy" | "environmental" | "code_of_conduct" | "health_safety" | "other";
export type PolicyStatus = "draft" | "active" | "archived";

export interface ESGPolicy {
  id: number;
  title: string;
  type: PolicyType;
  content?: string;
  version: string;
  effective_date: string;
  status: PolicyStatus;
  created_at: string;
  updated_at: string;
}

export interface PolicyAcknowledgement {
  id: number;
  policy_id: number;
  employee_id: number;
  acknowledged_at: string;
  signature_text?: string;
}


export type AuditStatus = "planned" | "ongoing" | "completed" | "cancelled";
export type IssueSeverity = "low" | "medium" | "high" | "critical";
export type IssueStatus = "open" | "in_progress" | "resolved" | "false_positive";

export interface Audit {
  id: number;
  title: string;
  department_id: number;
  department?: Department;
  status: AuditStatus;
  scope_start: string;
  scope_end: string;
  auditor_id?: number;
  auditor?: User;
}

export interface ComplianceIssue {
  id: number;
  audit_id: number;
  title: string;
  description?: string;
  severity: IssueSeverity;
  status: IssueStatus;
  owner_id?: number;
  owner?: User;
  due_date?: string;
}

export type ChallengeDifficulty = "easy" | "medium" | "hard" | "expert";
export type ChallengeStatus = "draft" | "active" | "under_review" | "completed" | "archived";

export interface Challenge {
  id: number;
  title: string;
  description?: string;
  category_id?: number;
  category?: Category;
  xp_reward: number;
  difficulty: ChallengeDifficulty;
  deadline?: string;
  evidence_required: boolean;
  status: ChallengeStatus;
}
