import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export interface UserProfile {
  user_id: string;
  email: string;
  name: string;
  age: number;
  sex: string;
  email_verified: boolean;
  created_at: string;
}

export interface Report {
  session_id: string;
  original_filename: string;
  status: string;
  created_at: string;
  has_genetic_results: boolean;
  has_questionnaire: boolean;
  has_recommendations: boolean;
  is_complete: boolean;
}

export interface FileUploadResponse {
  success: boolean;
  session_id: string;
  message: string;
  file_info: {
    original_name: string;
    size_bytes: number;
  };
  results: {
    file_info: {
      source: string;
      snp_count: number;
      build: number;
    };
    findings: GeneticFinding[];
    summary: {
      total_snps_in_file: number;
      nutrigenomics_snps_analyzed: number;
      high_risk: number;
      moderate_risk: number;
      low_risk: number;
      protective: number;
    };
  };
  next_step: string;
}

export interface AnalysisResponse {
  success: boolean;
  session_id: string;
  results: {
    file_info: {
      source: string;
      snp_count: number;
      build: number;
    };
    findings: GeneticFinding[];
    summary: {
      total_snps_in_file: number;
      nutrigenomics_snps_analyzed: number;
      high_risk: number;
      moderate_risk: number;
      low_risk: number;
      protective: number;
    };
  };
  next_step: string;
}

export interface GeneticFinding {
  rsid: string;
  gene: string;
  condition: string;
  genotype: string;
  risk_level: 'high' | 'moderate' | 'low' | 'protective';
  interpretation: string;
  recommendation: string;
  source: string;
}

export interface QuestionnaireAnswers {
  age: number;
  sex: 'male' | 'female' | 'other';
  activity_level: 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active';
  diet_type: 'omnivore' | 'vegetarian' | 'vegan' | 'pescatarian' | 'keto' | 'paleo' | 'other';
  alcohol_frequency: 'never' | 'rare' | 'occasional' | 'moderate' | 'frequent';
  caffeine_cups_per_day: number;
  digestive_issues: string[];
  health_goals: string[];
  current_supplements: string[];
  known_allergies: string[];
}

export interface NutrientRadarData {
  category: string;
  score: number;
  findings_count: number;
}

export interface RecommendationsResponse {
  success: boolean;
  session_id: string;
  generated_at: string;
  genetic_summary: {
    total_snps_in_file: number;
    nutrigenomics_snps_analyzed: number;
    high_risk: number;
    moderate_risk: number;
    low_risk: number;
    protective: number;
  };
  recommendations: {
    high_priority: Recommendation[];
    moderate_priority: Recommendation[];
    general_advice: GeneralAdvice[];
    foods_to_increase: string[];
    foods_to_limit: string[];
    supplements_to_consider: string[];
  };
  nutrient_radar: {
    radar_chart: NutrientRadarData[];
    description: string;
  };
  disclaimer: string;
}

export interface Recommendation {
  category: string;
  genetic_basis: string;
  recommendation: string;
  personalized_note?: string;
}

export interface GeneralAdvice {
  category: string;
  advice: string;
}

export interface MealMacros {
  protein_g: number;
  carbs_g: number;
  fats_g: number;
}

export interface Meal {
  name: string;
  description: string;
  ingredients?: string[];
  macros: MealMacros;
}

export interface Snack {
  name: string;
  description: string;
  macros: MealMacros;
}

export interface DayMealPlan {
  day: number;
  genetic_note: string;
  meals: {
    breakfast: Meal;
    lunch: Meal;
    dinner: Meal;
    snacks: Snack[];
  };
}

export interface MealPlanResponse {
  success: boolean;
  session_id: string;
  meal_plan: {
    success?: boolean;
    days?: number;
    meal_plan?: {
      days: DayMealPlan[];
    };
    generated_by?: string;
    disclaimer?: string;
    error?: string;
    fallback_advice?: string;
  };
  generated_at: string;
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      sessionStorage.removeItem('auth_token');
      sessionStorage.removeItem('genyo_session');
      window.location.replace('/landing');
    }
    return Promise.reject(error);
  }
);

export const nutrigenomicsAPI = {
  uploadFile: async (file: File): Promise<FileUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  analyzeGenetics: async (sessionId: string): Promise<AnalysisResponse> => {
    const response = await api.post('/api/analyze', { session_id: sessionId });
    return response.data;
  },

  submitQuestionnaire: async (sessionId: string, answers: QuestionnaireAnswers): Promise<any> => {
    const response = await api.post('/api/questionnaire', {
      session_id: sessionId,
      answers,
    });
    return response.data;
  },

  getRecommendations: async (sessionId: string): Promise<RecommendationsResponse> => {
    const response = await api.get(`/api/recommendations/${sessionId}`);
    return response.data;
  },

  getQuestionnaireTemplate: async (): Promise<any> => {
    const response = await api.get('/api/questionnaire/template');
    return response.data;
  },

  generateMealPlan: async (sessionId: string, days: number = 3): Promise<MealPlanResponse> => {
    const response = await api.post('/api/generate-meal-plan', {
      session_id: sessionId,
      days,
    });
    return response.data;
  },

  getMe: async (): Promise<{ success: boolean; user: UserProfile }> => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  updateProfile: async (data: { name?: string; age?: number; sex?: string }): Promise<{ success: boolean; user: UserProfile }> => {
    const response = await api.put('/api/auth/update-profile', data);
    return response.data;
  },

  getMyReports: async (): Promise<{ success: boolean; total_reports: number; reports: Report[] }> => {
    const response = await api.get('/api/auth/my-reports');
    return response.data;
  },

  deleteReport: async (sessionId: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/api/session/${sessionId}`);
    return response.data;
  },
};
