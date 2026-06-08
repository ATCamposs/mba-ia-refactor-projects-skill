module.exports = {
    dbUser: process.env.DB_USER || 'admin_master',
    dbPass: process.env.DB_PASS || 'dev-pass-change-me',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || 'pk_test_dev',
    smtpUser: process.env.SMTP_USER || 'no-reply@fullcycle.com.br',
    port: parseInt(process.env.PORT || '3000', 10),
};
