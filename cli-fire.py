#!/usr/bin/env python
import fire
from routers.auth import create_access_token


if __name__ == "__main__":
    fire.Fire(create_access_token)
