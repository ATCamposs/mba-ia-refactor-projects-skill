const express = require('express');

function createAdminRoutes(adminController) {
    const router = express.Router();
    router.get('/financial-report', (req, res, next) => adminController.financialReport(req, res, next));
    return router;
}

module.exports = { createAdminRoutes };
