// src/app/login/page.tsx
"use client";
import React, { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function LoginPage() {
    const { login } = useAuth();
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);
        try {
            await login(email, password);
            router.push("/");
        } catch (err: any) {
            setError(err.message || "Invalid credentials");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-[calc(100vh-3.5rem)] flex items-center justify-center px-4">
            <div className="w-full max-w-sm animate-fade-in">
                <div className="mb-8">
                    <h1 className="text-2xl font-bold mb-1">Log in</h1>
                    <p className="text-sm text-white/40">Continue watching the chaos unfold</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {error && (
                        <div className="px-3 py-2 rounded-lg bg-red-500/[0.06] border border-red-500/[0.1] text-sm text-red-400/80">
                            {error}
                        </div>
                    )}

                    <div>
                        <label className="block text-xs text-white/35 mb-1.5">Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            className="w-full bg-white/[0.04] border border-white/[0.08] rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:border-white/[0.15] transition text-white/90 placeholder:text-white/15"
                            placeholder="you@example.com"
                        />
                    </div>

                    <div>
                        <label className="block text-xs text-white/35 mb-1.5">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className="w-full bg-white/[0.04] border border-white/[0.08] rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:border-white/[0.15] transition text-white/90 placeholder:text-white/15"
                            placeholder="••••••••"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-2.5 rounded-lg text-sm font-medium bg-white text-black hover:bg-white/90 transition active:scale-[0.97] disabled:opacity-50"
                    >
                        {loading ? "Logging in…" : "Log in"}
                    </button>
                </form>

                <p className="text-center text-sm text-white/25 mt-6">
                    No account?{" "}
                    <Link href="/signup" className="text-white/60 hover:text-white transition">
                        Sign up
                    </Link>
                </p>
            </div>
        </div>
    );
}
