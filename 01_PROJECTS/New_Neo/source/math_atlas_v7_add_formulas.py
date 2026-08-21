#!/usr/bin/env python3
"""
MATHEMATICAL LANGUAGE ATLAS — v7 FORMULA INTEGRATION
=====================================================
This script adds actual mathematical formulas to the v7 civilizational framework,
transforming it from an empty framework into a genuine time capsule with content.

Run this AFTER running math_atlas_v7_civilizational.py to populate it with real knowledge.
"""

import sqlite3
from pathlib import Path

DB_FILE = Path("math_atlas_v7_civilizational.sqlite")

# ACTUAL MATHEMATICAL FORMULAS (Representative sample)
ACTUAL_FORMULAS = [
    ("Boltzmann distribution", "Physics", "Statistical mechanics",
        "Probability of a microstate in canonical ensemble.",
        r"P_i = \frac{e^{-E_i/k_B T}}{Z}", "Pᵢ = e^(-Eᵢ/kₚT)/Z",
        "canonical ensemble", "P,E,k,B,T,Z",
        "law", "proven", "Ludwig Boltzmann (1877)",
        "curated_v7", 4, 1877, "Ludwig Boltzmann"),
    
    ("RSA encryption", "Cryptography", "Public-key cryptography",
        "Encryption: c = m^e mod n, Decryption: m = c^d mod n.",
        r"c = m^e \pmod n,\ m = c^d \pmod n", "c = m^e mod n, m = c^d mod n",
        "n = pq, ed ≡ 1 (mod φ(n))", "c,m,e,d,n,p,q",
        "algorithm", "proven", "Rivest, Shamir, Adleman (1977)",
        "curated_v7", 4, 1977, "Rivest, Shamir, Adleman"),
    
    ("Character orthogonality (first)", "Algebra", "Representation theory",
        "Orthogonality of irreducible characters.",
        r"\frac{1}{|G|} \sum_{g \in G} \chi_i(g) \overline{\chi_j(g)} = \delta_{ij}",
        "(1/|G|) Σ χᵢ(g)χ̄ⱼ(g) = δᵢⱼ",
        "irreducible characters", "χ,G,g,i,j,δ",
        "theorem", "proven", "Ferdinand Georg Frobenius (1896)",
        "curated_v7", 5, 1896, "Ferdinand Georg Frobenius"),
    
    ("Compactness theorem", "Logic", "Model theory",
        "A set of sentences has a model iff every finite subset has a model.",
        r"\text{If } \Sigma \text{ is finitely satisfiable, then } \Sigma \text{ is satisfiable}",
        "If Σ is finitely satisfiable, then Σ is satisfiable",
        "first-order logic", "Σ",
        "theorem", "proven", "Kurt Gödel (1930) & Anatoly Maltsev (1936)",
        "curated_v7", 5, 1930, "Kurt Gödel & Anatoly Maltsev"),
    
    ("Snake lemma", "Algebra", "Homological algebra",
        "Long exact sequence from commutative diagram with exact rows.",
        r"\ker(\alpha) \to \ker(\beta) \to \ker(\gamma) \to \text{coker}(\alpha)",
        "ker(α) → ker(β) → ker(γ) → coker(α)",
        "abelian category", "ker,α,β,γ",
        "theorem", "proven", "Eilenberg & Mac Lane (1942)",
        "curated_v7", 5, 1942, "Samuel Eilenberg & Saunders Mac Lane"),
    
    ("Van Kampen theorem", "Topology", "Algebraic topology",
        "Fundamental group of union via free product with amalgamation.",
        r"\pi_1(X) \cong \pi_1(U) *_{\pi_1(U \cap V)} \pi_1(V)",
        "π₁(X) ≅ π₁(U) *_{π₁(U∩V)} π₁(V)",
        "X = U ∪ V, U∩V path-connected", "π,U,V",
        "theorem", "proven", "Egbert van Kampen (1933)",
        "curated_v7", 5, 1933, "Egbert van Kampen"),
    
    ("Parseval's identity", "Analysis", "Fourier analysis",
        "Energy conservation in Fourier series.",
        r"\int_{-\pi}^{\pi} |f(x)|^2 dx = \sum_{n=-\infty}^\infty |\hat{f}(n)|^2",
        "∫_{-π}^{π} |f(x)|² dx = Σ |f̂(n)|²",
        "L² functions", "f,x,n",
        "theorem", "proven", "Marc-Antoine Parseval (1799)",
        "curated_v7", 4, 1799, "Marc-Antoine Parseval"),
    
    ("Wedderburn's little theorem", "Algebra", "Ring theory",
        "Finite division rings are fields.",
        r"R \text{ finite division ring } \Rightarrow R \text{ field}",
        "R finite division ring ⇒ R field",
        "ring theory", "R",
        "theorem", "proven", "Joseph Wedderburn (1905)",
        "curated_v7", 4, 1905, "Joseph Wedderburn"),
    
    ("Gauss-Bonnet-Chern theorem", "Geometry", "Differential geometry",
        "Total curvature relates to Euler characteristic.",
        r"\int_M \text{Pf}(\Omega) = \chi(M)",
        "∫ₘ Pf(Ω) = χ(M)",
        "even-dimensional oriented manifold", "Pf,Ω,χ,M",
        "theorem", "proven", "Shiing-Shen Chern (1944)",
        "curated_v7", 5, 1944, "Shiing-Shen Chern"),
    
    ("Dirichlet's theorem on arithmetic progressions", "Number theory", "Analytic number theory",
        "Infinitely many primes in arithmetic progression.",
        r"\text{primes } \equiv a \pmod d \text{ infinite if } \gcd(a,d)=1",
        "primes ≡ a (mod d) infinite if gcd(a,d)=1",
        "arithmetic progression", "a,d",
        "theorem", "proven", "Johann Dirichlet (1837)",
        "curated_v7", 5, 1837, "Johann Dirichlet"),
    
    ("Martingale convergence theorem", "Probability", "Stochastic processes",
        "L¹-bounded martingales converge almost surely.",
        r"M_n \to M_\infty \text{ a.s. if } \sup_n E[|M_n|] < \infty",
        "Mₙ → M_∞ a.s. if supₙ E[|Mₙ|] < ∞",
        "martingale", "M,E",
        "theorem", "proven", "Joseph Doob (1940)",
        "curated_v7", 5, 1940, "Joseph Doob"),
    
    ("Peano axiom 1: Zero is natural", "Foundations", "Arithmetic",
        "Zero is a natural number.", r"0 \in \mathbb{N}", "0 ∈ ℕ", "", "",
        "axiom", "axiomatic", "Peano (1889)", "curated_v7", 1, 1889, "Giuseppe Peano"),
    
    ("Modus ponens", "Logic", "Propositional logic",
        "From P and P→Q, infer Q.", r"P, P\to Q \vdash Q",
        "P, P → Q ⊢ Q", "", "P,Q", "rule", "axiomatic",
        "Ancient Greece", "curated_v7", 1, -300, "Aristotle (attributed)"),
    
    ("De Morgan's law (conjunction)", "Logic", "Propositional logic",
        "Negation of conjunction equals disjunction of negations.",
        r"\neg(P\land Q)\equiv \neg P\lor\neg Q", "¬(P∧Q) ≡ ¬P∨¬Q",
        "", "P,Q", "theorem", "proven", "De Morgan (1847)",
        "curated_v7", 2, 1847, "Augustus De Morgan"),
    
    ("Quadratic formula", "Algebra", "Polynomial equations",
        "Solutions to ax²+bx+c=0.",
        r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}", "x = (-b±√(b²-4ac))/(2a)",
        "a≠0", "a,b,c,x", "theorem", "proven",
        "Ancient Babylonians", "curated_v7", 2, -2000, "Babylonian mathematicians"),
    
    ("Pythagorean theorem", "Geometry", "Euclidean geometry",
        "a²+b²=c² in a right triangle.", r"a^2+b^2=c^2", "a²+b²=c²",
        "right triangle, legs a,b, hyp c", "a,b,c", "theorem",
        "proven", "Pythagoras (attributed)", "curated_v7", 2,
        -500, "Pythagoras"),
    
    ("Central limit theorem", "Probability", "Limit theorems",
        "Standardized sample mean converges to standard normal.",
        r"\frac{\bar X_n-\mu}{\sigma/\sqrt n}\xrightarrow{d}N(0,1)",
        "(X̄ₙ-μ)/(σ/√n) →ᵈ N(0,1)", "Xᵢ i.i.d., finite mean/variance",
        "X,n,μ,σ", "theorem", "proven",
        "Pierre-Simon Laplace (1810)", "curated_v7", 5,
        1810, "Pierre-Simon Laplace"),
    
    ("Euler's identity", "Analysis", "Complex analysis",
        "e^(iπ) + 1 = 0.", r"e^{i\pi}+1=0", "e^(iπ)+1 = 0", "",
        "e,i,π", "identity", "proven", "Leonhard Euler (1748)",
        "curated_v7", 3, 1748, "Leonhard Euler"),
]

def main():
    if not DB_FILE.exists():
        print(f"Error: {DB_FILE} not found. Run math_atlas_v7_civilizational.py first.")
        return
    
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    print(f"Adding {len(ACTUAL_FORMULAS)} actual mathematical formulas to v7 database...")
    
    for formula in ACTUAL_FORMULAS:
        try:
            cur.execute("""
                INSERT INTO formulas 
                (name, domain_family, domain, statement, latex, unicode,
                 constraints, variables, provenance, status, proof_status, source,
                 difficulty_level, historical_year, historical_attribution, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))
            """, formula)
            print(f"  Added: {formula[0]}")
        except sqlite3.IntegrityError as e:
            print(f"  Skipped (already exists): {formula[0]}")
    
    conn.commit()
    
    # Verify
    count = cur.execute("SELECT COUNT(*) FROM formulas").fetchone()[0]
    print(f"\nTotal formulas in database: {count}")
    
    conn.close()
    print("\nFormulas added successfully. The v7 civilizational time capsule now contains actual mathematical knowledge.")

if __name__ == "__main__":
    main()
