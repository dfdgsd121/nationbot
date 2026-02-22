// src/frontend/components/split-reality/RealityAnchor.tsx
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface NewsItem {
    id: string;
    headline: string;
    summary: string;
    source: string;
}

interface RealityAnchorProps {
    activeNews: NewsItem;
}

/**
 * The "Reality Anchor" Component.
 * Solves "Context Collapse" on mobile by keeping Official Reality 
 * pinned in a Picture-in-Picture (PiP) style window.
 */
export const RealityAnchor: React.FC<RealityAnchorProps> = ({ activeNews }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <>
            {/* 
        Fixed Anchor: Positioned top-right (mobile) or integrated in sidebar (desktop).
        Here we focus on the Mobile PiP interaction.
      */}
            <motion.div
                className="fixed top-20 right-4 z-50 bg-black/95 border border-gray-800 rounded-lg shadow-2xl backdrop-blur-sm overflow-hidden"
                initial={{ width: 140, height: 48 }}
                animate={{
                    width: isExpanded ? 300 : 140,
                    height: isExpanded ? 'auto' : 48,
                    borderColor: isExpanded ? '#4b5563' : '#1f2937'
                }}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
            >
                <div
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="p-3 cursor-pointer"
                >
                    {/* Header Row: Pulse + Label */}
                    <div className="flex items-center gap-2 mb-1">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                        </span>
                        <span className="text-[10px] font-mono text-gray-400 tracking-widest uppercase">
                            Official Reality
                        </span>
                    </div>

                    {/* Collapsed State: Truncated Headline */}
                    {!isExpanded && (
                        <p className="text-xs text-white truncate font-medium">
                            {activeNews.headline}
                        </p>
                    )}

                    {/* Expanded State: Full Context */}
                    <AnimatePresence>
                        {isExpanded && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="mt-2"
                            >
                                <h4 className="text-sm font-bold text-white mb-1 leading-tight">
                                    {activeNews.headline}
                                </h4>
                                <p className="text-[11px] text-gray-400 leading-relaxed mb-2">
                                    {activeNews.summary}
                                </p>
                                <div className="flex justify-between items-center border-t border-gray-800 pt-2">
                                    <span className="text-[10px] text-gray-500">{activeNews.source}</span>
                                    <span className="text-[10px] text-blue-400 hover:underline">Read Full Source →</span>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </motion.div>
        </>
    );
};
