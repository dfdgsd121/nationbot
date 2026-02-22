// src/frontend/components/split-reality/LeftSidebar.tsx
import React from 'react';

interface NewsItem {
    id: string;
    headline: string;
    source: string;
    time: string;
}

/**
 * Left Pane: "Official Reality"
 * Displays the factual news feed.
 * Hidden on mobile (replaced by PiP RealityAnchor).
 */
export const LeftSidebar = () => {
    // Mock Data
    const newsItems: NewsItem[] = [
        { id: '1', headline: 'US Federal Reserve holds rates steady at 5.25%', source: 'Reuters', time: '10m ago' },
        { id: '2', headline: 'China announces new trade partnerships in Africa', source: 'AP News', time: '25m ago' },
        { id: '3', headline: 'Global climate summit concludes with mixed results', source: 'BBC', time: '1h ago' },
    ];

    return (
        <aside className="hidden lg:flex flex-col w-1/5 min-h-screen p-4 border-r border-gray-800 bg-black sticky top-0 h-screen overflow-y-auto">
            <h3 className="text-xs font-mono font-bold text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                <span className="w-2 h-2 bg-gray-600 rounded-full" />
                Official Reality
            </h3>

            <div className="space-y-6">
                {newsItems.map((item) => (
                    <div key={item.id} className="group cursor-pointer">
                        <div className="flex justify-between items-baseline mb-1">
                            <span className="text-[10px] font-bold text-gray-500">{item.source}</span>
                            <span className="text-[10px] text-gray-600">{item.time}</span>
                        </div>
                        <h4 className="text-sm text-gray-300 font-medium leading-normal group-hover:text-white transition-colors">
                            {item.headline}
                        </h4>
                    </div>
                ))}
            </div>

            <div className="mt-auto pt-8 text-[10px] text-gray-600">
                Data provided by Module 01 (Oracle)
            </div>
        </aside>
    );
};
