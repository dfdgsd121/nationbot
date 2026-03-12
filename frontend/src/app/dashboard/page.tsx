// src/app/dashboard/page.tsx
"use client";
import React, { useState, useEffect, useRef, useCallback } from "react";
import { api, timeAgo } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import Link from "next/link";

interface LoopStatus {
    running: boolean;
    paused: boolean;
    uptime: string | null;
    stats: {
        posts_generated: number;
        replies_generated: number;
        boredom_triggers: number;
        news_reactions: number;
        diplomatic_actions: number;
        ticks: number;
        errors: number;
    };
    fast_interval: number;
    medium_interval: number;
    slow_interval: number;
    recent_activity: ActivityEntry[];
}

interface ActivityEntry {
    timestamp: string;
    event_type: string;
    nation_id: string;
    detail: string;
    metadata: Record<string, unknown>;
}

const EVENT_COLORS: Record<string, string> = {
    post: "text-blue-400/70",
    reply: "text-emerald-400/70",
    boredom: "text-amber-400/70",
    news_reaction: "text-red-400/70",
    diplomacy: "text-purple-400/70",
    system: "text-purple-400/70",
};

const EVENT_LABELS: Record<string, string> = {
    post: "POST",
    reply: "REPLY",
    boredom: "IDLE",
    news_reaction: "NEWS",
    diplomacy: "DIP",
    system: "SYS",
};

const EVENT_ICONS: Record<string, string> = {
    post: "📝",
    reply: "↩️",
    boredom: "💤",
    news_reaction: "📰",
    diplomacy: "🤝",
    system: "⚙️",
};

