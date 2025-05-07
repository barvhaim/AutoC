from typing import Optional
import logging
from datetime import datetime
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from backend.run import run

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cli")

auto_c_logo = """     _         _         ____ 
    / \  _   _| |_ ___  / ___|
   / _ \| | | | __/ _ \| |    
  / ___ \ |_| | || (_) | |___ 
 /_/   \_\__,_|\__\___/ \____|
 """


def _create_tag(keyword):
    """Create a styled tag string"""
    return f"[black on cyan] {keyword} [/]"


def _create_qa_panel(question, answer):
    """Create a styled Q&A panel"""
    content = f"[bold cyan]Q:[/] {question}\n\n" f"[bold green]A:[/] {answer}"
    return Panel(content, border_style="bright_black", padding=(1, 2))


def _display_header(console: Console):
    console.print(
        Panel(
            Text(auto_c_logo, style="bold white"),
            subtitle=f"Automated IoCs Extraction Tool",
        )
    )


def _display_results(console: Console, res: dict, url: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(
        Panel(
            Text(f"🕵️‍♂️ Blog Analysis Report: {url}", style="bold white"),
            subtitle=f"Generated at {timestamp}",
            style="blue",
        )
    )

    keywords = res.get("keywords_found")
    qna = res.get("qna")
    iocs = res.get("iocs_found")

    # Keywords
    keyword_text = Text(
        f"\n🔍 DETECTED KEYWORDS ({len(keywords)})\n", style="bold yellow"
    )
    console.print(keyword_text)
    if keywords:
        tags = " ".join(_create_tag(keyword) for keyword in keywords)
        console.print(tags + "\n")
    else:
        console.print("No keywords found\n")

    # Q&A
    qna_text = Text(f"\n📝 Q&A ({len(qna)})\n", style="bold yellow")
    console.print(qna_text)
    if qna:
        qa_panels = [_create_qa_panel(item["question"], item["answer"]) for item in qna]

        # Display panels in columns if terminal is wide enough
        console.print(Columns(qa_panels, equal=True, expand=True))
    else:
        console.print("No Q&A found\n")

    # IoCs
    iocs_text = Text(f"\n⚠️ DETECTED IoCs ({len(iocs)})\n", style="bold yellow")
    console.print(iocs_text)
    if iocs:
        ioc_table = Table(show_header=True, header_style="bold magenta")
        ioc_table.add_column("Type", style="yellow")
        ioc_table.add_column("Value", style="white")

        for ioc in iocs:
            ioc_table.add_row(ioc["type"], ioc["value"])
        console.print(ioc_table)
    else:
        console.print("No IoCs found\n")

    # MITRE  Classification
    mitre_ttp = res.get("mitre_ttp", [])
    if mitre_ttp is None:
        return
    mitre_text = Text(f"\n🎯 MITRE TTPs ({len(mitre_ttp)})\n", style="bold yellow")
    console.print(mitre_text)

    if mitre_ttp:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Max Confidence", style="green", justify="right")
        table.add_column("URL", style="blue", overflow="fold")

        for ttp in mitre_ttp:
            confidence = f"{ttp.get('confidence', 0):.3f}"
            table.add_row(
                ttp["id"],
                ttp["name"],
                confidence,
                ttp["url"],
            )

        console.print(table)
    else:
        console.print("No MITRE TTPs detected\n")

@click.group()
def cli():
    """AutoC is a framework for Automated IoCs extraction."""


@click.command()
@click.option("--url", help="URL of the blog post to extract IoCs from.")
def extract(url: Optional[str]):
    """Extract IoCs from a blog post."""
    console = Console()
    try:
        _display_header(console=console)
        if not url:
            url = input("Enter the URL of the blog post: ")
        res = run(url=url)
        _display_results(console=console, res=res, url=url)
    except Exception as e:
        logger.error(f"Error: {str(e)}")


cli.add_command(extract)

if __name__ == "__main__":
    cli()
