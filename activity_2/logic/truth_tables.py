"""Truth-table checks for Questions 2-4: prints every table used in the README and asserts each answer."""
from itertools import product


def implies(p, q):
    return not p or q


def truth_table(title, names, columns):
    """columns: (header, function of the row's values) pairs; the last column is the sentence.
    Prints the table and returns the sentence's value in every row."""
    headers = names + [h for h, _ in columns]
    print(f"{title}\n" + " | ".join(headers))
    results = []
    for vals in product((True, False), repeat=len(names)):
        out = [f(*vals) for _, f in columns]
        results.append(out[-1])
        print(" | ".join("T" if v else "F" for v in (*vals, *out)))
    print()
    return results


def classify(results):
    return "valid" if all(results) else "unsatisfiable" if not any(results) else "neither"


q2a = truth_table("Q2a  Smoke => Fire", ["S", "F"], [("S => F", implies)])

q2b = truth_table("Q2b  ((S & H) => F) <=> ((S => F) | (H => F))", ["S", "H", "F"], [
    ("(S & H) => F", lambda s, h, f: implies(s and h, f)),
    ("(S => F) | (H => F)", lambda s, h, f: implies(s, f) or implies(h, f)),
    ("sentence", lambda s, h, f: implies(s and h, f) == (implies(s, f) or implies(h, f))),
])

q3a = truth_table("Q3a  B | C", ["A", "B", "C", "D"], [("B | C", lambda a, b, c, d: b or c)])

q3b = truth_table("Q3b  (A => B) & A & ~B & C & D", ["A", "B", "C", "D"], [
    ("sentence", lambda a, b, c, d: implies(a, b) and a and not b and c and d),
])

lhs = lambda f, d, p: implies(f, p) or implies(d, p)
rhs = lambda f, d, p: implies(f and d, p)
clause = lambda f, d, p: not f or not d or p
q4 = truth_table("Q4  [(Food => Party) | (Drinks => Party)] => [(Food & Drinks) => Party]", ["Fo", "Dr", "Pa"], [
    ("Fo => Pa", lambda f, d, p: implies(f, p)),
    ("Dr => Pa", lambda f, d, p: implies(d, p)),
    ("LHS", lhs),
    ("RHS", rhs),
    ("sentence", lambda f, d, p: implies(lhs(f, d, p), rhs(f, d, p))),
])

assert classify(q2a) == "neither"
assert classify(q2b) == "valid"
assert sum(q3a) == 12
assert sum(q3b) == 0
assert classify(q4) == "valid"
# Q4b: both sides convert to the same single CNF clause (~Food | ~Drinks | Party)
assert all(lhs(*v) == rhs(*v) == clause(*v) for v in product((True, False), repeat=3))
print("All answers check out: Q2a neither, Q2b valid, Q3a 12 models, Q3b 0 models, Q4 valid.")
