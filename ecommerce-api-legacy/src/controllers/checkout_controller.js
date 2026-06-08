const courseModel = require('../models/course_model');
const userModel = require('../models/user_model');
const enrollmentModel = require('../models/enrollment_model');
const paymentModel = require('../models/payment_model');
const auditLogModel = require('../models/audit_log_model');
const { processPayment } = require('../services/payment_service');
const { badCrypto } = require('../utils/crypto');

function createCheckoutController(db, cacheService) {
    async function checkout(req, res, next) {
        try {
            const userName = req.body.usr;
            const email = req.body.eml;
            const password = req.body.pwd;
            const courseId = req.body.c_id;
            const cardNumber = req.body.card;

            if (!userName || !email || !courseId || !cardNumber) {
                return res.status(400).send('Bad Request');
            }

            const course = await courseModel.findActiveById(db, courseId);
            if (!course) {
                return res.status(404).send('Curso não encontrado');
            }

            let user = await userModel.findByEmail(db, email);
            let userId;

            if (!user) {
                const passwordHash = badCrypto(password || '123456');
                userId = await userModel.create(db, userName, email, passwordHash);
            } else {
                userId = user.id;
            }

            console.log('[LOG] Processando pagamento de checkout');
            const { status } = processPayment(cardNumber);

            if (status === 'DENIED') {
                return res.status(400).send('Pagamento recusado');
            }

            const enrollmentId = await enrollmentModel.create(db, userId, courseId);
            await paymentModel.create(db, enrollmentId, course.price, status);
            await auditLogModel.logCheckout(db, courseId, userId);

            cacheService.set(`last_checkout_${userId}`, course.title);

            return res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
        } catch (err) {
            if (err.message && err.message.includes('UNIQUE')) {
                return res.status(500).send('Erro ao criar usuário');
            }
            return next(err);
        }
    }

    return { checkout };
}

module.exports = { createCheckoutController };
