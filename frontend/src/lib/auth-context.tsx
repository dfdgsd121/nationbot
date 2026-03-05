// src/lib/auth-context.tsx
"use client";
import React, { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { api, UserProfile, AuthResponse } from "./api";

interface AuthContextType {
    user: UserProfile | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    guestInteractionCount: number;
    login: (email: string, pass: string) => Promise<void>;
    signup: (email: string, user: string, pass: string) => Promise<void>;
    googleLogin: (token: string) => Promise<void>;
    logout: () => void;
    recordGuestInteraction: () => void; // Call this when guest likes/replies
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<UserProfile | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [guestInteractionCount, setGuestInteractionCount] = useState(0);

    useEffect(() => {
        // Load state from local storage
        const token = localStorage.getItem("access_token");
        const storedCount = localStorage.getItem("guest_interactions");

        if (storedCount) setGuestInteractionCount(parseInt(storedCount));

        if (token) {
            api.getProfile()
                .then(setUser)
                .catch(() => logout()) // Invalid token
                .finally(() => setIsLoading(false));
        } else {
            setIsLoading(false);
        }
    }, []);

    const saveTokens = (data: AuthResponse) => {
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        api.getProfile().then(setUser);
    };

    const login = async (email: string, pass: string) => {
        const data = await api.login(email, pass);
        saveTokens(data);
    };

    const signup = async (email: string, username: string, pass: string) => {
        const data = await api.signup(email, username, pass);
        saveTokens(data);
    };

    const googleLogin = async (token: string) => {
        const data = await api.googleAuth(token);
        saveTokens(data);
    };

    const logout = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        setUser(null);
    };

    const recordGuestInteraction = () => {
        if (user) return;
        const newCount = guestInteractionCount + 1;
        setGuestInteractionCount(newCount);
        localStorage.setItem("guest_interactions", newCount.toString());
    };

    return (
        <AuthContext.Provider value={{
            user,
            isAuthenticated: !!user,
            isLoading,
            guestInteractionCount,
            login,
            signup,
            googleLogin,
            logout,
            recordGuestInteraction
        }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};
