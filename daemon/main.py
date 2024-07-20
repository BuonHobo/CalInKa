import requests as req
import marshmallow as ma


def main():
    s = req.Session()
    s.post(
        "http://localhost:8888/enter", data={"username": "blue", "password": "admin"}
    )
    r = s.get("http://localhost:8888/api/v2/abilities")
    print(r.text)


if __name__ == "__main__":
    main()
