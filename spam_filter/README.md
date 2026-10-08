# Q1 – Spam Filter Email Agent

## Running

Requires Python 3.9+ (standard library only).

```bash
cd spam_filter
python -m unittest -v                     # run the tests
python agent.py                           # sort data/inbox into ./out/spam and ./out/email
python agent.py path/to/inbox --out sorted --data path/to/lists
```

Each `.eml` file is copied into `out/spam/` or `out/email/`, so the inbox stays as it was and the sample data can be reused.

### Test data

- `data/allow_list.txt`, `data/restrict_list.txt`, `data/bad_words.txt` hold one entry per line. Lines starting with `#` are ignored.
- `data/inbox/` holds 9 sample emails, one per rule or edge case. The expected result for each file is in `EXPECTED` in `test_agent.py`:

| File | Case | Expected |
|---|---|---|
| 01 | allowed domain, 8 bad words | email |
| 02 | restricted domain, clean body | spam |
| 03 | unknown domain, 6 bad words | spam |
| 04 | unknown domain, exactly 5 bad words | email |
| 05 | base64-encoded body with 7 bad words | spam |
| 06 | clean body, bad words in a text attachment | spam |
| 07 | subdomain of an allowed domain (`mail.github.com`) | email |
| 08 | lookalike of an allowed domain (`fakegithub.com`) | spam |
| 09 | unknown domain, clean body | email |

## a) PEAS

| | |
|---|---|
| **Performance measure** | Share of emails filed correctly. Few false positives (real mail sent to spam, the costlier mistake) and few false negatives (spam left in the inbox). Allow and restrict lists always obeyed. |
| **Environment** | Incoming `.eml` files (headers + body, possibly encoded, possibly with text attachments), the allow list, restrict list and bad word list, and the `spam` and `email` directories. |
| **Actuators** | Moving or copying the file into the `spam` or `email` directory. |
| **Sensors** | Reading the `.eml` file: parsing the `From` header to get the sender's domain, decoding the body and text attachments (base64, quoted-printable, charsets), and reading the three lists. |

## b) Properties of the task environment

- **Fully observable.** Everything needed for the decision (sender domain, body, the lists) is in the current email and the lists.
- **Single agent.** Spammers do adapt over time, but there is no live opponent while the agent classifies a single email.
- **Deterministic.** The same email and lists always lead to the same result, and filing an email always works.
- **Episodic.** Each email is its own episode. Classifying one has no effect on the next.
- **Static.** The email and lists don't change while the agent is deciding.
- **Discrete.** There's a finite set of percepts (words, domains) and two actions (spam or email).
- **Known.** The rules are given in full by the specification.

## c) Agent type

A **simple reflex agent**. The environment is fully observable and episodic, so the right action depends only on the current percept. No internal state or model of the world is needed (that would be a model-based agent), and the agent isn't weighing goals or utilities. The specification is already a set of condition–action rules, checked in priority order:

1. sender domain on the allow list → `email`
2. sender domain on the restrict list → `spam`
3. more than 5 bad-word occurrences in the body or text attachments → `spam`
4. otherwise → `email`

## d) Implementation

`agent.py` follows AIMA's `SimpleReflexAgentProgram` (Figure 2.10):

- `interpret_input` is the sensor. It parses the raw `.eml` bytes with Python's `email` package and returns the state `{allowed, restricted, bad_words}`.
- `rule_match` returns the first rule in `RULES` whose condition holds, and the agent returns that rule's action.
- `run` is the environment loop. It feeds each email to the agent and carries out the action by filing the email into the right folder.

Design decisions:

- A sender matches a listed domain if it is that domain or a subdomain of it, so `mail.github.com` matches `github.com` but `fakegithub.com` doesn't.
- Bad words are counted per occurrence, case-insensitively, on whole words.
- If a domain is on both lists, the allow list wins, because the specification says allow-list mail is non-spam "regardless of its contents".
- The specification describes the restrict list as "safe domains". That reads as a typo, since emails from those domains are classified as spam, so it's treated as a list of unsafe domains.
