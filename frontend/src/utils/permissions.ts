/**
 * VoxCore Role-Based Access Control (RBAC)
 * 
 * Role Hierarchy:
 * - god: Full platform control (super-admin)
 * - admin: Full company control
 * - developer: Dev tools + schema access
 * - analyst: Run queries only
 * - viewer: Dashboards only
 */

export const ADMIN_ROLES = ["god", "admin"];
export const DEV_ROLES = ["god", "admin", "developer"];
export const QUERY_ROLES = ["god", "platform_owner", "admin", "developer", "analyst", "ai_analyst"];
export const DASHBOARD_ROLES = ["god", "platform_owner", "admin", "developer", "analyst", "ai_analyst", "viewer"];
export const PLATFORM_OWNER_ROLES = ["god", "platform_owner"];

/**
 * Check if user has admin access (god or admin role)
 * Admins bypass all restrictions on their tier
 */
export function isAdmin(role?: string): boolean {
  return role ? ADMIN_ROLES.includes(role) : false;
}

/**
 * Check if user can access developer tools
 */
export function isDeveloper(role?: string): boolean {
  return role ? DEV_ROLES.includes(role) : false;
}

/**
 * Check if user can execute queries
 */
export function canRunQueries(role?: string): boolean {
  return role ? QUERY_ROLES.includes(role) : false;
}

/**
 * Check if user can access dashboards
 */
export function canAccessDashboards(role?: string): boolean {
  return role ? DASHBOARD_ROLES.includes(role) : false;
}

/**
 * Check if user can access the global platform control center.
 */
export function canAccessControlCenter(role?: string, isSuperAdmin?: boolean): boolean {
  if (isSuperAdmin) return true;
  return role ? PLATFORM_OWNER_ROLES.includes(role) : false;
}

/**
 * Get human-readable role label
 */
export function getRoleLabel(role?: string): string {
  const labels: Record<string, string> = {
    god: "🌟 God Admin",
    platform_owner: "🧠 Platform Owner",
    admin: "👑 Admin",
    developer: "💻 Developer",
    analyst: "📊 Analyst",
    ai_analyst: "📊 AI Analyst",
    viewer: "👁️ Viewer",
  };
  return role ? labels[role] || role : "Unknown";
}

/**
 * Get role badge color
 */
export function getRoleBadgeColor(role?: string): string {
  const colors: Record<string, string> = {
    god: "#ff6b6b",      // red
    platform_owner: "#8b5cf6", // violet
    admin: "#ffd43b",    // yellow
    developer: "#4ecdc4", // teal
    analyst: "#95e1d3",   // mint
    ai_analyst: "#7dd3fc", // sky
    viewer: "#6c757d",    // gray
  };
  return role ? colors[role] || "#6c757d" : "#6c757d";
}

/**
 * Check if user has access to a specific feature
 */
export interface FeatureAccess {
  runQueries: boolean;
  devSpace: boolean;
  firewallRules: boolean;
  manageUsers: boolean;
  schema: boolean;
  governance: boolean;
}

export function getFeatureAccess(role?: string): FeatureAccess {
  return {
    runQueries: canRunQueries(role),
    devSpace: isDeveloper(role),
    firewallRules: isAdmin(role),
    manageUsers: isAdmin(role),
    schema: isDeveloper(role),
    governance: isAdmin(role),
  };
}
