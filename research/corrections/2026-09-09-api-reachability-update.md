# 9 September 2026 EUDAMED API reachability update

Status: operational correction / method note.

## Why this correction exists

On 8 September 2026, ClinicOps repeatedly observed the public `udiDiData` route serving around page 30,000 while probes around page 32,000 failed. That observation was recorded as a point-in-time deep-offset reachability wall.

The first live GitHub `Ops Watch` canary on 9 September 2026 did **not** reproduce that boundary.

Workflow run:
https://github.com/aliiskandar310796-beep/ClinicOps/actions/runs/34352492799

Captured at: `2026-09-09T12:42:04.925344+00:00`

## Canary result

The same bounded route returned HTTP 200 for all three probe points:

| Page | HTTP | Returned items | Total elements | Elapsed |
|---:|---:|---:|---:|---:|
| 0 | 200 | 50 | 3,394,504 | 0.548 s |
| 30,000 | 200 | 50 | 3,394,504 | 13.418 s |
| 32,000 | 200 | 50 | 3,394,504 | 13.292 s |

## Correct interpretation

The 8 September page-32,000 failures were a real ClinicOps operational observation for that run context, but they must **not** be treated as a stable public-API boundary.

As of the 9 September GitHub Actions probe:

- page 32,000 was reachable;
- the earlier apparent ~32k wall did not reproduce;
- deep-offset access remained much slower than page 0 in this run;
- 50 records were returned at each requested page size of 50;
- none of this establishes full-register reachability beyond the tested pages.

## Method consequence

Do not publish a fixed statement such as `the public API becomes inaccessible above page 30,000`.

Instead say, when relevant:

> ClinicOps has observed deep-offset reachability varying across runs. Bounded canary probes are retained as operational evidence, and any coverage statement must be tied to the exact retrieval date and tested frame.

Future canaries should detect changes in page reachability rather than encode the 8 September wall as a permanent expectation.
