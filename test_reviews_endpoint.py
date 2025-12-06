from app import app
import json

with app.test_client() as client:
    resp = client.get('/product/5/reviews?page=1&sort=recent&rating=all')
    print(f'GET /product/5/reviews: {resp.status_code}')
    if resp.status_code == 200:
        data = json.loads(resp.data)
        print(f'Success: {data.get("success")}')
        print(f'Total reviews: {data.get("stats", {}).get("total_reviews")}')
        if data.get('reviews'):
            print(f'Reviews returned: {len(data["reviews"])}')
            if data['reviews']:
                print(f'First review user_name: {data["reviews"][0].get("user_name")}')
    else:
        print(f'Error: {resp.data.decode()[:300]}')
