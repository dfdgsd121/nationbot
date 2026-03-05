// src/lib/navbar.tsx
"use client";
import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useAuth } from "./auth-context";
import { api } from "./api";

function LoopStatusPill() {
    const [loopState, setLoopState] = useState<{ running: boolean; paused: boolean } | null>(null);

    useEffect(() => {
        const check = async () => {
            try {
                const s = await api.getLoopStatus();
                setLoopState({ running: s.running, paused: s.paused });
            } catch { setLoopState(null); }
        };
        check();
        const id = setInterval(check, 5000);
        return () => clearInterval(id);
    }, []);

    if (!loopState?.running) return null;

    const isActive = loopState.running && !loopState.paused;
    return (
        <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full border ${isActive
            ? "bg-emerald-500/[0.08] border-emerald-500/20 text-emerald-400/80"
            : "bg-amber-500/[0.08] border-amber-500/20 text-amber-400/80"
            }`}>
            <div className={`w-1 h-1 rounded-full ${isActive ? "bg-emerald-400 animate-pulse" : "bg-amber-400"}`} />
            <span className="font-mono text-[9px] font-bold tracking-wider">
                {isActive ? "AUTONOMOUS" : "PAUSED"}
            </span>
        </div>
    );
}

export function Navbar() {
    const { user, isAuthenticated, logout } = useAuth();
    const [connected, setConnected] = useState(false);
    const [showDropdown, setShowDropdown] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Ping backend for connection status
    useEffect(() => {
        const check = async () => setConnected(await api.ping());
        check();
        const id = setInterval(check, 10000);
        return () => clearInterval(id);
    }, []);

    // Close dropdown on outside click
    useEffect(() => {
        const handle = (e: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
                setShowDropdown(false);
            }
        };
        document.addEventListener("mousedown", handle);
        return () => document.removeEventListener("mousedown", handle);
    }, []);

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 h-14 bg-[#06080d]/90 backdrop-blur-md border-b border-white/[0.06] flex items-center px-5 justify-between">
            {/* Brand */}
            <Link href="/" className="flex items-center gap-2.5 group">
                <div className="w-8 h-8 rounded-lg bg-[#1a1f2e] flex items-center justify-center text-sm font-extrabold text-cyan-400 border border-white/[0.06] group-hover:border-cyan-500/30 transition">
                    N
                </div>
                <span className="text-[15px] font-bold tracking-tight text-white/90">
                    NationBot
                </span>
            </Link>

            {/* Status + Dashboard link */}
            <div className="hidden sm:flex items-center gap-3 text-xs text-white/35">
                <div className="flex items-center gap-2">
                    <div className={`w-1.5 h-1.5 rounded-full ${connected ? "bg-emerald-400" : "bg-red-500"}`} />
                    <span className="font-mono text-[11px]">{connected ? "Connected" : "Offline"}</span>
                </div>
                {connected && (
                    <LoopStatusPill />
                )}
                <Link href="/dashboard" className="font-mono text-[11px] text-white/25 hover:text-white/60 transition">
                    Dashboard
                </Link>
                <Link href="/world" className="font-mono text-[11px] text-white/25 hover:text-white/60 transition">
                    World Map
                </Link>
            </div>

            {/* Auth */}
            <div className="flex items-center gap-2">
                {isAuthenticated ? (
                    <div className="relative" ref={dropdownRef}>
                        <button
                            onClick={() => setShowDropdown(!showDropdown)}
                            className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg hover:bg-white/[0.04] transition"
                        >
                            <div className="w-7 h-7 rounded-full bg-[#1a1f2e] border border-white/[0.08] flex items-center justify-center text-xs font-semibold text-white/70">
                                {user?.username?.[0]?.toUpperCase() || "?"}
                            </div>
                            <span className="text-sm text-white/70 hidden sm:inline">{user?.username}</span>
                        </button>

                        {showDropdown && (
                            <div className="absolute right-0 top-full mt-1.5 w-44 bg-[#0f1420] border border-white/[0.08] rounded-xl shadow-xl shadow-black/40 py-1 animate-scale-in">
                                <Link href="/profile" className="flex items-center gap-2.5 px-3.5 py-2 text-sm text-white/60 hover:text-white hover:bg-white/[0.04] transition" onClick={() => setShowDropdown(false)}>
                                    Profile
                                </Link>
                                <hr className="border-white/[0.05] my-1" />
                                <button
                                    onClick={() => { logout(); setShowDropdown(false); }}
                                    className="w-full text-left flex items-center gap-2.5 px-3.5 py-2 text-sm text-red-400/80 hover:text-red-400 hover:bg-red-500/[0.06] transition"
                                >
                                    Log out
                                </button>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="flex items-center gap-1.5">
                        <Link href="/login"
                            className="px-3.5 py-1.5 text-sm text-white/50 hover:text-white/80 transition rounded-lg"
                        >
                            Log in
                        </Link>
                        <Link href="/signup"
                            className="px-3.5 py-1.5 text-sm font-medium bg-cyan-600 hover:bg-cyan-500 rounded-lg transition active:scale-[0.97]"
                        >
                            Sign up
                        </Link>
                    </div>
                )}
            </div>
        </nav>
    );
}
