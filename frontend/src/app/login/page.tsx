// src/app/login/page.tsx
"use client";
import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "@/lib/auth-context";
import Link from "next/link";
import { useRouter } from "next/navigation";

declare global {
    interface Window {
        google?: any;
    }
}

export default function LoginPage() {
    const { login, googleLogin } = useAuth();
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const [focusField, setFocusField] = useState<string | null>(null);
    const googleBtnRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const initGoogle = () => {
            if (window.google && googleBtnRef.current) {
                window.google.accounts.id.initialize({
                    client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "",
                    callback: handleGoogleResponse,
                    auto_select: false,
                });
                window.google.accounts.id.renderButton(googleBtnRef.current, {
                    type: "standard",
                    theme: "filled_black",
                    size: "large",
                    width: 380,
                    text: "signin_with",
                    shape: "pill",
                });
            }
        };
        const timer = setInterval(() => {
            if (window.google) { initGoogle(); clearInterval(timer); }
        }, 100);
        return () => clearInterval(timer);
    }, []);

    const handleGoogleResponse = async (response: any) => {
        setError(""); setLoading(true);
        try { await googleLogin(response.credential); router.push("/"); }
        catch (err: any) { setError(err.message || "Google sign-in failed"); }
        finally { setLoading(false); }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault(); setError(""); setLoading(true);
        try { await login(email, password); router.push("/"); }
        catch (err: any) { setError(err.message || "Invalid credentials"); }
        finally { setLoading(false); }
    };

    return (
        <div className="min-h-[calc(100vh-3.5rem)] flex items-center justify-center px-4 relative overflow-hidden">
            {/* Animated background orbs */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-32 -left-32 w-96 h-96 bg-cyan-500/[0.07] rounded-full blur-[120px] animate-breathe" />
                <div className="absolute -bottom-48 -right-32 w-[500px] h-[500px] bg-purple-500/[0.05] rounded-full blur-[140px] animate-breathe" style={{ animationDelay: "1.5s" }} />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-500/[0.03] rounded-full blur-[160px]" />
            </div>

            <div className="w-full max-w-[420px] animate-slide-up relative z-10">
                {/* Glass card */}
                <div className="glass rounded-2xl p-8 shadow-2xl shadow-black/40">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 border border-white/[0.1] flex items-center justify-center text-2xl mb-4 shadow-lg shadow-cyan-500/10">
                            🌐
                        </div>
                        <h1 className="text-2xl font-bold gradient-text-brand">Welcome back</h1>
                        <p className="text-sm text-white/35 mt-1">Enter the geopolitical simulation</p>
                    </div>

                    {/* Google Sign-In */}
                    <div className="mb-5">
                        <div ref={googleBtnRef} className="flex justify-center" />
                    </div>

                    {/* Divider */}
                    <div className="flex items-center gap-3 mb-5">
                        <div className="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.1] to-transparent" />
                        <span className="text-[10px] text-white/20 uppercase tracking-[0.2em] font-medium">or continue with email</span>
                        <div className="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.1] to-transparent" />
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        {error && (
                            <div className="px-4 py-3 rounded-xl bg-red-500/[0.08] border border-red-500/[0.15] text-sm text-red-400/90 flex items-center gap-2 animate-fade-in">
                                <span className="text-red-400">⚠</span> {error}
                            </div>
                        )}

                        <div className="space-y-1.5">
                            <label className="block text-xs text-white/40 font-medium ml-1">Email address</label>
                            <div className={`relative rounded-xl border transition-all duration-300 ${
                                focusField === "email" ? "border-cyan-500/30 shadow-[0_0_20px_rgba(0,212,255,0.08)]" : "border-white/[0.08]"
                            }`}>
                                <input
                                    type="email" value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    onFocus={() => setFocusField("email")}
                                    onBlur={() => setFocusField(null)}
                                    required
                                    className="w-full bg-white/[0.03] rounded-xl px-4 py-3 text-sm focus:outline-none text-white/90 placeholder:text-white/15"
                                    placeholder="diplomat@nation.gov"
                                />
                            </div>
                        </div>

                        <div className="space-y-1.5">
                            <label className="block text-xs text-white/40 font-medium ml-1">Password</label>
                            <div className={`relative rounded-xl border transition-all duration-300 ${
                                focusField === "password" ? "border-cyan-500/30 shadow-[0_0_20px_rgba(0,212,255,0.08)]" : "border-white/[0.08]"
                            }`}>
                                <input
                                    type="password" value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    onFocus={() => setFocusField("password")}
                                    onBlur={() => setFocusField(null)}
                                    required
                                    className="w-full bg-white/[0.03] rounded-xl px-4 py-3 text-sm focus:outline-none text-white/90 placeholder:text-white/15"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        <button
                            type="submit" disabled={loading}
                            className="w-full py-3 rounded-xl text-sm font-semibold bg-gradient-to-r from-cyan-500 to-blue-600 text-white hover:from-cyan-400 hover:to-blue-500 transition-all duration-300 active:scale-[0.97] disabled:opacity-50 shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30"
                        >
                            {loading ? (
                                <span className="flex items-center justify-center gap-2">
                                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                    Authenticating...
                                </span>
                            ) : "Log in"}
                        </button>
                    </form>

                    <p className="text-center text-sm text-white/25 mt-6">
                        New to NationBot?{" "}
                        <Link href="/signup" className="text-cyan-400/80 hover:text-cyan-300 transition font-medium">
                            Create an account
                        </Link>
                    </p>
                </div>

                {/* Bottom tagline */}
                <div className="text-center mt-6">
                    <p className="text-[11px] text-white/15 font-mono">
                        20 AI-driven nations · Real-time diplomacy · Your move
                    </p>
                </div>
            </div>
        </div>
    );
}
