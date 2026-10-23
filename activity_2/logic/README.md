# Questions 2–4 – Propositional Logic

Every truth table below is printed by `truth_tables.py`, which also asserts each answer:

```bash
cd logic
python truth_tables.py
```

Notation: ¬ not, ∧ and, ∨ or, ⇒ implies, ⇔ if and only if. A sentence is **valid** if it is true in every model, **unsatisfiable** if it is true in none, and **neither** (satisfiable but not valid) otherwise.

## Q2 – Satisfiability (10%)

### a) Smoke ⇒ Fire — **neither** (satisfiable, not valid)

| Smoke | Fire | Smoke ⇒ Fire |
|---|---|---|
| T | T | T |
| T | F | **F** |
| F | T | T |
| F | F | T |

It is true in three models, so it is satisfiable. It is false when Smoke is true and Fire is false, so it is not valid.

### b) ((Smoke ∧ Heat) ⇒ Fire) ⇔ ((Smoke ⇒ Fire) ∨ (Heat ⇒ Fire)) — **valid**

Using the equivalence rules:

| Step | Left side | Right side |
|---|---|---|
| Start | (S ∧ H) ⇒ F | (S ⇒ F) ∨ (H ⇒ F) |
| Implication elimination | ¬(S ∧ H) ∨ F | (¬S ∨ F) ∨ (¬H ∨ F) |
| De Morgan / associativity | ¬S ∨ ¬H ∨ F | ¬S ∨ ¬H ∨ F ∨ F |
| Idempotence (F ∨ F ≡ F) | ¬S ∨ ¬H ∨ F | ¬S ∨ ¬H ∨ F |

Both sides reduce to the same sentence α, and α ⇔ α is true in every model. The truth table agrees: the two sides match in all 8 rows.

| S | H | F | (S ∧ H) ⇒ F | (S ⇒ F) ∨ (H ⇒ F) | Sentence |
|---|---|---|---|---|---|
| T | T | T | T | T | T |
| T | T | F | F | F | T |
| T | F | T | T | T | T |
| T | F | F | T | T | T |
| F | T | T | T | T | T |
| F | T | F | T | T | T |
| F | F | T | T | T | T |
| F | F | F | T | T | T |

## Q3 – Models (10%)

With four propositions there are 2⁴ = 16 possible models.

### a) B ∨ C — **12 models**

B ∨ C is false only when B and C are both false. That fixes 2 of the 4 symbols and leaves A and D free, so it is false in 2² = 4 models. It is true in 16 − 4 = **12**. (Equivalently: 3 good (B, C) combinations × 4 (A, D) combinations = 12.)

### b) (A ⇒ B) ∧ A ∧ ¬B ∧ C ∧ D — **0 models**

The conjuncts A and ¬B force A = T and B = F. But then A ⇒ B is T ⇒ F, which is false, so the whole conjunction is false. No assignment satisfies it. The sentence is unsatisfiable, with **0** models. (By modus ponens, A and A ⇒ B give B, which contradicts ¬B.) The script confirms this: all 16 rows are F.

## Q4 – Resolution (20%)

Sentence: [(Food ⇒ Party) ∨ (Drinks ⇒ Party)] ⇒ [(Food ∧ Drinks) ⇒ Party]

### a) Enumeration — **valid**

| Food | Drinks | Party | Food ⇒ Party | Drinks ⇒ Party | Left side | Right side | Sentence |
|---|---|---|---|---|---|---|---|
| T | T | T | T | T | T | T | T |
| T | T | F | F | F | F | F | T |
| T | F | T | T | T | T | T | T |
| T | F | F | F | T | T | T | T |
| F | T | T | T | T | T | T | T |
| F | T | F | T | F | T | T | T |
| F | F | T | T | T | T | T | T |
| F | F | F | T | T | T | T | T |

The sentence is true in all 8 models, so it is **valid** (and so also satisfiable). The left and right sides have identical columns, so the implication can never be T ⇒ F.

### b) CNF conversion

Left side:

1. (Food ⇒ Party) ∨ (Drinks ⇒ Party)
2. Implication elimination: (¬Food ∨ Party) ∨ (¬Drinks ∨ Party)
3. Associativity and commutativity: ¬Food ∨ ¬Drinks ∨ Party ∨ Party
4. Idempotence: **¬Food ∨ ¬Drinks ∨ Party**

Right side:

1. (Food ∧ Drinks) ⇒ Party
2. Implication elimination: ¬(Food ∧ Drinks) ∨ Party
3. De Morgan: (¬Food ∨ ¬Drinks) ∨ Party
4. Associativity: **¬Food ∨ ¬Drinks ∨ Party**

Both sides become the same single clause, call it α. So the sentence is α ⇒ α ≡ ¬α ∨ α, which is true in every model. This confirms (a).

Converting the whole sentence shows the same thing. ¬α ∨ α = (Food ∧ Drinks ∧ ¬Party) ∨ (¬Food ∨ ¬Drinks ∨ Party). Distributing ∨ over ∧ gives three clauses:

(Food ∨ ¬Food ∨ ¬Drinks ∨ Party) ∧ (Drinks ∨ ¬Food ∨ ¬Drinks ∨ Party) ∧ (¬Party ∨ ¬Food ∨ ¬Drinks ∨ Party)

Each clause contains a complementary pair (Food/¬Food, Drinks/¬Drinks, Party/¬Party), so each clause is always true, and so is the sentence.

### c) Proof by resolution

To show a sentence is valid, show that its negation is unsatisfiable by deriving the empty clause.

¬[LHS ⇒ RHS] ≡ LHS ∧ ¬RHS ≡ (¬Food ∨ ¬Drinks ∨ Party) ∧ ¬(¬Food ∨ ¬Drinks ∨ Party)
≡ (¬Food ∨ ¬Drinks ∨ Party) ∧ Food ∧ Drinks ∧ ¬Party (De Morgan, double negation)

Clauses:

| # | Clause | From |
|---|---|---|
| 1 | ¬Food ∨ ¬Drinks ∨ Party | LHS |
| 2 | Food | ¬RHS |
| 3 | Drinks | ¬RHS |
| 4 | ¬Party | ¬RHS |
| 5 | ¬Drinks ∨ Party | resolve 1, 2 on Food |
| 6 | Party | resolve 5, 3 on Drinks |
| 7 | **{ } (empty clause)** | resolve 6, 4 on Party |

The negation leads to a contradiction, so it is unsatisfiable, and the original sentence is **valid**.
