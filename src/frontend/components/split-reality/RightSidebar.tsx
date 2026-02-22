// src/frontend/components/split-reality/RightSidebar.tsx
import React from 'react';

interface NationRank {
    rank: number;
    nation_id: string;
    score: number;
    trend: 'up' | 'down' | 'flat';
}

interface TrendingTopic {
    id: string;
    tag: string;
    volume: string;
}

/**
 * Right Pane: "Leaderboard & Stats"
 * Displays who is winning the AI simulation.
 */
export const RightSidebar = () => {
    // Mock Data
    const rankings: NationRank[] = [
        { rank: 1, nation_id: 'USA', score: 9840, trend: 'up' },
        { rank: 2, nation_id: 'CHN', score: 9650, trend: 'up' },
        { rank: 3, nation_id: 'FRA', score: 4300, trend: 'down' },
        { rank: 4, nation_id: 'DEU', score: 4100, trend: 'flat' },
    ];

    const trends: TrendingTopic[] = [
        { id: '1', tag: '#TradeWar', volume: '1.2M' },
        { id: '2', tag: '#MoonBase', volume: '850K' },
        { id: '3', tag: '#BaguetteStrike', volume: '400K' },
    ];

    return (
        <aside className="hidden lg:flex flex-col w-1/5 min-h-screen p-4 border-l border-gray-800 bg-black sticky top-0 h-screen overflow-y-auto">
            {/* Leaderboard Section */}
            <div className="mb-8">
                <h3 className="text-xs font-mono font-bold text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                    <span className="text-yellow-500">🏆</span> Leaderboard
                </h3>
                <div className="space-y-3">
                    {rankings.map((nation) => (
                        <div key={nation.nation_id} className="flex items-center justify-between p-2 rounded bg-gray-900/50 hover:bg-gray-800 transition-colors cursor-pointer">
                            <div className="flex items-center gap-3">
                                <span className={`font-mono text-sm ${nation.rank === 1 ? 'text-yellow-500 font-bold' : 'text-gray-500'}`}>
                                    #{nation.rank}
                                </span>
                                <span className="font-bold text-gray-200">{nation.nation_id}</span>
                            </div>
                            <div className="text-right">
                                <div className="text-xs font-mono text-gray-400">{nation.score}</div>
                                <div className={`text-[9px] ${nation.trend === 'up' ? 'text-green-500' : 'text-red-500'}`}>
                                    {nation.trend === 'up' ? '▲' : '▼'}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Trends Section */}
            <div>
                <h3 className="text-xs font-mono font-bold text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                    <span className="text-blue-500">📈</span> Trending
                </h3>
                <div className="space-y-2">
                    {trends.map((topic) => (
                        <div key={topic.id} className="flex justify-between items-center group cursor-pointer">
                            <span className="text-sm text-gray-300 group-hover:text-blue-400 transition-colors">
                                {topic.tag}
                            </span>
                            <span className="text-[10px] text-gray-600">{topic.volume}</span>
                        </div>
                    ))}
                </div>
            </div>
        </aside>
    );
};
