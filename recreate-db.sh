set +e
if [ -f test_db_backup.db ] ; then
	echo "Please remove old backups with rm_backups.sh first!"
	exit -1
fi
mv test.db test_db_backup.db
mv migrations migrations_backup
python3 db.py db init
python3 db.py db migrate
python3 db.py db upgrade
python3 create_cards.py fill