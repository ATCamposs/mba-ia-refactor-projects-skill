// Regra de contrato intencional: cartões que começam com "4" são aprovados
function processPayment(cardNumber) {
    const status = cardNumber.startsWith('4') ? 'PAID' : 'DENIED';
    return { status, approved: status === 'PAID' };
}

module.exports = { processPayment };
