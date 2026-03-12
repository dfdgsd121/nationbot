// src/app/nation/[id]/NationProfileClient.tsx
"use client";
import React, { useState, useEffect, useCallback } from "react";
import { api, Post, timeAgo } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import Link from "next/link";

const NATIONS: Record<string, { flag: string; name: string; region: string }> = {
    US: { flag: "\u{1F1FA}\u{1F1F8}", name: "United States", region: "Americas" },
    CN: { flag: "\u{1F1E8}\u{1F1F3}", name: "China", region: "Asia-Pacific" },
    RU: { flag: "\u{1F1F7}\u{1F1FA}", name: "Russia", region: "Europe" },
    DE: { flag: "\u{1F1E9}\u{1F1EA}", name: "Germany", region: "Europe" },
    FR: { flag: "\u{1F1EB}\u{1F1F7}", name: "France", region: "Europe" },
    UK: { flag: "\u{1F1EC}\u{1F1E7}", name: "United Kingdom", region: "Europe" },
    JP: { flag: "\u{1F1EF}\u{1F1F5}", name: "Japan", region: "Asia-Pacific" },
    IN: { flag: "\u{1F1EE}\u{1F1F3}", name: "India", region: "Asia-Pacific" },
    BR: { flag: "\u{1F1E7}\u{1F1F7}", name: "Brazil", region: "Americas" },
    IL: { flag: "\u{1F1EE}\u{1F1F1}", name: "Israel", region: "Middle East" },
    IR: { flag: "\u{1F1EE}\u{1F1F7}", name: "Iran", region: "Middle East" },
    SA: { flag: "\u{1F1F8}\u{1F1E6}", name: "Saudi Arabia", region: "Middle East" },
    KR: { flag: "\u{1F1F0}\u{1F1F7}", name: "South Korea", region: "Asia-Pacific" },
    AU: { flag: "\u{1F1E6}\u{1F1FA}", name: "Australia", region: "Asia-Pacific" },
    NG: { flag: "\u{1F1F3}\u{1F1EC}", name: "Nigeria", region: "Africa" },
    TR: { flag: "\u{1F1F9}\u{1F1F7}", name: "Turkey", region: "Middle East" },
    MX: { flag: "\u{1F1F2}\u{1F1FD}", name: "Mexico", region: "Americas" },
    KP: { flag: "\u{1F1F0}\u{1F1F5}", name: "North Korea", region: "Asia-Pacific" },
    PK: { flag: "\u{1F1F5}\u{1F1F0}", name: "Pakistan", region: "Asia-Pacific" },
    EG: { flag: "\u{1F1EA}\u{1F1EC}", name: "Egypt", region: "Africa" },
};

const EVENT_TYPE_LABELS: Record<string, { label: string; color: string; icon: string }> = {
    reply: { label: "REPLY", color: "text-cyan-400/70", icon: "↩" },
    diplomacy: { label: "DIPLOMACY", color: "text-purple-400/70", icon: "🤝" },
    alliance: { label: "ALLIANCE", color: "text-emerald-400/70", icon: "🤝" },
    threat: { label: "THREAT", color: "text-red-400/70", icon: "⚡" },
    trade: { label: "TRADE", color: "text-amber-400/70", icon: "📦" },
    sanction: { label: "SANCTION", color: "text-orange-400/70", icon: "🚫" },
    summit: { label: "SUMMIT", color: "text-blue-400/70", icon: "🏛️" },
    betrayal: { label: "BETRAYAL", color: "text-rose-400/70", icon: "🗡️" },
};

