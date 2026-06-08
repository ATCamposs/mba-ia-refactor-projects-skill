function errorHandler(err, req, res, next) {
    console.error(err);
    const status = err.status || 500;
    const message = err.message || 'Erro interno';
    if (res.headersSent) {
        return next(err);
    }
    if (typeof message === 'string' && !message.startsWith('{')) {
        return res.status(status).send(message);
    }
    return res.status(status).json({ error: message });
}

module.exports = { errorHandler };
