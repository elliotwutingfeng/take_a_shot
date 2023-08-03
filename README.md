<div align="center">

  <h3 align="center">Take A Shot</h3>
  <img src="images/lens.svg" alt="Lens" width="200" height="200">

  <p align="center">
    Capture screenshot and/or HTML source code data of any given webpage and print it to stdout.
  </p>

  <p align="center">
    <strong>Output format:</strong> JSON string containing b64-encoded data.
  </p>

  <p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" alt="Python"/></a>
  <a href="https://docker.com"><img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/></a>
  <a href="https://google.com/chrome"><img src="https://img.shields.io/badge/Google_chrome-4285F4?style=for-the-badge&logo=Google-chrome&logoColor=white" alt="Google Chrome"/></a>
  </p>

  <p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/LICENSE-MIT-GREEN?style=for-the-badge" alt="MIT license"/></a>
  </p>

</div>

## Implementation details

- Uses Google Chrome in headless mode.
- Works well even with vertically long webpages.
- Webpages with fixed headers generally work well, but fixed footers may lead to unusual results.

Forked and modified from: <https://github.com/mokemokechicken/docker_capture_web>

## Requirements

Tested on the following environment

### Linux

- Linux 6.1
- Docker Version 24.0.5

## Usage

### Build

```bash
./build
```

Then either run

```bash
./capture <URL> [options]
```

or alternatively run

```bash
docker run --cap-drop=all --security-opt=no-new-privileges --rm elliotwutingfeng/take_a_shot <URL> [options]
```

## Output Format

```json
{
  "screenshot": "<PNG screenshot as b64-encoded string>",
  "source_code": "<HTML source code as b64-encoded string>"
}
```

## Examples

### Default User Agent

```bash
docker run --cap-drop=all --security-opt=no-new-privileges --rm elliotwutingfeng/take_a_shot "https://example.com"
```

### Specify User Agent

```bash
docker run --cap-drop=all --security-opt=no-new-privileges --rm elliotwutingfeng/take_a_shot "https://example.com" --window-size 390x844 --ua 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/113.0 Mobile/15E148 Safari/605.1.15'
```

## Help

```bash
usage: takeashot.py [-h] [--screenshot] [--source-code]
                    [--window-size WINDOW_SIZE] [--ua USER_AGENT]
                    [--wait WAIT] [--lang LANG] [--language LANGUAGE] [-v]
                    [--vv]
                    url

positional arguments:
  url                   specify URL

options:
  -h, --help            show this help message and exit
  --screenshot          Take screenshot
  --source-code         Extract source code
  --window-size WINDOW_SIZE
                        specify window size like 1200x800
  --ua USER_AGENT       specify user-agent
  --wait WAIT           specify wait seconds after scroll down
  --lang LANG           set LANG environment variable
  --language LANGUAGE   set LANGUAGE environment variable
  -v                    set LogLevel to INFO
  --vv                  set LogLevel to DEBUG
```

## Credits

[Link](CREDITS.md)