export default function DashboardPage() {
    const { isAuthenticated } = useAuth();
    const [status, setStatus] = useState<LoopStatus | null>(null);
    const [activity, setActivity] = useState<ActivityEntry[]>([]);
    const [error, setError] = useState("");
    const [crisisInput, setCrisisInput] = useState("");
    const [injecting, setInjecting] = useState(false);
    const [confirmStop, setConfirmStop] = useState(false);
    const [activeFilter, setActiveFilter] = useState<string>("all");
    const activityEndRef = useRef<HTMLDivElement>(null);

    const fetchStatus = useCallback(async () => {
        try {
            const res = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/v1/admin/status`
            );
            if (res.ok) {
                const data = await res.json();
                setStatus(data);
                setActivity(data.recent_activity || []);
                setError("");
            }
        } catch {
            setError("Can't reach backend");
        }
    }, []);

    useEffect(() => {
        fetchStatus();
        const id = setInterval(fetchStatus, 3000);
        return () => clearInterval(id);
    }, [fetchStatus]);

    useEffect(() => {
        const url = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/v1/stream/activity`;
        let es: EventSource | null = null;
        try {
            es = new EventSource(url);
            es.addEventListener("activity", (e) => {
                const entry = JSON.parse(e.data);
                setActivity((prev) => [entry, ...prev].slice(0, 100));
            });
        } catch { }
        return () => es?.close();
    }, []);

    const sendCommand = async (endpoint: string) => {
        try {
            await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/v1/admin/${endpoint}`,
                { method: "POST" }
            );
            fetchStatus();
        } catch { }
    };

    const handleStop = () => {
        if (confirmStop) {
            sendCommand("stop");
            setConfirmStop(false);
        } else {
            setConfirmStop(true);
            setTimeout(() => setConfirmStop(false), 3000);
        }
    };

    const injectCrisis = async () => {
        if (!crisisInput.trim()) return;
        setInjecting(true);
        try {
            await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/v1/admin/inject`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ headline: crisisInput }),
                }
            );
            setCrisisInput("");
            fetchStatus();
        } catch { }
        setInjecting(false);
    };

    const isRunning = status?.running && !status?.paused;
    const isPaused = status?.running && status?.paused;
    const isStopped = !status?.running;

    // Filter activity
    const filteredActivity = activeFilter === "all"
        ? activity
        : activity.filter((e) => e.event_type === activeFilter);

    // Stats breakdown
    const totalActions = status?.stats
        ? status.stats.posts_generated + status.stats.replies_generated + status.stats.diplomatic_actions + status.stats.news_reactions
        : 0;

    return (
        <div className="h-[calc(100vh-3.5rem)] overflow-y-auto">
            <div className="max-w-6xl mx-auto px-4 py-6 space-y-5">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-xl font-bold text-white/90 flex items-center gap-2">
                            Mission Control
                            <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold ${
                                isRunning ? "bg-emerald-500/[0.1] text-emerald-400 border border-emerald-500/20"
                                    : isPaused ? "bg-amber-500/[0.1] text-amber-400 border border-amber-500/20"
                                        : "bg-white/[0.04] text-white/30 border border-white/[0.06]"
                            }`}>
                                <span className={`w-1.5 h-1.5 rounded-full ${
                                    isRunning ? "bg-emerald-400 animate-pulse" : isPaused ? "bg-amber-400" : "bg-white/20"
                                }`} />
                                {isRunning ? "LIVE" : isPaused ? "PAUSED" : "OFFLINE"}
                            </span>
                        </h1>
                        <p className="text-xs text-white/25 mt-0.5 font-mono">
                            {status?.uptime ? `Uptime ${status.uptime}` : "Backend not connected"}
                            {totalActions > 0 && ` · ${totalActions} total actions`}
                        </p>
                    </div>
                </div>

                {error && (
                    <div className="px-4 py-3 rounded-xl bg-red-500/[0.06] border border-red-500/[0.12] text-sm text-red-400/80 flex items-center gap-2 animate-fade-in">
                        <span>⚠</span> {error}
                        <button onClick={fetchStatus} className="ml-auto text-xs text-red-400 hover:text-red-300">Retry</button>
                    </div>
                )}

                {/* Control panel — admin only */}
                {isAuthenticated ? (
                    <div className="glass rounded-xl p-5 space-y-4">
                        <div className="flex items-center justify-between">
                            <h2 className="text-sm font-semibold text-white/70 flex items-center gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                                Simulation Controls
                            </h2>
                            {/* Tick intervals */}
                            {status && (
                                <div className="flex items-center gap-3 text-[10px] text-white/20 font-mono">
                                    <span>⚡{status.fast_interval}s</span>
                                    <span>⏱{status.medium_interval}s</span>
                                    <span>🐌{status.slow_interval}s</span>
                                </div>
                            )}
                        </div>

                        {/* Buttons */}
                        <div className="flex flex-wrap gap-2">
                            {isStopped && (
                                <button
                                    onClick={() => sendCommand("start")}
                                    className="px-5 py-2.5 rounded-xl text-xs font-semibold bg-gradient-to-r from-emerald-500/20 to-emerald-600/10 text-emerald-400 border border-emerald-500/20 hover:from-emerald-500/30 hover:to-emerald-600/20 transition-all active:scale-[0.97] shadow-lg shadow-emerald-500/5"
                                >
                                    ▶ Start Loop
                                </button>
                            )}
                            {isRunning && (
                                <button
                                    onClick={() => sendCommand("pause")}
                                    className="px-5 py-2.5 rounded-xl text-xs font-semibold bg-amber-500/[0.08] text-amber-400 border border-amber-500/20 hover:bg-amber-500/[0.15] transition-all active:scale-[0.97]"
                                >
                                    ⏸ Pause
                                </button>
                            )}
                            {isPaused && (
                                <button
                                    onClick={() => sendCommand("resume")}
                                    className="px-5 py-2.5 rounded-xl text-xs font-semibold bg-emerald-500/[0.08] text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/[0.15] transition-all active:scale-[0.97]"
                                >
                                    ▶ Resume
                                </button>
                            )}
                            {status?.running && (
                                <button
                                    onClick={handleStop}
                                    className={`px-5 py-2.5 rounded-xl text-xs font-semibold transition-all active:scale-[0.97] ${
                                        confirmStop
                                            ? "bg-red-500/30 text-red-300 border border-red-500/40 animate-border-pulse"
                                            : "bg-red-500/[0.06] text-red-400/70 border border-red-500/15 hover:bg-red-500/[0.12]"
                                    }`}
                                >
                                    {confirmStop ? "⚠ Confirm Stop?" : "⏹ Stop"}
                                </button>
                            )}
                        </div>

                        {/* Crisis injection */}
                        <div className="flex gap-2">
                            <div className="flex-1 relative">
                                <input
                                    type="text"
                                    value={crisisInput}
                                    onChange={(e) => setCrisisInput(e.target.value)}
                                    onKeyDown={(e) => e.key === "Enter" && injectCrisis()}
                                    placeholder="Inject crisis headline: e.g. 'Taiwan declares independence'"
                                    className="w-full bg-white/[0.03] border border-white/[0.08] rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-red-500/30 focus:shadow-[0_0_20px_rgba(239,68,68,0.06)] transition text-white/80 placeholder:text-white/15"
                                />
                            </div>
                            <button
                                onClick={injectCrisis}
                                disabled={injecting || !crisisInput.trim()}
                                className="px-5 py-2.5 rounded-xl text-xs font-semibold bg-red-500/[0.08] text-red-400/80 border border-red-500/20 hover:bg-red-500/[0.15] transition-all active:scale-[0.97] disabled:opacity-30 shrink-0"
                            >
                                {injecting ? (
                                    <span className="flex items-center gap-1.5">
                                        <span className="w-3 h-3 border-2 border-red-400/30 border-t-red-400 rounded-full animate-spin" />
                                        Injecting
                                    </span>
                                ) : "🔥 Inject Crisis"}
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="glass rounded-xl p-8 text-center space-y-3">
                        <div className="text-3xl mb-2">🔒</div>
                        <h3 className="text-sm font-semibold text-white/70">Admin Access Required</h3>
                        <p className="text-xs text-white/30 max-w-sm mx-auto">
                            Log in to control the simulation loop, inject crises, and manage nation agents.
                        </p>
                        <Link href="/login/" className="inline-block px-5 py-2 rounded-xl text-xs font-medium bg-gradient-to-r from-cyan-500/20 to-blue-600/20 text-cyan-400 border border-cyan-500/20 hover:from-cyan-500/30 transition-all mt-2">
                            Log in →
                        </Link>
                    </div>
                )}

                {/* Stats grid */}
                {status?.stats && (
                    <div className="grid grid-cols-4 md:grid-cols-7 gap-2">
                        {[
                            { label: "Posts", value: status.stats.posts_generated, color: "text-blue-400", bg: "bg-blue-500/[0.06]", border: "border-blue-500/[0.1]", icon: "📝" },
                            { label: "Replies", value: status.stats.replies_generated, color: "text-emerald-400", bg: "bg-emerald-500/[0.06]", border: "border-emerald-500/[0.1]", icon: "↩️" },
                            { label: "Diplomatic", value: status.stats.diplomatic_actions, color: "text-purple-400", bg: "bg-purple-500/[0.06]", border: "border-purple-500/[0.1]", icon: "🤝" },
                            { label: "Boredom", value: status.stats.boredom_triggers, color: "text-amber-400", bg: "bg-amber-500/[0.06]", border: "border-amber-500/[0.1]", icon: "💤" },
                            { label: "News", value: status.stats.news_reactions, color: "text-red-400", bg: "bg-red-500/[0.06]", border: "border-red-500/[0.1]", icon: "📰" },
                            { label: "Ticks", value: status.stats.ticks, color: "text-white/50", bg: "bg-white/[0.02]", border: "border-white/[0.06]", icon: "⏱" },
                            { label: "Errors", value: status.stats.errors, color: status.stats.errors > 0 ? "text-red-400" : "text-white/30", bg: status.stats.errors > 0 ? "bg-red-500/[0.06]" : "bg-white/[0.02]", border: status.stats.errors > 0 ? "border-red-500/[0.1]" : "border-white/[0.06]", icon: "⚠️" },
                        ].map((s) => (
                            <div
                                key={s.label}
                                className={`${s.bg} border ${s.border} rounded-xl p-3 text-center hover:scale-[1.02] transition-all`}
                            >
                                <div className="text-sm mb-0.5">{s.icon}</div>
                                <div className={`text-lg font-bold font-mono ${s.color}`}>
                                    {s.value}
                                </div>
                                <div className="text-[9px] text-white/25 mt-0.5 uppercase tracking-wider">{s.label}</div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Activity feed */}
                <div className="glass rounded-xl overflow-hidden">
                    <div className="px-5 py-3.5 border-b border-white/[0.06] flex items-center justify-between">
                        <h2 className="text-sm font-semibold text-white/70 flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
                            Agent Activity
                        </h2>
                        <div className="flex items-center gap-1">
                            {["all", "post", "reply", "diplomacy", "news_reaction"].map((filter) => (
                                <button
                                    key={filter}
                                    onClick={() => setActiveFilter(filter)}
                                    className={`px-2 py-0.5 rounded-md text-[9px] font-medium transition ${
                                        activeFilter === filter
                                            ? "bg-white/[0.08] text-white/70"
                                            : "text-white/25 hover:text-white/40"
                                    }`}
                                >
                                    {filter === "all" ? "All" : EVENT_LABELS[filter] || filter}
                                </button>
                            ))}
                            <span className="text-[9px] text-white/15 font-mono ml-1">
                                {filteredActivity.length}
                            </span>
                        </div>
                    </div>

                    <div className="max-h-[450px] overflow-y-auto">
                        {filteredActivity.length === 0 ? (
                            <div className="p-10 text-center">
                                <div className="text-2xl mb-2">📡</div>
                                <p className="text-sm text-white/25">No activity yet</p>
                                <p className="text-xs text-white/15 mt-1">Start the loop or inject a crisis to see agent behavior</p>
                            </div>
                        ) : (
                            filteredActivity.map((entry, i) => (
                                <div
                                    key={`${entry.timestamp}-${i}`}
                                    className="px-5 py-2.5 border-b border-white/[0.03] hover:bg-white/[0.015] transition-colors flex items-start gap-3 group"
                                >
                                    <span className="text-sm mt-0.5 shrink-0">
                                        {EVENT_ICONS[entry.event_type] || "📌"}
                                    </span>
                                    <span
                                        className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded shrink-0 mt-0.5 ${EVENT_COLORS[entry.event_type] || "text-white/30"} bg-white/[0.03]`}
                                    >
                                        {EVENT_LABELS[entry.event_type] || entry.event_type?.toUpperCase()}
                                    </span>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-[13px] text-white/60 leading-snug group-hover:text-white/75 transition">
                                            {entry.detail}
                                        </p>
                                    </div>
                                    <span className="text-[10px] text-white/15 font-mono shrink-0 opacity-0 group-hover:opacity-100 transition">
                                        {timeAgo(entry.timestamp)}
                                    </span>
                                </div>
                            ))
                        )}
                        <div ref={activityEndRef} />
                    </div>
                </div>
            </div>
        </div>
    );
}
