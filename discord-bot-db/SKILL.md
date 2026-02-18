---
name: discord-bot-db
description: "Manages the TechFren Discord bot database. Use when asked to download, query, inspect, or analyze the Discord bot database, Discord messages, user points, channel summaries, or anything related to the techfren-discord-bot data. Also use when asked for a daily summary, yesterday's summary, or Discord community recap."
---

# Discord Bot Database Management

## Overview
This skill provides workflows for accessing and querying the TechFren Discord bot's SQLite database hosted on an AWS EC2 server. The bot tracks Discord messages, channel summaries, user points, and custom role colors.

The bot runs a daily summarization at midnight UTC — it summarizes all messages from the past 24 hours per channel, stores them in `channel_summaries`, then **deletes raw messages older than 24 hours**. This means the `channel_summaries` table is the primary historical archive.

## Server Details
- **Host:** `52.90.156.99` (AWS EC2, Ubuntu)
- **SSH Key:** `discord-bot.pem` (located in the `techfren-discord-bot` repo root)
- **Remote DB Path:** `/home/ubuntu/techfren-discord-bot/data/discord_messages.db`
- **Local Repo:** `~/Development/techfren-discord-bot`
- **Local DB Copy:** `~/Documents/agent-notes/discord_messages.db`

## Workflow 1: Download Fresh Database Copy

Always download a fresh copy before querying to ensure up-to-date data.

```bash
cd ~/Development/techfren-discord-bot
scp -i discord-bot.pem ubuntu@52.90.156.99:/home/ubuntu/techfren-discord-bot/data/discord_messages.db ~/Documents/agent-notes/discord_messages.db
```

## Workflow 2: Query the Database

Use `sqlite3` to query the local copy:

```bash
sqlite3 ~/Documents/agent-notes/discord_messages.db "YOUR QUERY HERE"
```

## Workflow 3: SSH to Server

For live inspection or bot management:

```bash
cd ~/Development/techfren-discord-bot
ssh -i discord-bot.pem ubuntu@52.90.156.99
```

## Workflow 4: Get Yesterday's Community Summary

Use this when asked for a daily recap, yesterday's summary, or what happened in the Discord. Always download fresh first (Workflow 1), then run:

### Step 1: Download fresh DB
```bash
cd ~/Development/techfren-discord-bot
scp -i discord-bot.pem ubuntu@52.90.156.99:/home/ubuntu/techfren-discord-bot/data/discord_messages.db ~/Documents/agent-notes/discord_messages.db
```

### Step 2: Get yesterday's date and fetch all channel summaries for that date
```bash
YESTERDAY=$(date -v-1d +%Y-%m-%d)
echo "=== Summaries for $YESTERDAY ==="
sqlite3 ~/Documents/agent-notes/discord_messages.db "SELECT channel_name, message_count, active_users, active_users_list, summary_text FROM channel_summaries WHERE date='$YESTERDAY' ORDER BY message_count DESC;"
```

### Step 3: If yesterday has no summaries, find the most recent date that does
```bash
sqlite3 ~/Documents/agent-notes/discord_messages.db "SELECT date, COUNT(*) as channels, SUM(message_count) as total_msgs FROM channel_summaries GROUP BY date ORDER BY date DESC LIMIT 5;"
```
Then query that date instead.

### Step 4: Also grab any current raw messages not yet summarized (today's activity so far)
```bash
sqlite3 ~/Documents/agent-notes/discord_messages.db "SELECT channel_name, COUNT(*) as msgs, GROUP_CONCAT(DISTINCT author_name) as users FROM messages WHERE is_bot=0 GROUP BY channel_name ORDER BY msgs DESC;"
```

### Step 5: Compose a natural language recap
Combine the channel summaries into a cohesive daily recap covering:
- **Overall activity**: total messages, active channels, active users
- **Key discussions per channel**: main topics, notable quotes, links shared
- **Top contributors**: who was most active
- **Highlights**: anything interesting, funny, or notable

Present it in a conversational tone suitable for reading aloud or posting.

## Workflow 5: Get Summary for a Specific Date

Same as Workflow 4 but replace `$YESTERDAY` with the target date:

```bash
sqlite3 ~/Documents/agent-notes/discord_messages.db "SELECT channel_name, message_count, active_users, active_users_list, summary_text FROM channel_summaries WHERE date='2025-06-20' ORDER BY message_count DESC;"
```

## Workflow 6: Weekly/Multi-day Trend Analysis

```bash
sqlite3 ~/Documents/agent-notes/discord_messages.db "SELECT date, COUNT(*) as channels, SUM(message_count) as total_msgs FROM channel_summaries WHERE date >= date('now', '-7 days') GROUP BY date ORDER BY date DESC;"
```

## Database Schema

