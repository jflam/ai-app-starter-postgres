import express from 'express';
import cors from 'cors';
import { prisma, getRandomFortune } from './db';

const app = express();
const PORT = process.env.PORT || 4000;

app.use(cors());

app.get('/api/fortunes/random', async (_req, res) => {
  try {
    const fortune = await getRandomFortune();
    if (!fortune) return res.status(404).json({ error: 'No fortunes found.' });
    res.json(fortune);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error.' });
  }
});

const server = app.listen(PORT, () => {
  console.log(`🪄 Fortune API listening at http://localhost:${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  server.close(async () => {
    await prisma.$disconnect();
    console.log('Server shut down gracefully');
  });
});
