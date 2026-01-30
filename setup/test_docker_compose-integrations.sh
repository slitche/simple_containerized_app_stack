docker cp ./generate_sample_users.py $(pwd | awk -F'/' '{print $NF}')-app-1:/app/generate_sample_users.py
docker compose exec app python generate_sample_users.py
token=$(curl -X POST "http://<private_IP>:8000/login?username=alice&password=password123" | grep -oP '(?<="token":")[^"]+') #check using a sample user
curl "http://<private_IP>:8000/status?token=${token}"
echo ""