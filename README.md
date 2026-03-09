# semantic-scholar-skills

`semantic-scholar-skills` contains the standalone async Semantic Scholar core client extracted from the MCP server repo, so the request models, transport, and error handling can be used without pulling in FastMCP, FastAPI, or the server runtime.

## Included

- Request models for papers, authors, snippets, and recommendations
- Async `S2Client` and compatibility transport helpers
- HTTP transport with rate limiting and API-key handling
- Standalone exception model
- Offline pytest coverage for the core layer

## Not included

- MCP tool wrappers
- FastAPI HTTP bridge
- Server runtime and deployment entrypoints

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
import asyncio

from semantic_scholar_skills.core import PaperDetailsRequest, S2Client, S2Transport


async def main() -> None:
    client = S2Client(S2Transport())
    paper = await client.get_paper(
        PaperDetailsRequest(
            paper_id="CorpusId:215416146",
            fields=["title", "year"],
        )
    )
    print(paper["title"])


asyncio.run(main())
```

## Testing

```bash
pytest -m 'not live' -q
```

## Provenance

This package was extracted from `/Users/yuzongmin/repos/semantic-scholar-fastmcp-mcp-server`, which is based on the upstream Semantic Scholar MCP server project at `https://github.com/zongmin-yu/semantic-scholar-fastmcp-mcp-server`.
