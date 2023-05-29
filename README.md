# Take A Shot

[![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Google Chrome](https://img.shields.io/badge/Google_chrome-4285F4?style=for-the-badge&logo=Google-chrome&logoColor=white)](https://google.com/chrome)

[![MIT License](https://img.shields.io/badge/LICENSE-MIT-GREEN?style=for-the-badge)](LICENSE)

Capture screenshot and/or HTML source code data of any given webpage and print it to stdout.

**Output format:** JSON string containing b64-encoded data.

## Implementation details

- Uses Google Chrome in headless mode.
- Works well even with vertically long webpages.
- Webpages with fixed headers generally work well, but fixed footers may lead to unusual results.

Forked and modified from: <https://github.com/mokemokechicken/docker_capture_web>

## Requirements

Tested on the following environment

### Linux

- Linux 6.1
- Docker Version 23.0.4

## Usage

### Build

```bash
./build
```

Then either run

```bash
./capture <URL> [options]
```

or run

```bash
docker run --rm elliotwutingfeng/take_a_shot <URL> [options]
```

## Output Format

```json
{
  "screenshot": "<PNG screenshot as b64-encoded string>",
  "source_code": "<HTML source code as b64-encoded string>"
}
```

## Examples

### PC

```bash
docker run --rm elliotwutingfeng/take_a_shot "https://example.com"
```

### iPhone

```bash
docker run --rm elliotwutingfeng/take_a_shot "https://example.com" --window-size 414x735 --ua 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
```

## Help

```bash
usage: takeashot.py [-h] [--screenshot] [--source-code] [--window-size WINDOW_SIZE] [--ua USER_AGENT] [--wait WAIT] [--lang LANG] [--language LANGUAGE] [-v] [--vv] url

positional arguments:
  url                   specify URL

options:
  -h, --help            show this help message and exit
  --screenshot          Take screenshot
  --source-code         Extract source code
  --window-size WINDOW_SIZE
                        specify window size like 1200x800
  --ua USER_AGENT       specify user-agent
  --wait WAIT           specify wait seconds after scroll
  --lang LANG           set LANG environment variable
  --language LANGUAGE   set LANGUAGE environment variable
  -v                    set LogLevel to INFO
  --vv                  set LogLevel to DEBUG
```

## Credits

[Link](CREDITS.md)
