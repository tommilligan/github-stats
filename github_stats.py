import argparse
import logging
import os
from datetime import datetime
from typing import Optional

import jinja2
from dotenv import load_dotenv
from github import Github, NamedUser
from pydantic import BaseModel

_log = logging.getLogger(__file__)


class UserStats(BaseModel):
    created_at: datetime
    followers: int
    following: int
    hireable: Optional[bool]
    login: str
    name: Optional[str]
    private_gists: Optional[int]
    public_gists: int
    public_repos: int
    total_private_repos: Optional[int]

    starred: int

    @staticmethod
    def from_user(user: NamedUser) -> "UserStats":
        starred = sum(1 for _ in user.get_starred())
        return UserStats(
            created_at=user.created_at,
            email=user.email,
            followers=user.followers,
            following=user.following,
            hireable=user.hireable,
            login=user.login,
            name=user.name,
            private_gists=user.private_gists,
            public_gists=user.public_gists,
            public_repos=user.public_repos,
            role=user.role,
            total_private_repos=user.total_private_repos,
            starred=starred,
        )


def run_dump(args: argparse.Namespace) -> None:
    """Entrypoint for dumping user stats from github"""

    github_token = os.getenv("GITHUB_TOKEN")
    if github_token is None:
        _log.warning(
            "No github token set. You are unauthenticated and may be rate-limited."
        )
    github_client = Github(github_token)

    _log.info("Fetching %d users from github", len(args.logins))
    users = [
        UserStats.from_user(github_client.get_user(login)) for login in args.logins
    ]
    _log.info("Writing stats to '%s'", args.output)
    with open(args.output, "w") as fh:
        for user in users:
            fh.write(user.json())
            fh.write("\n")


def run_html(args: argparse.Namespace) -> None:
    """Entrypoint for loading stats from jsonl and displaying them as html"""

    _log.info("Loading stats from '%s'", args.stats)
    with open(args.stats, "r") as fh:
        users = list(map(UserStats.parse_raw, fh.readlines()))

    _log.info("Generating HTML with %d users", len(users))
    loader = jinja2.FileSystemLoader("./index.jinja2")
    env = jinja2.Environment(loader=loader, autoescape=True)
    template = env.get_template("")

    _log.info("Writing HTML to '%s'", args.output)
    with open(args.output, "w") as fh:
        fh.write(template.render(items=users))


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="github user stats")

    subparsers = parser.add_subparsers(required=True, dest="subcommand")
    dump = subparsers.add_parser("dump")
    dump.set_defaults(execute=run_dump)
    dump.add_argument(
        "--logins",
        required=True,
        type=str,
        nargs="+",
        help="User logins to collect stats for",
    )
    dump.add_argument(
        "--output",
        required=True,
        type=str,
        help="File to dump stats to",
    )

    html = subparsers.add_parser("html")
    html.set_defaults(execute=run_html)
    html.add_argument(
        "--stats",
        required=True,
        type=str,
        help="File to load stats from",
    )
    html.add_argument(
        "--output",
        required=True,
        type=str,
        help="File to dump html to",
    )

    return parser


def main() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s|%(name)s|%(levelname)s|%(message)s")
    )
    root_logger.handlers = [stream_handler]

    load_dotenv()

    parser = get_parser()
    args = parser.parse_args()
    args.execute(args)


if __name__ == "__main__":
    main()
