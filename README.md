# The World in One Page — Wednesday 18 November 2026

A newspaper front page that sums up the world news of Wednesday 18 November
2026 in a single image. The day is still young in UTC when this page was
built; it covers what the day had reported by the morning in Asia.

## The day, as reported

- **Lead: APEC opens in Shenzhen** — Xi Jinping delivers the opening
  keynote as the 33rd APEC Economic Leaders' Meeting begins, 21 economies
  gathered under the theme "Building an Asia-Pacific Community to Prosper
  Together".
- **Trump lands in Shenzhen** — arrives from Manila after the ASEAN summit;
  the first US president to visit China twice in one year, with the
  Xi–Trump–Putin trilateral set for Thursday.
- **Putin to address the CEO Summit** — the Russian leader speaks at the
  APEC CEO Summit opening ceremony.
- **Anthropic prices a record IPO** — $70 to $78 a share, up to $64.4
  billion, with the Nasdaq debut set for Thursday under the ticker ANT.
- **Ukraine grain harvest may halve** — Black Sea exports blocked by
  Russian attacks; 30 million tonnes forecast for 2027, down from 62
  million in 2026.
- **AI chips top the APEC agenda** — chip curbs and AI governance in focus
  alongside trade.
- **First trip since midterm defeat** — Trump's first travel abroad since
  his party's heavy midterm losses.

## The entry

- `entry.png` — the finished front page, 1024x1024, JPEG bytes under the
  `.png` name (the competition reads the format from the first bytes).
- `main.py` — Python 3.13, standard library only, no network. It probes
  the artwork (size at most 1 MiB, a real PNG or JPEG header, dimensions
  at most 1024x1024), copies it to `$MAKEFUN_OUTPUT_DIR` (else `/output`)
  in 64 KiB chunks, then re-reads the copy and checks both its size and
  its SHA-256 against the source. Any failed check writes nothing and
  exits non-zero.

## Check it

```sh
mkdir -p out1 out2
MAKEFUN_OUTPUT_DIR=out1 python3 main.py
MAKEFUN_OUTPUT_DIR=out2 python3 main.py
cmp out1/entry.png out2/entry.png   # byte-identical across runs
```
