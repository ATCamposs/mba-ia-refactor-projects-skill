const { dbRun } = require('./db');

async function logCheckout(db, courseId, userId) {
    await dbRun(db, "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))", [`Checkout curso ${courseId} por ${userId}`]);
}

module.exports = { logCheckout };
