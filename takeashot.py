import os
import sys
import json
from argparse import ArgumentParser, Namespace
from collections import namedtuple
from logging import CRITICAL, DEBUG, INFO, basicConfig, getLogger
from time import sleep
from io import BytesIO
from base64 import b64encode

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

ClientInfo = namedtuple(
    "ClientInfo", "full_width full_height window_width window_height"
)
logger = getLogger(__name__)


def get_args() -> Namespace:
    """Parse Command-line args.

    Returns:
        Namespace: Args.
    """
    parser = ArgumentParser()
    parser.add_argument("url", help="specify URL")
    parser.add_argument("--screenshot", help="Take screenshot", action="store_true")
    parser.add_argument(
        "--source-code", help="Extract source code", action="store_true"
    )
    parser.add_argument(
        "--window-size",
        help="specify window size like 1200x800",
        dest="window_size",
        type=str,
    )
    parser.add_argument("--ua", help="specify user-agent", dest="user_agent", type=str)
    parser.add_argument(
        "--wait",
        help="specify wait seconds after scroll down",
        dest="wait",
        type=float,
        default=0.6,
    )
    parser.add_argument(
        "--lang",
        help="set LANG environment variable",
        dest="lang",
        type=str,
        default="en_US.UTF-8",
    )
    parser.add_argument(
        "--language",
        help="set LANGUAGE environment variable",
        dest="language",
        type=str,
        default="en_US",
    )
    parser.add_argument(
        "-v", help="set LogLevel to INFO", dest="log_info", action="store_true"
    )
    parser.add_argument(
        "--vv", help="set LogLevel to DEBUG", dest="log_debug", action="store_true"
    )

    return parser.parse_args()


def main():
    args = get_args()

    if not args.url:
        raise ValueError("No URL specified")

    screenshot, source_code = args.screenshot, args.source_code
    if not any((screenshot, source_code)):
        screenshot, source_code = True, True

    if args.lang:
        os.environ["LANG"] = args.lang
    if args.language:
        os.environ["LANGUAGE"] = args.language

    if args.window_size:
        window_size = tuple(map(int, args.window_size.split("x")))
        if len(window_size) != 2:
            raise ValueError("window-size must be of format {width}x{height}")
        if any(x <= 0 for x in window_size):
            raise ValueError("Dimension <= 0 not allowed in window-size")
    else:
        window_size = (1200, 800)

    if args.log_info:
        log_level = INFO
    elif args.log_debug:
        log_level = DEBUG
    else:
        log_level = CRITICAL
    basicConfig(
        level=log_level, format="%(asctime)s@%(name)s %(levelname)s # %(message)s"
    )

    take_snapshot(
        args.url,
        screenshot,
        source_code,
        window_size=window_size,
        user_agent=args.user_agent,
        wait=args.wait,
    )


