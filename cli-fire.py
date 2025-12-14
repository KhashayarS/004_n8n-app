#!/usr/bin/env python
import fire
from routers.auth import create_token


if __name__ == "__main__":
    fire.Fire(create_token)
