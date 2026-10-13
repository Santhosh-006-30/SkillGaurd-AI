// Central typed API service layer for SkillGuard AI SOC Dashboard

const getAuthHeaders = (): HeadersInit => {
  const token = localStorage.getItem('skillguard_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: {
    code: string;
    message: string;
  };
}

export const api = {
  // Health
  getHealth: async () => {
    const res = await fetch('/api/v1/health', { headers: getAuthHeaders() });
    return (await res.json()) as ApiResponse<any>;
  },

  // Analytics
  getOverview: async () => {
    const res = await fetch('/api/v1/analytics/overview', { headers: getAuthHeaders() });
    return (await res.json()) as ApiResponse<{
      total_centres: number;
      active_cameras: number;
      total_cameras: number;
      open_alerts: number;
      high_risk_centres: number;
      average_compliance: number;
      total_attendance_discrepancies: number;
      total_infrastructure_shortages: number;
      offline_cameras: number;
    }>;
  },

  getRiskDistribution: async () => {
    const res = await fetch('/api/v1/analytics/risk-distribution', { headers: getAuthHeaders() });
    return (await res.json()) as ApiResponse<Array<{ name: string; count: number; percentage: number }>>;
  },

  getComplianceTrend: async () => {
    const res = await fetch('/api/v1/analytics/compliance-trend', { headers: getAuthHeaders() });
    return (await res.json()) as ApiResponse<Array<{ date: string; attendance_score: number; infrastructure_score: number; overall_score: number }>>;
  },

  getAlertsTrend: async () => {
    const res = await fetch('/api/v1/analytics/alerts-trend', { headers: getAuthHeaders() });
    return (await res.json()) as ApiResponse<Array<{ date: string; critical_count: number; high_count: number; medium_count: number; low_count: number }>>;
  },

  getRankings: async () => {
    const res = await fetch('/api/v1/analytics/rankings', { headers: getAuthHeaders() });
    return (await res.json()) as ApiResponse<Array<{ centre_code: string; name: string; district: string; overall_score: number; risk_level: string; open_alerts: number }>>;
  },

  // Centres
  getCentres: async (params?: { district?: string; search?: string; status?: string }) => {
    const query = new URLSearchParams();
    if (params?.district) query.set('district', params.district);
    if (params?.search) query.set('search', params.search);
    if (params?.status) query.set('status', params.status);
    const res = await fetch(`/api/v1/centres?${query.toString()}`, { headers: getAuthHeaders() });
    return (await res.json()) as ApiResponse<any[]>;
  },

  getCentre: async (id: number | string) => {
    const res = await fetch(`/api/v1/centres/${id}`, { headers: getAuthHeaders() });
    return (await res.json()) as ApiResponse<any>;
  },

  getCentreSummary: async (id: number | string) => {
    const res = await fetch(`/api/v1/centres/${id}/summary`, { headers: getAuthHeaders() });
    return (await res.json()) as ApiResponse<any>;
  },

  // Cameras
  getCameras: async (centreId?: number | string) => {
    const url = centreId ? `/api/v1/centres/${centreId}/cameras` : '/api/v1/cameras';
    const res = await fetch(url, { headers: getAuthHeaders() });
    return (await res.json()) as ApiResponse<any[]>;
  },

  // Attendance
  getCentreAttendance: async (centreId: number | string) => {
    const res = await fetch(`/api/v1/centres/${centreId}/attendance`, { headers: getAuthHeaders() });
    return (await res.json()) as ApiResponse<any[]>;
  },

  getAttendanceReconciliation: async (centreId: number | string) => {
    const res = await fetch(`/api/v1/centres/${centreId}/attendance/reconciliation`, { headers: getAuthHeaders() });
    return (await res.json()) as ApiResponse<any>;
  },

  // Inventory
  getCentreInventory: async (centreId: number | string) => {
    const res = await fetch(`/api/v1/centres/${centreId}/inventory`, { headers: getAuthHeaders() });
    return (await res.json()) as ApiResponse<any[]>;
  },

  getInventoryCompliance: async (centreId: number | string) => {
    const res = await fetch(`/api/v1/centres/${centreId}/inventory/compliance`, { headers: getAuthHeaders() });
    return (await res.json()) as ApiResponse<any>;
  },

  // Alerts
  getAlerts: async (params?: { centre_id?: number | string; severity?: string; status?: string }) => {
    const query = new URLSearchParams();
    if (params?.centre_id) query.set('centre_id', String(params.centre_id));
    if (params?.severity) query.set('severity', params.severity);
    if (params?.status) query.set('status', params.status);
    const res = await fetch(`/api/v1/alerts?${query.toString()}`, { headers: getAuthHeaders() });
    return (await res.json()) as ApiResponse<any[]>;
  },

  updateAlertStatus: async (alertId: number | string, newStatus: string) => {
    const res = await fetch(`/api/v1/alerts/${alertId}/status`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify({ status: newStatus }),
    });
    return (await res.json()) as ApiResponse<any>;
  },

  // Evaluation
  getEvaluationResults: async () => {
    const res = await fetch('/api/v1/evaluation/results', { headers: getAuthHeaders() });
    return (await res.json()) as ApiResponse<any>;
  },

  // Reports
  getReports: async (centreId: number | string) => {
    const res = await fetch(`/api/v1/reports/centre/${centreId}`, { headers: getAuthHeaders() });
    return (await res.json()) as ApiResponse<any>;
  },
};
