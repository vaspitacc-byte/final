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

# ---------------- Singleton ----------------
db = DatabaseManager()
