-- カルラライブ 受付用デジタルチケット

CREATE TABLE events (
  id                TEXT PRIMARY KEY,             -- URL に入る会のID
  title             TEXT NOT NULL,
  held_on           TEXT NOT NULL,                -- 開催日 YYYY-MM-DD（日本時間）
  time_note         TEXT NOT NULL DEFAULT '',     -- 例：13:00 開場／13:30 開演
  venue             TEXT NOT NULL DEFAULT '',
  capacity          INTEGER NOT NULL DEFAULT 300, -- 会場参加の上限
  stream_url        TEXT NOT NULL DEFAULT '',     -- オンライン参加者に見せる配信のURL
  staff_key         TEXT NOT NULL,                -- 受付スタッフ用のURLに入る鍵
  door_key          TEXT NOT NULL,                -- 受付に置くタグ（NFC・掲示QR）のURLに入る鍵
  door_code         TEXT NOT NULL,                -- 受付で伝える4桁のコード
  reception_open    INTEGER NOT NULL DEFAULT 0,   -- 受付中だけ、タッチとタグで入場できる
  registration_open INTEGER NOT NULL DEFAULT 0,   -- 申込フォームを開けているか
  online_manual     INTEGER,                      -- 配信サービス側の視聴者数（手入力）
  retention_days    INTEGER NOT NULL DEFAULT 30,
  purge_on          TEXT NOT NULL,                -- この日（日本時間）を過ぎたら名簿を消す
  purged_at         TEXT,
  summary_json      TEXT,                         -- 名簿を消すときに残す集計（個人情報なし）
  line_channel_id   TEXT,
  line_secret_enc   TEXT,                         -- LINEログインのチャネルシークレット（暗号化）
  created_at        TEXT NOT NULL
);

CREATE TABLE attendees (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id        TEXT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  token           TEXT NOT NULL UNIQUE,           -- チケットのURLに入る鍵
  name            TEXT NOT NULL,
  email           TEXT NOT NULL DEFAULT '',
  org             TEXT NOT NULL DEFAULT '',
  kind            TEXT NOT NULL DEFAULT 'venue' CHECK (kind IN ('venue', 'online')),
  source          TEXT NOT NULL,                  -- csv / form / line / staff / door
  line_user_id    TEXT,
  line_friend     INTEGER NOT NULL DEFAULT 0,     -- 申込の時点で友だちだった
  line_friend_new INTEGER NOT NULL DEFAULT 0,     -- この申込で新しく友だちになった
  checked_in_at   TEXT,
  checkin_method  TEXT,                           -- qr / touch / door / staff
  watched_at      TEXT,                           -- チケットから配信を開いた時刻
  mailed_at       TEXT,
  code_fails      INTEGER NOT NULL DEFAULT 0,     -- 4桁コードの入力まちがいの回数
  created_at      TEXT NOT NULL
);

CREATE INDEX attendees_event ON attendees (event_id, id);
CREATE INDEX attendees_email ON attendees (event_id, email);
CREATE UNIQUE INDEX attendees_line ON attendees (event_id, line_user_id) WHERE line_user_id IS NOT NULL;
