// src/app/world/page.tsx
"use client";
import React, { useState, useEffect, useMemo } from "react";
import { api } from "@/lib/api";
import Link from "next/link";

const NATIONS = [
    { id: "US", flag: "\u{1F1FA}\u{1F1F8}", name: "United States", x: 22, y: 38 },
    { id: "CN", flag: "\u{1F1E8}\u{1F1F3}", name: "China", x: 75, y: 38 },
    { id: "RU", flag: "\u{1F1F7}\u{1F1FA}", name: "Russia", x: 65, y: 22 },
    { id: "DE", flag: "\u{1F1E9}\u{1F1EA}", name: "Germany", x: 50, y: 28 },
    { id: "FR", flag: "\u{1F1EB}\u{1F1F7}", name: "France", x: 47, y: 32 },
    { id: "UK", flag: "\u{1F1EC}\u{1F1E7}", name: "United Kingdom", x: 46, y: 26 },
    { id: "JP", flag: "\u{1F1EF}\u{1F1F5}", name: "Japan", x: 83, y: 36 },
    { id: "IN", flag: "\u{1F1EE}\u{1F1F3}", name: "India", x: 70, y: 48 },
    { id: "BR", flag: "\u{1F1E7}\u{1F1F7}", name: "Brazil", x: 30, y: 65 },
    { id: "IL", flag: "\u{1F1EE}\u{1F1F1}", name: "Israel", x: 56, y: 40 },
    { id: "IR", flag: "\u{1F1EE}\u{1F1F7}", name: "Iran", x: 62, y: 40 },
    { id: "SA", flag: "\u{1F1F8}\u{1F1E6}", name: "Saudi Arabia", x: 58, y: 46 },
    { id: "KR", flag: "\u{1F1F0}\u{1F1F7}", name: "South Korea", x: 81, y: 38 },
    { id: "AU", flag: "\u{1F1E6}\u{1F1FA}", name: "Australia", x: 85, y: 72 },
    { id: "NG", flag: "\u{1F1F3}\u{1F1EC}", name: "Nigeria", x: 48, y: 52 },
    { id: "TR", flag: "\u{1F1F9}\u{1F1F7}", name: "Turkey", x: 55, y: 35 },
    { id: "MX", flag: "\u{1F1F2}\u{1F1FD}", name: "Mexico", x: 18, y: 48 },
    { id: "KP", flag: "\u{1F1F0}\u{1F1F5}", name: "North Korea", x: 80, y: 34 },
    { id: "PK", flag: "\u{1F1F5}\u{1F1F0}", name: "Pakistan", x: 66, y: 44 },
    { id: "EG", flag: "\u{1F1EA}\u{1F1EC}", name: "Egypt", x: 53, y: 44 },
];

const NATION_MAP = Object.fromEntries(NATIONS.map((n) => [n.id, n]));

interface Relationship {
    from: string;
    to: string;
    score: number;
}

