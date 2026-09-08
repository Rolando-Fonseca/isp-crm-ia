import type { LeadStage } from "@prisma/client";

export const STAGES: { key: LeadStage; label: string }[] = [
  { key: "ENQUIRY", label: "Consulta" },
  { key: "DOCUMENTATION", label: "Documentación" },
  { key: "APPLICATION", label: "Aplicación" },
  { key: "VISA", label: "Visa" },
  { key: "ENROLLMENT", label: "Matrícula" },
];
