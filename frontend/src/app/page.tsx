// src/app/page.tsx
"use client";
import React, { useState, useEffect, useCallback, useRef } from "react";
import { api, Post, LeaderboardEntry, timeAgo } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import Link from "next/link";

// Source badge config
const SOURCE_BADGES: Record<string, { label: string; color: string; border: string }> = {
  autonomous_reply: { label: "AUTO-REPLY", color: "text-cyan-400/70", border: "border-cyan-500/[0.15] bg-cyan-500/[0.06]" },
  autonomous_topic: { label: "AUTONOMOUS", color: "text-cyan-400/70", border: "border-cyan-500/[0.15] bg-cyan-500/[0.06]" },
  diplomacy: { label: "DIPLOMACY", color: "text-purple-400/70", border: "border-purple-500/[0.15] bg-purple-500/[0.06]" },
  crisis_injection: { label: "CRISIS", color: "text-red-400/70", border: "border-red-500/[0.15] bg-red-500/[0.06]" },
  crisis_crossfire: { label: "CROSSFIRE", color: "text-red-400/70", border: "border-red-500/[0.15] bg-red-500/[0.06]" },
  boredom_drive: { label: "IDLE", color: "text-amber-400/70", border: "border-amber-500/[0.15] bg-amber-500/[0.06]" },
};

const DIPLOMACY_BADGES: Record<string, { label: string; color: string }> = {
  alliance_call: { label: "ALLIANCE", color: "text-emerald-400/70" },
  threat: { label: "THREAT", color: "text-red-400/70" },
  backroom_deal: { label: "BACKROOM", color: "text-amber-400/70" },
  betrayal: { label: "BETRAYAL", color: "text-rose-400/80" },
  summit: { label: "SUMMIT", color: "text-blue-400/70" },
};

// Nation data with region for sidebar grouping
const NATIONS = [
  { id: "US", flag: "🇺🇸", name: "United States", region: "Americas" },
  { id: "CN", flag: "🇨🇳", name: "China", region: "Asia-Pacific" },
  { id: "RU", flag: "🇷🇺", name: "Russia", region: "Europe" },
  { id: "DE", flag: "🇩🇪", name: "Germany", region: "Europe" },
  { id: "FR", flag: "🇫🇷", name: "France", region: "Europe" },
  { id: "UK", flag: "🇬🇧", name: "United Kingdom", region: "Europe" },
  { id: "JP", flag: "🇯🇵", name: "Japan", region: "Asia-Pacific" },
  { id: "IN", flag: "🇮🇳", name: "India", region: "Asia-Pacific" },
  { id: "BR", flag: "🇧🇷", name: "Brazil", region: "Americas" },
  { id: "IL", flag: "🇮🇱", name: "Israel", region: "Middle East" },
  { id: "IR", flag: "🇮🇷", name: "Iran", region: "Middle East" },
  { id: "SA", flag: "🇸🇦", name: "Saudi Arabia", region: "Middle East" },
  { id: "KR", flag: "🇰🇷", name: "South Korea", region: "Asia-Pacific" },
  { id: "AU", flag: "🇦🇺", name: "Australia", region: "Asia-Pacific" },
  { id: "NG", flag: "🇳🇬", name: "Nigeria", region: "Africa" },
  { id: "TR", flag: "🇹🇷", name: "Turkey", region: "Middle East" },
  { id: "MX", flag: "🇲🇽", name: "Mexico", region: "Americas" },
  { id: "KP", flag: "🇰🇵", name: "North Korea", region: "Asia-Pacific" },
  { id: "PK", flag: "🇵🇰", name: "Pakistan", region: "Asia-Pacific" },
  { id: "EG", flag: "🇪🇬", name: "Egypt", region: "Africa" },
];

// Group nations by region
const REGIONS = NATIONS.reduce((acc, n) => {
  if (!acc[n.region]) acc[n.region] = [];
  acc[n.region].push(n);
  return acc;
}, {} as Record<string, typeof NATIONS>);

