const API_BASE_URL = 'http://localhost:8000';

export interface UploadedFile {
  id: number;
  filename: string;
  file_type: string;
  upload_time: string;
  file_path: string;
  user_id: number;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  file: UploadedFile;
  user: {
    id: number;
    firebase_uid: string;
    email: string;
    display_name: string;
    created_at: string;
  };
}

export interface UserInfo {
  firebase_uid: string;
  email: string;
  display_name: string;
  created_at: string;
}

export interface EmbeddingsResponse {
  success: boolean;
  message: string;
  file_id: number;
  user_id: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

export interface SearchResult {
  content: string;
  metadata: Record<string, any>;
  score?: number;
}

export interface SearchResponse {
  success: boolean;
  query: string;
  results: SearchResult[];
  count: number;
}

class ApiService {
  private getAuthHeaders(): HeadersInit {
    // Get the Firebase ID token from localStorage or wherever you store it
    const token = localStorage.getItem('firebase_id_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }

  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('firebase_id_token');
    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
  }

  async getUserInfo(): Promise<UserInfo> {
    const response = await fetch(`${API_BASE_URL}/me`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get user info');
    }

    return response.json();
  }

  async getUserFiles(): Promise<UploadedFile[]> {
    const response = await fetch(`${API_BASE_URL}/files`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get user files');
    }

    return response.json();
  }

  async generateEmbeddings(fileId: number): Promise<EmbeddingsResponse> {
    const response = await fetch(`${API_BASE_URL}/embeddings/generate-embeddings`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ file_id: fileId }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to generate embeddings');
    }

    return response.json();
  }

  async getEmbeddingsStatus(fileId: number): Promise<EmbeddingsResponse> {
    const response = await fetch(`${API_BASE_URL}/embeddings/status/${fileId}`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get embeddings status');
    }

    return response.json();
  }

  async searchEmbeddings(query: string, k: number = 5): Promise<SearchResponse> {
    const response = await fetch(`${API_BASE_URL}/embeddings/search?query=${encodeURIComponent(query)}&k=${k}`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to search embeddings');
    }

    return response.json();
  }

  async healthCheck(): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/`);
    
    if (!response.ok) {
      throw new Error('API health check failed');
    }

    return response.json();
  }
}

export const apiService = new ApiService(); 