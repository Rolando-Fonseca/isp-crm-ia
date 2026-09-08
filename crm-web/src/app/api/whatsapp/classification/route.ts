import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";
import { isInternalRequest } from "@/lib/internal-auth";

type ClassificationBody = {
  messageId: string;
  needsHuman: boolean;
  intent?: string | null;
  confidence?: number | null;
  countryOfInterest?: string | null;
};

export async function POST(request: Request) {
  if (!isInternalRequest(request)) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  const body = (await request.json()) as Partial<ClassificationBody>;
  if (!body.messageId || typeof body.needsHuman !== "boolean") {
    return NextResponse.json({ error: "messageId and needsHuman are required" }, { status: 400 });
  }

  const message = await prisma.message.findUnique({
    where: { id: body.messageId },
    select: { id: true, lead: { select: { id: true, countryOfInterest: true } } },
  });
  if (!message) {
    return NextResponse.json({ error: "message not found" }, { status: 404 });
  }

  // El agente solo enriquece: rellena el pais si faltaba y marca si hace falta
  // un asesor. Cambiar de etapa sigue siendo decision humana (human-in-the-loop).
  await prisma.$transaction([
    prisma.message.update({
      where: { id: message.id },
      data: { intent: body.intent ?? null, confidence: body.confidence ?? null },
    }),
    prisma.lead.update({
      where: { id: message.lead.id },
      data: {
        needsHuman: body.needsHuman,
        countryOfInterest: message.lead.countryOfInterest ?? body.countryOfInterest ?? undefined,
      },
    }),
  ]);

  return NextResponse.json({ ok: true });
}
