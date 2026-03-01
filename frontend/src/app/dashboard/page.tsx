// src/app/dashboard/page.tsx
"use client";
import React, { useState, useEffect, useRef, useCallback } from "react";
import { api, timeAgo } from "@/lib/api";

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

export default function DashboardPage() {
    const [status, setStatus] = useState<LoopStatus | null>(null);
    const [activity, setActivity] = useState<ActivityEntry[]>([]);
    const [error, setError] = useState("");
    const [crisisInput, setCrisisInput] = useState("");
    const [injecting, setInjecting] = useState(false);
    const activityEndRef = useRef<HTMLDivElement>(null);

    // Fetch status periodically
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

    // Connect to activity SSE
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

    return (
        <div className="h-[calc(100vh-3.5rem)] overflow-y-auto">
            <div className="max-w-6xl mx-auto px-4 py-6 space-y-5">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-xl font-bold text-white/90">Mission Control</h1>
                        <p className="text-xs text-white/30 mt-0.5">
                            {status?.uptime ? `Uptime: ${status.uptime}` : "Offline"}
                        </p>
                    </div>

                    {/* Status indicator */}
                    <div className="flex items-center gap-2">
                        <div
                            className={`w-2 h-2 rounded-full ${isRunning
                                ? "bg-emerald-400 animate-pulse"
                                : isPaused
                                    ? "bg-amber-400"
                                    : "bg-white/20"
                                }`}
                        />
                        <span className="text-xs text-white/40 font-mono">
                            {isRunning ? "RUNNING" : isPaused ? "PAUSED" : "STOPPED"}
                        </span>
                    </div>
                </div>

                {error && (
                    <div className="px-3 py-2 rounded-lg bg-red-500/[0.06] border border-red-500/[0.1] text-sm text-red-400/80">
                        {error}
                    </div>
                )}

                {/* Control panel */}
                <div className="border border-white/[0.06] rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-4">
                        <h2 className="text-sm font-medium text-white/60">Controls</h2>
                    </div>

                    <div className="flex flex-wrap gap-2 mb-4">
                        {isStopped && (
                            <button
                                onClick={() => sendCommand("start")}
                                className="px-4 py-2 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-400/80 border border-emerald-500/20 hover:bg-emerald-500/20 transition"
                            >
                                Start Loop
                            </button>
                        )}
                        {isRunning && (
                            <button
                                onClick={() => sendCommand("pause")}
                                className="px-4 py-2 rounded-lg text-xs font-medium bg-amber-500/10 text-amber-400/80 border border-amber-500/20 hover:bg-amber-500/20 transition"
                            >
                                Pause
                            </button>
                        )}
                        {isPaused && (
                            <button
                                onClick={() => sendCommand("resume")}
                                className="px-4 py-2 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-400/80 border border-emerald-500/20 hover:bg-emerald-500/20 transition"
                            >
                                Resume
                            </button>
                        )}
                        {status?.running && (
                            <button
                                onClick={() => sendCommand("stop")}
                                className="px-4 py-2 rounded-lg text-xs font-medium bg-red-500/10 text-red-400/80 border border-red-500/20 hover:bg-red-500/20 transition"
                            >
                                Stop
                            </button>
                        )}
                    </div>

                    {/* Crisis injection */}
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={crisisInput}
                            onChange={(e) => setCrisisInput(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && injectCrisis()}
                            placeholder="Inject crisis: e.g. 'Taiwan declares independence'"
                            className="flex-1 bg-white/[0.03] border border-white/[0.08] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-white/[0.15] transition text-white/80 placeholder:text-white/15"
                        />
                        <button
                            onClick={injectCrisis}
                            disabled={injecting || !crisisInput.trim()}
                            className="px-4 py-2 rounded-lg text-xs font-medium bg-red-500/10 text-red-400/80 border border-red-500/20 hover:bg-red-500/20 transition disabled:opacity-30"
                        >
                            {injecting ? "Injecting…" : "Inject"}
                        </button>
                    </div>
                </div>

                {/* Stats grid */}
                {status?.stats && (
                    <div className="grid grid-cols-4 md:grid-cols-7 gap-3">
                        {[
                            { label: "Posts", value: status.stats.posts_generated, color: "text-blue-400/70" },
                            { label: "Replies", value: status.stats.replies_generated, color: "text-emerald-400/70" },
                            { label: "Diplomatic", value: status.stats.diplomatic_actions, color: "text-purple-400/70" },
                            { label: "Boredom", value: status.stats.boredom_triggers, color: "text-amber-400/70" },
                            { label: "News", value: status.stats.news_reactions, color: "text-red-400/70" },
                            { label: "Ticks", value: status.stats.ticks, color: "text-white/40" },
                            { label: "Errors", value: status.stats.errors, color: status.stats.errors > 0 ? "text-red-400" : "text-white/30" },
                        ].map((s) => (
                            <div
                                key={s.label}
                                className="bg-white/[0.02] border border-white/[0.05] rounded-lg p-3 text-center"
                            >
                                <div className={`text-lg font-bold font-mono ${s.color}`}>
                                    {s.value}
                                </div>
                                <div className="text-[10px] text-white/25 mt-0.5">{s.label}</div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Tick intervals */}
                {status && (
                    <div className="flex items-center gap-4 text-[11px] text-white/25 px-1">
                        <span>Fast: {status.fast_interval}s</span>
                        <span>·</span>
                        <span>Medium: {status.medium_interval}s</span>
                        <span>·</span>
                        <span>Slow: {status.slow_interval}s</span>
                    </div>
                )}

                {/* Activity feed */}
                <div className="border border-white/[0.06] rounded-lg overflow-hidden">
                    <div className="px-4 py-3 border-b border-white/[0.06] flex items-center justify-between">
                        <h2 className="text-sm font-medium text-white/60">Agent Activity</h2>
                        <span className="text-[10px] text-white/20 font-mono">
                            {activity.length} events
                        </span>
                    </div>

                    <div className="max-h-[400px] overflow-y-auto">
                        {activity.length === 0 ? (
                            <div className="p-8 text-center text-sm text-white/20">
                                No activity yet — start the loop or inject a crisis
                            </div>
                        ) : (
                            activity.map((entry, i) => (
                                <div
                                    key={`${entry.timestamp}-${i}`}
                                    className="px-4 py-2.5 border-b border-white/[0.03] hover:bg-white/[0.01] transition-colors flex items-start gap-3"
                                >
                                    {/* Event type badge */}
                                    <span
                                        className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded shrink-0 mt-0.5 ${EVENT_COLORS[entry.event_type] || "text-white/30"
                                            } bg-white/[0.03]`}
                                    >
                                        {EVENT_LABELS[entry.event_type] || entry.event_type.toUpperCase()}
                                    </span>

                                    {/* Detail */}
                                    <div className="flex-1 min-w-0">
                                        <p className="text-[13px] text-white/60 leading-snug">
                                            {entry.detail}
                                        </p>
                                    </div>

                                    {/* Timestamp */}
                                    <span className="text-[10px] text-white/15 font-mono shrink-0">
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
