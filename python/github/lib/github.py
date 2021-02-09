#!/usr/bin/env python3
import json
import sys
from urllib.request import urlopen, Request
from typing import Optional


def get_pages(link_headers: str) -> dict:
    return {
        link.split(';')[1].split("=")[1].strip('"'): link.split(';')[0].strip("<").strip(">")
        for link in link_headers.split(',')
    }


def get_links(link_headers: Optional[str] = None) -> dict:
    if link_headers is None:
        return {}
    else:
        return get_pages(link_headers=link_headers)


def decode_response(response) -> dict:
    decoded_response: dict = {}
    try:
        decoded_response = json.loads(response.read())
        return decoded_response
    except Exception as e:
        print("decoded response is empty dict, error was {}".format(e), file=sys.stderr)
    else:
        return decoded_response


def ask_github(
        path: str,
        token: str,
        headers: Optional[dict] = None,
        body: Optional[dict] = None,
        http_verb: str = "GET",
        github_url: str = "https://api.github.com"
) -> dict:
    nothing = {}
    headers = headers or nothing
    body = body or nothing
    default_headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    encoded_body = json.dumps(body).encode("utf-8")
    request = Request(
        url=f"{github_url}{path}",
        method=http_verb,
        headers={**default_headers, **headers},
        data=encoded_body
    )
    response = urlopen(request)
    content = {
        "decoded_response": decode_response(response),
        "response_headers": response.headers,
        "status_code": response.status
    }
    links = get_links(link_headers=content["response_headers"].get("Link"))
    while "next" in links.keys():
        next_response = ask_github(
            path=links["next"].replace(github_url, ''),
            token=token
        )
        content["decoded_response"] += next_response["decoded_response"]
        links = get_links(link_headers=next_response["response_headers"].get("Link"))
    return content
