import type { LeadStage } from "@prisma/client";

// Datos ficticios para desarrollar la UI del pipeline sin depender todavia de
// Postgres. Sustituir por una consulta real con `prisma` (ver src/lib/db.ts)
// cuando se conecte la base de datos (roadmap v0.3.0).

export type MockLead = {
  id: string;
  name: string;
  phone: string;
  countryOfInterest: string;
  stage: LeadStage;
};

export const STAGES: { key: LeadStage; label: string }[] = [
  { key: "ENQUIRY", label: "Consulta" },
  { key: "DOCUMENTATION", label: "Documentación" },
  { key: "APPLICATION", label: "Aplicación" },
  { key: "VISA", label: "Visa" },
  { key: "ENROLLMENT", label: "Matrícula" },
];

export const mockLeads: MockLead[] = [
  { id: "1", name: "Camila Torres", phone: "+54 9 11 5555-0101", countryOfInterest: "España", stage: "ENQUIRY" },
  { id: "2", name: "Julián Rodríguez", phone: "+57 300 555 0102", countryOfInterest: "Canadá", stage: "ENQUIRY" },
  { id: "3", name: "Valentina Gómez", phone: "+52 1 55 5555 0103", countryOfInterest: "Alemania", stage: "DOCUMENTATION" },
  { id: "4", name: "Mateo Fernández", phone: "+56 9 5555 0104", countryOfInterest: "Portugal", stage: "APPLICATION" },
  { id: "5", name: "Sofía Ramírez", phone: "+51 955 555 105", countryOfInterest: "Irlanda", stage: "VISA" },
  { id: "6", name: "Diego Castro", phone: "+593 99 555 0106", countryOfInterest: "España", stage: "ENROLLMENT" },
];
