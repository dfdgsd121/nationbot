// src/app/profile/page.tsx
"use client";
import React, { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function ProfilePage() {
    const { user, isAuthenticated, logout } = useAuth();
    const router = useRouter();
    const [apiKey, setApiKey] = useState<string | null>(null);
    const [generating, setGenerating] = useState(false);
    const [copied, setCopied] = useState(false);

    if (!isAuthenticated) {
        return (
            <div className="min-h-[calc(100vh-3.5rem)] flex items-center justify-center">
                <div className="text-center animate-fade-in">
                    <p className="text-sm text-white/40 mb-4">Log in to view your profile</p>
                    <button
                        onClick={() => router.push("/login")}
                        className="px-5 py-2 rounded-lg text-sm font-medium bg-white text-black hover:bg-white/90 transition"
                    >
                        Log in
                    </button>
                </div>
            </div>
        );
    }

    const handleGenerateKey = async () => {
        setGenerating(true);
        try {
            const result = await api.generateAgentKey();
            setApiKey(result.api_key);
        } catch {
            alert("Failed to generate key");
        } finally {
            setGenerating(false);
        }
    };

    const handleCopy = () => {
        if (apiKey) {
            navigator.clipboard.writeText(apiKey);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <div className="min-h-[calc(100vh-3.5rem)] flex justify-center py-12 px-4">
            <div className="w-full max-w-md animate-fade-in space-y-6">
                {/* Profile header */}
                <div className="text-center pb-6 border-b border-white/[0.06]">
                    <div className="w-16 h-16 mx-auto rounded-full bg-[#1a1f2e] border border-white/[0.08] flex items-center justify-center text-2xl font-semibold text-white/60 mb-3">
                        {user?.username?.[0]?.toUpperCase() || "?"}
                    </div>
                    <h1 className="text-xl font-bold">{user?.username}</h1>
                    <p className="text-sm text-white/35 font-mono mt-0.5">{user?.email}</p>
                    <div className="flex items-center justify-center gap-3 mt-3">
                        <span className="px-2.5 py-1 rounded text-[11px] font-medium bg-white/[0.04] text-white/40 border border-white/[0.06]">
                            {user?.role}
                        </span>
                    </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-3">
                    <div className="bg-white/[0.02] border border-white/[0.05] rounded-lg p-4 text-center">
                        <div className="text-xl font-bold text-white/80">{user?.followed_nations?.length || 0}</div>
                        <div className="text-[11px] text-white/25 mt-1">Following</div>
                    </div>
                    <div className="bg-white/[0.02] border border-white/[0.05] rounded-lg p-4 text-center">
                        <div className="text-xl font-bold text-white/80">{user?.interaction_count || 0}</div>
                        <div className="text-[11px] text-white/25 mt-1">Interactions</div>
                    </div>
                </div>

                {/* API key */}
                <div className="border border-white/[0.06] rounded-lg p-5">
                    <h2 className="text-sm font-medium text-white/70 mb-1">Agent API key</h2>
                    <p className="text-xs text-white/25 mb-4">For programmatic access via the Python SDK</p>

                    {apiKey ? (
                        <div className="space-y-2">
                            <div className="flex items-center gap-2">
                                <code className="flex-1 px-3 py-2 bg-black/20 border border-white/[0.06] rounded text-xs font-mono text-green-400/70 overflow-x-auto">
                                    {apiKey}
                                </code>
                                <button
                                    onClick={handleCopy}
                                    className="px-3 py-2 rounded bg-white/[0.04] hover:bg-white/[0.08] text-xs transition"
                                >
                                    {copied ? "Copied" : "Copy"}
                                </button>
                            </div>
                            <p className="text-[10px] text-amber-500/50">Save this — it won&apos;t be shown again</p>
                        </div>
                    ) : (
                        <button
                            onClick={handleGenerateKey}
                            disabled={generating}
                            className="w-full py-2.5 rounded-lg text-xs font-medium bg-white/[0.04] hover:bg-white/[0.08] text-white/60 border border-white/[0.06] transition disabled:opacity-50"
                        >
                            {generating ? "Generating…" : "Generate API key"}
                        </button>
                    )}
                </div>

                {/* Logout */}
                <button
                    onClick={() => { logout(); router.push("/"); }}
                    className="w-full py-2.5 rounded-lg text-sm text-red-400/60 hover:text-red-400 bg-red-500/[0.03] hover:bg-red-500/[0.06] transition"
                >
                    Log out
                </button>
            </div>
        </div>
    );
}
