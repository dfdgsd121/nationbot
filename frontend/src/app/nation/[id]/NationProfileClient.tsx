// src/app/nation/[id]/NationProfileClient.tsx
"use client";
import React, { useState, useEffect } from "react";
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

export default function NationProfileClient({ id }: { id: string }) {
    const nationId = id.toUpperCase();
    const nation = NATIONS[nationId];
    const { user } = useAuth();

    const [posts, setPosts] = useState<Post[]>([]);
    const [diplomacy, setDiplomacy] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<"posts" | "diplomacy">("posts");

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            try {
                const [feedData, dipData] = await Promise.all([
                    api.loadFeed(),
                    api.getNationDiplomacy(nationId),
                ]);
                const nationPosts = (feedData.posts || [])
                    .filter((p: Post) => p.nation_id === nationId)
                    .sort((a: Post, b: Post) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
                setPosts(nationPosts);
                setDiplomacy(dipData);
            } catch { }
            setLoading(false);
        };
        load();
    }, [nationId]);

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

    const allies = diplomacy?.allies || [];
    const enemies = diplomacy?.enemies || [];

    return (
        <div className="h-[calc(100vh-3.5rem)] flex flex-col overflow-hidden">
            {/* Nation Header */}
            <div className="border-b border-white/[0.05] bg-gradient-to-r from-[#0a0e18] to-[#06080d] px-6 py-6 shrink-0">
                <div className="max-w-4xl mx-auto flex items-center gap-5">
                    <div className="w-20 h-20 rounded-2xl bg-[#1a1f2e] flex items-center justify-center text-4xl border border-white/[0.06] shadow-lg">
                        {nation.flag}
                    </div>
                    <div className="flex-1">
                        <h1 className="text-2xl font-bold text-white">{nation.name}</h1>
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
                        </div>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="border-b border-white/[0.05] px-6 bg-[#06080d] shrink-0">
                <div className="max-w-4xl mx-auto flex gap-0.5">
                    {(["posts", "diplomacy"] as const).map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`px-4 py-3 text-sm font-medium border-b-2 transition ${activeTab === tab
                                ? "border-cyan-500 text-white"
                                : "border-transparent text-white/30 hover:text-white/50"
                                }`}
                        >
                            {tab === "posts" ? "Posts" : "Diplomacy"}
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
                                        <span>{post.likes} likes</span>
                                        <span>{post.boosts} boosts</span>
                                        <span>{post.forks} forks</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
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
                                                <Link
                                                    key={a.id}
                                                    href={`/nation/${a.id.toLowerCase()}`}
                                                    className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-emerald-500/[0.04] border border-emerald-500/[0.08] hover:bg-emerald-500/[0.08] transition"
                                                >
                                                    <span className="text-lg">{n?.flag}</span>
                                                    <span className="text-sm text-white/70 flex-1">{n?.name || a.id}</span>
                                                    <div className="w-24 h-1.5 bg-white/[0.04] rounded-full overflow-hidden">
                                                        <div
                                                            className="h-full bg-emerald-500/60 rounded-full transition-all"
                                                            style={{ width: `${Math.min(100, Math.abs(a.score) * 10)}%` }}
                                                        />
                                                    </div>
                                                    <span className="text-[11px] font-mono text-emerald-400/60 w-10 text-right">
                                                        +{a.score.toFixed(1)}
                                                    </span>
                                                </Link>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>

                            {/* Enemies */}
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
                                                <Link
                                                    key={e.id}
                                                    href={`/nation/${e.id.toLowerCase()}`}
                                                    className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-red-500/[0.04] border border-red-500/[0.08] hover:bg-red-500/[0.08] transition"
                                                >
                                                    <span className="text-lg">{n?.flag}</span>
                                                    <span className="text-sm text-white/70 flex-1">{n?.name || e.id}</span>
                                                    <div className="w-24 h-1.5 bg-white/[0.04] rounded-full overflow-hidden">
                                                        <div
                                                            className="h-full bg-red-500/60 rounded-full transition-all"
                                                            style={{ width: `${Math.min(100, Math.abs(e.score) * 10)}%` }}
                                                        />
                                                    </div>
                                                    <span className="text-[11px] font-mono text-red-400/60 w-10 text-right">
                                                        {e.score.toFixed(1)}
                                                    </span>
                                                </Link>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
