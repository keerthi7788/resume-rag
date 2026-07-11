from mcp.server.fastmcp import FastMCP

from tools import (
    extract_requirements,
    compare_candidates,
    generate_interview_questions,
)

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import os

mcp = FastMCP("Resume Filesystem MCP")


class ResumeWatcher(FileSystemEventHandler):

    def __init__(self):
        self.new_files = []

    def on_created(self, event):

        if not event.is_directory:

            self.new_files.append(event.src_path)


@mcp.tool()
def extract_requirements_tool(job_description: str):
    """
    Extract requirements from a Job Description.
    """
    return extract_requirements(job_description)


@mcp.tool()
def compare_candidates_tool(candidate_ids: list[str]):
    """
    Compare multiple candidates.
    """
    return compare_candidates(candidate_ids)


@mcp.tool()
def generate_interview_questions_tool(candidate_id: str):
    """
    Generate interview questions.
    """
    return generate_interview_questions(candidate_id)


@mcp.tool()
def watch_directory(directory: str):
    """
    Watch a directory for newly added resumes.
    """

    if not os.path.isdir(directory):

        return {
            "status": "error",
            "message": "Directory not found."
        }

    watcher = ResumeWatcher()

    observer = Observer()

    observer.schedule(
        watcher,
        directory,
        recursive=False
    )

    observer.start()

    return {
        "status": "watching",
        "directory": directory,
        "message": "Watching for new resume files."
    }


@mcp.tool()
def batch_process(files: list[str]):
    """
    Process multiple resume files.
    """

    results = []

    for file in files:

        if os.path.exists(file):

            results.append(
                {
                    "file": file,
                    "status": "processed"
                }
            )

        else:

            results.append(
                {
                    "file": file,
                    "status": "not_found"
                }
            )

    return results


@mcp.resource("resume://status")
def status():

    return {

        "server": "Resume Filesystem MCP",

        "status": "running",

        "tools": [

            "extract_requirements",

            "compare_candidates",

            "generate_interview_questions",

            "watch_directory",

            "batch_process"

        ]
    }


if __name__ == "__main__":
    mcp.run()