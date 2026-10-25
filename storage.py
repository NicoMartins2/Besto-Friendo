"""Configuração por servidor; credenciais nunca são gravadas no SQLite."""
from contextlib import closing
import json
import sqlite3
from pathlib import Path

DEFAULTS = {
    'provider': 'openai', 'model': 'gpt-4o-mini',
    'agent': 'Você é BestoFriendo, um assistente prestativo. Responda em português brasileiro, salvo pedido contrário.',
    'tone': 'amigável e direto', 'configured': False,
}


class ConfigStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('CREATE TABLE IF NOT EXISTS configs (guild_id INTEGER PRIMARY KEY, data TEXT NOT NULL)')

    def get(self, guild_id: int) -> dict:
        with closing(sqlite3.connect(self.path)) as db, db:
            row = db.execute('SELECT data FROM configs WHERE guild_id = ?', (guild_id,)).fetchone()
        return {**DEFAULTS, **(json.loads(row[0]) if row else {})}

    def update(self, guild_id: int, **changes) -> dict:
        if changes.keys() - DEFAULTS.keys():
            raise ValueError('Campo de configuração desconhecido; chaves de API pertencem ao .env.')
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT data FROM configs WHERE guild_id = ?', (guild_id,)).fetchone()
            config = {**DEFAULTS, **(json.loads(row[0]) if row else {}), **changes}
            db.execute('INSERT INTO configs VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET data=excluded.data',
                       (guild_id, json.dumps(config, ensure_ascii=False)))
        return config
