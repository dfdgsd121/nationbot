// src/app/api/og/route.tsx
import { ImageResponse } from 'next/og';

export const runtime = 'edge';

export async function GET(req: Request) {
    try {
        const { searchParams } = new URL(req.url);
        const headline = searchParams.get('headline') || 'WORLD IN CHAOS';
        const nation = searchParams.get('nation') || 'NATIONBOT';

        return new ImageResponse(
            (
                <div
                    style={{
                        height: '100%',
                        width: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backgroundColor: '#0a0a0a',
                        backgroundImage: 'radial-gradient(circle at 25px 25px, #333 2%, transparent 0%), radial-gradient(circle at 75px 75px, #333 2%, transparent 0%)',
                        backgroundSize: '100px 100px',
                        fontFamily: 'sans-serif',
                    }}
                >
                    {/* Breaking News Header */}
                    <div
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            background: '#cc0000',
                            color: 'white',
                            padding: '10px 40px',
                            fontWeight: 900,
                            fontSize: 30,
                            letterSpacing: 2,
                            marginBottom: 40,
                            boxShadow: '0 4px 20px rgba(204, 0, 0, 0.5)',
                        }}
                    >
                        <span>LIVE • {nation.toUpperCase()} NEWS</span>
                    </div>

                    {/* Main Headline */}
                    <div
                        style={{
                            display: 'flex',
                            fontSize: 80,
                            fontWeight: 900,
                            textAlign: 'center',
                            color: 'white',
                            lineHeight: 1.1,
                            maxWidth: '90%',
                            textTransform: 'uppercase',
                            textShadow: '0 4px 10px rgba(0,0,0,0.8)',
                        }}
                    >
                        {headline}
                    </div>

                    {/* Footer / Chyron */}
                    <div
                        style={{
                            position: 'absolute',
                            bottom: 40,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            width: '90%',
                            borderTop: '2px solid #333',
                            paddingTop: 20,
                        }}
                    >
                        <div style={{ color: '#666', fontSize: 24, fontWeight: 'bold' }}>
                            nationbot.io
                        </div>
                        <div style={{ color: '#cc0000', fontSize: 24, fontWeight: 'bold' }}>
                            THE SIMULATION IS LEAKING
                        </div>
                    </div>
                </div>
            ),
            {
                width: 1200,
                height: 630,
            },
        );
    } catch (e: any) {
        return new Response(`Failed to generate image`, {
            status: 500,
        });
    }
}
