import argparse
import base64
from pathlib import Path
import sys

HTML_VIEWER_PATH = Path(__file__).with_name("static_viewer.html")


def embbed_data_to_viewer(input_data_file_path):
    input = Path(input_data_file_path)
    output = input.with_name(f"{input.name}.html")
    base64Content = ""

    if input.exists():
        with open(input, "rb") as data:
            dataContent = data.read()
            base64Content = base64.b64encode(dataContent)
            base64Content = base64Content.decode().replace("\n", "")

        with open(HTML_VIEWER_PATH, mode="r", encoding="utf-8") as srcHtml:
            with open(output, mode="w", encoding="utf-8") as dstHtml:
                for line in srcHtml:
                    if "</body>" in line:
                        dstHtml.write("<script>\n")
                        dstHtml.write(
                            "var container = document.querySelector('.content');\n"
                        )
                        dstHtml.write('var base64Str = "%s";\n\n' % base64Content)
                        dstHtml.write(
                            "OfflineLocalView.load(container, { base64Str });\n"
                        )
                        dstHtml.write("</script>\n")

                    dstHtml.write(line)


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
        parser.print_help()
        sys.exit(0)

    embbed_data_to_viewer(input_file)


if __name__ == "__main__":
    main()
