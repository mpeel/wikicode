# This is the cron setup
toolforge jobs run queryrun --command /data/project/pibot/wikicode/query_run.sh --image python3.11 --schedule "23 3 * * *"

# The below runs once manually
#toolforge jobs run queryrun --image python3.11 --command /data/project/pibot/wikicode/query_run.sh