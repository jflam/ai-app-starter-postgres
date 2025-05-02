import { PrismaClient } from '@prisma/client';

export const prisma = new PrismaClient();

export async function getRandomFortune() {
  const count = await prisma.fortune.count();
  const skip = Math.floor(Math.random() * count);
  return prisma.fortune.findFirst({ skip });
}
