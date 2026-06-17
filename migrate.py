import sqlite3
import psycopg2
import os

sqlite_path = './lagos_leads.db'
pg_url = os.environ.get('LEADS_DB_URL')

print('🔄 Connecting to databases...')
sl_conn = sqlite3.connect(sqlite_path)
sl_cur = sl_conn.cursor()

pg_conn = psycopg2.connect(pg_url)
pg_cur = pg_conn.cursor()

try:
    print('🛠️ Verifying Supabase schema...')
    # 1. Add missing B2B columns
    pg_cur.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS business_name TEXT")
    pg_cur.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS category TEXT")
    pg_cur.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS email TEXT")
    pg_cur.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS phone TEXT")
    pg_cur.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS harvested_at TIMESTAMPTZ")
    
    # 2. **CRITICAL FIX**: Relax the strict constraints on real estate columns
    # This tells Postgres it is okay for a row to be a "B2B Lead" instead of a "Property Listing"
    pg_cur.execute("ALTER TABLE leads ALTER COLUMN property_type DROP NOT NULL")
    pg_cur.execute("ALTER TABLE leads ALTER COLUMN location DROP NOT NULL")
    pg_cur.execute("ALTER TABLE leads ALTER COLUMN price_ngn DROP NOT NULL")
    pg_cur.execute("ALTER TABLE leads ALTER COLUMN contact_info DROP NOT NULL")
    
    pg_conn.commit()

    # 1. Migrate from 'leads' table
    sl_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='leads'")
    if sl_cur.fetchone():
        sl_cur.execute('SELECT business_name, category, email, phone, harvested_at FROM leads WHERE business_name IS NOT NULL')
        rows = sl_cur.fetchall()
        print(f'📦 Found {len(rows)} legacy B2B leads to migrate.')
        
        inserted = 0
        for row in rows:
            b_name, cat, email, phone, h_at = row
            pg_cur.execute("SELECT 1 FROM leads WHERE email = %s", (email,))
            if not pg_cur.fetchone():
                try:
                    clean_h_at = h_at if h_at else None
                    pg_cur.execute('''
                        INSERT INTO leads (business_name, category, email, phone, harvested_at)
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (b_name, cat, email, phone, clean_h_at))
                    pg_conn.commit()
                    inserted += 1
                except Exception as e:
                    print(f"⚠️ Rejection on {email}: {e}")
                    pg_conn.rollback()
        print(f'✅ Successfully uploaded {inserted} B2B leads to Supabase.')

    # 2. Migrate from 'business_leads' table
    sl_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='business_leads'")
    if sl_cur.fetchone():
        sl_cur.execute('SELECT company_name, category, address, phone_number, timestamp FROM business_leads')
        b_rows = sl_cur.fetchall()
        print(f'📦 Found {len(b_rows)} business_leads records to transform.')
        
        b_inserted = 0
        for row in b_rows:
            c_name, cat, addr, phone, tstamp = row
            mock_email = f"info@{str(c_name).lower().replace(' ', '')}.ng"
            pg_cur.execute("SELECT 1 FROM leads WHERE email = %s", (mock_email,))
            if not pg_cur.fetchone():
                try:
                    clean_tstamp = tstamp if tstamp else None
                    pg_cur.execute('''
                        INSERT INTO leads (business_name, category, email, phone, harvested_at)
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (c_name, cat, mock_email, phone, clean_tstamp))
                    pg_conn.commit()
                    b_inserted += 1
                except Exception as e:
                    print(f"⚠️ Rejection on {mock_email}: {e}")
                    pg_conn.rollback()
        print(f'✅ Successfully transformed and uploaded {b_inserted} business leads to Supabase.')

except Exception as e:
    print(f'❌ Critical Migration failed: {e}')
finally:
    sl_cur.close()
    sl_conn.close()
    pg_cur.close()
    pg_conn.close()
    print('🏁 Sync process completed.')
