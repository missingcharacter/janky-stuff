#!/usr/bin/env python3
import json
import logging
import sys
from urllib.request import urlopen, Request
from typing import Optional


class Github:
    log = logging.getLogger(__name__)


    def __init__(
        self,
        github_url: str = "https://api.github.com"
    ) -> None:
        self.github_url = github_url


    def ask(
        self,
        path: str,
        token: str,
        headers: dict = {},
        body: dict = {},
        http_verb: str = "GET"
    ) -> dict:
        default_headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {token}"
        }
        encoded_body = json.dumps(body).encode("utf-8")
        full_path = f"{self.github_url}{path}"
        request = Request(
            url=full_path,
            method=http_verb,
            headers={**default_headers, **headers},
            data=encoded_body
        )
        response = urlopen(request)
        self.log.debug("Response code to %s on %s was: [%s]", http_verb, full_path, response.status)
        content = self._decode_response(response)
        links = self._get_links(link_headers=response.headers.get("Link"))
        while "next" in links.keys():
            next_request = Request(
                url=links["next"],
                method=http_verb,
                headers={**default_headers, **headers},
                data=encoded_body
            )
            next_response = urlopen(next_request)
            content += self._decode_response(next_response)
            links = self._get_links(link_headers=next_response.headers.get("Link"))
        return content


    def _decode_response(self, response) -> dict:
        decoded_response: dict = {}
        try:
            decoded_response = json.loads(response.read())
        except Exception as e:
            self.log.debug("decoded response is empty dict, error was [%s]", e)
        finally:
            return decoded_response


    def _get_links(self, link_headers: Optional[str] = None) -> dict:
        if link_headers is None:
            return {}
        else:
            return self._get_pages(link_headers=link_headers)


    def _get_pages(self, link_headers: str) -> dict:
        return {
            self._get_link_key(link): self._get_link_value(link)
            for link in link_headers.split(',')
        }


    def _get_link_key(self, link: str) -> str:
        return self._remove_unwanted_characters(link.split(';')[1].split("=")[1])

    def _get_link_value(self, link: str) -> str:
        return self._remove_unwanted_characters(link.split(';')[0])

    def _remove_unwanted_characters(self, string_to_clean: str) -> str:
        self.log.debug("String to clean is: [%s]", string_to_clean)
        unwanted_characters = ["<", ">", " ", '"']
        for character in unwanted_characters:
            string_to_clean = string_to_clean.replace(character, '')
        self.log.debug("Cleaned up string is: [%s]", string_to_clean)
        return string_to_clean
