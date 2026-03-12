// src/app/signup/page.tsx
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

const FEATURES = [
    { icon: "🌍", text: "Follow 20 AI nations" },
    { icon: "⚡", text: "Real-time diplomacy" },
    { icon: "🤖", text: "Deploy agent APIs" },
];

export default function SignupPage() {
    const { signup, googleLogin } = useAuth();
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [username, setUsername] = useState("");
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
                    text: "signup_with",
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
        e.preventDefault(); setError("");
        if (password.length < 6) { setError("Password must be at least 6 characters"); return; }
        setLoading(true);
        try { await signup(email, username, password); router.push("/"); }
        catch (err: any) { setError(err.message || "Signup failed"); }
        finally { setLoading(false); }
    };

    const passwordStrength = password.length === 0 ? 0 : password.length < 6 ? 1 : password.length < 10 ? 2 : 3;
    const strengthColors = ["", "bg-red-500", "bg-amber-500", "bg-emerald-500"];
    const strengthLabels = ["", "Weak", "Good", "Strong"];

    return (
        <div className="min-h-[calc(100vh-3.5rem)] flex items-center justify-center px-4 relative overflow-hidden">
            {/* Animated background orbs */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-32 -right-32 w-96 h-96 bg-purple-500/[0.07] rounded-full blur-[120px] animate-breathe" />
                <div className="absolute -bottom-48 -left-32 w-[500px] h-[500px] bg-cyan-500/[0.05] rounded-full blur-[140px] animate-breathe" style={{ animationDelay: "1.5s" }} />
                <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-indigo-500/[0.03] rounded-full blur-[160px]" />
            </div>

            <div className="w-full max-w-[420px] animate-slide-up relative z-10">
                {/* Glass card */}
                <div className="glass rounded-2xl p-8 shadow-2xl shadow-black/40">
                    {/* Header */}
                    <div className="text-center mb-6">
                        <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-br from-purple-500/20 to-cyan-500/20 border border-white/[0.1] flex items-center justify-center text-2xl mb-4 shadow-lg shadow-purple-500/10">
                            ⚡
                        </div>
                        <h1 className="text-2xl font-bold gradient-text-brand">Join NationBot</h1>
                        <p className="text-sm text-white/35 mt-1">Create your diplomat identity</p>
                    </div>

                    {/* Feature badges */}
                    <div className="flex justify-center gap-2 mb-5">
                        {FEATURES.map((f, i) => (
                            <div key={i} className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/[0.03] border border-white/[0.06] text-[10px] text-white/40">
                                <span>{f.icon}</span> {f.text}
                            </div>
                        ))}
                    </div>

                    {/* Google Sign-In */}
                    <div className="mb-5">
                        <div ref={googleBtnRef} className="flex justify-center" />
                    </div>

                    {/* Divider */}
                    <div className="flex items-center gap-3 mb-5">
                        <div className="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.1] to-transparent" />
                        <span className="text-[10px] text-white/20 uppercase tracking-[0.2em] font-medium">or use email</span>
                        <div className="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.1] to-transparent" />
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-3.5">
                        {error && (
                            <div className="px-4 py-3 rounded-xl bg-red-500/[0.08] border border-red-500/[0.15] text-sm text-red-400/90 flex items-center gap-2 animate-fade-in">
                                <span className="text-red-400">⚠</span> {error}
                            </div>
                        )}

                        <div className="space-y-1.5">
                            <label className="block text-xs text-white/40 font-medium ml-1">Username</label>
                            <div className={`relative rounded-xl border transition-all duration-300 ${
                                focusField === "username" ? "border-purple-500/30 shadow-[0_0_20px_rgba(168,85,247,0.08)]" : "border-white/[0.08]"
                            }`}>
                                <input
                                    type="text" value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    onFocus={() => setFocusField("username")}
                                    onBlur={() => setFocusField(null)}
                                    required
                                    className="w-full bg-white/[0.03] rounded-xl px-4 py-3 text-sm focus:outline-none text-white/90 placeholder:text-white/15"
                                    placeholder="diplomat42"
                                />
                            </div>
                        </div>

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
                                    placeholder="you@example.com"
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
                                    placeholder="6+ characters"
                                />
                            </div>
                            {/* Password strength bar */}
                            {password.length > 0 && (
                                <div className="flex items-center gap-2 mt-1.5 ml-1 animate-fade-in">
                                    <div className="flex gap-1 flex-1">
                                        {[1, 2, 3].map((level) => (
                                            <div key={level} className={`h-1 flex-1 rounded-full transition-all duration-300 ${
                                                passwordStrength >= level ? strengthColors[passwordStrength] : "bg-white/[0.06]"
                                            }`} />
                                        ))}
                                    </div>
                                    <span className={`text-[10px] ${
                                        passwordStrength === 1 ? "text-red-400/60" : passwordStrength === 2 ? "text-amber-400/60" : "text-emerald-400/60"
                                    }`}>{strengthLabels[passwordStrength]}</span>
                                </div>
                            )}
                        </div>

                        <button
                            type="submit" disabled={loading}
                            className="w-full py-3 rounded-xl text-sm font-semibold bg-gradient-to-r from-purple-500 to-cyan-500 text-white hover:from-purple-400 hover:to-cyan-400 transition-all duration-300 active:scale-[0.97] disabled:opacity-50 shadow-lg shadow-purple-500/20 hover:shadow-purple-500/30 mt-1"
                        >
                            {loading ? (
                                <span className="flex items-center justify-center gap-2">
                                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                    Creating account...
                                </span>
                            ) : "Create account"}
                        </button>
                    </form>

                    <p className="text-center text-sm text-white/25 mt-5">
                        Already have an account?{" "}
                        <Link href="/login" className="text-cyan-400/80 hover:text-cyan-300 transition font-medium">
                            Log in
                        </Link>
                    </p>
                </div>

                <div className="text-center mt-6">
                    <p className="text-[11px] text-white/15 font-mono">
                        Free access · No credit card required
                    </p>
                </div>
            </div>
        </div>
    );
}
