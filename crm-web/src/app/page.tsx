import Link from "next/link";
import { prisma } from "@/lib/db";

export default async function Home() {
  const leadCount = await prisma.lead.count();

  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col items-start justify-center gap-6 p-8">
      <div>
        <h1 className="text-3xl font-semibold text-neutral-900">ISP CRM IA</h1>
        <p className="mt-2 text-neutral-500">
          CRM con IA y canal de WhatsApp para gestión de leads de estudiantes
          internacionales. Proyecto de portafolio, independiente de producción.
        </p>
      </div>

      <div className="rounded-lg bg-neutral-50 p-4 text-sm text-neutral-600 ring-1 ring-neutral-200">
        {leadCount} leads en la base de datos (Postgres local, datos de ejemplo).
      </div>

      <Link
        href="/leads"
        className="rounded-full bg-neutral-900 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-neutral-700"
      >
        Ver pipeline de leads →
      </Link>
    </main>
  );
}
