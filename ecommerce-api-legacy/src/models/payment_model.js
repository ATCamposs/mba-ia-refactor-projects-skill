const { dbRun } = require('./db');

async function create(db, enrollmentId, amount, status) {
    await dbRun(db, 'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [enrollmentId, amount, status]);
}

module.exports = { create };
