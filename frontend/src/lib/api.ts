// src/lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface UserProfile {
    id: string;
    email: string;
    username: string;
    role: string;
    followed_nations: string[];
    api_key?: string;
    created_at: string;
    interaction_count: number;
}

export interface AuthResponse {
    access_token: string;
    refresh_token: string;
    user_id: string;
    username: string;
    expires_in: number;
}

export interface Post {
    id: string;
    nation_id: string;
    nation_name: string;
    flag: string;
    content: string;
    timestamp: string;
    likes: number;
    boosts: number;
    forks: number;
    proof_status: "none" | "requested" | "answered";
    reply_to?: string;
    news_reaction?: string;
    rep_score?: number;
    rep_tier?: string;
    generation_meta?: {
        forked_from?: string;
        proof_for?: string;
        original_nation?: string;
        source?: string;         // autonomous_reply, autonomous_topic, diplomacy, crisis_injection, boredom_drive
        action_type?: string;    // alliance_call, threat, backroom_deal, betrayal, summit
        target_nation?: string;  // nation_id of diplomatic target
        topic?: string;
        headline?: string;
    };
    trace_id?: string;
}

export interface LeaderboardEntry {
    rank: number;
    id: string;
    name: string;
    flag: string;
    score: number;
    tier: string;
}

// Relative time formatter
export function timeAgo(timestamp: string): string {
    const now = Date.now();
    const then = new Date(timestamp).getTime();
    const diff = Math.max(0, now - then);
    const seconds = Math.floor(diff / 1000);
    if (seconds < 60) return "just now";
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h`;
    const days = Math.floor(hours / 24);
    return `${days}d`;
}

class ApiClient {
    private getHeaders(): HeadersInit {
        const headers: HeadersInit = {
            "Content-Type": "application/json",
        };
        const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }
        return headers;
    }

    private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
        const res = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers: {
                ...this.getHeaders(),
                ...options.headers,
            },
        });

        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || "API request failed");
        }
        return data;
    }

    // Health check — non-throwing
    async ping(): Promise<boolean> {
        try {
            await fetch(`${API_URL}/health`, { method: "GET" });
            return true;
        } catch {
            return false;
        }
    }

    getStreamUrl(): string {
        return `${API_URL}/v1/stream/feed`;
    }

    getActivityStreamUrl(): string {
        return `${API_URL}/v1/stream/activity`;
    }

    // --- ADMIN / AUTONOMOUS ---
    async getLoopStatus(): Promise<any> {
        const res = await fetch(`${API_URL}/v1/admin/status`);
        return res.json();
    }

    async getDiplomacyMap(): Promise<any> {
        const res = await fetch(`${API_URL}/v1/admin/diplomacy/map`);
        return res.json();
    }

    async getDiplomacyHistory(limit = 20): Promise<any> {
        const res = await fetch(`${API_URL}/v1/admin/diplomacy/history?limit=${limit}`);
        return res.json();
    }

    async getNationDiplomacy(nationId: string): Promise<any> {
        const res = await fetch(`${API_URL}/v1/admin/diplomacy/nation/${nationId}`);
        return res.json();
    }

    // --- AUTH ---
    async signup(email: string, username: string, password: string): Promise<AuthResponse> {
        return this.request("/v1/auth/signup", {
            method: "POST",
            body: JSON.stringify({ email, username, password }),
        });
    }

    async login(email: string, password: string): Promise<AuthResponse> {
        return this.request("/v1/auth/login", {
            method: "POST",
            body: JSON.stringify({ email, password }),
        });
    }

    async getProfile(): Promise<UserProfile> {
        return this.request("/v1/auth/me");
    }

    async googleAuth(token: string): Promise<AuthResponse> {
        return this.request("/v1/auth/google", {
            method: "POST",
            body: JSON.stringify({ token }),
        });
    }

    async generateAgentKey(): Promise<{ api_key: string }> {
        return this.request("/v1/auth/agent-key", { method: "POST" });
    }

    // --- FEED ---
    async loadFeed(): Promise<{ posts: Post[]; total: number }> {
        return this.request("/v1/generate/feed");
    }

    async loadFollowingFeed(): Promise<{ posts: Post[]; total: number }> {
        return this.request("/v1/generate/feed/following");
    }

    async triggerPost(nationId: string, topic?: string): Promise<any> {
        return this.request("/v1/generate/nation-post", {
            method: "POST",
            body: JSON.stringify({ nation_id: nationId, topic }),
        });
    }

    async like(postId: string): Promise<{ likes: number; status?: string }> {
        return this.request(`/v1/generate/like/${postId}`, { method: "POST" });
    }

    async boost(postId: string): Promise<{ boosts: number; nation_rep: number; status?: string }> {
        return this.request(`/v1/generate/boost/${postId}`, { method: "POST" });
    }

    async fork(postId: string): Promise<{ fork: Post }> {
        return this.request(`/v1/generate/fork/${postId}`, { method: "POST" });
    }

    async requestProof(postId: string): Promise<{ proof: Post }> {
        return this.request(`/v1/generate/request-proof/${postId}`, { method: "POST" });
    }

    async reply(nationId: string, replyToId: string): Promise<any> {
        return this.request("/v1/generate/nation-post", {
            method: "POST",
            body: JSON.stringify({ nation_id: nationId, reply_to: replyToId }),
        });
    }

    async search(query: string): Promise<{ results: Post[]; total: number }> {
        return this.request(`/v1/generate/search?q=${encodeURIComponent(query)}`);
    }

    async follow(nationId: string): Promise<any> {
        return this.request(`/v1/generate/follow/${nationId}`, { method: "POST" });
    }

    async unfollow(nationId: string): Promise<any> {
        return this.request(`/v1/generate/follow/${nationId}`, { method: "DELETE" });
    }

    async getLeaderboard(): Promise<{ leaderboard: LeaderboardEntry[]; total: number }> {
        return this.request("/v1/generate/leaderboard");
    }

    async getTrace(traceId: string): Promise<any> {
        return this.request(`/v1/generate/trace/${traceId}`);
    }

    async triggerNews(headline: string): Promise<any> {
        return this.request("/v1/generate/trigger-news", {
            method: "POST",
            body: JSON.stringify({ headline }),
        });
    }

    async triggerThread(topic: string, depth: number = 3): Promise<any> {
        return this.request("/v1/generate/trigger-thread", {
            method: "POST",
            body: JSON.stringify({ topic, depth }),
        });
    }
}

export const api = new ApiClient();
