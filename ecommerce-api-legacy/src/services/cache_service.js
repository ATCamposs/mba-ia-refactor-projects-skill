class CacheService {
    constructor() {
        this._store = {};
    }

    set(key, data) {
        console.log(`[LOG] Salvando no cache: ${key}`);
        this._store[key] = data;
    }

    get(key) {
        return this._store[key];
    }
}

module.exports = { CacheService };