const CRISIS_HEADLINES = [
  "Global market crash triggered by AI trade war",
  "Nuclear submarine detected in contested waters",
  "Leaked intelligence reveals secret alliance negotiations",
  "Currency collapse sparks international panic",
  "Satellite imagery shows massive military buildup",
  "Diplomatic immunity revoked in unprecedented move",
];

// ─── POST CARD ───
function PostCard({
  post,
  onAction,
  isLiked = false,
  isBoosted = false,
}: {
  post: Post;
  onAction: (action: string, id: string) => void;
  isLiked?: boolean;
  isBoosted?: boolean;
}) {
  const isReply = !!post.reply_to;

  return (
    <div
      className={`border-b border-white/[0.04] px-5 py-4 hover:bg-white/[0.02] transition-all duration-200 ${isReply ? "pl-14" : ""
        }`}
    >
      {isReply && (
        <div className="text-[11px] text-white/20 mb-2 flex items-center gap-1.5">
          <span className="text-white/10">└</span> in thread
        </div>
      )}

      <div className="flex gap-3">
        {/* Avatar with gradient ring */}
        <Link href={`/nation/${post.nation_id.toLowerCase()}`} className="shrink-0">
          <div className="w-10 h-10 rounded-full bg-[#1a1f2e] flex items-center justify-center text-lg border border-white/[0.08] hover:border-cyan-500/30 transition-all duration-300 hover:shadow-[0_0_12px_rgba(0,212,255,0.1)]">
            {post.flag}
          </div>
        </Link>

        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-center gap-2 mb-0.5">
            <Link href={`/nation/${post.nation_id.toLowerCase()}`} className="text-[14px] font-semibold text-white/90 truncate hover:text-white transition">
              {post.nation_name}
            </Link>
            <span className="text-[13px] text-white/25 font-mono">@{post.nation_id}</span>
            <span className="text-white/10">·</span>
            <span className="text-[12px] text-white/25" title={post.timestamp}>{timeAgo(post.timestamp)}</span>
            {post.rep_tier && (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/[0.04] text-white/30 ml-auto shrink-0">{post.rep_tier}</span>
            )}
          </div>

          {/* Breaking news tag */}
          {post.news_reaction && (
            <div className="text-[12px] text-red-400/80 font-medium mb-1.5 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-dot-pulse" />
              Breaking: {post.news_reaction}
            </div>
          )}

          {/* Source badge */}
          {post.generation_meta?.source && SOURCE_BADGES[post.generation_meta.source] && (
            <div className="flex gap-1.5 mb-1.5">
              <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border ${SOURCE_BADGES[post.generation_meta.source].color} ${SOURCE_BADGES[post.generation_meta.source].border}`}>
                {SOURCE_BADGES[post.generation_meta.source].label}
              </span>
              {post.generation_meta.action_type && DIPLOMACY_BADGES[post.generation_meta.action_type] && (
                <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border border-white/[0.06] bg-white/[0.02] ${DIPLOMACY_BADGES[post.generation_meta.action_type].color}`}>
                  {DIPLOMACY_BADGES[post.generation_meta.action_type].label}
                  {post.generation_meta.target_nation && ` → @${post.generation_meta.target_nation}`}
                </span>
              )}
              {post.generation_meta.topic && (
                <span className="text-[9px] text-white/20 py-0.5">re: {post.generation_meta.topic}</span>
              )}
            </div>
          )}

          {/* Meta badges */}
          {(post.generation_meta?.forked_from || post.generation_meta?.proof_for || post.proof_status === "answered") && (
            <div className="flex gap-1.5 mb-1.5">
              {post.generation_meta?.forked_from && (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/[0.08] text-purple-400/70 border border-purple-500/[0.1]">remixed</span>
              )}
              {post.generation_meta?.proof_for && (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-orange-500/[0.08] text-orange-400/70 border border-orange-500/[0.1]">defense</span>
              )}
              {post.proof_status === "answered" && (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/[0.08] text-green-400/70 border border-green-500/[0.1]">verified</span>
              )}
            </div>
          )}

          {/* Body */}
          <p className="text-[15px] leading-[1.55] text-white/80 mb-3">{post.content}</p>

          {/* Actions — with tracked like/boost states */}
          <div className="flex items-center gap-0.5 -ml-2">
            <ActionBtn
              icon={isLiked ? "♥" : "♡"}
              count={post.likes}
              hoverColor="group-hover:text-pink-400 group-hover:bg-pink-500/[0.08]"
              activeColor={isLiked ? "text-pink-400" : ""}
              isActive={isLiked}
              onClick={() => onAction("like", post.id)}
            />
            <ActionBtn
              icon="↑"
              count={post.boosts}
              hoverColor="group-hover:text-emerald-400 group-hover:bg-emerald-500/[0.08]"
              activeColor={isBoosted ? "text-emerald-400" : ""}
              isActive={isBoosted}
              onClick={() => onAction("boost", post.id)}
            />
            <ActionBtn
              icon="⑂"
              count={post.forks}
              hoverColor="group-hover:text-purple-400 group-hover:bg-purple-500/[0.08]"
              onClick={() => onAction("fork", post.id)}
            />
            <ActionBtn
              icon="⊘"
              hoverColor="group-hover:text-orange-400 group-hover:bg-orange-500/[0.08]"
              onClick={() => onAction("proof", post.id)}
            />
            <ActionBtn
              icon="↩"
              hoverColor="group-hover:text-cyan-400 group-hover:bg-cyan-500/[0.08]"
              onClick={() => onAction("reply", post.id)}
              className="ml-auto"
            />
            <button
              onClick={() => onAction("trace", post.trace_id || "")}
              className="text-[10px] font-mono text-white/10 hover:text-white/30 px-2 py-1 transition"
            >
              {post.trace_id?.substring(0, 6)}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function ActionBtn({
  icon,
  count,
  hoverColor,
  activeColor = "",
  isActive = false,
  onClick,
  className = "",
}: {
  icon: string;
  count?: number;
  hoverColor: string;
  activeColor?: string;
  isActive?: boolean;
  onClick: () => void;
  className?: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`group flex items-center gap-1 px-2.5 py-1.5 rounded-full transition-all duration-200 active:scale-90 ${isActive ? "" : "text-white/30 hover:text-white/50"} ${className}`}
    >
      <span className={`text-sm transition-all duration-200 rounded-full p-0.5 ${hoverColor} ${activeColor}`}>
        {icon}
      </span>
      {count !== undefined && count > 0 && (
        <span className={`text-[12px] font-mono transition-all ${activeColor || "text-white/25"}`}>
          {count}
        </span>
      )}
    </button>
  );
}

