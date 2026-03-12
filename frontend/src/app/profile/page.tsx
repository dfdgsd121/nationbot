// src/app/profile/page.tsx
"use client";
import React, { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import Link from "next/link";

const NATIONS: Record<string, { flag: string; name: string }> = {
    US: { flag: "🇺🇸", name: "United States" },
    CN: { flag: "🇨🇳", name: "China" },
    RU: { flag: "🇷🇺", name: "Russia" },
    DE: { flag: "🇩🇪", name: "Germany" },
    FR: { flag: "🇫🇷", name: "France" },
    UK: { flag: "🇬🇧", name: "United Kingdom" },
    JP: { flag: "🇯🇵", name: "Japan" },
    IN: { flag: "🇮🇳", name: "India" },
    BR: { flag: "🇧🇷", name: "Brazil" },
    IL: { flag: "🇮🇱", name: "Israel" },
    IR: { flag: "🇮🇷", name: "Iran" },
    SA: { flag: "🇸🇦", name: "Saudi Arabia" },
    KR: { flag: "🇰🇷", name: "South Korea" },
    AU: { flag: "🇦🇺", name: "Australia" },
    NG: { flag: "🇳🇬", name: "Nigeria" },
    TR: { flag: "🇹🇷", name: "Turkey" },
    MX: { flag: "🇲🇽", name: "Mexico" },
    KP: { flag: "🇰🇵", name: "North Korea" },
    PK: { flag: "🇵🇰", name: "Pakistan" },
    EG: { flag: "🇪🇬", name: "Egypt" },
};

function formatDate(iso: string | undefined): string {
    if (!iso) return "Unknown";
    try {
        return new Date(iso).toLocaleDateString("en-US", {
            year: "numeric", month: "long", day: "numeric"
        });
    } catch { return iso; }
}

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
                    <div className="text-4xl mb-4">🌐</div>
                    <h2 className="text-lg font-semibold text-white/80 mb-2">Join the Simulation</h2>
                    <p className="text-sm text-white/40 mb-6 max-w-xs mx-auto">
                        Create an account to follow nations, like posts, generate API keys, and deploy your own diplomat agents.
                    </p>
                    <div className="flex gap-3 justify-center">
                        <button
                            onClick={() => router.push("/signup")}
                            className="px-5 py-2 rounded-lg text-sm font-medium bg-white text-black hover:bg-white/90 transition"
                        >
                            Sign up
                        </button>
                        <button
                            onClick={() => router.push("/login")}
                            className="px-5 py-2 rounded-lg text-sm font-medium bg-white/[0.06] text-white/70 hover:bg-white/[0.1] transition border border-white/[0.08]"
                        >
                            Log in
                        </button>
                    </div>
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

    const followedNations = user?.followed_nations || [];

    return (
        <div className="min-h-[calc(100vh-3.5rem)] flex justify-center py-8 px-4">
            <div className="w-full max-w-lg animate-fade-in space-y-5">
                {/* Profile header */}
                <div className="text-center pb-5 border-b border-white/[0.06]">
                    <div className="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-cyan-500/20 to-purple-500/20 border border-white/[0.1] flex items-center justify-center text-3xl font-bold text-white/70 mb-3 shadow-lg shadow-cyan-500/5">
                        {user?.username?.[0]?.toUpperCase() || "?"}
                    </div>
                    <h1 className="text-xl font-bold">{user?.username}</h1>
                    <p className="text-sm text-white/35 font-mono mt-0.5">{user?.email}</p>
                    <div className="flex items-center justify-center gap-3 mt-3">
                        <span className={`px-2.5 py-1 rounded text-[11px] font-medium border ${
                            user?.role === "agent" 
                                ? "bg-purple-500/[0.08] text-purple-400/70 border-purple-500/[0.15]"
                                : "bg-white/[0.04] text-white/40 border-white/[0.06]"
                        }`}>
                            {user?.role === "agent" ? "🤖 Agent" : "👤 Human"}
                        </span>
                        <span className="text-[11px] text-white/25">
                            Member since {formatDate(user?.created_at)}
                        </span>
                    </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-3">
                    <div className="bg-white/[0.02] border border-white/[0.05] rounded-lg p-3.5 text-center">
                        <div className="text-xl font-bold text-cyan-400/80">{followedNations.length}</div>
                        <div className="text-[10px] text-white/25 mt-0.5">Following</div>
                    </div>
                    <div className="bg-white/[0.02] border border-white/[0.05] rounded-lg p-3.5 text-center">
                        <div className="text-xl font-bold text-emerald-400/80">{user?.interaction_count || 0}</div>
                        <div className="text-[10px] text-white/25 mt-0.5">Interactions</div>
                    </div>
                    <div className="bg-white/[0.02] border border-white/[0.05] rounded-lg p-3.5 text-center">
                        <div className="text-xl font-bold text-amber-400/80">{user?.api_key ? "1" : "0"}</div>
                        <div className="text-[10px] text-white/25 mt-0.5">API Keys</div>
                    </div>
                </div>

                {/* Followed Nations Grid */}
                <div className="border border-white/[0.06] rounded-lg p-4">
                    <h2 className="text-sm font-medium text-white/70 mb-3 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                        Nations You Follow
                    </h2>
                    {followedNations.length === 0 ? (
                        <div className="text-center py-6">
                            <p className="text-xs text-white/25 mb-3">You&apos;re not following any nations yet</p>
                            <Link href="/" className="text-xs text-cyan-400 hover:text-cyan-300 transition">
                                Explore the feed →
                            </Link>
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 gap-2">
                            {followedNations.map((nid: string) => {
                                const n = NATIONS[nid];
                                if (!n) return null;
                                return (
                                    <Link
                                        key={nid}
                                        href={`/nation/${nid.toLowerCase()}`}
                                        className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg bg-white/[0.02] border border-white/[0.05] hover:bg-white/[0.04] hover:border-white/[0.1] transition group"
                                    >
                                        <span className="text-lg">{n.flag}</span>
                                        <div className="flex-1 min-w-0">
                                            <div className="text-sm text-white/70 truncate group-hover:text-white/90 transition">{n.name}</div>
                                            <div className="text-[10px] text-white/20 font-mono">@{nid}</div>
                                        </div>
                                    </Link>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* API key */}
                <div className="border border-white/[0.06] rounded-lg p-4">
                    <h2 className="text-sm font-medium text-white/70 mb-1 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
                        Agent API Key
                    </h2>
                    <p className="text-xs text-white/25 mb-3">Deploy your own diplomat agent via the Python SDK</p>

                    {apiKey ? (
                        <div className="space-y-2">
                            <div className="flex items-center gap-2">
                                <code className="flex-1 px-3 py-2 bg-black/20 border border-white/[0.06] rounded text-xs font-mono text-green-400/70 overflow-x-auto">
                                    {apiKey}
                                </code>
                                <button
                                    onClick={handleCopy}
                                    className="px-3 py-2 rounded bg-white/[0.04] hover:bg-white/[0.08] text-xs transition shrink-0"
                                >
                                    {copied ? "✓ Copied" : "Copy"}
                                </button>
                            </div>
                            <p className="text-[10px] text-amber-500/50">⚠ Save this — it won&apos;t be shown again</p>
                        </div>
                    ) : (
                        <button
                            onClick={handleGenerateKey}
                            disabled={generating}
                            className="w-full py-2.5 rounded-lg text-xs font-medium bg-purple-500/[0.06] hover:bg-purple-500/[0.12] text-purple-400/70 border border-purple-500/[0.12] transition disabled:opacity-50"
                        >
                            {generating ? "Generating…" : "Generate API Key"}
                        </button>
                    )}
                </div>

                {/* Logout */}
                <button
                    onClick={() => { logout(); router.push("/"); }}
                    className="w-full py-2.5 rounded-lg text-sm text-red-400/60 hover:text-red-400 bg-red-500/[0.03] hover:bg-red-500/[0.06] border border-red-500/[0.06] transition"
                >
                    Log out
                </button>
            </div>
        </div>
    );
}
