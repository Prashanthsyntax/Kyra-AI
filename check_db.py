# check_db.py  ← save in KyraAI root folder
from db import get_session, Message, DigestLog, ConversationMemory, FactCategory, CalendarLog

session = get_session()

print('='*60)
print('CONVERSATION MEMORY')
print('='*60)
rows = session.query(ConversationMemory).order_by(ConversationMemory.id.asc()).all()
if rows:
    for r in rows:
        print(f'[{r.created_at}] {r.role.upper()}: {r.content[:100]}')
else:
    print('Empty.')

print()
print('='*60)
print('MESSAGES')
print('='*60)
rows = session.query(Message).order_by(Message.timestamp.asc()).all()
if rows:
    for m in rows:
        print(f'[{m.timestamp}] {m.sender}: {m.body[:100]}')
else:
    print('Empty.')

print()
print('='*60)
print('DIGEST LOG')
print('='*60)
rows = session.query(DigestLog).order_by(DigestLog.sent_at.asc()).all()
if rows:
    for d in rows:
        print(f'[{d.sent_at}] {d.content[:300]}')
        print('---')
else:
    print('Empty.')

print()
print('='*60)
print('CALENDAR LOG')
print('='*60)
rows = session.query(CalendarLog).order_by(CalendarLog.created_at.asc()).all()
if rows:
    for c in rows:
        print(f'[{c.created_at}] {c.title} | {c.start_time} → {c.end_time}')
else:
    print('Empty.')

print()
print('='*60)
print('FACT POINTER')
print('='*60)
row = session.query(FactCategory).first()
categories = ['AI','Politics','Science','Space','History','Tech','Psychology']
if row:
    print(f'Pointer: {row.pointer} → Next: {categories[row.pointer % len(categories)]}')
else:
    print('Empty.')

session.close()