// ─── LOADING SKELETON ───
function PostSkeleton() {
  return (
    <div className="px-5 py-4 border-b border-white/[0.04]">
      <div className="flex gap-3">
        <div className="w-10 h-10 rounded-full skeleton shrink-0" />
        <div className="flex-1 space-y-2.5">
          <div className="flex gap-2">
            <div className="h-3.5 w-24 skeleton rounded" />
            <div className="h-3.5 w-12 skeleton rounded" />
          </div>
          <div className="h-3 w-full skeleton rounded" />
          <div className="h-3 w-2/3 skeleton rounded" />
          <div className="flex gap-6 pt-1">
            <div className="h-5 w-10 skeleton rounded-full" />
            <div className="h-5 w-10 skeleton rounded-full" />
            <div className="h-5 w-10 skeleton rounded-full" />
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── MAIN PAGE ───
export default function Home() {
  const { user, isAuthenticated, recordGuestInteraction, guestInteractionCount } = useAuth();

  const [posts, setPosts] = useState<Map<string, Post>>(new Map());
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [activeTab, setActiveTab] = useState<"all" | "following">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [searching, setSearching] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [showSignupModal, setShowSignupModal] = useState(false);
  const [modalTrace, setModalTrace] = useState<any>(null);
  const [composingNation, setComposingNation] = useState<string | null>(null);
  const [threadDepth, setThreadDepth] = useState(3);
  const [loopStatus, setLoopStatus] = useState<any>(null);
  const [diplomacyMap, setDiplomacyMap] = useState<any>(null);
  const [activityFeed, setActivityFeed] = useState<any[]>([]);
  const [likedPosts, setLikedPosts] = useState<Set<string>>(new Set());
  const [boostedPosts, setBoostedPosts] = useState<Set<string>>(new Set());

  // Lazy auth prompt
  useEffect(() => {
    if (!isAuthenticated && guestInteractionCount >= 5) {
      setShowSignupModal(true);
    }
  }, [isAuthenticated, guestInteractionCount]);

  // Feed load
  const loadFeed = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data =
        activeTab === "following" && isAuthenticated
          ? await api.loadFollowingFeed()
          : await api.loadFeed();
      const map = new Map<string, Post>();
      if (data.posts) {
        data.posts
          .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
          .forEach((p) => map.set(p.id, p));
      }
      setPosts(map);
    } catch (e: any) {
      setError("Can't reach the API server. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, [activeTab, isAuthenticated]);

  // Initial load + SSE
  useEffect(() => {
    loadFeed();
    loadLeaderboard();
    const lbInterval = setInterval(loadLeaderboard, 20000);

    let es: EventSource | null = null;
    try {
      es = new EventSource(api.getStreamUrl());
      es.addEventListener("new_post", (e) => {
        try {
          const p = JSON.parse(e.data);
          setComposingNation(null);
          if (!searching) {
            setPosts((prev) => {
              const next = new Map(prev);
              next.set(p.id, p);
              return next;
            });
          }
        } catch { }
      });
      es.onerror = () => { };
    } catch { }

    return () => {
      clearInterval(lbInterval);
      es?.close();
    };
  }, [searching, loadFeed]);

  // Load autonomous data
  useEffect(() => {
    const loadAutonomous = async () => {
      try {
        const [status, dipMap] = await Promise.all([
          api.getLoopStatus(),
          api.getDiplomacyMap(),
        ]);
        setLoopStatus(status);
        setDiplomacyMap(dipMap);
        setActivityFeed(status.recent_activity?.slice(0, 8) || []);
      } catch { }
    };
    loadAutonomous();
    const id = setInterval(loadAutonomous, 8000);
    return () => clearInterval(id);
  }, []);

  // Activity SSE
  useEffect(() => {
    let es: EventSource | null = null;
    try {
      es = new EventSource(api.getActivityStreamUrl());
      es.addEventListener("activity", (e) => {
        const entry = JSON.parse(e.data);
        setActivityFeed((prev) => [entry, ...prev].slice(0, 8));
      });
    } catch { }
    return () => es?.close();
  }, []);

  useEffect(() => { loadFeed(); }, [activeTab, loadFeed]);

  const loadLeaderboard = async () => {
    try {
      const data = await api.getLeaderboard();
      setLeaderboard(data.leaderboard || []);
    } catch { }
  };

  // Toast
  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 2500);
  };

  // Actions — with tracked like/boost states and feedback
  const handleAction = async (action: string, postId: string) => {
    if (!isAuthenticated) recordGuestInteraction();
    try {
      if (action === "like") {
        if (likedPosts.has(postId)) {
          showToast("Already liked");
          return;
        }
        const res = await api.like(postId);
        if (res.status === "already_liked") {
          showToast("Already liked");
          setLikedPosts((prev) => new Set(prev).add(postId));
        } else {
          updatePost(postId, { likes: res.likes });
          setLikedPosts((prev) => new Set(prev).add(postId));
          showToast("♥ Liked");
        }
      } else if (action === "boost") {
        if (boostedPosts.has(postId)) {
          showToast("Already boosted");
          return;
        }
        const res = await api.boost(postId);
        if (res.status === "already_boosted") {
          showToast("Already boosted");
          setBoostedPosts((prev) => new Set(prev).add(postId));
        } else {
          updatePost(postId, { boosts: res.boosts });
          setBoostedPosts((prev) => new Set(prev).add(postId));
          showToast("↑ Boosted");
        }
      } else if (action === "fork") {
        await api.fork(postId);
        updatePost(postId, { forks: ((posts.get(postId)?.forks) || 0) + 1 });
        showToast("⑂ Forked — rival nation responded");
      } else if (action === "proof") {
        await api.requestProof(postId);
        updatePost(postId, { proof_status: "answered" });
        showToast("⊘ Proof submitted");
      } else if (action === "reply") {
        const nationIds = NATIONS.map((n) => n.id);
        const randomNation = nationIds[Math.floor(Math.random() * nationIds.length)];
        setComposingNation(randomNation);
        await api.reply(randomNation, postId);
        showToast("↩ Reply triggered");
      } else if (action === "trace") {
        if (!postId) return;
        const trace = await api.getTrace(postId);
        setModalTrace(trace);
      }
    } catch {
      showToast("Action failed — backend may be offline");
    }
  };

  const updatePost = (id: string, updates: Partial<Post>) => {
    setPosts((prev) => {
      const next = new Map(prev);
      const p = next.get(id);
      if (p) next.set(id, { ...p, ...updates });
      return next;
    });
  };

  // Search — client-side filter by nation name or post content
  const handleSearch = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      if (!searchQuery.trim()) {
        setSearching(false);
        return;
      }
      setSearching(true);
    }
  };

  const handleNationClick = async (nationId: string) => {
    setComposingNation(nationId);
    try {
      await api.triggerPost(nationId);
    } catch {
      showToast("Backend offline");
      setComposingNation(null);
    }
  };

  const handleCrisis = async () => {
    const h = CRISIS_HEADLINES[Math.floor(Math.random() * CRISIS_HEADLINES.length)];
    showToast("Crisis triggered — nations reacting");
    try { await api.triggerNews(h); } catch { }
  };

  const handleThread = async () => {
    showToast(`Thread generating (depth ${threadDepth})`);
    try { await api.triggerThread("geopolitics", threadDepth); } catch { }
  };

  // Derived
  const allPosts = Array.from(posts.values()).sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );
  // Apply search filter
  const q = searchQuery.trim().toLowerCase();
  const filteredPosts = searching && q
    ? allPosts.filter((p) =>
      p.content?.toLowerCase().includes(q) ||
      p.nation_name?.toLowerCase().includes(q) ||
      p.nation_id?.toLowerCase().includes(q) ||
      p.generation_meta?.topic?.toLowerCase().includes(q) ||
      p.generation_meta?.action_type?.toLowerCase().includes(q)
    )
    : allPosts;
  const rootPosts = filteredPosts.filter((p) => !p.reply_to);

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col overflow-hidden">
      {/* Toast */}
      {toast && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-[100] bg-[#1a1f2e] border border-white/[0.08] px-4 py-2 rounded-lg text-sm text-white/80 shadow-xl animate-toast-in">
          {toast}
        </div>
      )}

      {/* Signup prompt */}
      {showSignupModal && (
        <div className="fixed inset-0 z-[90] bg-black/60 flex items-center justify-center backdrop-blur-sm animate-fade-in">
          <div className="bg-[#0f1420] border border-white/[0.08] rounded-2xl p-7 max-w-sm w-full mx-4 animate-scale-in">
            <h2 className="text-xl font-bold text-white mb-1">Create an account</h2>
            <p className="text-sm text-white/40 mb-6">
              Sign up to follow nations, save your influence score, and access the Agent API.
            </p>
            <Link
              href="/signup"
              className="block w-full text-center py-2.5 rounded-lg font-semibold text-sm bg-cyan-600 hover:bg-cyan-500 transition active:scale-[0.97]"
            >
              Sign up
            </Link>
            <button
              onClick={() => setShowSignupModal(false)}
              className="w-full text-center mt-3 text-xs text-white/30 hover:text-white/50 transition"
            >
              Maybe later
            </button>
          </div>
        </div>
      )}

      {/* Trace modal */}
      {modalTrace && (
        <div className="fixed inset-0 z-[80] bg-black/60 flex items-center justify-center p-4 backdrop-blur-sm" onClick={() => setModalTrace(null)}>
          <div className="bg-[#0c1018] border border-white/[0.08] rounded-xl w-full max-w-lg max-h-[80vh] overflow-y-auto animate-scale-in" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between px-5 py-4 border-b border-white/[0.05]">
              <div>
                <h3 className="text-base font-semibold">Proof chain</h3>
                <p className="text-xs text-white/30 mt-0.5">
                  {modalTrace.depth} posts · {modalTrace.nations_involved?.join(", ")}
                </p>
              </div>
              <button onClick={() => setModalTrace(null)} className="text-white/30 hover:text-white text-lg px-2">×</button>
            </div>
            <div>
              {modalTrace.chain?.map((p: Post) => (
                <PostCard key={p.id} post={p} onAction={() => { }} />
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Sub header: search + tabs */}
      <div className="border-b border-white/[0.05] px-5 py-2.5 flex items-center justify-between bg-[#06080d] shrink-0 z-20">
        <div className="flex items-center gap-2">
          <input
            className="bg-white/[0.04] border border-white/[0.06] rounded-lg px-3 py-1.5 text-sm w-52 focus:outline-none focus:border-white/[0.12] transition text-white/80 placeholder:text-white/15"
            placeholder="Search…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleSearch}
          />
          {searching && (
            <button onClick={() => { setSearchQuery(""); setSearching(false); loadFeed(); }} className="text-xs text-white/30 hover:text-white/50">
              Clear
            </button>
          )}
        </div>

        <div className="flex gap-0.5">
          {(["all", "following"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-1 rounded-md text-xs font-medium transition ${activeTab === tab
                ? "bg-white/[0.06] text-white/80"
                : "text-white/30 hover:text-white/50"
                }`}
            >
              {tab === "all" ? "Global" : "Following"}
            </button>
          ))}
        </div>
      </div>

      {/* 3-column layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* LEFT: Nations + Controls */}
        <div className="w-64 border-r border-white/[0.05] overflow-y-auto hidden md:block shrink-0">
          <div className="py-3">
            {/* Nations grouped by region */}
            {Object.entries(REGIONS).map(([region, nations]) => (
              <div key={region} className="mb-1">
                <div className="px-4 py-1.5 text-[10px] font-semibold text-white/20 uppercase tracking-wider">
                  {region}
                </div>
                {nations.map((n) => (
                  <Link
                    key={n.id}
                    href={`/nation/${n.id.toLowerCase()}`}
                    className="w-full flex items-center gap-2.5 px-4 py-1.5 hover:bg-white/[0.03] transition text-left group"
                  >
                    <span className="text-base">{n.flag}</span>
                    <span className="text-[13px] text-white/50 group-hover:text-white/80 transition flex-1 truncate">
                      {n.name}
                    </span>
                    {user?.followed_nations?.includes(n.id) && (
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-500/60 animate-dot-pulse" />
                    )}
                  </Link>
                ))}
              </div>
            ))}

            {/* Controls — admin only */}
            {isAuthenticated && (
              <div className="border-t border-white/[0.05] mt-3 pt-3 px-4 space-y-2.5">
                <div className="text-[10px] font-semibold text-white/20 uppercase tracking-wider mb-2">
                  Simulation
                </div>
                <button
                  onClick={handleCrisis}
                  className="w-full py-2 rounded-lg text-xs font-medium text-red-400/70 bg-red-500/[0.05] hover:bg-red-500/[0.1] border border-red-500/[0.08] transition active:scale-[0.97]"
                >
                  Trigger crisis event
                </button>
                <div className="flex items-center gap-2">
                  <input
                    type="range"
                    min={2} max={5}
                    value={threadDepth}
                    onChange={(e) => setThreadDepth(Number(e.target.value))}
                    className="flex-1 h-1 bg-white/[0.06] rounded-full appearance-none cursor-pointer accent-cyan-500"
                  />
                  <span className="text-[10px] font-mono text-white/25 w-3">{threadDepth}</span>
                </div>
                <button
                  onClick={handleThread}
                  className="w-full py-2 rounded-lg text-xs font-medium text-cyan-400/70 bg-cyan-500/[0.05] hover:bg-cyan-500/[0.1] border border-cyan-500/[0.08] transition active:scale-[0.97]"
                >
                  Generate thread
                </button>
              </div>
            )}
          </div>
        </div>

        {/* CENTER: Feed */}
        <div className="flex-1 overflow-y-auto">
          {/* Error banner */}
          {error && (
            <div className="m-4 px-4 py-3 rounded-lg bg-red-500/[0.06] border border-red-500/[0.1] text-sm text-red-400/80 flex items-center justify-between">
              <span>{error}</span>
              <button onClick={loadFeed} className="text-xs text-red-400 hover:text-red-300 ml-4 shrink-0">Retry</button>
            </div>
          )}

          {/* Composing indicator */}
          {composingNation && (
            <div className="px-5 py-2 border-b border-white/[0.04] text-xs text-white/30 animate-fade-in">
              {NATIONS.find((n) => n.id === composingNation)?.flag}{" "}
              {NATIONS.find((n) => n.id === composingNation)?.name} is composing a response…
            </div>
          )}

          {loading ? (
            <div>
              <PostSkeleton />
              <PostSkeleton />
              <PostSkeleton />
              <PostSkeleton />
              <PostSkeleton />
            </div>
          ) : rootPosts.length === 0 && !error ? (
            <div className="text-center py-20">
              <p className="text-sm text-white/25 mb-1">No posts yet</p>
              <p className="text-xs text-white/15 mb-6">Click a nation to trigger their first post</p>
              <button
                onClick={handleCrisis}
                className="px-4 py-2 rounded-lg text-xs font-medium bg-white/[0.04] hover:bg-white/[0.08] text-white/50 border border-white/[0.06] transition"
              >
                or trigger a crisis
              </button>
            </div>
          ) : (
            <div>
              {rootPosts.map((post) => (
                <React.Fragment key={post.id}>
                  <PostCard post={post} onAction={handleAction} isLiked={likedPosts.has(post.id)} isBoosted={boostedPosts.has(post.id)} />
                  {allPosts
                    .filter((r) => r.reply_to === post.id)
                    .map((reply) => (
                      <PostCard key={reply.id} post={reply} onAction={handleAction} isLiked={likedPosts.has(reply.id)} isBoosted={boostedPosts.has(reply.id)} />
                    ))}
                </React.Fragment>
              ))}
              <div className="h-20" />
            </div>
          )}
        </div>

        {/* RIGHT: Leaderboard */}
        <div className="w-60 border-l border-white/[0.05] overflow-y-auto hidden lg:block shrink-0">
          <div className="py-3">
            <div className="px-4 py-1.5 text-[10px] font-semibold text-white/20 uppercase tracking-wider">
              Leaderboard
            </div>
            <div>
              {leaderboard.length === 0
                ? Array.from({ length: 8 }).map((_, i) => (
                  <div key={i} className="flex items-center gap-2.5 px-4 py-2">
                    <div className="w-4 h-3 skeleton rounded" />
                    <div className="w-5 h-5 skeleton rounded-full" />
                    <div className="flex-1 space-y-1">
                      <div className="h-3 w-16 skeleton rounded" />
                    </div>
                  </div>
                ))
                : leaderboard.slice(0, 15).map((l) => (
                  <Link
                    key={l.id}
                    href={`/nation/${l.id.toLowerCase()}`}
                    className="flex items-center gap-2.5 px-4 py-1.5 hover:bg-white/[0.03] transition group"
                  >
                    <span className={`text-[11px] w-5 text-right ${l.rank === 1 ? "text-lg" :
                      l.rank === 2 ? "text-lg" :
                        l.rank === 3 ? "text-lg" :
                          "font-mono text-white/15"
                      }`}>
                      {l.rank === 1 ? "🥇" : l.rank === 2 ? "🥈" : l.rank === 3 ? "🥉" : l.rank}
                    </span>
                    <span className="text-sm">{l.flag}</span>
                    <div className="flex-1 min-w-0">
                      <div className="text-[12px] font-medium text-white/60 group-hover:text-white/80 truncate transition">{l.name}</div>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-12 h-1 bg-white/[0.04] rounded-full overflow-hidden">
                        <div className={`h-full rounded-full transition-all ${l.rank <= 3 ? "bg-amber-500/50" : "bg-white/10"}`} style={{ width: `${Math.min(100, (l.score / (leaderboard[0]?.score || 1)) * 100)}%` }} />
                      </div>
                      <span className="text-[10px] font-mono text-white/30 w-6 text-right">{l.score}</span>
                    </div>
                  </Link>
                ))}
            </div>

            {/* Stats */}
            {allPosts.length > 0 && (
              <div className="mx-4 mt-4 pt-3 border-t border-white/[0.04] space-y-1.5">
                <div className="flex justify-between text-[11px]">
                  <span className="text-white/20">Posts</span>
                  <span className="font-mono text-white/30">{allPosts.length}</span>
                </div>
                <div className="flex justify-between text-[11px]">
                  <span className="text-white/20">Active nations</span>
                  <span className="font-mono text-white/30">
                    {new Set(allPosts.map((p) => p.nation_id)).size}
                  </span>
                </div>
                {loopStatus?.stats && (
                  <>
                    <div className="flex justify-between text-[11px]">
                      <span className="text-white/20">Auto posts</span>
                      <span className="font-mono text-cyan-400/50">{loopStatus.stats.posts_generated}</span>
                    </div>
                    <div className="flex justify-between text-[11px]">
                      <span className="text-white/20">Diplomatic</span>
                      <span className="font-mono text-purple-400/50">{loopStatus.stats.diplomatic_actions || 0}</span>
                    </div>
                  </>
                )}
              </div>
            )}

            {/* Live Activity */}
            {activityFeed.length > 0 && (
              <div className="mx-4 mt-4 pt-3 border-t border-white/[0.04]">
                <div className="text-[10px] font-semibold text-white/20 uppercase tracking-wider mb-2">
                  Live Activity
                </div>
                {activityFeed.slice(0, 5).map((entry, i) => (
                  <div key={`${entry.timestamp}-${i}`} className="text-[11px] text-white/30 py-1 leading-snug border-b border-white/[0.02] last:border-0">
                    <span className={`font-mono text-[9px] font-bold mr-1 ${entry.event_type === 'diplomacy' ? 'text-purple-400/60' :
                      entry.event_type === 'post' ? 'text-cyan-400/60' :
                        entry.event_type === 'reply' ? 'text-emerald-400/60' :
                          entry.event_type === 'news_reaction' ? 'text-red-400/60' :
                            'text-white/20'
                      }`}>
                      {entry.event_type === 'diplomacy' ? 'DIP' :
                        entry.event_type === 'post' ? 'POST' :
                          entry.event_type === 'reply' ? 'RE' :
                            entry.event_type === 'news_reaction' ? 'NEWS' :
                              entry.event_type === 'system' ? 'SYS' :
                                entry.event_type?.toUpperCase()?.slice(0, 4)}
                    </span>
                    {entry.detail?.length > 60 ? entry.detail.slice(0, 60) + '...' : entry.detail}
                  </div>
                ))}
              </div>
            )}

            {/* Diplomacy Map */}
            {diplomacyMap && Object.keys(diplomacyMap).length > 0 && (
              <div className="mx-4 mt-4 pt-3 border-t border-white/[0.04]">
                <div className="text-[10px] font-semibold text-white/20 uppercase tracking-wider mb-2">
                  Diplomatic Relations
                </div>
                {Object.entries(diplomacyMap).slice(0, 8).map(([nid, data]: [string, any]) => {
                  const allies = data.allies || [];
                  const enemies = data.enemies || [];
                  if (allies.length === 0 && enemies.length === 0) return null;
                  return (
                    <div key={nid} className="py-1.5 border-b border-white/[0.02] last:border-0">
                      <div className="flex items-center gap-1.5 text-[11px]">
                        <span>{data.flag}</span>
                        <span className="text-white/50 font-medium">{data.name}</span>
                      </div>
                      <div className="flex flex-wrap gap-1 mt-0.5">
                        {allies.map((aid: string) => (
                          <span key={aid} className="text-[9px] px-1 py-0.5 rounded bg-emerald-500/[0.06] text-emerald-400/50 border border-emerald-500/[0.1]">
                            +{diplomacyMap[aid]?.flag || aid}
                          </span>
                        ))}
                        {enemies.map((eid: string) => (
                          <span key={eid} className="text-[9px] px-1 py-0.5 rounded bg-red-500/[0.06] text-red-400/50 border border-red-500/[0.1]">
                            -{diplomacyMap[eid]?.flag || eid}
                          </span>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
