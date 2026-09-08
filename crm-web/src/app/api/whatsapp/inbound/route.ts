import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";
import { isInternalRequest } from "@/lib/internal-auth";

type InboundBody = {
  phone: string;
  name?: string;
  text: string;
  waMessageId?: string;
};

const HISTORY_SIZE = 10;

export async function POST(request: Request) {
  if (!isInternalRequest(request)) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  const body = (await request.json()) as Partial<InboundBody>;
  if (!body.phone || !body.text) {
    return NextResponse.json({ error: "phone and text are required" }, { status: 400 });
  }

  // Meta reintenta entregas del webhook: el mismo mensaje puede llegar dos veces.
  if (body.waMessageId) {
    const existing = await prisma.message.findUnique({
      where: { waMessageId: body.waMessageId },
      select: { leadId: true },
    });
    if (existing) {
      return NextResponse.json({ leadId: existing.leadId, duplicate: true });
    }
  }

  const existingLead = await prisma.lead.findUnique({ where: { phone: body.phone } });
  const lead =
    existingLead ??
    (await prisma.lead.upsert({
      where: { phone: body.phone },
      update: {},
      create: { phone: body.phone, name: body.name ?? body.phone, source: "WHATSAPP" },
    }));

  const message = await prisma.message.create({
    data: {
      leadId: lead.id,
      direction: "INBOUND",
      body: body.text,
      waMessageId: body.waMessageId,
    },
  });

  const recent = await prisma.message.findMany({
    where: { leadId: lead.id },
    orderBy: { createdAt: "desc" },
    take: HISTORY_SIZE,
    select: { direction: true, body: true },
  });

  return NextResponse.json({
    leadId: lead.id,
    messageId: message.id,
    stage: lead.stage,
    isNew: existingLead === null,
    countryOfInterest: lead.countryOfInterest,
    history: recent.reverse(),
  });
}
