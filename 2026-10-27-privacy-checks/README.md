# Privacy checks pilot (2026-10-27)

The three checks from [the story](https://worklore.dev/s/2026-10-27-a-reader-found-three-gaps-in-my-privacy-policy-the-same-thre), run without source code over 100 remote MCP servers sampled (seed 8, one per host) from the registry scan in `../2026-10-06-mcp-scan/random-1000/contracts.jsonl`.

- `pilot.py`: fetches each server's website, finds the privacy page (link text or URL containing "privacy" or its equivalent in a dozen languages, else common paths), counts the pages of the sitemap (cap 40) that link to it in the HTML without JavaScript (door), lists every negative sentence with its section (negatives), calls `tools/list` on the MCP endpoint without sign-in and compares the tools and their string arguments with the policy text (freetext). One Haiku call per policy (`claude -p --tools ""`) judges whether each negative has a same-section sentence saying what is done, lists conflicting sentence pairs, and names tool inputs the policy never describes.
- `results.jsonl`: one row per host, raw. `report.md`: the summary and the table. `run.log`: progress.
- The free-text check is the half that needs no source: whether the policy names the inputs at all. Where user text ends up (public page, another network) needs the code, so a row says "unnamed", never "leaks".

Before publishing anything from this: hand-check every flagged row, and tell each site named in the text before it goes out. Non-English policies are fetched but the negative-sentence regex is English, so their negatives count is 0 and the model pass is skipped; that is a limitation of the pilot, not a finding.

Rerun: `python3 pilot.py 100` (skips hosts already in results.jsonl); `python3 -c "import pilot; pilot.report()"` rebuilds the report.
