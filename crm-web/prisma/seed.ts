import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

// Telefonos en formato E.164 (+codigo pais + numero), igual que el wa_id que
// entrega WhatsApp Cloud API, para que el upsert por telefono no duplique leads.
const leads = [
  { name: "Camila Torres", phone: "+5491155550101", countryOfInterest: "España", stage: "ENQUIRY" as const },
  { name: "Julián Rodríguez", phone: "+573005550102", countryOfInterest: "Canadá", stage: "ENQUIRY" as const },
  { name: "Valentina Gómez", phone: "+5215555550103", countryOfInterest: "Alemania", stage: "DOCUMENTATION" as const },
  { name: "Mateo Fernández", phone: "+56955550104", countryOfInterest: "Portugal", stage: "APPLICATION" as const },
  { name: "Sofía Ramírez", phone: "+51955555105", countryOfInterest: "Irlanda", stage: "VISA" as const },
  { name: "Diego Castro", phone: "+593995550106", countryOfInterest: "España", stage: "ENROLLMENT" as const },
];

async function main() {
  for (const lead of leads) {
    await prisma.lead.upsert({
      where: { phone: lead.phone },
      update: {},
      create: lead,
    });
  }
  console.log(`Seed listo: ${leads.length} leads.`);
}

main()
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
