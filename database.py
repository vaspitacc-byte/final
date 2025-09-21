# database.py
import aiosqlite
from config import DB_PATH

class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    async def initialize_database(self):
        async with aiosqlite.connect(self.db_path) as db:
            # ---------------- Server Config ----------------
            await db.execute('''
                CREATE TABLE IF NOT EXISTS server_config (
                    guild_id INTEGER PRIMARY KEY,
                    admin_role_id INTEGER,
                    staff_role_id INTEGER,
                    helper_role_id INTEGER,
                    viewer_role_id INTEGER,
                    blocked_role_id INTEGER,
                    reward_role_id INTEGER,
                    ticket_category_id INTEGER,
                    transcript_channel_id INTEGER,
                    guidelines_channel_id INTEGER,
                    requestor_points INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # ---------------- Admin Roles ----------------
            await db.execute('''
                CREATE TABLE IF NOT EXISTS admin_roles (
                    guild_id INTEGER,
                    role_id INTEGER,
                    PRIMARY KEY (guild_id, role_id)
                )
            ''')

            # ---------------- Tickets ----------------
            await db.execute('''
                CREATE TABLE IF NOT EXISTS tickets (
                    guild_id INTEGER,
                    channel_id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    category TEXT,
                    message_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            await db.execute('''
                CREATE TABLE IF NOT EXISTS active_tickets (
                    guild_id INTEGER,
                    channel_id INTEGER PRIMARY KEY,
                    creator_id INTEGER,
                    ticket_type TEXT,
                    ticket_number INTEGER,
                    helpers TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # ---------------- Points ----------------
            await db.execute('''
                CREATE TABLE IF NOT EXISTS point_values (
                    guild_id INTEGER,
                    ticket_type TEXT,
                    points INTEGER,
                    PRIMARY KEY (guild_id, ticket_type)
                )
            ''')

            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_points (
                    guild_id INTEGER,
                    user_id INTEGER,
                    points INTEGER DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            ''')

            # ---------------- Helper Slots ----------------
            await db.execute('''
                CREATE TABLE IF NOT EXISTS helper_slots (
                    guild_id INTEGER,
                    ticket_type TEXT,
                    slots INTEGER,
                    PRIMARY KEY (guild_id, ticket_type)
                )
            ''')

            # ---------------- Custom Commands ----------------
            await db.execute('''
                CREATE TABLE IF NOT EXISTS custom_commands (
                    guild_id INTEGER,
                    command_name TEXT,
                    content TEXT NOT NULL,
                    PRIMARY KEY (guild_id, command_name)
                )
            ''')

            # ---------------- Custom Command Attachments ----------------
            await db.execute('''
                CREATE TABLE IF NOT EXISTS custom_command_attachments (
                    guild_id INTEGER,
                    command_name TEXT,
                    attachment_url TEXT,
                    PRIMARY KEY (guild_id, command_name, attachment_url)
                )
            ''')

            # ---------------- Embed Templates ----------------
            await db.execute('''
                CREATE TABLE IF NOT EXISTS embed_templates (
                    guild_id INTEGER,
                    template_name TEXT,
                    title TEXT,
                    description TEXT,
                    color INTEGER,
                    PRIMARY KEY (guild_id, template_name)
                )
            ''')

            await db.execute('''
                CREATE TABLE IF NOT EXISTS embed_fields (
                    guild_id INTEGER,
                    template_name TEXT,
                    field_name TEXT,
                    field_value TEXT,
                    inline INTEGER DEFAULT 0,
                    PRIMARY KEY (guild_id, template_name, field_name)
                )
            ''')

            # ---------------- Talk Logs ----------------
            await db.execute('''
                CREATE TABLE IF NOT EXISTS talk_logs (
                    guild_id INTEGER,
                    channel_id INTEGER,
                    user_id INTEGER,
                    content TEXT,
                    embeds TEXT,
                    attachments TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            await db.commit()

    # ===================== Server Config =====================
    async def get_server_config(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT * FROM server_config WHERE guild_id = ?', (guild_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None

    async def update_server_config(self, guild_id: int, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT guild_id FROM server_config WHERE guild_id = ?', (guild_id,)) as cursor:
                exists = await cursor.fetchone()
            if exists:
                set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
                values = list(kwargs.values()) + [guild_id]
                await db.execute(f'UPDATE server_config SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE guild_id = ?', values)
            else:
                columns = ['guild_id'] + list(kwargs.keys())
                placeholders = ', '.join(['?' for _ in columns])
                values = [guild_id] + list(kwargs.values())
                await db.execute(f'INSERT INTO server_config ({", ".join(columns)}) VALUES ({placeholders})', values)
            await db.commit()

    # ===================== Custom Commands =====================
    async def get_custom_command(self, guild_id: int, command_name: str):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT content FROM custom_commands WHERE guild_id = ? AND command_name = ?', (guild_id, command_name)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                command_data = {'content': row[0], 'attachments': []}
                # Fetch attachments
                async with db.execute('SELECT attachment_url FROM custom_command_attachments WHERE guild_id = ? AND command_name = ?', (guild_id, command_name)) as c2:
                    rows2 = await c2.fetchall()
                    command_data['attachments'] = [r[0] for r in rows2] if rows2 else []
                return command_data

    async def set_custom_command(self, guild_id: int, command_name: str, content: str, attachments: list = None):
        attachments = attachments or []
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('INSERT OR REPLACE INTO custom_commands (guild_id, command_name, content) VALUES (?, ?, ?)', (guild_id, command_name, content))
            # Clear old attachments
            await db.execute('DELETE FROM custom_command_attachments WHERE guild_id = ? AND command_name = ?', (guild_id, command_name))
            for url in attachments:
                await db.execute('INSERT INTO custom_command_attachments (guild_id, command_name, attachment_url) VALUES (?, ?, ?)', (guild_id, command_name, url))
            await db.commit()

    # ===================== Talk Logs =====================
    async def log_talk_message(self, guild_id: int, channel_id: int, user_id: int, content: str, embeds: list, attachments: list):
        embeds_str = str(embeds)  # Save as string
        attachments_str = ",".join(attachments) if attachments else ""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('INSERT INTO talk_logs (guild_id, channel_id, user_id, content, embeds, attachments) VALUES (?, ?, ?, ?, ?, ?)',
                             (guild_id, channel_id, user_id, content, embeds_str, attachments_str))
            await db.commit()


# ---------------- Singleton ----------------
db = DatabaseManager()
