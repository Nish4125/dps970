"""Spam filter email agent, built as a simple reflex agent (AIMA Figure 2.10)."""
import argparse
import re
import shutil
from collections import namedtuple
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from pathlib import Path

DATA = Path(__file__).parent / "data"
BAD_WORD_LIMIT = 5

Rule = namedtuple("Rule", "condition action")

# Order matters: the allow list beats everything, the restrict list beats the word count.
RULES = [
    Rule(lambda s: s["allowed"], "email"),
    Rule(lambda s: s["restricted"], "spam"),
    Rule(lambda s: s["bad_words"] > BAD_WORD_LIMIT, "spam"),
    Rule(lambda s: True, "email"),
]


def simple_reflex_agent_program(rules, interpret_input):
    """AIMA SimpleReflexAgentProgram: percept -> state -> matching rule -> action."""
    def program(percept):
        state = interpret_input(percept)
        rule = rule_match(state, rules)
        action = rule.action
        return action
    return program


def rule_match(state, rules):
    for rule in rules:
        if rule.condition(state):
            return rule


def load_list(path):
    lines = (line.strip().lower() for line in Path(path).read_text().splitlines())
    return {line for line in lines if line and not line.startswith("#")}


def in_domains(domain, domains):
    """True if domain is on the list or is a subdomain of a listed domain."""
    return any(domain == d or domain.endswith("." + d) for d in domains)


def text_of(part):
    try:
        return part.get_content()
    except (LookupError, UnicodeError):  # unknown or lying charset
        return (part.get_payload(decode=True) or b"").decode("utf-8", "replace")


def body_text(msg):
    """All readable text: the body plus any text/* attachments, decoded."""
    return " ".join(text_of(p) for p in msg.walk() if p.get_content_maintype() == "text")


def make_interpret_input(allow, restrict, bad_words):
    """Sensor: turn raw .eml bytes into the state the rules look at."""
    def interpret_input(percept):
        msg = BytesParser(policy=policy.default).parsebytes(percept)
        domain = parseaddr(str(msg["From"] or ""))[1].rpartition("@")[2].lower()
        words = re.findall(r"\w+", body_text(msg).lower())
        return {
            "allowed": in_domains(domain, allow),
            "restricted": in_domains(domain, restrict),
            "bad_words": sum(w in bad_words for w in words),
        }
    return interpret_input


def make_agent(data=DATA):
    data = Path(data)
    return simple_reflex_agent_program(RULES, make_interpret_input(
        load_list(data / "allow_list.txt"),
        load_list(data / "restrict_list.txt"),
        load_list(data / "bad_words.txt"),
    ))


def run(inbox, out, data=DATA):
    """Environment loop: feed each .eml to the agent and carry out its action
    by copying the file into out/spam or out/email. The inbox is left untouched."""
    agent = make_agent(data)
    results = {}
    for eml in sorted(Path(inbox).glob("*.eml")):
        action = agent(eml.read_bytes())
        dest = Path(out) / action
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(eml, dest)
        results[eml.name] = action
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sort .eml files into spam/ and email/.")
    parser.add_argument("inbox", nargs="?", default=DATA / "inbox")
    parser.add_argument("--out", default="out")
    parser.add_argument("--data", default=DATA, help="folder holding the three list files")
    args = parser.parse_args()
    for name, action in run(args.inbox, args.out, args.data).items():
        print(f"{action:5}  {name}")
