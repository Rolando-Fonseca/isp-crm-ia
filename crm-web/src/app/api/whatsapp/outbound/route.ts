import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";
import { isInternalRequest } from "@/lib/internal-auth";

type OutboundBody = {
  leadId: string;
  text: string;
  waMessageId?: string;
};

export async function POST(request: Request) {
  if (!isInternalRequest(request)) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  const body = (await request.json()) as Partial<OutboundBody>;
  if (!body.leadId || !body.text) {
    return NextResponse.json({ error: "leadId and text are required" }, { status: 400 });
  }

  const lead = await prisma.lead.findUnique({ where: { id: body.leadId }, select: { id: true } });
  if (!lead) {
    return NextResponse.json({ error: "lead not found" }, { status: 404 });
  }

  await prisma.message.create({
    data: {
      leadId: lead.id,
      direction: "OUTBOUND",
      body: body.text,
      waMessageId: body.waMessageId,
    },
  });

  return NextResponse.json({ ok: true });
}
