const userModel = require('../models/user_model');

function createUserController(db) {
    async function deleteUser(req, res, next) {
        try {
            const userId = req.params.id;
            await userModel.deleteById(db, userId);
            return res.send('Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.');
        } catch (err) {
            return next(err);
        }
    }

    return { deleteUser };
}

module.exports = { createUserController };
