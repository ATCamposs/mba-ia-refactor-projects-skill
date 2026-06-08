const { dbGet, dbRun } = require('./db');

async function findByEmail(db, email) {
    return dbGet(db, 'SELECT id FROM users WHERE email = ?', [email]);
}

async function create(db, name, email, passwordHash) {
    const result = await dbRun(db, 'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, passwordHash]);
    return result.lastID;
}

async function deleteById(db, userId) {
    return dbRun(db, 'DELETE FROM users WHERE id = ?', [userId]);
}

module.exports = { findByEmail, create, deleteById };