export default function WorldPage() {
    const [diplomacyMap, setDiplomacyMap] = useState<any>(null);
    const [selectedNation, setSelectedNation] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const data = await api.getDiplomacyMap();
                setDiplomacyMap(data);
            } catch { }
            setLoading(false);
        };
        load();
        const id = setInterval(load, 10000);
        return () => clearInterval(id);
    }, []);

    // Build relationships from diplomacy map
    const relationships = useMemo(() => {
        if (!diplomacyMap) return [];
        const rels: Relationship[] = [];
        const seen = new Set<string>();

        Object.entries(diplomacyMap).forEach(([nid, data]: [string, any]) => {
            [...(data.allies || []), ...(data.enemies || [])].forEach((rel: any) => {
                const key = [nid, rel.id].sort().join("-");
                if (!seen.has(key)) {
                    seen.add(key);
                    rels.push({ from: nid, to: rel.id, score: rel.score });
                }
            });
        });
        return rels;
    }, [diplomacyMap]);

    const selectedData = selectedNation && diplomacyMap ? diplomacyMap[selectedNation] : null;

    return (
        <div className="h-[calc(100vh-3.5rem)] flex flex-col overflow-hidden">
            {/* Header */}
            <div className="border-b border-white/[0.05] px-6 py-4 bg-[#06080d] shrink-0 flex items-center justify-between">
                <div>
                    <h1 className="text-xl font-bold text-white">World Diplomacy Map</h1>
                    <p className="text-xs text-white/30 mt-0.5">
                        {relationships.length} active relationships between {NATIONS.length} nations
                    </p>
                </div>
                <div className="flex items-center gap-4 text-[10px]">
                    <div className="flex items-center gap-1.5">
                        <div className="w-6 h-0.5 bg-emerald-500/60" />
                        <span className="text-white/30">Alliance</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <div className="w-6 h-0.5 bg-red-500/60" />
                        <span className="text-white/30">Rivalry</span>
                    </div>
                </div>
            </div>

            {/* Map + Details */}
            <div className="flex flex-1 overflow-hidden">
                {/* SVG Map */}
                <div className="flex-1 relative overflow-hidden bg-[#050810]">
                    {loading ? (
                        <div className="absolute inset-0 flex items-center justify-center">
                            <div className="text-sm text-white/20 animate-pulse">Loading diplomatic relations...</div>
                        </div>
                    ) : (
                        <svg viewBox="0 0 100 85" className="w-full h-full" preserveAspectRatio="xMidYMid meet">
                            {/* Grid dots */}
                            <defs>
                                <pattern id="dots" x="0" y="0" width="5" height="5" patternUnits="userSpaceOnUse">
                                    <circle cx="2.5" cy="2.5" r="0.15" fill="rgba(255,255,255,0.03)" />
                                </pattern>
                            </defs>
                            <rect width="100" height="85" fill="url(#dots)" />

                            {/* Relationship lines */}
                            {relationships.map((rel) => {
                                const from = NATION_MAP[rel.from];
                                const to = NATION_MAP[rel.to];
                                if (!from || !to) return null;

                                const isAlly = rel.score > 0;
                                const strength = Math.min(1, Math.abs(rel.score) / 5);
                                const isSelected = selectedNation === rel.from || selectedNation === rel.to;

                                return (
                                    <line
                                        key={`${rel.from}-${rel.to}`}
                                        x1={from.x}
                                        y1={from.y}
                                        x2={to.x}
                                        y2={to.y}
                                        stroke={isAlly ? "rgba(52, 211, 153, VAR)" : "rgba(248, 113, 113, VAR)"}
                                        strokeWidth={isSelected ? 0.4 : 0.2}
                                        opacity={isSelected ? 0.8 : 0.3}
                                        style={{
                                            stroke: isAlly
                                                ? `rgba(52, 211, 153, ${isSelected ? 0.8 : 0.15 + strength * 0.3})`
                                                : `rgba(248, 113, 113, ${isSelected ? 0.8 : 0.15 + strength * 0.3})`,
                                        }}
                                        className="transition-all duration-500"
                                    />
                                );
                            })}

                            {/* Nation nodes */}
                            {NATIONS.map((n) => {
                                const isSelected = selectedNation === n.id;
                                return (
                                    <g
                                        key={n.id}
                                        onClick={() => setSelectedNation(isSelected ? null : n.id)}
                                        className="cursor-pointer"
                                    >
                                        {/* Glow effect */}
                                        {isSelected && (
                                            <circle
                                                cx={n.x}
                                                cy={n.y}
                                                r="3"
                                                fill="none"
                                                stroke="rgba(34, 211, 238, 0.3)"
                                                strokeWidth="0.3"
                                                className="animate-pulse"
                                            />
                                        )}
                                        {/* Node circle */}
                                        <circle
                                            cx={n.x}
                                            cy={n.y}
                                            r={isSelected ? "2" : "1.5"}
                                            fill={isSelected ? "rgba(34, 211, 238, 0.2)" : "rgba(255,255,255,0.06)"}
                                            stroke={isSelected ? "rgba(34, 211, 238, 0.6)" : "rgba(255,255,255,0.12)"}
                                            strokeWidth="0.2"
                                            className="transition-all duration-300"
                                        />
                                        {/* Flag */}
                                        <text
                                            x={n.x}
                                            y={n.y + 0.5}
                                            textAnchor="middle"
                                            fontSize={isSelected ? "2.5" : "2"}
                                            className="pointer-events-none select-none transition-all"
                                        >
                                            {n.flag}
                                        </text>
                                        {/* Label */}
                                        <text
                                            x={n.x}
                                            y={n.y + 3.5}
                                            textAnchor="middle"
                                            fontSize="1.2"
                                            fill={isSelected ? "rgba(34, 211, 238, 0.8)" : "rgba(255,255,255,0.25)"}
                                            className="pointer-events-none select-none font-sans"
                                        >
                                            {n.name}
                                        </text>
                                    </g>
                                );
                            })}
                        </svg>
                    )}
                </div>

                {/* Detail panel */}
                {selectedNation && selectedData && (
                    <div className="w-72 border-l border-white/[0.05] overflow-y-auto bg-[#06080d] shrink-0 animate-fade-in">
                        <div className="p-4 border-b border-white/[0.04]">
                            <div className="flex items-center gap-2.5 mb-2">
                                <span className="text-2xl">{NATION_MAP[selectedNation]?.flag}</span>
                                <div>
                                    <div className="text-sm font-semibold">{NATION_MAP[selectedNation]?.name}</div>
                                    <div className="text-[10px] font-mono text-white/30">@{selectedNation}</div>
                                </div>
                            </div>
                            <Link
                                href={`/nation/${selectedNation}`}
                                className="block text-center py-1.5 rounded-md text-xs text-cyan-400/80 bg-cyan-500/[0.06] border border-cyan-500/[0.1] hover:bg-cyan-500/[0.1] transition"
                            >
                                View Full Profile
                            </Link>
                        </div>

                        {/* Allies */}
                        <div className="p-4 border-b border-white/[0.04]">
                            <div className="text-[10px] font-semibold text-emerald-400/60 uppercase tracking-wider mb-2">
                                Allies ({(selectedData.allies || []).length})
                            </div>
                            {(selectedData.allies || []).map((a: any) => (
                                <div
                                    key={a.id}
                                    onClick={() => setSelectedNation(a.id)}
                                    className="flex items-center gap-2 py-1.5 text-sm cursor-pointer hover:bg-white/[0.02] rounded px-1 transition"
                                >
                                    <span>{NATION_MAP[a.id]?.flag}</span>
                                    <span className="text-white/50 flex-1 text-xs">{NATION_MAP[a.id]?.name}</span>
                                    <span className="text-[10px] font-mono text-emerald-400/50">+{a.score.toFixed(1)}</span>
                                </div>
                            ))}
                        </div>

                        {/* Enemies */}
                        <div className="p-4">
                            <div className="text-[10px] font-semibold text-red-400/60 uppercase tracking-wider mb-2">
                                Rivals ({(selectedData.enemies || []).length})
                            </div>
                            {(selectedData.enemies || []).map((e: any) => (
                                <div
                                    key={e.id}
                                    onClick={() => setSelectedNation(e.id)}
                                    className="flex items-center gap-2 py-1.5 text-sm cursor-pointer hover:bg-white/[0.02] rounded px-1 transition"
                                >
                                    <span>{NATION_MAP[e.id]?.flag}</span>
                                    <span className="text-white/50 flex-1 text-xs">{NATION_MAP[e.id]?.name}</span>
                                    <span className="text-[10px] font-mono text-red-400/50">{e.score.toFixed(1)}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
