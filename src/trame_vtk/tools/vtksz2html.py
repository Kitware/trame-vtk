import argparse
import base64
import sys
from pathlib import Path
from typing import TextIO

HTML_VIEWER_PATH = Path(__file__).with_name("static_viewer.html")


def data_to_base64(data: bytes):
    base64Content = base64.b64encode(data)
    return base64Content.decode().replace("\n", "")


def write_html(data: bytes, output: TextIO):
    base64Content = data_to_base64(data)
    with open(HTML_VIEWER_PATH, mode="r", encoding="utf-8") as srcHtml:
        for line in srcHtml:
            if "</body>" in line:
                output.write("<script>\n")
                output.write("var container = document.querySelector('.content');\n")
                output.write('var base64Str = "%s";\n\n' % base64Content)
                output.write("OfflineLocalView.load(container, { base64Str });\n")
                output.write("</script>\n")

            output.write(line)


def embed_data_to_viewer_file(data: bytes, output_file: Path):
    with open(output_file, mode="w", encoding="utf-8") as dstHtml:
        write_html(data, dstHtml)


def main():
    parser = argparse.ArgumentParser(description="HTML exporter for local view data")

    parser.add_argument(
        "--input",
        help="Input data file",
    )

    args, _ = parser.parse_known_args()

    if args.input is None:
        parser.print_help()
        sys.exit(0)

    input_file = Path(args.input)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file {input_file.name} not found.")

    input = Path(input_file)
    output = input.with_name(f"{input.name}.html")

    with open(input, "rb") as data:
        data = data.read()

    embed_data_to_viewer_file(data, output)


if __name__ == "__main__":
    main()
