import { prisma } from "@/lib/db";
import { STAGES } from "@/lib/stages";

export default async function LeadsPage() {
  const leads = await prisma.lead.findMany({ orderBy: { createdAt: "asc" } });

  return (
    <main className="min-h-screen bg-neutral-50 p-8">
      <h1 className="text-2xl font-semibold text-neutral-900">Pipeline de leads</h1>
      <p className="mt-1 text-sm text-neutral-500">
        {leads.length} leads en base de datos (Postgres local).
      </p>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {STAGES.map((stage) => {
          const leadsInStage = leads.filter((lead) => lead.stage === stage.key);
          return (
            <div key={stage.key} className="rounded-lg bg-white p-3 shadow-sm ring-1 ring-neutral-200">
              <h2 className="flex items-center justify-between text-sm font-medium text-neutral-700">
                {stage.label}
                <span className="rounded-full bg-neutral-100 px-2 py-0.5 text-xs text-neutral-500">
                  {leadsInStage.length}
                </span>
              </h2>
              <div className="mt-3 flex flex-col gap-2">
                {leadsInStage.map((lead) => (
                  <div key={lead.id} className="rounded-md border border-neutral-200 p-2 text-sm">
                    <div className="flex items-start justify-between gap-2">
                      <p className="font-medium text-neutral-900">{lead.name}</p>
                      {lead.needsHuman && (
                        <span className="shrink-0 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
                          Necesita asesor
                        </span>
                      )}
                    </div>
                    {lead.countryOfInterest && (
                      <p className="text-neutral-500">{lead.countryOfInterest}</p>
                    )}
                    <p className="text-neutral-400">{lead.phone}</p>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </main>
  );
}