def take_snapshot(
    url: str,
    screenshot: bool,
    source_code: bool,
    window_size: tuple[int, int] | None = None,
    user_agent: str | None = None,
    wait: float | None = None,
) -> None:
    """Collect snapshot data from URL. Data can be either screenshot, HTML source code, or both.

    Args:
        url (str): URL to take snapshot of.
        screenshot (bool): Enable screenshot capture.
        source_code (bool): Enable HTML source code extraction.
        window_size (tuple[int, int] | None, optional): Screenshot window size (width, height).
    Defaults to None.
        user_agent (str | None, optional): HTTP User-Agent request header. Defaults to None.
        wait (float | None, optional): Wait seconds after scroll down". Defaults to None.

    Returns:
        None: Print JSON string containing b64-encoded snapshot data to stdout.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-tools")
    # not good for security but prevents `DevToolsActivePort file doesn't exist` error in Docker
    options.add_argument("--no-sandbox")
    # Default shared memory directory size of 64 MB is not sufficient
    options.add_argument("--shm-size=2gb")
    desired_capabilities = dict(acceptInsecureCerts=True)
    if user_agent:
        options.add_argument(f"user-agent={user_agent}")
    if window_size:
        options.add_argument(f"window-size={window_size[1]},{window_size[0]}")
    driver = webdriver.Chrome(
        options=options, desired_capabilities=desired_capabilities
    )

    driver.get(url)
    driver.implicitly_wait(5)
    prepare_capture(driver)
    client_info = get_client_info(driver)

    user_agent = driver.execute_script("return navigator.userAgent")
    logger.info("%s | %s", repr(client_info), user_agent)

    output = {}
    if screenshot:
        output["screenshot"] = capture_screen_area(driver, client_info, wait=wait)
    if source_code:
        output["source_code"] = capture_source_code(driver)
    driver.close()

    print(json.dumps(output), file=sys.stdout)


def capture_screen_area(
    driver: webdriver.Chrome, client_info: ClientInfo, wait: float | None
) -> str:
    """Capture webpage screenshot in PNG format

    Args:
        driver (webdriver.Chrome): ChromeDriver.
        client_info (ClientInfo): Webpage dimensions.
        wait (float | None): Wait seconds after scroll down.

    Returns:
        str: PNG format screenshot as b64-encoded string.
    """
    for y_pos in range(0, client_info.full_height - client_info.window_height, 300):
        scroll_to(driver, 0, y_pos)
        sleep(wait or 0.2)

    client_info = get_client_info(driver)

    y_pos = client_info.full_height - client_info.window_height
    x_delta = client_info.window_width
    y_delta = client_info.window_height - 200

    Image.MAX_IMAGE_PIXELS = (
        357913940  # Support larger images; ~1GB for a 24-bit (3 bpp) image.
    )
    canvas = Image.new("RGB", (client_info.full_width, client_info.full_height))
    while y_pos > -y_delta:
        x_pos = 0
        while x_pos < client_info.full_width:
            scroll_to(driver, x_pos, y_pos)
            sleep(wait or 0.2)
            cur_x, cur_y = get_current_pos(driver)
            logger.info(
                "scrolling to {(%d, %d)}, current pos is {(%d, %d)}",
                x_pos,
                y_pos,
                cur_x,
                cur_y,
            )
            img = Image.open(BytesIO(driver.get_screenshot_as_png()))
            resized_image = img.resize(
                (client_info.window_width, client_info.window_height)
            )
            canvas.paste(resized_image, (cur_x, cur_y))
            img.close()
            resized_image.close()
            x_pos += x_delta
        y_pos -= y_delta
    img_byte_arr = BytesIO()
    canvas.save(img_byte_arr, format="PNG")
    return b64encode(img_byte_arr.getvalue()).decode("ascii")


def capture_source_code(driver: webdriver.Chrome) -> str:
    """Capture webpage HTML source code.

    Args:
        driver (webdriver.Chrome): ChromeDriver.

    Returns:
        str: Webpage HTML source code as b64-encoded string.
    """
    return b64encode(driver.page_source.encode()).decode("ascii")


def get_client_info(driver: webdriver.Chrome) -> ClientInfo:
    """Get webpage dimensions.

    Args:
        driver (webdriver.Chrome): ChromeDriver.

    Returns:
        ClientInfo: Webpage dimensions.
    """

    return ClientInfo(
        *driver.execute_script(
            """
function max(nums) {
    return Math.max.apply(Math, nums.filter(function(x) {
        return x;
    }));
}
return [
    max([
        document.documentElement.clientWidth,
        document.body ? document.body.scrollWidth : 0,
        document.documentElement.scrollWidth,
        document.body ? document.body.offsetWidth : 0,
        document.documentElement.offsetWidth
    ]),
    max([
        document.documentElement.clientHeight,
        document.body ? document.body.scrollHeight : 0,
        document.documentElement.scrollHeight,
        document.body ? document.body.offsetHeight : 0,
        document.documentElement.offsetHeight
    ]),
    window.innerWidth,
    window.innerHeight
];
"""
        )
    )


def prepare_capture(driver: webdriver.Chrome) -> None:
    """Configure `driver` to handle overflow content.

    Args:
        driver (webdriver.Chrome): ChromeDriver.

    Returns:
        None: `driver` is ready to handle overflow content.
    """
    driver.execute_script(
        """
        document.body.style.overflowY = 'visible';
        // document.documentElement.style.overflow = 'hidden';
    """
    )


def scroll_to(driver: webdriver.Chrome, x: int, y: int) -> None:
    """Scroll to a particular set of coordinates in the webpage.
    See https://developer.mozilla.org/en-US/docs/Web/API/Window/scrollTo

    Args:
        driver (webdriver.Chrome): ChromeDriver.
        x (int): Pixel along the horizontal axis of the webpage to be displayed in the upper left.
        y (int): Pixel along the vertical axis of the document to be displayed in the upper left.
    """
    driver.execute_script("window.scrollTo.apply(null, arguments)", x, y)


def get_current_pos(driver: webdriver.Chrome) -> tuple[int, int]:
    """Get current webpage position's X-Y coordinates.

    Args:
        driver (webdriver.Chrome): ChromeDriver

    Returns:
        tuple[int, int]: Current webpage position's X-Y coordinates.
    """
    return driver.execute_script("return [window.scrollX, window.scrollY]")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e, file=sys.stderr)