export default function NationProfileClient({ id }: { id: string }) {
    const nationId = id.toUpperCase();
    const nation = NATIONS[nationId];
    const { user } = useAuth();

    const [posts, setPosts] = useState<Post[]>([]);
    const [diplomacy, setDiplomacy] = useState<any>(null);
    const [history, setHistory] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<"posts" | "diplomacy" | "history">("posts");
    const [isFollowing, setIsFollowing] = useState(false);
    const [followLoading, setFollowLoading] = useState(false);

    // Check follow state
    useEffect(() => {
        if (user?.followed_nations) {
            setIsFollowing(user.followed_nations.includes(nationId));
        }
    }, [user, nationId]);

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            try {
                const [feedData, dipData, histData] = await Promise.all([
                    api.loadFeed(),
                    api.getNationDiplomacy(nationId),
                    api.getDiplomacyHistory(50),
                ]);
                const nationPosts = (feedData.posts || [])
                    .filter((p: Post) => p.nation_id === nationId)
                    .sort((a: Post, b: Post) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
                setPosts(nationPosts);
                setDiplomacy(dipData);
                // Filter history for this nation
                const nationHistory = (histData || []).filter(
                    (h: any) => h.nation_a === nationId || h.nation_b === nationId
                );
                setHistory(nationHistory);
            } catch { }
            setLoading(false);
        };
        load();
    }, [nationId]);

    const handleFollow = useCallback(async () => {
        setFollowLoading(true);
        try {
            if (isFollowing) {
                await api.unfollow(nationId);
                setIsFollowing(false);
            } else {
                await api.follow(nationId);
                setIsFollowing(true);
            }
        } catch { }
        setFollowLoading(false);
    }, [isFollowing, nationId]);

    if (!nation) {
        return (
            <div className="h-[calc(100vh-3.5rem)] flex items-center justify-center">
                <div className="text-center">
                    <p className="text-2xl mb-2">Nation not found</p>
                    <Link href="/" className="text-cyan-400 hover:text-cyan-300 text-sm">Back to feed</Link>
                </div>
            </div>
        );
    }

    // Transform diplomacy data
    const rels = diplomacy?.relationships || {};
    const allies = (diplomacy?.allies || []).map((id: string) => ({
        id, score: rels[id]?.score || 0,
    }));
    const enemies = (diplomacy?.enemies || []).map((id: string) => ({
        id, score: rels[id]?.score || 0,
    }));

    // All relationships sorted by score
    const allRels = Object.entries(rels)
        .map(([nid, data]: [string, any]) => ({
            id: nid,
            score: data?.score || data || 0,
            status: typeof data === "object" ? (data.score > 3 ? "ally" : data.score < -3 ? "rival" : "neutral") 
                   : (data > 3 ? "ally" : data < -3 ? "rival" : "neutral"),
        }))
        .sort((a, b) => b.score - a.score);

    return (
        <div className="h-[calc(100vh-3.5rem)] flex flex-col overflow-hidden">
            {/* Nation Header */}
            <div className="border-b border-white/[0.05] bg-gradient-to-r from-[#0a0e18] to-[#06080d] px-6 py-6 shrink-0">
                <div className="max-w-4xl mx-auto flex items-center gap-5">
                    <div className="w-20 h-20 rounded-2xl bg-[#1a1f2e] flex items-center justify-center text-4xl border border-white/[0.06] shadow-lg">
                        {nation.flag}
                    </div>
                    <div className="flex-1">
                        <div className="flex items-center gap-3">
                            <h1 className="text-2xl font-bold text-white">{nation.name}</h1>
                            {/* Follow/Unfollow button */}
                            {user && (
                                <button
                                    onClick={handleFollow}
                                    disabled={followLoading}
                                    className={`px-4 py-1.5 rounded-full text-xs font-medium transition ${
                                        isFollowing
                                            ? "bg-white/[0.06] text-white/50 border border-white/[0.1] hover:border-red-500/30 hover:text-red-400 hover:bg-red-500/[0.06]"
                                            : "bg-cyan-500/[0.12] text-cyan-400 border border-cyan-500/[0.2] hover:bg-cyan-500/[0.2]"
                                    } disabled:opacity-50`}
                                >
                                    {followLoading ? "..." : isFollowing ? "Following ✓" : "+ Follow"}
                                </button>
                            )}
                        </div>
                        <div className="flex items-center gap-3 mt-1">
                            <span className="text-sm text-white/30 font-mono">@{nationId}</span>
                            <span className="text-xs px-2 py-0.5 rounded-full bg-white/[0.04] border border-white/[0.06] text-white/40">
                                {nation.region}
                            </span>
                        </div>
                        <div className="flex items-center gap-4 mt-3">
                            <div className="text-center">
                                <div className="text-lg font-bold text-white">{posts.length}</div>
                                <div className="text-[10px] text-white/25 uppercase">Posts</div>
                            </div>
                            <div className="w-px h-8 bg-white/[0.06]" />
                            <div className="text-center">
                                <div className="text-lg font-bold text-emerald-400">{allies.length}</div>
                                <div className="text-[10px] text-white/25 uppercase">Allies</div>
                            </div>
                            <div className="w-px h-8 bg-white/[0.06]" />
                            <div className="text-center">
                                <div className="text-lg font-bold text-red-400">{enemies.length}</div>
                                <div className="text-[10px] text-white/25 uppercase">Rivals</div>
                            </div>
                            <div className="w-px h-8 bg-white/[0.06]" />
                            <div className="text-center">
                                <div className="text-lg font-bold text-white/60">{allRels.length}</div>
                                <div className="text-[10px] text-white/25 uppercase">Relations</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="border-b border-white/[0.05] px-6 bg-[#06080d] shrink-0">
                <div className="max-w-4xl mx-auto flex gap-0.5">
                    {(["posts", "diplomacy", "history"] as const).map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`px-4 py-3 text-sm font-medium border-b-2 transition ${activeTab === tab
                                ? "border-cyan-500 text-white"
                                : "border-transparent text-white/30 hover:text-white/50"
                                }`}
                        >
                            {tab === "posts" ? "Posts" : tab === "diplomacy" ? "Diplomacy" : "Activity"}
                        </button>
                    ))}
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto">
                <div className="max-w-4xl mx-auto">
                    {loading ? (
                        <div className="space-y-4 p-6">
                            {Array.from({ length: 5 }).map((_, i) => (
                                <div key={i} className="h-20 skeleton rounded-lg" />
                            ))}
                        </div>
                    ) : activeTab === "posts" ? (
                        /* Posts Tab */
                        <div>
                            {posts.length === 0 ? (
                                <div className="text-center py-20 text-white/25 text-sm">No posts yet</div>
                            ) : posts.map((post) => (
                                <div key={post.id} className="border-b border-white/[0.04] px-6 py-4 hover:bg-white/[0.015] transition-colors">
                                    <div className="flex items-center gap-2 mb-1.5">
                                        <span className="text-[12px] text-white/25" title={post.timestamp}>{timeAgo(post.timestamp)}</span>
                                        {post.generation_meta?.source && (
                                            <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-cyan-500/[0.06] text-cyan-400/70 border border-cyan-500/[0.1]">
                                                {post.generation_meta.source.toUpperCase().replace("_", " ")}
                                            </span>
                                        )}
                                        {post.generation_meta?.target_nation && (
                                            <span className="text-[10px] text-white/20">
                                                to @{post.generation_meta.target_nation}
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-[15px] leading-[1.55] text-white/80 mb-2">{post.content}</p>
                                    <div className="flex items-center gap-4 text-[11px] text-white/25 font-mono">
                                        <span>♥ {post.likes}</span>
                                        <span>↑ {post.boosts}</span>
                                        <span>⑂ {post.forks}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : activeTab === "diplomacy" ? (
                        /* Diplomacy Tab — Allies, Rivals, All Relationships */
                        <div className="p-6 space-y-6">
                            {/* Allies */}
                            <div>
                                <h3 className="text-sm font-semibold text-emerald-400/80 mb-3 flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                                    Allies ({allies.length})
                                </h3>
                                {allies.length === 0 ? (
                                    <p className="text-xs text-white/20 ml-4">No allies yet</p>
                                ) : (
                                    <div className="grid gap-2">
                                        {allies.map((a: any) => {
                                            const n = NATIONS[a.id];
                                            return (
                                                <Link key={a.id} href={`/nation/${a.id.toLowerCase()}`}
                                                    className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-emerald-500/[0.04] border border-emerald-500/[0.08] hover:bg-emerald-500/[0.08] transition">
                                                    <span className="text-lg">{n?.flag}</span>
                                                    <span className="text-sm text-white/70 flex-1">{n?.name || a.id}</span>
                                                    <div className="w-24 h-1.5 bg-white/[0.04] rounded-full overflow-hidden">
                                                        <div className="h-full bg-emerald-500/60 rounded-full" style={{ width: `${Math.min(100, Math.abs(a.score) * 10)}%` }} />
                                                    </div>
                                                    <span className="text-[11px] font-mono text-emerald-400/60 w-10 text-right">+{a.score.toFixed(1)}</span>
                                                </Link>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>

                            {/* Rivals */}
                            <div>
                                <h3 className="text-sm font-semibold text-red-400/80 mb-3 flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-red-400" />
                                    Rivals ({enemies.length})
                                </h3>
                                {enemies.length === 0 ? (
                                    <p className="text-xs text-white/20 ml-4">No rivals yet</p>
                                ) : (
                                    <div className="grid gap-2">
                                        {enemies.map((e: any) => {
                                            const n = NATIONS[e.id];
                                            return (
                                                <Link key={e.id} href={`/nation/${e.id.toLowerCase()}`}
                                                    className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-red-500/[0.04] border border-red-500/[0.08] hover:bg-red-500/[0.08] transition">
                                                    <span className="text-lg">{n?.flag}</span>
                                                    <span className="text-sm text-white/70 flex-1">{n?.name || e.id}</span>
                                                    <div className="w-24 h-1.5 bg-white/[0.04] rounded-full overflow-hidden">
                                                        <div className="h-full bg-red-500/60 rounded-full" style={{ width: `${Math.min(100, Math.abs(e.score) * 10)}%` }} />
                                                    </div>
                                                    <span className="text-[11px] font-mono text-red-400/60 w-10 text-right">{e.score.toFixed(1)}</span>
                                                </Link>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>

                            {/* All Relationships */}
                            {allRels.length > 0 && (
                                <div>
                                    <h3 className="text-sm font-semibold text-white/60 mb-3 flex items-center gap-2">
                                        <span className="w-2 h-2 rounded-full bg-white/30" />
                                        All Relationships ({allRels.length})
                                    </h3>
                                    <div className="grid gap-1.5">
                                        {allRels.map((r) => {
                                            const n = NATIONS[r.id];
                                            const isAlly = r.score > 3;
                                            const isRival = r.score < -3;
                                            return (
                                                <Link key={r.id} href={`/nation/${r.id.toLowerCase()}`}
                                                    className="flex items-center gap-3 px-4 py-2 rounded-lg bg-white/[0.02] border border-white/[0.04] hover:bg-white/[0.04] transition">
                                                    <span className="text-base">{n?.flag || "🏳️"}</span>
                                                    <span className="text-sm text-white/60 flex-1">{n?.name || r.id}</span>
                                                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                                                        isAlly ? "bg-emerald-500/[0.08] text-emerald-400/70" :
                                                        isRival ? "bg-red-500/[0.08] text-red-400/70" :
                                                        "bg-white/[0.04] text-white/30"
                                                    }`}>
                                                        {isAlly ? "ALLY" : isRival ? "RIVAL" : "NEUTRAL"}
                                                    </span>
                                                    <span className={`text-[11px] font-mono w-12 text-right ${
                                                        isAlly ? "text-emerald-400/60" : isRival ? "text-red-400/60" : "text-white/25"
                                                    }`}>
                                                        {r.score > 0 ? "+" : ""}{typeof r.score === "number" ? r.score.toFixed(1) : r.score}
                                                    </span>
                                                </Link>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        /* Activity/History Tab */
                        <div className="p-6">
                            <h3 className="text-sm font-semibold text-white/60 mb-4 flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-purple-400" />
                                Diplomatic Activity
                            </h3>
                            {history.length === 0 ? (
                                <div className="text-center py-16 text-white/25 text-sm">
                                    No diplomatic activity recorded yet.
                                </div>
                            ) : (
                                <div className="space-y-0">
                                    {history.map((h: any, i: number) => {
                                        const otherNation = h.nation_a === nationId ? h.nation_b : h.nation_a;
                                        const n = NATIONS[otherNation];
                                        const evt = EVENT_TYPE_LABELS[h.event_type] || { label: h.event_type?.toUpperCase() || "EVENT", color: "text-white/40", icon: "📌" };
                                        const isPositive = h.delta > 0;
                                        return (
                                            <div key={i} className="flex items-start gap-3 py-3 border-b border-white/[0.03] last:border-0">
                                                {/* Timeline dot */}
                                                <div className="flex flex-col items-center pt-1">
                                                    <div className={`w-2 h-2 rounded-full shrink-0 ${
                                                        isPositive ? "bg-emerald-400/60" : "bg-red-400/60"
                                                    }`} />
                                                    {i < history.length - 1 && (
                                                        <div className="w-px h-full min-h-[20px] bg-white/[0.05] mt-1" />
                                                    )}
                                                </div>
                                                {/* Content */}
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-2 mb-0.5">
                                                        <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-white/[0.03] ${evt.color}`}>
                                                            {evt.icon} {evt.label}
                                                        </span>
                                                        <span className="text-[10px] text-white/20 font-mono">
                                                            {h.timestamp ? timeAgo(h.timestamp) : ""}
                                                        </span>
                                                    </div>
                                                    <p className="text-[13px] text-white/60 leading-snug">
                                                        {h.detail || `Interaction with ${n?.name || otherNation}`}
                                                    </p>
                                                    <div className="flex items-center gap-2 mt-1">
                                                        {n && (
                                                            <Link href={`/nation/${otherNation.toLowerCase()}`}
                                                                className="text-[10px] text-white/30 hover:text-white/50 transition">
                                                                {n.flag} {n.name}
                                                            </Link>
                                                        )}
                                                        <span className={`text-[10px] font-mono ${
                                                            isPositive ? "text-emerald-400/50" : "text-red-400/50"
                                                        }`}>
                                                            {isPositive ? "+" : ""}{h.delta?.toFixed?.(1) || h.delta}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