### messages (primary table — only holds last ~24h of data)
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT PK | Discord message ID |
| author_id | TEXT | Discord user ID |
| author_name | TEXT | Display name |
| channel_id | TEXT | Channel ID |
| channel_name | TEXT | Channel name |
| guild_id | TEXT | Server ID |
| guild_name | TEXT | Server name |
| content | TEXT | Message text |
| created_at | TIMESTAMP | When sent |
| is_bot | INTEGER | 1 if bot message |
| is_command | INTEGER | 1 if command |
| command_type | TEXT | Type of command |
| scraped_url | TEXT | URL found in message |
| scraped_content_summary | TEXT | AI summary of URL |
| scraped_content_key_points | TEXT | Key points from URL |
| image_descriptions | TEXT | AI descriptions of images |
| reply_to_message_id | TEXT | Parent message ID |

**Indexes:** author_id, channel_id, guild_id, created_at, is_command, reply_to_message_id

### channel_summaries (historical archive — primary data source for past activity)
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| channel_id | TEXT | Channel ID |
| channel_name | TEXT | Channel name |
| guild_id | TEXT | Server ID |
| guild_name | TEXT | Server name |
| date | TEXT | Summary date |
| summary_text | TEXT | AI-generated summary |
| message_count | INTEGER | Messages that day |
| active_users | INTEGER | User count |
| active_users_list | TEXT | List of active users |
| created_at | TIMESTAMP | When generated |
| metadata | TEXT | Extra metadata |

**Indexes:** channel_id, date

### user_points
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| author_id | TEXT | Discord user ID |
| author_name | TEXT | Display name |
| guild_id | TEXT | Server ID |
| total_points | INTEGER | Current point total |
| last_updated | TIMESTAMP | Last change |

**Unique constraint:** (author_id, guild_id)

### daily_point_awards
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| author_id | TEXT | Discord user ID |
| author_name | TEXT | Display name |
| guild_id | TEXT | Server ID |
| date | TEXT | Award date |
| points_awarded | INTEGER | Points given |
| reason | TEXT | Why awarded |
| created_at | TIMESTAMP | When awarded |

**Unique constraint:** (author_id, guild_id, date)

### user_role_colors
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| author_id | TEXT | Discord user ID |
| author_name | TEXT | Display name |
| guild_id | TEXT | Server ID |
| role_id | TEXT | Discord role ID |
| color_hex | TEXT | Hex color code |
| color_name | TEXT | Human-readable color |
| points_per_day | INTEGER | Daily cost |
| started_at | TIMESTAMP | When started |
| last_charged_date | TEXT | Last charge date |
| created_at | TIMESTAMP | When created |

**Unique constraint:** (author_id, guild_id)

## Common Queries

### Most active users
```sql
SELECT author_name, COUNT(*) as msg_count FROM messages WHERE is_bot = 0 GROUP BY author_id ORDER BY msg_count DESC LIMIT 10;
```

### Messages per channel
```sql
SELECT channel_name, COUNT(*) as msg_count FROM messages GROUP BY channel_id ORDER BY msg_count DESC;
```

### Recent messages
```sql
SELECT author_name, content, created_at FROM messages ORDER BY created_at DESC LIMIT 20;
```

### Top points leaderboard
```sql
SELECT author_name, total_points FROM user_points ORDER BY total_points DESC LIMIT 10;
```

### Daily activity
```sql
SELECT DATE(created_at) as day, COUNT(*) as msgs FROM messages GROUP BY day ORDER BY day DESC LIMIT 14;
```

### Messages with scraped URLs
```sql
SELECT author_name, scraped_url, scraped_content_summary FROM messages WHERE scraped_url IS NOT NULL ORDER BY created_at DESC LIMIT 10;
```

### Channel summaries for a date range
```sql
SELECT date, channel_name, message_count, active_users, SUBSTR(summary_text, 1, 200) as preview FROM channel_summaries WHERE date BETWEEN '2025-06-01' AND '2025-06-30' ORDER BY date DESC, message_count DESC;
```

## Best Practices

1. **Always download fresh** before analysis — the local copy may be stale
2. **Use LIMIT** on queries to avoid dumping thousands of rows
3. **Quote strings** properly in SQL — use single quotes for values
4. **Check is_bot = 0** when analyzing human activity
5. **The SSH key** must be accessed from the repo directory since it's a relative path
6. **For historical data, use channel_summaries** — the messages table only has the last ~24h
7. **Summaries run at midnight UTC** — yesterday's summary may not exist yet if it hasn't run

## Troubleshooting

- **Permission denied on SSH:** Make sure you're in the repo dir and the key has correct permissions (`chmod 400 discord-bot.pem`)
- **Connection timeout:** The EC2 instance may be stopped — check AWS console
- **Database locked:** Another process is writing — wait and retry, or download a copy
- **No summaries for yesterday:** The midnight UTC job may not have run yet — check today's raw messages instead, or query the most recent available summary date
