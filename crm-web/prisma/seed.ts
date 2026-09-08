import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

const leads = [
  { name: "Camila Torres", phone: "+54 9 11 5555-0101", countryOfInterest: "España", stage: "ENQUIRY" as const },
  { name: "Julián Rodríguez", phone: "+57 300 555 0102", countryOfInterest: "Canadá", stage: "ENQUIRY" as const },
  { name: "Valentina Gómez", phone: "+52 1 55 5555 0103", countryOfInterest: "Alemania", stage: "DOCUMENTATION" as const },
  { name: "Mateo Fernández", phone: "+56 9 5555 0104", countryOfInterest: "Portugal", stage: "APPLICATION" as const },
  { name: "Sofía Ramírez", phone: "+51 955 555 105", countryOfInterest: "Irlanda", stage: "VISA" as const },
  { name: "Diego Castro", phone: "+593 99 555 0106", countryOfInterest: "España", stage: "ENROLLMENT" as const },
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
