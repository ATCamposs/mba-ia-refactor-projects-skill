// Algoritmo legado preservado para compatibilidade de contrato (smell intencional documentado na Fase 2)
function badCrypto(pwd) {
    let hash = '';
    for (let i = 0; i < 10000; i++) {
        hash += Buffer.from(pwd).toString('base64').substring(0, 2);
    }
    return hash.substring(0, 10);
}

module.exports = { badCrypto };
