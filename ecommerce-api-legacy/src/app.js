const express = require('express');
const config = require('./config/settings');
const { createDatabase, initDb } = require('./models/db');
const { CacheService } = require('./services/cache_service');
const { createCheckoutController } = require('./controllers/checkout_controller');
const { createAdminController } = require('./controllers/admin_controller');
const { createUserController } = require('./controllers/user_controller');
const { createCheckoutRoutes } = require('./views/checkout_routes');
const { createAdminRoutes } = require('./views/admin_routes');
const { createUserRoutes } = require('./views/user_routes');
const { errorHandler } = require('./middlewares/error_handler');

async function bootstrap() {
    const app = express();
    app.use(express.json());

    const db = createDatabase();
    await initDb(db);

    const cacheService = new CacheService();
    const checkoutController = createCheckoutController(db, cacheService);
    const adminController = createAdminController(db);
    const userController = createUserController(db);

    app.use('/api', createCheckoutRoutes(checkoutController));
    app.use('/api/admin', createAdminRoutes(adminController));
    app.use('/api', createUserRoutes(userController));
    app.use(errorHandler);

    app.listen(config.port, () => {
        console.log(`Frankenstein LMS rodando na porta ${config.port}...`);
    });
}

bootstrap().catch((err) => {
    console.error('Falha ao iniciar aplicação:', err);
    process.exit(1);
});
