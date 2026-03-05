// src/app/nation/[id]/page.tsx — Server component wrapper
import NationProfileClient from "./NationProfileClient";

const NATION_IDS = [
    "us", "cn", "ru", "de", "fr", "uk", "jp", "in", "br", "il",
    "ir", "sa", "kr", "au", "ng", "tr", "mx", "kp", "pk", "eg",
];

export function generateStaticParams() {
    return NATION_IDS.map((id) => ({ id }));
}

export default async function NationProfilePage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = await params;
    return <NationProfileClient id={id} />;
}
