-- AlterTable
ALTER TABLE "Lead" ADD COLUMN     "needsHuman" BOOLEAN NOT NULL DEFAULT false;

-- AlterTable
ALTER TABLE "Message" ADD COLUMN     "confidence" DOUBLE PRECISION,
ADD COLUMN     "intent" TEXT;

