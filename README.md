# github-stats

Collect stats for a bunch of Github users, and present them in an interactive HTML table.

## Usage

(optional) To authenticate yourself with the github API, generate a [PAT token](https://github.com/settings/tokens),
and set it in a `.env` file in this repo:

```bash
GITHUB_TOKEN=mygithubtoken
```

First, collect stats about some users:

```bash
python github_stats.py dump --logins tommilligan --output stats.jsonl
```

Then, compile the stats into a nice HTML output:

```bash
python github_stats.py html --stats stats.jsonl --output stats.html
```

## Dependencies

Install python requirements with `pip install -r requirements.txt`.

For nice interactive tables, the HTML pulls in a CDN hosted copy of JQuery and [DataTables](https://datatables.net/examples/basic_init/zero_configuration.html).
