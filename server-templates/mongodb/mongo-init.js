console.log('initializing DB...');

db.createUser({
  user: 'admin',
  pwd: 'password',
  roles: [
    {
      role: 'readWrite',
      db: 'mcTemplatesDb',
    },
  ],
});

db = db.getSiblingDB('mcTemplatesDb');

db.createCollection('templates');

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

console.log('initializing DB complete');
