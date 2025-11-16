import sys
import yaml
from utils import class_db

try:
    with open("scrapper/utils/config_era.yaml", "r") as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    print("Config file not found")
    sys.exit()


try:
    db_instace = class_db.DbMethods()
    create_cursor = db_instace.create_cursor(db_name=config["db_name"], user=config["user"],
                                            password=config["password"], port=config["port"])

    rows = db_instace.query_data(config["intersect_admin_levels"])

    for row in rows:

        lat = row[0]
        lng = row[1]

        params = row + (lng, lat)
        db_instace.execute_query(config["insert_query"], params, commit=True)

    db_instace.close()
except Exception as e:
    print(f"Please check {e}")
