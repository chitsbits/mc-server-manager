db.createUser({
  user: 'admin',
  pwd: 'password',
  roles: [
    {
      role: 'readWrite',
      db: 'minecraftServersDB',
    },
  ],
});

db = db.getSiblingDB('minecraftServersDB');

db.createCollection('serverTemplates');

db.serverTemplates.createIndex({ templateName: 1 }, { unique: true });

db.serverTemplates.insertMany([
  {
    templateName: 'Survival Mode',
    description: 'Default survival mode template.',
    worldType: 'NORMAL',
    difficulty: 'EASY',
    mods: [],
  },
  {
    templateName: 'Creative Mode',
    description: 'Unleash your creativity with unlimited resources.',
    worldType: 'CREATIVE',
    difficulty: 'PEACEFUL',
    mods: ['BuildCraft', 'IndustrialCraft'],
  },
  // Add more templates as needed
]);
