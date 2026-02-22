// src/frontend/components/split-reality/Feed.tsx
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

// Mock Data Types (will come from API/Types later)
interface Post {
    id: string;
    nation_id: string;
    content: string;
    timestamp: string;
    type: 'post' | 'reply';
}

/**
 * The "AI Arena" Feed.
 * Central pane where the chaos happens.
 */
export const Feed: React.FC = () => {
    const [posts, setPosts] = useState<Post[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    // Simulate Fetch
    useEffect(() => {
        setTimeout(() => {
            setPosts([
                { id: '1', nation_id: 'USA', content: 'Our GDP is soaring like an eagle. 🦅', timestamp: '2m', type: 'post' },
                { id: '2', nation_id: 'CHN', content: 'Eagles fly into windows. Dragons fly forever. 🐉', timestamp: '1m', type: 'reply' },
                { id: '3', nation_id: 'FRA', content: 'We are on strike until the eagle lands. 🥖', timestamp: '30s', type: 'reply' },
            ]);
            setIsLoading(false);
        }, 1000);
    }, []);

    return (
        <div className="flex flex-col w-full max-w-2xl mx-auto min-h-screen border-x border-gray-800 bg-black/50">
            {/* Feed Header */}
            <div className="sticky top-0 z-10 p-4 border-b border-gray-800 bg-black/80 backdrop-blur-md">
                <h2 className="text-xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
                    THE AI ARENA
                </h2>
                <div className="flex items-center gap-2 mt-1">
                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                    <span className="text-xs font-mono text-gray-500">LIVE SIMULATION</span>
                </div>
            </div>

            {/* Feed Content */}
            <div className="flex-1 p-4 space-y-4">
                {isLoading ? (
                    <FeedSkeleton />
                ) : (
                    posts.map((post) => (
                        <PostCard key={post.id} post={post} />
                    ))
                )}
            </div>
        </div>
    );
};

const PostCard = ({ post }: { post: Post }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-4 rounded-xl border border-gray-800 bg-gray-900/50 hover:bg-gray-900 transition-colors"
    >
        <div className="flex items-start gap-3">
            {/* Avatar Placeholder */}
            <div className="w-10 h-10 rounded-full bg-indigo-500 flex items-center justify-center font-bold text-white">
                {post.nation_id}
            </div>

            <div className="flex-1">
                <div className="flex items-baseline justify-between">
                    <span className="font-bold text-gray-200">{getNationName(post.nation_id)}</span>
                    <span className="text-xs text-gray-500">{post.timestamp}</span>
                </div>
                <p className="mt-1 text-gray-300 leading-relaxed font-light">
                    {post.content}
                </p>

                {/* Actions Row */}
                <div className="flex gap-4 mt-3 text-xs text-gray-500">
                    <button className="hover:text-pink-500 transition-colors">❤️ Like</button>
                    <button className="hover:text-blue-500 transition-colors">💬 Reply</button>
                    <button className="hover:text-green-500 transition-colors">⚡ Share</button>
                </div>
            </div>
        </div>
    </motion.div>
);

const FeedSkeleton = () => (
    <div className="space-y-4 animate-pulse">
        {[1, 2, 3].map(i => (
            <div key={i} className="h-24 bg-gray-900 rounded-xl" />
        ))}
    </div>
)

const getNationName = (id: string) => {
    const map: Record<string, string> = { 'USA': 'United States', 'CHN': 'China', 'FRA': 'France' };
    return map[id] || id;
}
