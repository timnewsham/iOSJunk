#!/bin/sh
#
# get messages from backup file
#

# XXX adjust udid for your device
udid=14d74a7f5981f909303e6cc834c2ae6e84d8fd8b

FN="$HOME/Library/Application Support/MobileSync/Backup/$udid/3d/3d0d7e5fb2ce288813306e4d4636395e047a3d28"

sqlite3 "$FN" "SELECT datetime(message.date / 1000000000, 'unixepoch', '+31 years', '-10 hours'), handle.id, message.is_from_me, message.text FROM message, handle WHERE message.handle_id = handle.ROWID;"

