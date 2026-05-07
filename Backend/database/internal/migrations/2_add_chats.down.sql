DROP INDEX IF EXISTS idx_queries_chat_id_created_at;
DROP INDEX IF EXISTS idx_queries_user_id_created_at;
DROP INDEX IF EXISTS idx_chats_user_id_updated_at;

ALTER TABLE queries DROP COLUMN IF EXISTS prompt;
ALTER TABLE queries DROP COLUMN IF EXISTS chat_id;

DROP TABLE IF EXISTS chats;
