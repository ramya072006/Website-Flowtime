import mongoose from 'mongoose';
import { config } from '../config';

const wipe = async () => {
  console.log('Connecting to MongoDB...');
  await mongoose.connect(config.mongoUri, {
    serverSelectionTimeoutMS: 30000,
    family: 4,
  });
  console.log('Connected.');

  const db = mongoose.connection.db;
  if (!db) throw new Error('No DB connection');

  const collections = await db.listCollections().toArray();
  console.log(`Found ${collections.length} collections to drop...`);

  for (const col of collections) {
    await db.dropCollection(col.name);
    console.log(`  Dropped: ${col.name}`);
  }

  console.log('\n✅ All data wiped. Fresh database ready.');
  await mongoose.disconnect();
};

wipe().catch((err) => {
  console.error('Wipe failed:', err);
  process.exit(1);
});
