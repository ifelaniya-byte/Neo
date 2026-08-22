#!/usr/bin/env python3
"""
MATHEMATICAL LANGUAGE ATLAS — v6 ULTRA COMPLETION EXPANSION
================================================================
This expansion builds on v5 (238 formulas) by adding 142 new formulas
across critical gaps: statistical mechanics, cryptography, representation
theory, model theory, homological algebra, algebraic topology, and deeper
coverage of existing domains.

Total after v6: 380 formulas

This file is meant to be merged with the v5 base script by:
1. Appending FORMULAS_EXPANSION_V6 to FORMULAS
2. Appending PROOF_STRATEGIES_V6 to PROOF_STRATEGIES
3. Appending CROSS_DOMAIN_BRIDGE_SPECS_V6 to CROSS_DOMAIN_BRIDGE_SPECS
4. Updating GROWTH_DIRECTIVES and KNOWN_GAPS as shown
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

# ═══════════════════════════════════════════════════════════
# STATISTICAL MECHANICS EXPANSION (18 formulas)
# ═══════════════════════════════════════════════════════════
FORMULAS_EXPANSION_STATISTICAL_MECHANICS = [
    Formula("Boltzmann distribution", "Physics", "Statistical mechanics",
        "Probability of a microstate in canonical ensemble.",
        r"P_i = \frac{e^{-E_i/k_B T}}{Z}", "Pᵢ = e^(-Eᵢ/kₚT)/Z",
        "canonical ensemble", "P,E,k,B,T,Z",
        "law", "proven", "Ludwig Boltzmann (1877)",
        difficulty_level=4, historical_year=1877,
        historical_attribution="Ludwig Boltzmann",
        translations={"es":"Distribución de Boltzmann.",
                      "fr":"Distribution de Boltzmann.",
                      "de":"Boltzmann-Verteilung.",
                      "zh":"玻尔兹曼分布。"}),

    Formula("Partition function (canonical)", "Physics", "Statistical mechanics",
        "Sum over all microstates weighted by Boltzmann factor.",
        r"Z = \sum_i e^{-E_i/k_B T}", "Z = Σ e^(-Eᵢ/kₚT)",
        "canonical ensemble", "Z,E,k,B,T,i",
        "definition", "accepted_without_proof",
        "Josiah Willard Gibbs (1902)", difficulty_level=4,
        historical_year=1902, historical_attribution="Josiah Willard Gibbs"),

    Formula("Helmholtz free energy", "Physics", "Statistical mechanics",
        "Thermodynamic potential from partition function.",
        r"F = -k_B T \ln Z", "F = -kₚT ln Z",
        "canonical ensemble", "F,k,B,T,Z",
        "law", "proven", "Hermann von Helmholtz (1882)",
        difficulty_level=4, historical_year=1882,
        historical_attribution="Hermann von Helmholtz",
        dependencies=["Partition function (canonical)"]),

    Formula("Gibbs entropy formula", "Physics", "Statistical mechanics",
        "Entropy from microstate probabilities.",
        r"S = -k_B \sum_i P_i \ln P_i", "S = -kₚ Σ Pᵢ ln Pᵢ",
        "∑Pᵢ = 1", "S,k,B,P,i",
        "law", "proven", "Josiah Willard Gibbs (1878)",
        difficulty_level=4, historical_year=1878,
        historical_attribution="Josiah Willard Gibbs",
        dependencies=["Shannon entropy"]),

    Formula("Maxwell-Boltzmann distribution", "Physics", "Statistical mechanics",
        "Speed distribution of particles in ideal gas.",
        r"f(v) = 4\pi \left(\frac{m}{2\pi k_B T}\right)^{3/2} v^2 e^{-mv^2/2k_B T}",
        "f(v) = 4π(m/2πkₚT)^(3/2) v² e^(-mv²/2kₚT)",
        "ideal gas, equilibrium", "f,v,m,k,B,T",
        "law", "proven", "James Clerk Maxwell (1860)",
        difficulty_level=4, historical_year=1860,
        historical_attribution="James Clerk Maxwell & Ludwig Boltzmann"),

    Formula("Fermi-Dirac distribution", "Physics", "Statistical mechanics",
        "Occupancy of energy states by fermions.",
        r"f(E) = \frac{1}{e^{(E-\mu)/k_B T} + 1}",
        "f(E) = 1/(e^((E-μ)/kₚT) + 1)",
        "fermions, Pauli exclusion", "f,E,μ,k,B,T",
        "law", "proven", "Enrico Fermi & Paul Dirac (1926)",
        difficulty_level=4, historical_year=1926,
        historical_attribution="Enrico Fermi & Paul Dirac"),

    Formula("Bose-Einstein distribution", "Physics", "Statistical mechanics",
        "Occupancy of energy states by bosons.",
        r"f(E) = \frac{1}{e^{(E-\mu)/k_B T} - 1}",
        "f(E) = 1/(e^((E-μ)/kₚT) - 1)",
        "bosons, no exclusion", "f,E,μ,k,B,T",
        "law", "proven", "Satyendra Bose & Albert Einstein (1924)",
        difficulty_level=4, historical_year=1924,
        historical_attribution="Satyendra Bose & Albert Einstein"),

    Formula("Grand canonical partition function", "Physics", "Statistical mechanics",
        "Partition function with variable particle number.",
        r"\Xi = \sum_{N=0}^\infty e^{\mu N/k_B T} Z_N",
        "Ξ = Σ e^(μN/kₚT) Z_N",
        "grand canonical ensemble", "Ξ,μ,N,k,B,T,Z",
        "definition", "accepted_without_proof",
        "Josiah Willard Gibbs", difficulty_level=5),

    Formula("Landau free energy", "Physics", "Statistical mechanics",
        "Free energy functional for phase transitions.",
        r"F = \int \left[a(T-T_c)\psi^2 + b\psi^4 + \frac{1}{2}K(\nabla\psi)^2\right] dV",
        "F = ∫ [a(T-T_c)ψ² + bψ⁴ + (1/2)K(∇ψ)²] dV",
        "order parameter ψ", "F,a,b,K,T,T_c,ψ",
        "model", "accepted_without_proof",
        "Lev Landau (1937)", difficulty_level=5,
        historical_year=1937, historical_attribution="Lev Landau"),

    Formula("Ising model Hamiltonian", "Physics", "Statistical mechanics",
        "Spin model for ferromagnetism.",
        r"H = -J\sum_{\langle i,j\rangle} \sigma_i \sigma_j - h\sum_i \sigma_i",
        "H = -J Σ σᵢσⱼ - h Σ σᵢ",
        "σᵢ = ±1 spins", "H,J,h,σ",
        "model", "accepted_without_proof",
        "Ernst Ising (1925)", difficulty_level=4,
        historical_year=1925, historical_attribution="Ernst Ising"),

    Formula("Fluctuation-dissipation theorem", "Physics", "Statistical mechanics",
        "Linear response of equilibrium system to perturbation.",
        r"\chi(\omega) = \frac{1}{k_B T} \int_0^\infty \langle A(t)A(0)\rangle e^{i\omega t} dt",
        "χ(ω) = (1/kₚT) ∫ ⟨A(t)A(0)⟩ e^(iωt) dt",
        "equilibrium", "χ,k,B,T,A,ω",
        "theorem", "proven", "Harry Nyquist (1928)",
        difficulty_level=5, historical_year=1928,
        historical_attribution="Harry Nyquist & Herbert Callen"),

    Formula("Kramers-Kronig relations", "Physics", "Statistical mechanics",
        "Real and imaginary parts of causal response functions.",
        r"\chi'(\omega) = \frac{1}{\pi} \mathcal{P}\int_{-\infty}^\infty \frac{\chi''(\omega')}{\omega'-\omega} d\omega'",
        "χ'(ω) = (1/π) P ∫ χ''(ω')/(ω'-ω) dω'",
        "causality", "χ,ω",
        "theorem", "proven", "Ralph Kronig & Hendrik Kramers (1926)",
        difficulty_level=5, historical_year=1926,
        historical_attribution="Ralph Kronig & Hendrik Kramers"),

    Formula("Onsager reciprocal relations", "Physics", "Statistical mechanics",
        "Symmetry of transport coefficients.",
        r"L_{ij} = L_{ji}", "Lᵢⱼ = Lⱼᵢ",
        "time-reversal symmetry", "L,i,j",
        "law", "proven", "Lars Onsager (1931)",
        difficulty_level=5, historical_year=1931,
        historical_attribution="Lars Onsager"),

    Formula("Einstein relation (diffusion)", "Physics", "Statistical mechanics",
        "Diffusion coefficient from mobility.",
        r"D = \mu k_B T", "D = μ kₚ T",
        "Einstein-Smoluchowski", "D,μ,k,B,T",
        "law", "proven", "Albert Einstein (1905)",
        difficulty_level=4, historical_year=1905,
        historical_attribution="Albert Einstein"),

    Formula("Kadanoff block spin", "Physics", "Statistical mechanics",
        "Renormalization group transformation.",
        r"\psi' = b^{-\chi} \sum_{\text{block}} \psi",
        "ψ' = b^(-χ) Σ ψ (block)",
        "scale invariance", "ψ,b,χ",
        "method", "accepted_without_proof",
        "Leo Kadanoff (1966)", difficulty_level=5,
        historical_year=1966, historical_attribution="Leo Kadanoff"),

    Formula("Wilson renormalization group", "Physics", "Statistical mechanics",
        "Flow of coupling constants under scale transformation.",
        r"\frac{dg}{d\ell} = \beta(g)", "dg/dℓ = β(g)",
        "critical phenomena", "g,ℓ,β",
        "theory", "proven", "Kenneth Wilson (1971)",
        difficulty_level=5, historical_year=1971,
        historical_attribution="Kenneth Wilson",
        dependencies=["Kadanoff block spin"]),

    Formula("Liouville's theorem (phase space)", "Physics", "Statistical mechanics",
        "Phase space volume conserved under Hamiltonian flow.",
        r"\frac{d\rho}{dt} = \{\rho, H\} = 0", "dρ/dt = {ρ,H} = 0",
        "Hamiltonian dynamics", "ρ,H",
        "theorem", "proven", "Joseph Liouville (1838)",
        difficulty_level=4, historical_year=1838,
        historical_attribution="Joseph Liouville"),

    Formula("BBGKY hierarchy", "Physics", "Statistical mechanics",
        "Hierarchical equations for correlation functions.",
        r"\frac{\partial f_N}{\partial t} + \{f_N, H_N\} = \sum_{i=1}^N \int d\mathbf{x}_{N+1} \frac{\partial V_{i,N+1}}{\partial \mathbf{x}_i} \cdot \frac{\partial f_{N+1}}{\partial \mathbf{p}_i}",
        "∂f_N/∂t + {f_N,H_N} = Σ ∫ ∂V/∂x · ∂f_{N+1}/∂p",
        "many-body system", "f,N,H,V,x,p",
        "equation", "accepted_without_proof",
        "Bogoliubov, Born, Green, Kirkwood, Yvon", difficulty_level=5),
]

# ═══════════════════════════════════════════════════════════
# CRYPTOGRAPHY EXPANSION (18 formulas)
# ═══════════════════════════════════════════════════════════
FORMULAS_EXPANSION_CRYPTOGRAPHY = [
    Formula("RSA encryption", "Cryptography", "Public-key cryptography",
        "Encryption: c = m^e mod n, Decryption: m = c^d mod n.",
        r"c = m^e \pmod n,\ m = c^d \pmod n", "c = m^e mod n, m = c^d mod n",
        "n = pq, ed ≡ 1 (mod φ(n))", "c,m,e,d,n,p,q",
        "algorithm", "proven", "Rivest, Shamir, Adleman (1977)",
        difficulty_level=4, historical_year=1977,
        historical_attribution="Rivest, Shamir, Adleman",
        dependencies=["Euler's totient theorem", "Fundamental theorem of arithmetic"]),

    Formula("Diffie-Hellman key exchange", "Cryptography", "Key exchange",
        "Shared secret from discrete logarithm problem.",
        r"g^{ab} \pmod p", "g^(ab) mod p",
        "p prime, g generator", "g,a,b,p",
        "protocol", "proven", "Diffie & Hellman (1976)",
        difficulty_level=4, historical_year=1976,
        historical_attribution="Whitfield Diffie & Martin Hellman",
        dependencies=["Discrete logarithm problem"]),

    Formula("ElGamal encryption", "Cryptography", "Public-key cryptography",
        "Public-key encryption based on discrete logarithm.",
        r"c_1 = g^k \pmod p,\ c_2 = m \cdot y^k \pmod p",
        "c₁ = g^k mod p, c₂ = m·y^k mod p",
        "y = g^x mod p", "c₁,c₂,g,k,p,m,y,x",
        "algorithm", "proven", "Taher ElGamal (1985)",
        difficulty_level=4, historical_year=1985,
        historical_attribution="Taher ElGamal",
        dependencies=["Diffie-Hellman key exchange"]),

    Formula("Elliptic curve discrete logarithm", "Cryptography", "Elliptic curve cryptography",
        "Hard problem: find k given P and kP on elliptic curve.",
        r"Q = kP", "Q = kP",
        "P, Q on elliptic curve E(F_p)", "Q,k,P,E,F,p",
        "problem", "open", "Koblitz & Miller (1985)",
        difficulty_level=5, historical_year=1985,
        historical_attribution="Neal Koblitz & Victor Miller"),

    Formula("SHA-256 compression function", "Cryptography", "Hash functions",
        "Core compression in SHA-256 hash algorithm.",
        r"H_i = \Sigma_1(E_i) + Ch(E_i, F_i, G_i) + K_i + W_i + H_{i-1}",
        "Hᵢ = Σ₁(Eᵢ) + Ch(Eᵢ,Fᵢ,Gᵢ) + Kᵢ + Wᵢ + Hᵢ₋₁",
        "Merkle-Damgård construction", "H,E,F,G,K,W",
        "algorithm", "proven", "NSA (2001)",
        difficulty_level=5, historical_year=2001,
        historical_attribution="NSA"),

    Formula("Birthday attack bound", "Cryptography", "Cryptanalysis",
        "Expected collisions after O(√n) samples.",
        r"P(\text{collision}) \approx 1 - e^{-k(k-1)/(2n)}",
        "P(collision) ≈ 1 - e^(-k(k-1)/(2n))",
        "n possible values", "P,k,n",
        "theorem", "proven", "Classical probability",
        difficulty_level=3, dependencies=["Pigeonhole principle"]),

    Formula("Hardy-Littlewood circle method", "Cryptography", "Analytic number theory",
        "Method for analyzing additive problems in integers.",
        r"r(n) = \int_0^1 \left(\sum_{a=1}^n e(a^2 x)\right)^k e(-nx) dx",
        "r(n) = ∫₀¹ (Σ e(a²x))^k e(-nx) dx",
        "Waring's problem", "r,n,a,x,k",
        "method", "proven", "Hardy & Littlewood (1920s)",
        difficulty_level=5, historical_year=1923,
        historical_attribution="G.H. Hardy & J.E. Littlewood"),

    Formula("Goldreich-Levin theorem", "Cryptography", "Hard-core predicates",
        "Hard-core bit from one-way function.",
        r"B(x) = \bigoplus_{i \in S} x_i", "B(x) = ⊕_{i∈S} xᵢ",
        "hard-core predicate", "B,x,S",
        "theorem", "proven", "Oded Goldreich & Leonid Levin (1989)",
        difficulty_level=5, historical_year=1989,
        historical_attribution="Oded Goldreich & Leonid Levin"),

    Formula("Zero-knowledge proof definition", "Cryptography", "Interactive proofs",
        "Completeness, soundness, zero-knowledge properties.",
        r"\text{Pr[V accepts (P,V)]} \ge 1 - \epsilon_{\text{comp}}",
        "Pr[V accepts (P,V)] ≥ 1 - ε_comp",
        "completeness", "P,V,ε",
        "definition", "accepted_without_proof",
        "Goldwasser, Micali, Rackoff (1989)", difficulty_level=5,
        historical_year=1989,
        historical_attribution="Goldwasser, Micali, Rackoff"),

    Formula("Schnorr identification protocol", "Cryptography", "Zero-knowledge proofs",
        "Efficient zero-knowledge identification.",
        r"y = g^x \pmod p,\ r = g^k \pmod p,\ e,\ s = k + ex \pmod q",
        "y = g^x mod p, r = g^k mod p, e, s = k + ex mod q",
        "q divides p-1", "y,g,x,p,r,k,e,s,q",
        "protocol", "proven", "Claus Schnorr (1989)",
        difficulty_level=4, historical_year=1989,
        historical_attribution="Claus Schnorr"),

    Formula("Blum integers", "Cryptography", "Number theory",
        "Product of two primes congruent to 3 mod 4.",
        r"n = pq,\ p \equiv q \equiv 3 \pmod 4", "n = pq, p ≡ q ≡ 3 (mod 4)",
        "special quadratic residues", "n,p,q",
        "definition", "accepted_without_proof",
        "Manuel Blum (1982)", difficulty_level=3,
        historical_year=1982, historical_attribution="Manuel Blum"),

    Formula("Quadratic residuosity problem", "Cryptography", "Number theory",
        "Determine if x is quadratic residue modulo n with unknown factorization.",
        r"x \equiv y^2 \pmod n", "x ≡ y² (mod n)",
        "n = pq, factorization unknown", "x,y,n",
        "problem", "open", "Goldwasser & Micali (1982)",
        difficulty_level=5, historical_year=1982,
        historical_attribution="Goldwasser & Micali"),

    Formula("Lattice-based cryptography basis", "Cryptography", "Post-quantum cryptography",
        "Shortest vector problem in lattices.",
        r"\|\mathbf{v}\| = \min_{\mathbf{w} \in L \setminus \{0\}} \|\mathbf{w}\|",
        "‖v‖ = min_{w∈L\\{0}} ‖w‖",
        "lattice L", "v,w,L",
        "problem", "open", "Ajtai (1996)",
        difficulty_level=5, historical_year=1996,
        historical_attribution="Miklós Ajtai"),

    Formula("Learning with errors", "Cryptography", "Post-quantum cryptography",
        "Distinguish (A, As+e) from uniform.",
        r"\mathbf{s} \in \mathbb{Z}_q^n,\ \mathbf{e} \in \mathbb{Z}_q^m,\ A \in \mathbb{Z}_q^{m \times n}",
        "s ∈ Z_q^n, e ∈ Z_q^m, A ∈ Z_q^{m×n}",
        "small error e", "s,e,A,q,m,n",
        "problem", "open", "Regev (2005)",
        difficulty_level=5, historical_year=2005,
        historical_attribution="Oded Regev"),

    Formula("NTRU encryption", "Cryptography", "Post-quantum cryptography",
        "Lattice-based public-key encryption.",
        r"h = f \cdot g^{-1} \pmod {x^N-1, q}",
        "h = f·g^(-1) mod (x^N-1, q)",
        "polynomial rings", "h,f,g,x,N,q",
        "algorithm", "proven", "Hoffstein, Pipher, Silverman (1998)",
        difficulty_level=5, historical_year=1998,
        historical_attribution="Hoffstein, Pipher, Silverman"),

    Formula("Secret sharing (Shamir)", "Cryptography", "Threshold cryptography",
        "t-out-of-n secret sharing using polynomials.",
        r"f(x) = s + a_1 x + \cdots + a_{t-1} x^{t-1} \pmod p",
        "f(x) = s + a₁x + ... + a_{t-1}x^{t-1} mod p",
        "degree t-1 polynomial", "f,s,a,x,t,p",
        "scheme", "proven", "Adi Shamir (1979)",
        difficulty_level=4, historical_year=1979,
        historical_attribution="Adi Shamir",
        dependencies=["Polynomial interpolation"]),

    Formula("Verifiable secret sharing", "Cryptography", "Threshold cryptography",
        "Secret sharing with verification of shares.",
        r"\sigma_i = f(i),\ \text{commit } C_j = g^{a_j}",
        "σᵢ = f(i), commit Cⱼ = g^{aⱼ}",
        "Feldman protocol", "σ,f,i,C,g,a",
        "protocol", "proven", "Feldman (1987)",
        difficulty_level=5, historical_year=1987,
        historical_attribution="Feldman",
        dependencies=["Secret sharing (Shamir)"]),

    Formula(" oblivious transfer", "Cryptography", "Secure computation",
        "One sender, one receiver, one of two messages received.",
        r"\text{Receiver learns } m_b,\ \text{Sender learns nothing}",
        "Receiver learns m_b, Sender learns nothing",
        "semi-honest model", "m,b",
        "protocol", "proven", "Rabin (1981)",
        difficulty_level=5, historical_year=1981,
        historical_attribution="Michael Rabin"),
]

# ═══════════════════════════════════════════════════════════
# REPRESENTATION THEORY EXPANSION (16 formulas)
# ═══════════════════════════════════════════════════════════
FORMULAS_EXPANSION_REPRESENTATION = [
    Formula("Character orthogonality (first)", "Algebra", "Representation theory",
        "Orthogonality of irreducible characters.",
        r"\frac{1}{|G|} \sum_{g \in G} \chi_i(g) \overline{\chi_j(g)} = \delta_{ij}",
        "(1/|G|) Σ χᵢ(g)χ̄ⱼ(g) = δᵢⱼ",
        "irreducible characters", "χ,G,g,i,j,δ",
        "theorem", "proven", "Ferdinand Georg Frobenius (1896)",
        difficulty_level=5, historical_year=1896,
        historical_attribution="Ferdinand Georg Frobenius"),

    Formula("Character orthogonality (second)", "Algebra", "Representation theory",
        "Orthogonality of class functions.",
        r"\sum_{i=1}^k \chi_i(g) \overline{\chi_i(h)} = \frac{|G|}{|C_G(g)|} \delta_{[g],[h]}",
        "Σ χᵢ(g)χ̄ᵢ(h) = |G|/|C_G(g)| δ_{[g],[h]}",
        "conjugacy classes", "χ,g,h,G,C",
        "theorem", "proven", "Ferdinand Georg Frobenius",
        difficulty_level=5, dependencies=["Character orthogonality (first)"]),

    Formula("Burnside's lemma", "Algebra", "Representation theory",
        "Number of orbits of group action.",
        r"|X/G| = \frac{1}{|G|} \sum_{g \in G} |X^g|",
        "|X/G| = (1/|G|) Σ |X^g|",
        "G acts on X", "X,G,g",
        "theorem", "proven", "William Burnside (1911)",
        difficulty_level=4, historical_year=1911,
        historical_attribution="William Burnside"),

    Formula("Maschke's theorem", "Algebra", "Representation theory",
        "Complete reducibility of representations over characteristic zero.",
        r"V \cong \bigoplus_i V_i", "V ≅ ⊕ Vᵢ",
        "char(K) ∤ |G|", "V,K,G",
        "theorem", "proven", "Heinrich Maschke (1898)",
        difficulty_level=4, historical_year=1898,
        historical_attribution="Heinrich Maschke"),

    Formula("Schur's lemma", "Algebra", "Representation theory",
        "Intertwining operators for irreducible representations.",
        r"\text{If } \phi: V \to W \text{ is } G\text{-equivocal and } V,W \text{ irreducible, then } \phi = 0 \text{ or isomorphism}",
        "If φ: V→W is G-equivariant and V,W irreducible, then φ=0 or isomorphism",
        "algebraically closed field", "φ,V,W,G",
        "theorem", "proven", "Issai Schur (1905)",
        difficulty_level=4, historical_year=1905,
        historical_attribution="Issai Schur"),

    Formula("Schur orthogonality relations", "Algebra", "Representation theory",
        "Matrix elements of irreducible representations.",
        r"\sum_{g \in G} \rho_i(g)_{kl} \overline{\rho_j(g)_{mn}} = \frac{|G|}{d_i} \delta_{ij} \delta_{km} \delta_{ln}",
        "Σ ρᵢ(g)_{kl}ρ̄ⱼ(g)_{mn} = |G|/dᵢ δᵢⱼ δ_{km} δ_{ln}",
        "irreducible representations", "ρ,G,g,d,i,j,k,l,m,n",
        "theorem", "proven", "Issai Schur",
        difficulty_level=5, dependencies=["Schur's lemma"]),

    Formula("Induced representation dimension", "Algebra", "Representation theory",
        "Dimension of induced representation.",
        r"\dim \text{Ind}_H^G V = [G:H] \dim V", "dim Ind_H^G V = [G:H] dim V",
        "H ≤ G", "dim,H,G,V",
        "theorem", "proven", "Georg Frobenius",
        difficulty_level=3),

    Formula("Frobenius reciprocity", "Algebra", "Representation theory",
        "Adjointness of induction and restriction.",
        r"\text{Hom}_G(\text{Ind}_H^G V, W) \cong \text{Hom}_H(V, \text{Res}_H^G W)",
        "Hom_G(Ind_H^G V, W) ≅ Hom_H(V, Res_H^G W)",
        "H ≤ G", "Hom,Ind,Res,H,G,V,W",
        "theorem", "proven", "Georg Frobenius (1898)",
        difficulty_level=5, historical_year=1898,
        historical_attribution="Georg Frobenius"),

    Formula("Peter-Weyl theorem", "Algebra", "Representation theory",
        "Decomposition of functions on compact groups.",
        r"L^2(G) \cong \bigoplus_{\pi \in \hat G} V_\pi \otimes V_\pi^*",
        "L²(G) ≅ ⊕_{π∈Ĝ} V_π ⊗ V_π*",
        "G compact", "L,G,π,V",
        "theorem", "proven", "Fritz Peter & Hermann Weyl (1927)",
        difficulty_level=5, historical_year=1927,
        historical_attribution="Fritz Peter & Hermann Weyl"),

    Formula("Regular representation decomposition", "Algebra", "Representation theory",
        "Regular representation splits into irreducibles.",
        r"\mathbb{C}[G] \cong \bigoplus_i V_i^{\oplus \dim V_i}",
        "ℂ[G] ≅ ⊕ V_i^(⊕ dim V_i)",
        "each V_i appears dim V_i times", "ℂ,G,V,dim",
        "theorem", "proven", "Georg Frobenius",
        difficulty_level=4, dependencies=["Maschke's theorem"]),

    Formula("Group determinant", "Algebra", "Representation theory",
        "Determinant whose factorization gives characters.",
        r"\Theta_G(x) = \det(x_{gh^{-1}})_{g,h \in G}",
        "Θ_G(x) = det(x_{gh^{-1}})_{g,h∈G}",
        "variables indexed by G", "Θ,x,G,h",
        "construction", "accepted_without_proof",
        "Georg Frobenius (1896)", difficulty_level=5,
        historical_year=1896, historical_attribution="Georg Frobenius"),

    Formula("Artin's theorem on induced characters", "Algebra", "Representation theory",
        "Rational characters as linear combinations of induced characters.",
        r"\chi = \sum_i a_i \text{Ind}_{H_i}^G(1)",
        "χ = Σ aᵢ Ind_{Hᵢ}^G(1)",
        "rational characters", "χ,a,Ind,H,G",
        "theorem", "proven", "Emil Artin (1930s)",
        difficulty_level=5, historical_year=1931,
        historical_attribution="Emil Artin"),

    Formula("Brauer's induction theorem", "Algebra", "Representation theory",
        "Every character is linear combination of characters induced from elementary subgroups.",
        r"\chi = \sum_i a_i \text{Ind}_{H_i}^G(\theta_i)",
        "χ = Σ aᵢ Ind_{Hᵢ}^G(θᵢ)",
        "Hᵢ elementary", "χ,a,Ind,H,θ",
        "theorem", "proven", "Richard Brauer (1945)",
        difficulty_level=5, historical_year=1945,
        historical_attribution="Richard Brauer"),

    Formula("Mackey's theorem", "Algebra", "Representation theory",
        "Restriction of induced representation.",
        r"\text{Res}_K^G \text{Ind}_H^G V \cong \bigoplus_{s \in K\backslash G/H} \text{Ind}_{K \cap sHs^{-1}}^K \text{Res}_{H \cap s^{-1}Ks}^H (s \cdot V)",
        "Res_K^G Ind_H^G V ≅ ⊕ Ind_{K∩sHs^{-1}}^K Res_{H∩s^{-1}Ks}^H (s·V)",
        "double cosets", "Res,Ind,K,G,H,s,V",
        "theorem", "proven", "George Mackey (1950s)",
        difficulty_level=5, historical_year=1952,
        historical_attribution="George Mackey"),

    Formula("Clifford theory", "Algebra", "Representation theory",
        "Representations of group with normal subgroup.",
        r"\text{Ind}_N^G \rho = \bigoplus_i \sigma_i",
        "Ind_N^G ρ = ⊕ σᵢ",
        "N ⊴ G", "Ind,N,G,ρ,σ",
        "theory", "proven", "Alfred Clifford (1937)",
        difficulty_level=5, historical_year=1937,
        historical_attribution="Alfred Clifford"),

    Formula("Deligne's theorem on weights", "Algebra", "Representation theory",
        "Decomposition of representations of reductive groups over finite fields.",
        r"R^i f_! \mathcal{F} \text{ is pure of weight } i",
        "Rⁱ f_! ℱ is pure of weight i",
        "ℓ-adic cohomology", "R,f,ℱ,i",
        "theorem", "proven", "Pierre Deligne (1974)",
        difficulty_level=5, historical_year=1974,
        historical_attribution="Pierre Deligne"),
]

# ═══════════════════════════════════════════════════════════
# MODEL THEORY EXPANSION (14 formulas)
# ═══════════════════════════════════════════════════════════
FORMULAS_EXPANSION_MODEL_THEORY = [
    Formula("Compactness theorem", "Logic", "Model theory",
        "A set of sentences has a model iff every finite subset has a model.",
        r"\text{If } \Sigma \text{ is finitely satisfiable, then } \Sigma \text{ is satisfiable}",
        "If Σ is finitely satisfiable, then Σ is satisfiable",
        "first-order logic", "Σ",
        "theorem", "proven", "Kurt Gödel (1930) & Anatoly Maltsev (1936)",
        difficulty_level=5, historical_year=1930,
        historical_attribution="Kurt Gödel & Anatoly Maltsev",
        dependencies=["Completeness theorem"]),

    Formula("Completeness theorem", "Logic", "Model theory",
        "Semantic validity implies syntactic provability.",
        r"\Sigma \models \phi \Rightarrow \Sigma \vdash \phi",
        "Σ ⊨ φ ⇒ Σ ⊢ φ",
        "first-order logic", "Σ,φ",
        "theorem", "proven", "Kurt Gödel (1930)",
        difficulty_level=5, historical_year=1930,
        historical_attribution="Kurt Gödel"),

    Formula("Löwenheim-Skolem (upward)", "Logic", "Model theory",
        "If a theory has infinite model, it has models of all larger cardinalities.",
        r"\text{If } |M| = \kappa \ge |\mathcal{L}|, \text{ then } \exists N: |N| = \lambda > \kappa",
        "If |M| = κ ≥ |ℒ|, then ∃N: |N| = λ > κ",
        "first-order theory", "M,κ,ℒ,N,λ",
        "theorem", "proven", "Leopold Löwenheim (1915) & Thoralf Skolem (1920)",
        difficulty_level=5, historical_year=1915,
        historical_attribution="Leopold Löwenheim & Thoralf Skolem"),

    Formula("Löwenheim-Skolem (downward)", "Logic", "Model theory",
        "If a countable theory has infinite model, it has countable model.",
        r"\text{If } \Sigma \text{ has infinite model, then } \Sigma \text{ has countable model}",
        "If Σ has infinite model, then Σ has countable model",
        "countable language", "Σ",
        "theorem", "proven", "Leopold Löwenheim & Thoralf Skolem",
        difficulty_level=5, dependencies=["Löwenheim-Skolem (upward)"]),

    Formula("Skolem's paradox", "Logic", "Model theory",
        "ZFC has countable model despite proving uncountable sets exist.",
        r"\text{Countable model of ZFC contains sets model thinks are uncountable}",
        "Countable model of ZFC contains sets model thinks are uncountable",
        "relativization of uncountability", "ZFC",
        "paradox", "resolved", "Thoralf Skolem (1922)",
        difficulty_level=5, historical_year=1922,
        historical_attribution="Thoralf Skolem",
        dependencies=["Löwenheim-Skolem (downward)"]),

    Formula("Morley's categoricity theorem", "Logic", "Model theory",
        "Countably categorical first-order theories are totally categorical.",
        r"\text{If } T \text{ is categorical in } \aleph_0, \text{ then } T \text{ categorical in all uncountable } \kappa",
        "If T categorical in ℵ₀, then T categorical in all uncountable κ",
        "first-order theory", "T,κ",
        "theorem", "proven", "Michael Morley (1965)",
        difficulty_level=5, historical_year=1965,
        historical_attribution="Michael Morley",
        dependencies=["Löwenheim-Skolem (upward)"]),

    Formula("Ehrenfeucht-Mostowski theorem", "Logic", "Model theory",
        "Every theory with infinite model has model with definable automorphisms.",
        r"\text{If } T \text{ has infinite model, then } T \text{ has model with infinite definable set}",
        "If T has infinite model, then T has model with infinite definable set",
        "first-order theory", "T",
        "theorem", "proven", "Ehrenfeucht & Mostowski (1956)",
        difficulty_level=5, historical_year=1956,
        historical_attribution="Ehrenfeucht & Mostowski"),

    Formula("Tarski's undefinability theorem", "Logic", "Model theory",
        "Arithmetic truth cannot be defined in arithmetic.",
        r"\text{No formula } \text{True}(x) \text{ in PA such that } \text{True}(\ulcorner \phi \urcorner) \leftrightarrow \phi",
        "No formula True(x) in PA such that True(⌜φ⌝) ↔ φ",
        "Peano arithmetic", "True,φ,PA",
        "theorem", "proven", "Alfred Tarski (1936)",
        difficulty_level=5, historical_year=1936,
        historical_attribution="Alfred Tarski"),

    Formula("Beth definability theorem", "Logic", "Model theory",
        "Implicit definability implies explicit definability.",
        r"\text{If } \phi \text{ implicitly defines } P, \text{ then } \exists \psi: \psi \text{ explicitly defines } P",
        "If φ implicitly defines P, then ∃ψ: ψ explicitly defines P",
        "first-order logic", "φ,P,ψ",
        "theorem", "proven", "Evert Beth (1953)",
        difficulty_level=5, historical_year=1953,
        historical_attribution="Evert Beth"),

    Formula("Craig interpolation theorem", "Logic", "Model theory",
        "If A → B, then ∃C such that A → C and C → B.",
        r"\Sigma \models \phi \Rightarrow \exists \theta: \Sigma \models \theta \land \theta \models \phi",
        "Σ ⊨ φ ⇒ ∃θ: Σ ⊨ θ ∧ θ ⊨ φ",
        "first-order logic", "Σ,φ,θ",
        "theorem", "proven", "William Craig (1957)",
        difficulty_level=5, historical_year=1957,
        historical_attribution="William Craig"),

    Formula("Lyndon's interpolation theorem", "Logic", "Model theory",
        "Interpolant preserving positive/negative atomic formulas.",
        r"\text{If } \phi \to \psi, \text{ then } \exists \theta \text{ with only positive atoms from } \phi, \text{ negative from } \psi",
        "If φ → ψ, then ∃θ with only positive atoms from φ, negative from ψ",
        "first-order logic", "φ,ψ,θ",
        "theorem", "proven", "Roger Lyndon (1959)",
        difficulty_level=5, historical_year=1959,
        historical_attribution="Roger Lyndon",
        dependencies=["Craig interpolation theorem"]),

    Formula("Robinson's joint consistency theorem", "Logic", "Model theory",
        "If theories are individually consistent and intersect consistently, then union is consistent.",
        r"\text{If } T_1, T_2 \text{ consistent and } T_1 \cap T_2 \text{ consistent, then } T_1 \cup T_2 \text{ consistent}",
        "If T₁,T₂ consistent and T₁∩T₂ consistent, then T₁∪T₂ consistent",
        "first-order theories", "T",
        "theorem", "proven", "Abraham Robinson (1956)",
        difficulty_level=5, historical_year=1956,
        historical_attribution="Abraham Robinson",
        dependencies=["Compactness theorem"]),

    Formula("Chang's two-cardinal theorem", "Logic", "Model theory",
        "Characterization of two-cardinal models.",
        r"\text{If } \exists M: |M| = \kappa, |A| = \lambda, \text{ then } \dots",
        "If ∃M: |M| = κ, |A| = λ, then ...",
        "first-order theory", "M,κ,A,λ",
        "theorem", "proven", "Chen Chung Chang (1965)",
        difficulty_level=5, historical_year=1965,
        historical_attribution="Chen Chung Chang"),

    Formula("Keisler-Shelah isomorphism theorem", "Logic", "Model theory",
        "Elementarily equivalent structures have isomorphic ultrapowers.",
        r"A \equiv B \Rightarrow \exists \mathcal{U}: A^{\mathcal{U}} \cong B^{\mathcal{U}}",
        "A ≡ B ⇒ ∃𝒰: A^𝒰 ≅ B^𝒰",
        "first-order structures", "A,B,𝒰",
        "theorem", "proven", "Jerome Keisler & Saharon Shelah (1964)",
        difficulty_level=5, historical_year=1964,
        historical_attribution="Jerome Keisler & Saharon Shelah",
        dependencies=["Compactness theorem"]),
]

# ═══════════════════════════════════════════════════════════
# HOMOLOGICAL ALGEBRA EXPANSION (16 formulas)
# ═══════════════════════════════════════════════════════════
FORMULAS_EXPANSION_HOMOLOGICAL = [
    Formula("Exact sequence definition", "Algebra", "Homological algebra",
        "Sequence where image equals kernel at each step.",
        r"\cdots \to A_{n-1} \xrightarrow{f_{n-1}} A_n \xrightarrow{f_n} A_{n+1} \to \cdots, \ \text{im}(f_{n-1}) = \ker(f_n)",
        "... → A_{n-1} → A_n → A_{n+1} → ..., im(f_{n-1}) = ker(f_n)",
        "abelian category", "A,f,im,ker",
        "definition", "accepted_without_proof",
        "Homological algebra", difficulty_level=3),

    Formula("Short exact sequence", "Algebra", "Homological algebra",
        "0 → A → B → C → 0 with exactness.",
        r"0 \to A \xrightarrow{f} B \xrightarrow{g} C \to 0,\ \text{im}(f) = \ker(g),\ f \text{ injective},\ g \text{ surjective}",
        "0 → A → B → C → 0, im(f) = ker(g), f injective, g surjective",
        "abelian category", "A,B,C,f,g",
        "definition", "accepted_without_proof",
        "Homological algebra", difficulty_level=3,
        dependencies=["Exact sequence definition"]),

    Formula("Snake lemma", "Algebra", "Homological algebra",
        "Long exact sequence from commutative diagram with exact rows.",
        r"\ker(\alpha) \to \ker(\beta) \to \ker(\gamma) \to \text{coker}(\alpha) \to \text{coker}(\beta) \to \text{coker}(\gamma)",
        "ker(α) → ker(β) → ker(γ) → coker(α) → coker(β) → coker(γ)",
        "abelian category", "ker,coker,α,β,γ",
        "theorem", "proven", "Eilenberg & Mac Lane (1942)",
        difficulty_level=5, historical_year=1942,
        historical_attribution="Samuel Eilenberg & Saunders Mac Lane"),

    Formula("Five lemma", "Algebra", "Homological algebra",
        "Isomorphism in commutative diagram with exact rows.",
        r"\text{If outer arrows are isomorphisms, then middle arrow is isomorphism}",
        "If outer arrows are isomorphisms, then middle arrow is isomorphism",
        "abelian category", "",
        "theorem", "proven", "Homological algebra",
        difficulty_level=4, dependencies=["Snake lemma"]),

    Formula("Nine lemma (3×3 lemma)", "Algebra", "Homological algebra",
        "Isomorphism in 3×3 commutative diagram with exact rows/columns.",
        r"\text{If eight of nine squares commute and rows/columns exact, then ninth commutes}",
        "If eight of nine squares commute and rows/columns exact, then ninth commutes",
        "abelian category", "",
        "theorem", "proven", "Homological algebra",
        difficulty_level=4, dependencies=["Five lemma"]),

    Formula("Splitting lemma", "Algebra", "Homological algebra",
        "Characterization of split short exact sequences.",
        r"0 \to A \to B \to C \to 0 \text{ splits } \iff B \cong A \oplus C",
        "0 → A → B → C → 0 splits ⇔ B ≅ A ⊕ C",
        "abelian category", "A,B,C",
        "theorem", "proven", "Homological algebra",
        difficulty_level=4, dependencies=["Short exact sequence"]),

    Formula("Chain complex definition", "Algebra", "Homological algebra",
        "Sequence with d² = 0.",
        r"\cdots \to C_{n+1} \xrightarrow{d_{n+1}} C_n \xrightarrow{d_n} C_{n-1} \to \cdots,\ d_n \circ d_{n+1} = 0",
        "... → C_{n+1} → C_n → C_{n-1} → ..., d_n ∘ d_{n+1} = 0",
        "abelian category", "C,d",
        "definition", "accepted_without_proof",
        "Homological algebra", difficulty_level=3),

    Formula("Homology definition", "Algebra", "Homological algebra",
        "Homology as quotient of kernel by image.",
        r"H_n = \ker(d_n) / \text{im}(d_{n+1})", "H_n = ker(d_n) / im(d_{n+1})",
        "chain complex", "H,d,ker,im",
        "definition", "accepted_without_proof",
        "Homological algebra", difficulty_level=3,
        dependencies=["Chain complex definition"]),

    Formula("Cohomology definition", "Algebra", "Homological algebra",
        "Cohomology as quotient of kernel by image in cochain complex.",
        r"H^n = \ker(d^n) / \text{im}(d^{n-1})", "H^n = ker(d^n) / im(d^{n-1})",
        "cochain complex", "H,d,ker,im",
        "definition", "accepted_without_proof",
        "Homological algebra", difficulty_level=3,
        dependencies=["Chain complex definition"]),

    Formula("Derived functor definition", "Algebra", "Homological algebra",
        "Right/left derived functors via projective/injective resolutions.",
        r"R^nF(A) = H^n(F(P_\bullet)),\ L_nF(A) = H_n(F(I^\bullet))",
        "RⁿF(A) = Hⁿ(F(P_•)), L_nF(A) = H_n(F(I^•))",
        "abelian category", "R,L,F,H,P,I",
        "definition", "accepted_without_proof",
        "Cartan & Eilenberg (1956)", difficulty_level=5,
        historical_year=1956, historical_attribution="Cartan & Eilenberg"),

    Formula("Ext functor", "Algebra", "Homological algebra",
        "Extensions via derived Hom functor.",
        r"\text{Ext}^n(A,B) = R^n\text{Hom}(A,B)",
        "Extⁿ(A,B) = RⁿHom(A,B)",
        "abelian category", "Ext,Hom",
        "definition", "accepted_without_proof",
        "Homological algebra", difficulty_level=4,
        dependencies=["Derived functor definition"]),

    Formula("Tor functor", "Algebra", "Homological algebra",
        "Tensor product derived functor.",
        r"\text{Tor}_n(A,B) = L_n(A \otimes B)",
        "Tor_n(A,B) = L_n(A ⊗ B)",
        "R-mod", "Tor,⊗",
        "definition", "accepted_without_proof",
        "Homological algebra", difficulty_level=4,
        dependencies=["Derived functor definition"]),

    Formula("Universal coefficient theorem", "Algebra", "Homological algebra",
        "Homology with coefficients related to integral homology.",
        r"0 \to \text{Ext}(H_{n-1}(X),G) \to H_n(X;G) \to \text{Hom}(H_n(X),G) \to 0",
        "0 → Ext(H_{n-1}(X),G) → H_n(X;G) → Hom(H_n(X),G) → 0",
        "abelian groups", "Ext,H,Hom,X,G",
        "theorem", "proven", "Eilenberg & Mac Lane",
        difficulty_level=5, historical_year=1942,
        historical_attribution="Eilenberg & Mac Lane",
        dependencies=["Ext functor"]),

    Formula("Künneth formula", "Algebra", "Homological algebra",
        "Homology of product space.",
        r"H_n(X \times Y) \cong \bigoplus_{i+j=n} H_i(X) \otimes H_j(Y) \oplus \bigoplus_{i+j=n-1} \text{Tor}(H_i(X), H_j(Y))",
        "H_n(X×Y) ≅ ⊕_{i+j=n} H_i(X)⊗H_j(Y) ⊕ ⊕_{i+j=n-1} Tor(H_i(X),H_j(Y))",
        "topological spaces", "H,X,Y,⊗,Tor",
        "theorem", "proven", "Heinrich Künneth (1922)",
        difficulty_level=5, historical_year=1922,
        historical_attribution="Heinrich Künneth",
        dependencies=["Tor functor"]),

    Formula("Grothendieck spectral sequence", "Algebra", "Homological algebra",
        "Spectral sequence for composition of derived functors.",
        r"E^2_{p,q} = R^p G (R^q F (A)) \Rightarrow R^{p+q} (G \circ F) (A)",
        "E²_{p,q} = R^pG(R^qF(A)) ⇒ R^{p+q}(G∘F)(A)",
        "abelian categories", "E,R,G,F,A",
        "theorem", "proven", "Alexander Grothendieck (1957)",
        difficulty_level=5, historical_year=1957,
        historical_attribution="Alexander Grothendieck",
        dependencies=["Derived functor definition"]),

    Formula("Leray-Serre spectral sequence", "Algebra", "Homological algebra",
        "Spectral sequence for fibration.",
        r"E^2_{p,q} = H_p(B; H_q(F)) \Rightarrow H_{p+q}(E)",
        "E²_{p,q} = H_p(B; H_q(F)) ⇒ H_{p+q}(E)",
        "fibration F → E → B", "E,H,B,F",
        "theorem", "proven", "Jean Leray (1946) & Jean-Pierre Serre (1951)",
        difficulty_level=5, historical_year=1946,
        historical_attribution="Jean Leray & Jean-Pierre Serre",
        dependencies=["Grothendieck spectral sequence"]),
]

# ═══════════════════════════════════════════════════════════
# ALGEBRAIC TOPOLOGY EXPANSION (18 formulas)
# ═══════════════════════════════════════════════════════════
FORMULAS_EXPANSION_ALGEBRAIC_TOPOLOGY = [
    Formula("Fundamental group definition", "Topology", "Algebraic topology",
        "Homotopy classes of loops based at point.",
        r"\pi_1(X,x_0) = \{[\gamma] : \gamma: [0,1] \to X, \gamma(0)=\gamma(1)=x_0\}",
        "π₁(X,x₀) = {[γ] : γ: [0,1] → X, γ(0)=γ(1)=x₀}",
        "topological space", "π,X,x,γ",
        "definition", "accepted_without_proof",
        "Henri Poincaré (1895)", difficulty_level=4,
        historical_year=1895, historical_attribution="Henri Poincaré"),

    Formula("Van Kampen theorem", "Topology", "Algebraic topology",
        "Fundamental group of union via free product with amalgamation.",
        r"\pi_1(X) \cong \pi_1(U) *_{\pi_1(U \cap V)} \pi_1(V)",
        "π₁(X) ≅ π₁(U) *_{π₁(U∩V)} π₁(V)",
        "X = U ∪ V, U∩V path-connected", "π,U,V",
        "theorem", "proven", "Egbert van Kampen (1933)",
        difficulty_level=5, historical_year=1933,
        historical_attribution="Egbert van Kampen",
        dependencies=["Fundamental group definition"]),

    Formula("Covering space lifting criterion", "Topology", "Algebraic topology",
        "Lift exists iff induced map on fundamental groups factors.",
        r"\tilde{f} \text{ exists } \iff f_*(\pi_1(X,x_0)) \subseteq p_*(\pi_1(\tilde{X},\tilde{x}_0))",
        "f̃ exists ⇔ f_*(π₁(X,x₀)) ⊆ p_*(π₁(ÃX,ãx₀))",
        "covering space p: ÃX → X", "f,p,π",
        "theorem", "proven", "Algebraic topology",
        difficulty_level=4, dependencies=["Fundamental group definition"]),

    Formula("Higher homotopy groups", "Topology", "Algebraic topology",
        "Homotopy classes of maps from spheres.",
        r"\pi_n(X,x_0) = \{[f] : f: (S^n, s_0) \to (X, x_0)\}",
        "π_n(X,x₀) = {[f] : f: (S^n, s₀) → (X, x₀)}",
        "topological space", "π,X,x,f,S",
        "definition", "accepted_without_proof",
        "Witold Hurewicz (1935)", difficulty_level=4,
        historical_year=1935, historical_attribution="Witold Hurewicz"),

    Formula("Hurewicz theorem", "Topology", "Algebraic topology",
        "First nontrivial homotopy group isomorphic to first nontrivial homology.",
        r"\pi_k(X) \cong H_k(X) \text{ for } k \le n \text{ if } \pi_1 = \cdots = \pi_{n-1} = 0",
        "π_k(X) ≅ H_k(X) for k ≤ n if π₁ = ... = π_{n-1} = 0",
        "simply-connected space", "π,H,X,k,n",
        "theorem", "proven", "Witold Hurewicz (1935)",
        difficulty_level=5, historical_year=1935,
        historical_attribution="Witold Hurewicz",
        dependencies=["Higher homotopy groups"]),

    Formula("Whitehead theorem", "Topology", "Algebraic topology",
        "Weak homotopy equivalence between CW complexes is homotopy equivalence.",
        r"f: X \to Y \text{ weak equivalence } \Rightarrow f \text{ homotopy equivalence}",
        "f: X → Y weak equivalence ⇒ f homotopy equivalence",
        "CW complexes", "f,X,Y",
        "theorem", "proven", "J.H.C. Whitehead (1949)",
        difficulty_level=5, historical_year=1949,
        historical_attribution="J.H.C. Whitehead",
        dependencies=["Higher homotopy groups"]),

    Formula("Simplicial homology definition", "Topology", "Algebraic topology",
        "Homology of simplicial complex via chain complex.",
        r"H_n(K) = \ker(\partial_n) / \text{im}(\partial_{n+1})",
        "H_n(K) = ker(∂_n) / im(∂_{n+1})",
        "simplicial complex K", "H,K,∂",
        "definition", "accepted_without_proof",
        "Algebraic topology", difficulty_level=4,
        dependencies=["Chain complex definition"]),

    Formula("Singular homology definition", "Topology", "Algebraic topology",
        "Homology via singular simplices.",
        r"H_n(X) = \ker(\partial_n) / \text{im}(\partial_{n+1})",
        "H_n(X) = ker(∂_n) / im(∂_{n+1})",
        "singular chain complex", "H,X,∂",
        "definition", "accepted_without_proof",
        "Samuel Eilenberg (1944)", difficulty_level=4,
        historical_year=1944, historical_attribution="Samuel Eilenberg"),

    Formula("Excision theorem", "Topology", "Algebraic topology",
        "Relative homology unchanged by excising subset.",
        r"H_n(X \setminus Z, A \setminus Z) \cong H_n(X,A)",
        "H_n(X\\Z, A\\Z) ≅ H_n(X,A)",
        "Z ⊂ int(A)", "H,X,A,Z",
        "theorem", "proven", "Algebraic topology",
        difficulty_level=5, dependencies=["Singular homology definition"]),

    Formula("Mayer-Vietoris sequence", "Topology", "Algebraic topology",
        "Long exact sequence for union of subspaces.",
        r"\cdots \to H_n(A \cap B) \to H_n(A) \oplus H_n(B) \to H_n(X) \to H_{n-1}(A \cap B) \to \cdots",
        "... → H_n(A∩B) → H_n(A)⊕H_n(B) → H_n(X) → H_{n-1}(A∩B) → ...",
        "X = A ∪ B", "H,A,B,X",
        "theorem", "proven", "Walther Mayer (1929) & Leopold Vietoris (1927)",
        difficulty_level=5, historical_year=1927,
        historical_attribution="Walther Mayer & Leopold Vietoris",
        dependencies=["Singular homology definition"]),

    Formula("Brouwer degree", "Topology", "Algebraic topology",
        "Homotopy invariant for maps S^n → S^n.",
        r"\deg(f) = \sum_{x \in f^{-1}(y)} \text{sign}(\det Df(x))",
        "deg(f) = Σ_{x∈f⁻¹(y)} sign(det Df(x))",
        "f: S^n → S^n", "deg,f,x,y",
        "definition", "accepted_without_proof",
        "L.E.J. Brouwer (1911)", difficulty_level=4,
        historical_year=1911, historical_attribution="L.E.J. Brouwer"),

    Formula("Homotopy groups of spheres", "Topology", "Algebraic topology",
        "Structure of π_n(S^k).",
        r"\pi_n(S^k) = \begin{cases} \mathbb{Z} & n = k \\ \mathbb{Z}_2 & n = k+1, k \ge 3 \\ \text{finite abelian} & n > k+1 \end{cases}",
        "π_n(S^k) = ℤ if n=k, ℤ₂ if n=k+1,k≥3, finite abelian if n>k+1",
        "stable range", "π,S,n,k",
        "theorem", "proven", "Various (Serre, Freudenthal)",
        difficulty_level=5, dependencies=["Higher homotopy groups"]),

    Formula("Cellular approximation theorem", "Topology", "Algebraic topology",
        "Maps between CW complexes homotopic to cellular maps.",
        r"f: X \to Y \text{ homotopic to cellular map}",
        "f: X → Y homotopic to cellular map",
        "CW complexes", "f,X,Y",
        "theorem", "proven", "Algebraic topology",
        difficulty_level=4),

    Formula("Eilenberg-Steenrod axioms", "Topology", "Algebraic topology",
        "Axioms characterizing homology theories.",
        r"\text{Functoriality, homotopy invariance, exactness, excision, dimension axiom}",
        "Functoriality, homotopy invariance, exactness, excision, dimension axiom",
        "homology theory", "",
        "axioms", "proven", "Eilenberg & Steenrod (1952)",
        difficulty_level=5, historical_year=1952,
        historical_attribution="Samuel Eilenberg & Norman Steenrod"),

    Formula("Cohomology ring structure", "Topology", "Algebraic topology",
        "Cup product gives ring structure on cohomology.",
        r"\smile: H^p(X) \times H^q(X) \to H^{p+q}(X)",
        "∪: H^p(X) × H^q(X) → H^{p+q}(X)",
        "cohomology", "H,X",
        "theorem", "proven", "Algebraic topology",
        difficulty_level=4, dependencies=["Cohomology definition"]),

    Formula("Poincaré duality", "Topology", "Algebraic topology",
        "Homology-cohomology duality for manifolds.",
        r"H^k(M) \cong H_{n-k}(M)",
        "H^k(M) ≅ H_{n-k}(M)",
        "closed oriented n-manifold", "H,M,n,k",
        "theorem", "proven", "Henri Poincaré (1895)",
        difficulty_level=5, historical_year=1895,
        historical_attribution="Henri Poincaré",
        dependencies=["Cohomology ring structure"]),

    Formula("Alexander duality", "Topology", "Algebraic topology",
        "Duality between homology of subspace and its complement.",
        r"\tilde{H}_k(S^n \setminus A) \cong \tilde{H}^{n-k-1}(A)",
        "H̃_k(S^n\\A) ≅ H̃^{n-k-1}(A)",
        "A ⊂ S^n", "H,S,n,A,k",
        "theorem", "proven", "James Alexander (1915)",
        difficulty_level=5, historical_year=1915,
        historical_attribution="James Alexander",
        dependencies=["Poincaré duality"]),

    Formula("Universal coefficient theorem (cohomology)", "Topology", "Algebraic topology",
        "Cohomology with coefficients from integral cohomology.",
        r"0 \to \text{Ext}(H_{n-1}(X),G) \to H^n(X;G) \to \text{Hom}(H_n(X),G) \to 0",
        "0 → Ext(H_{n-1}(X),G) → H^n(X;G) → Hom(H_n(X),G) → 0",
        "abelian groups", "Ext,H,Hom,X,G",
        "theorem", "proven", "Eilenberg & Mac Lane",
        difficulty_level=5, dependencies=["Ext functor"]),
]

# ═══════════════════════════════════════════════════════════
# DEEPER COVERAGE EXPANSION (42 formulas across existing domains)
# ═══════════════════════════════════════════════════════════
FORMULAS_EXPANSION_DEEPER = [
    # Deeper Analysis (8)
    Formula("Parseval's identity", "Analysis", "Fourier analysis",
        "Energy conservation in Fourier series.",
        r"\int_{-\pi}^{\pi} |f(x)|^2 dx = \sum_{n=-\infty}^\infty |\hat{f}(n)|^2",
        "∫_{-π}^{π} |f(x)|² dx = Σ |f̂(n)|²",
        "L² functions", "f,x,n",
        "theorem", "proven", "Marc-Antoine Parseval (1799)",
        difficulty_level=4, historical_year=1799,
        historical_attribution="Marc-Antoine Parseval",
        dependencies=["Fourier decomposition of sound"]),

    Formula("Plancherel theorem", "Analysis", "Fourier analysis",
        "L² isometry of Fourier transform.",
        r"\int_{-\infty}^\infty |f(x)|^2 dx = \int_{-\infty}^\infty |\hat{f}(\xi)|^2 d\xi",
        "∫ |f(x)|² dx = ∫ |f̂(ξ)|² dξ",
        "L²(R)", "f,x,ξ",
        "theorem", "proven", "Michel Plancherel (1910)",
        difficulty_level=4, historical_year=1910,
        historical_attribution="Michel Plancherel",
        dependencies=["Parseval's identity"]),

    Formula("Wiener-Khinchin theorem", "Analysis", "Signal processing",
        "Power spectral density equals autocorrelation Fourier transform.",
        r"S(\omega) = \int_{-\infty}^\infty R(\tau) e^{-i\omega\tau} d\tau",
        "S(ω) = ∫ R(τ) e^(-iωτ) dτ",
        "stationary process", "S,ω,R,τ",
        "theorem", "proven", "Norbert Wiener (1930) & Aleksandr Khinchin (1934)",
        difficulty_level=5, historical_year=1930,
        historical_attribution="Norbert Wiener & Aleksandr Khinchin"),

    Formula("Hilbert transform", "Analysis", "Harmonic analysis",
        "Singular integral operator conjugate to harmonic function.",
        r"(Hf)(x) = \frac{1}{\pi} \text{p.v.} \int_{-\infty}^\infty \frac{f(t)}{x-t} dt",
        "(Hf)(x) = (1/π) p.v. ∫ f(t)/(x-t) dt",
        "L²(R)", "H,f,x,t",
        "operator", "proven", "David Hilbert (1905)",
        difficulty_level=5, historical_year=1905,
        historical_attribution="David Hilbert"),

    Formula(" Calderón-Zygmund decomposition", "Analysis", "Harmonic analysis",
        "Decomposition of function into good and bad parts.",
        r"f = g + b",
        "f = g + b",
        "L¹(R^n)", "f,g,b",
        "theorem", "proven", "Alberto Calderón & Antoni Zygmund (1952)",
        difficulty_level=5, historical_year=1952,
        historical_attribution="Alberto Calderón & Antoni Zygmund"),

    Formula("Riesz-Thorin interpolation", "Analysis", "Functional analysis",
        "Boundedness of linear operators between L^p spaces.",
        r"\|T\|_{L^{p_\theta} \to L^{q_\theta}} \le \|T\|_{L^{p_0} \to L^{q_0}}^{1-\theta} \|T\|_{L^{p_1} \to L^{q_1}}^\theta",
        "‖T‖_{L^{p_θ}→L^{q_θ}} ≤ ‖T‖_{L^{p_0}→L^{q_0}}^{1-θ} ‖T‖_{L^{p_1}→L^{q_1}}^θ",
        "linear operator", "T,p,q,θ",
        "theorem", "proven", "Marcel Riesz (1926) & Gábor Szegő (1939)",
        difficulty_level=5, historical_year=1926,
        historical_attribution="Marcel Riesz & Gábor Szegő"),

    Formula("Marcinkiewicz interpolation", "Analysis", "Functional analysis",
        "Weak-type boundedness implies strong-type boundedness.",
        r"T: L^{p_0} \to L^{q_0,\infty},\ L^{p_1} \to L^{q_1,\infty} \Rightarrow T: L^{p_\theta} \to L^{q_\theta}",
        "T: L^{p_0}→L^{q_0,∞}, L^{p_1}→L^{q_1,∞} ⇒ T: L^{p_θ}→L^{q_θ}",
        "sublinear operator", "T,p,q,θ",
        "theorem", "proven", "Józef Marcinkiewicz (1939)",
        difficulty_level=5, historical_year=1939,
        historical_attribution="Józef Marcinkiewicz"),

    Formula("Bounded inverse theorem", "Analysis", "Functional analysis",
        "Bijective bounded operator has bounded inverse.",
        r"T \text{ bijective bounded } \Rightarrow T^{-1} \text{ bounded}",
        "T bijective bounded ⇒ T⁻¹ bounded",
        "Banach spaces", "T",
        "theorem", "proven", "Stefan Banach",
        difficulty_level=4, dependencies=["Open mapping theorem"]),

    # Deeper Algebra (8)
    Formula("Wedderburn's little theorem", "Algebra", "Ring theory",
        "Finite division rings are fields.",
        r"R \text{ finite division ring } \Rightarrow R \text{ field}",
        "R finite division ring ⇒ R field",
        "ring theory", "R",
        "theorem", "proven", "Joseph Wedderburn (1905)",
        difficulty_level=4, historical_year=1905,
        historical_attribution="Joseph Wedderburn"),

    Formula("Artin-Wedderburn theorem", "Algebra", "Ring theory",
        "Semisimple rings decompose into matrix rings over division rings.",
        r"R \cong \bigoplus_i M_{n_i}(D_i)",
        "R ≅ ⊕ M_{n_i}(D_i)",
        "semisimple ring", "R,M,D",
        "theorem", "proven", "Emil Artin & Joseph Wedderburn (1927)",
        difficulty_level=5, historical_year=1927,
        historical_attribution="Emil Artin & Joseph Wedderburn",
        dependencies=["Wedderburn's little theorem"]),

    Formula("Jordan-Hölder theorem", "Algebra", "Group theory",
        "Composition series length and factors unique up to permutation.",
        r"G = G_0 \triangleright G_1 \triangleright \cdots \triangleright G_n = \{e\}",
        "G = G₀ ⊳ G₁ ⊳ ... ⊳ G_n = {e}",
        "finite group", "G",
        "theorem", "proven", "Camille Jordan (1870) & Otto Hölder (1889)",
        difficulty_level=4, historical_year=1870,
        historical_attribution="Camille Jordan & Otto Hölder"),

    Formula("Sylow theorems (complete)", "Algebra", "Group theory",
        "Existence, conjugacy, and number of Sylow p-subgroups.",
        r"n_p \equiv 1 \pmod p,\ n_p \mid |G|/p^k",
        "n_p ≡ 1 (mod p), n_p | |G|/p^k",
        "finite group", "n,p,G,k",
        "theorem", "proven", "Ludwig Sylow (1872)",
        difficulty_level=4, historical_year=1872,
        historical_attribution="Ludwig Sylow",
        dependencies=["Lagrange's theorem (groups)"]),

    Formula("Structure theorem for finitely generated modules", "Algebra", "Module theory",
        "Decomposition into invariant factors or elementary divisors.",
        r"M \cong R^r \oplus \bigoplus_i R/(d_i)",
        "M ≅ R^r ⊕ ⊕ R/(d_i)",
        "PID R", "M,R,d",
        "theorem", "proven", "Module theory",
        difficulty_level=5, historical_year=1860s,
        historical_attribution="Various (Smith, Kronecker)"),

    Formula("Chinese remainder theorem (general)", "Algebra", "Ring theory",
        "Isomorphism for comaximal ideals.",
        r"R/(I_1 \cap \cdots \cap I_n) \cong R/I_1 \times \cdots \times R/I_n",
        "R/(I₁∩...∩I_n) ≅ R/I₁ × ... × R/I_n",
        "comaximal ideals", "R,I",
        "theorem", "proven", "Ring theory",
        difficulty_level=4, dependencies=["Chinese remainder theorem"]),

    Formula("Nakayama's lemma", "Algebra", "Commutative algebra",
        "Module generation by lifting from quotient.",
        r"M = IM \Rightarrow M = 0 \text{ or } I \text{ contained in Jacobson radical}",
        "M = IM ⇒ M = 0 or I contained in Jacobson radical",
        "finitely generated module", "M,I",
        "theorem", "proven", "Tadashi Nakayama (1951)",
        difficulty_level=5, historical_year=1951,
        historical_attribution="Tadashi Nakayama"),

    Formula("Krull's height theorem", "Algebra", "Commutative algebra",
        "Height of ideal generated by n elements ≤ n.",
        r"\text{ht}(I) \le n \text{ if } I = (f_1, \ldots, f_n)",
        "ht(I) ≤ n if I = (f₁,...,f_n)",
        "Noetherian ring", "ht,I,f",
        "theorem", "proven", "Wolfgang Krull (1928)",
        difficulty_level=5, historical_year=1928,
        historical_attribution="Wolfgang Krull"),

    # Deeper Geometry (8)
    Formula("Gauss-Bonnet-Chern theorem", "Geometry", "Differential geometry",
        "Generalization of Gauss-Bonnet to higher dimensions.",
        r"\int_M \text{Pf}(\Omega) = \chi(M)",
        "∫_M Pf(Ω) = χ(M)",
        "even-dimensional oriented manifold", "Pf,Ω,χ,M",
        "theorem", "proven", "Shiing-Shen Chern (1944)",
        difficulty_level=5, historical_year=1944,
        historical_attribution="Shiing-Shen Chern",
        dependencies=["Gauss-Bonnet theorem (2D)"]),

    Formula("De Rham cohomology", "Geometry", "Differential geometry",
        "Cohomology from closed vs exact differential forms.",
        r"H^k_{dR}(M) = \frac{\{\omega: d\omega = 0\}}{\{\omega = d\eta\}}",
        "H^k_{dR}(M) = {ω: dω=0}/{ω=dη}",
        "smooth manifold", "H,ω,d,M",
        "definition", "accepted_without_proof",
        "Georges de Rham (1931)", difficulty_level=4,
        historical_year=1931, historical_attribution="Georges de Rham"),

    Formula("Hodge decomposition", "Geometry", "Differential geometry",
        "Decomposition of forms into harmonic, exact, and coexact.",
        r"\Omega^k = \mathcal{H}^k \oplus d\Omega^{k-1} \oplus d^*\Omega^{k+1}",
        "Ω^k = ℋ^k ⊕ dΩ^{k-1} ⊕ d*Ω^{k+1}",
        "compact Riemannian manifold", "Ω,ℋ,d",
        "theorem", "proven", "William Hodge (1930s)",
        difficulty_level=5, historical_year=1935,
        historical_attribution="William Hodge",
        dependencies=["De Rham cohomology"]),

    Formula("Frobenius theorem (distributions)", "Geometry", "Differential geometry",
        "Integrability condition for distributions.",
        r"[X,Y] \in \mathcal{D} \text{ for all } X,Y \in \mathcal{D}",
        "[X,Y] ∈ D for all X,Y ∈ D",
        "involutory distribution", "X,Y,D",
        "theorem", "proven", "Ferdinand Georg Frobenius (1877)",
        difficulty_level=5, historical_year=1877,
        historical_attribution="Ferdinand Georg Frobenius"),

    Formula("Darboux's theorem", "Geometry", "Symplectic geometry",
        "Local canonical coordinates for symplectic forms.",
        r"\omega = \sum_i dq_i \wedge dp_i",
        "ω = Σ dq_i ∧ dp_i",
        "symplectic manifold", "ω,q,p",
        "theorem", "proven", "Gaston Darboux (1882)",
        difficulty_level=4, historical_year=1882,
        historical_attribution="Gaston Darboux"),

    Formula("Morse lemma", "Geometry", "Differential topology",
        "Local normal form for nondegenerate critical points.",
        r"f(x) = f(x_0) - x_1^2 - \cdots - x_\lambda^2 + x_{\lambda+1}^2 + \cdots + x_n^2",
        "f(x) = f(x₀) - x₁² - ... - x_λ² + x_{λ+1}² + ... + x_n²",
        "nondegenerate critical point", "f,x,λ",
        "theorem", "proven", "Marston Morse (1925)",
        difficulty_level=4, historical_year=1925,
        historical_attribution="Marston Morse"),

    Formula("Whitney embedding theorem", "Geometry", "Differential topology",
        "Smooth manifold embeds in Euclidean space.",
        r"M^n \hookrightarrow \mathbb{R}^{2n}",
        "M^n ↪ ℝ^{2n}",
        "smooth manifold", "M,n",
        "theorem", "proven", "Hassler Whitney (1936)",
        difficulty_level=5, historical_year=1936,
        historical_attribution="Hassler Whitney"),

    Formula("Whitney immersion theorem", "Geometry", "Differential topology",
        "Smooth manifold immerses in Euclidean space.",
        r"M^n \hookrightarrow \mathbb{R}^{2n-1}",
        "M^n ↪ ℝ^{2n-1}",
        "smooth manifold", "M,n",
        "theorem", "proven", "Hassler Whitney (1944)",
        difficulty_level=5, historical_year=1944,
        historical_attribution="Hassler Whitney",
        dependencies=["Whitney embedding theorem"]),

    # Deeper Number Theory (8)
    Formula("Dirichlet's theorem on arithmetic progressions", "Number theory", "Analytic number theory",
        "Infinitely many primes in arithmetic progression.",
        r"\text{primes } \equiv a \pmod d \text{ infinite if } \gcd(a,d)=1",
        "primes ≡ a (mod d) infinite if gcd(a,d)=1",
        "arithmetic progression", "a,d",
        "theorem", "proven", "Johann Dirichlet (1837)",
        difficulty_level=5, historical_year=1837,
        historical_attribution="Johann Dirichlet",
        dependencies=["Infinitude of primes"]),

    Formula("Birch and Swinnerton-Dyer conjecture", "Number theory", "Elliptic curves",
        "Rank of elliptic curve related to L-function zero (unproven).",
        r"\text{ord}_{s=1} L(E,s) = \text{rank}(E(\mathbb{Q}))",
        "ord_{s=1} L(E,s) = rank(E(ℚ))",
        "elliptic curve E over ℚ", "L,E,s,rank",
        "conjecture", "open", "Bryan Birch & Peter Swinnerton-Dyer (1960s)",
        difficulty_level=5, historical_year=1965,
        historical_attribution="Bryan Birch & Peter Swinnerton-Dyer"),

    Formula("Modularity theorem", "Number theory", "Elliptic curves",
        "Elliptic curves over ℚ correspond to modular forms.",
        r"E/\mathbb{Q} \text{ modular } \Leftrightarrow E \text{ corresponds to } f \in S_k(\Gamma_0(N))",
        "E/ℚ modular ⇔ E corresponds to f ∈ S_k(Γ₀(N))",
        "elliptic curve", "E,Γ,f,N",
        "theorem", "proven", "Wiles, Taylor, Breuil, Conrad, Diamond (1995-2001)",
        difficulty_level=5, historical_year=1995,
        historical_attribution="Andrew Wiles et al.",
        dependencies=["Fermat's last theorem"]),

    Formula("Sato-Tate conjecture", "Number theory", "Elliptic curves",
        "Distribution of Frobenius eigenvalues follows Sato-Tate measure.",
        r"\frac{1}{\pi} \frac{1}{2} \sin^2\theta \, d\theta",
        "(1/π)(1/2) sin²θ dθ",
        "elliptic curve without CM", "θ",
        "theorem", "proven", "Various (2006-2008)",
        difficulty_level=5, historical_year=2008,
        historical_attribution="Taylor et al."),

    Formula("Langlands program (overview)", "Number theory", "Automorphic forms",
        "Correspondence between Galois representations and automorphic forms.",
        r"\text{Gal}(\overline{\mathbb{Q}}/\mathbb{Q}) \leftrightarrow \text{Automorphic representations}",
        "Gal(ℚ̅/ℚ) ↔ Automorphic representations",
        "non-abelian class field theory", "Gal",
        "program", "open", "Robert Langlands (1967)",
        difficulty_level=5, historical_year=1967,
        historical_attribution="Robert Langlands"),

    Formula("Class field theory (Artin reciprocity)", "Number theory", "Algebraic number theory",
        "One-to-one correspondence between abelian extensions and generalized ideal class groups.",
        r"\text{Gal}(L/K)^{\text{ab}} \cong C_K / N_{L/K} C_L",
        "Gal(L/K)^{ab} ≅ C_K / N_{L/K} C_L",
        "number field K", "Gal,L,K,C",
        "theorem", "proven", "Emil Artin (1924-1927)",
        difficulty_level=5, historical_year=1924,
        historical_attribution="Emil Artin"),

    Formula("Iwasawa theory (main conjecture)", "Number theory", "Algebraic number theory",
        "Relation between p-adic L-functions and Iwasawa modules.",
        r"\text{char}(\varprojlim_n A_n) = f_p(T)",
        "char(lim A_n) = f_p(T)",
        "cyclotomic Z_p-extension", "char,A,f,p,T",
        "theorem", "proven", "Kenkichi Iwasawa (1960s, proved by Mazur-Wiles 1984)",
        difficulty_level=5, historical_year=1984,
        historical_attribution="Kenkichi Iwasawa, Barry Mazur, Andrew Wiles"),

    Formula("ABC conjecture", "Number theory", "Diophantine equations",
        "Relationship between a, b, c in a + b = c (unproven).",
        r"\text{rad}(abc)^{1+\epsilon} > c",
        "rad(abc)^{1+ε} > c",
        "coprime positive integers a,b,c", "rad,ε,c",
        "conjecture", "open", "Joseph Oesterlé & David Masser (1985)",
        difficulty_level=5, historical_year=1985,
        historical_attribution="Joseph Oesterlé & David Masser"),

    # Deeper Probability (10)
    Formula("Martingale convergence theorem", "Probability", "Stochastic processes",
        "L¹-bounded martingales converge almost surely.",
        r"M_n \to M_\infty \text{ a.s. if } \sup_n E[|M_n|] < \infty",
        "M_n → M_∞ a.s. if sup_n E[|M_n|] < ∞",
        "martingale", "M,E",
        "theorem", "proven", "Joseph Doob (1940)",
        difficulty_level=5, historical_year=1940,
        historical_attribution="Joseph Doob"),

    Formula("Doob's optional stopping theorem", "Probability", "Stochastic processes",
        "Stopping martingale at bounded stopping time preserves expectation.",
        r"E[M_\tau] = E[M_0]",
        "E[M_τ] = E[M_0]",
        "bounded stopping time", "M,τ",
        "theorem", "proven", "Joseph Doob",
        difficulty_level=4, dependencies=["Martingale convergence theorem"]),

    Formula("Girsanov theorem", "Probability", "Stochastic calculus",
        "Change of measure for removing drift from diffusion.",
        r"\frac{d\mathbb{Q}}{d\mathbb{P}} = \exp\left(-\int_0^T \theta_s dW_s - \frac{1}{2}\int_0^T \theta_s^2 ds\right)",
        "dQ/dP = exp(-∫ θ_s dW_s - (1/2)∫ θ_s² ds)",
        "continuous filtration", "Q,P,θ,W",
        "theorem", "proven", "Igor Girsanov (1960)",
        difficulty_level=5, historical_year=1960,
        historical_attribution="Igor Girsanov"),

    Formula("Itô's lemma", "Probability", "Stochastic calculus",
        "Chain rule for stochastic processes.",
        r"df(t,X_t) = \frac{\partial f}{\partial t} dt + \frac{\partial f}{\partial x} dX_t + \frac{1}{2} \frac{\partial^2 f}{\partial x^2} d\langle X \rangle_t",
        "df(t,X_t) = (∂f/∂t)dt + (∂f/∂x)dX_t + (1/2)(∂²f/∂x²)d⟨X⟩_t",
        "Itô process", "f,X,t",
        "theorem", "proven", "Kiyoshi Itô (1944)",
        difficulty_level=5, historical_year=1944,
        historical_attribution="Kiyoshi Itô"),

    Formula("Black-Scholes PDE derivation", "Probability", "Financial mathematics",
        "PDE for option prices from risk-neutral valuation.",
        r"\frac{\partial V}{\partial t} + \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 V}{\partial S^2} + rS \frac{\partial V}{\partial S} - rV = 0",
        "∂V/∂t + (1/2)σ²S²∂²V/∂S² + rS∂V/∂S - rV = 0",
        "geometric Brownian motion", "V,t,σ,S,r",
        "theorem", "proven", "Black & Scholes (1973)",
        difficulty_level=5, historical_year=1973,
        historical_attribution="Fischer Black & Myron Scholes",
        dependencies=["Itô's lemma"]),

    Formula("Kolmogorov's three-series theorem", "Probability", "Limit theorems",
        "Necessary and sufficient conditions for convergence of independent random variables.",
        r"\sum P(|X_n| > C) < \infty,\ \sum E[X_n 1_{|X_n| \le C}] \text{ converges},\ \sum \text{Var}(X_n 1_{|X_n| \le C}) < \infty",
        "Σ P(|X_n| > C) < ∞, Σ E[X_n 1_{|X_n|≤C}] converges, Σ Var(X_n 1_{|X_n|≤C}) < ∞",
        "independent X_n", "X,P,E,Var,C",
        "theorem", "proven", "Andrey Kolmogorov (1929)",
        difficulty_level=5, historical_year=1929,
        historical_attribution="Andrey Kolmogorov"),

    Formula("Lévy's continuity theorem", "Probability", "Characteristic functions",
        "Convergence in distribution iff characteristic functions converge.",
        r"X_n \Rightarrow X \iff \varphi_{X_n}(t) \to \varphi_X(t) \text{ for all } t",
        "X_n ⇒ X iff φ_{X_n}(t) → φ_X(t) for all t",
        "random variables", "X,φ",
        "theorem", "proven", "Paul Lévy (1922)",
        difficulty_level=4, historical_year=1922,
        historical_attribution="Paul Lévy"),

    Formula("Cramér's decomposition theorem", "Probability", "Probability theory",
        "Characterization of infinitely divisible distributions.",
        r"X = Y + Z \text{ with } Y,Z \text{ i.i.d.} \Rightarrow X \text{ infinitely divisible}",
        "X = Y + Z with Y,Z i.i.d. ⇒ X infinitely divisible",
        "probability distribution", "X,Y,Z",
        "theorem", "proven", "Harald Cramér (1936)",
        difficulty_level=5, historical_year=1936,
        historical_attribution="Harald Cramér"),

    Formula("Harris recurrence theorem", "Probability", "Markov chains",
        "Regularity condition for Markov chain recurrence.",
        r"\text{Chain is Harris recurrent } \iff \text{ visits sets infinitely often}",
        "Chain is Harris recurrent ⇔ visits sets infinitely often",
        "Markov chain", "",
        "theorem", "proven", "Theodore Harris (1956)",
        difficulty_level=5, historical_year=1956,
        historical_attribution="Theodore Harris"),

    Formula("Doob-Meyer decomposition", "Probability", "Stochastic processes",
        "Decomposition of submartingale into martingale and predictable increasing process.",
        r"X = M + A",
        "X = M + A",
        "submartingale X", "X,M,A",
        "theorem", "proven", "Joseph Doob & Catherine Meyer (1970s)",
        difficulty_level=5, historical_year=1970,
        historical_attribution="Joseph Doob & Catherine Meyer",
        dependencies=["Martingale convergence theorem"]),
]

# ═══════════════════════════════════════════════════════════
# MERGE ALL EXPANSIONS
# ═══════════════════════════════════════════════════════════
FORMULAS_EXPANSION_V6 = (
    FORMULAS_EXPANSION_STATISTICAL_MECHANICS +
    FORMULAS_EXPANSION_CRYPTOGRAPHY +
    FORMULAS_EXPANSION_REPRESENTATION +
    FORMULAS_EXPANSION_MODEL_THEORY +
    FORMULAS_EXPANSION_HOMOLOGICAL +
    FORMULAS_EXPANSION_ALGEBRAIC_TOPOLOGY +
    FORMULAS_EXPANSION_DEEPER
)  # Total: 18 + 18 + 16 + 14 + 16 + 18 + 42 = 142 formulas

# ═══════════════════════════════════════════════════════════
# EXPANDED PROOF STRATEGIES (12 new)
# ═══════════════════════════════════════════════════════════
PROOF_STRATEGIES_V6 = [
    {"name":"Statistical mechanical ensemble averaging","family":"Physics",
     "description":"Derive macroscopic properties from microcanonical/canonical/grand canonical ensembles.",
     "template":"Define ensemble partition function Z. Compute expectation ⟨O⟩ = (1/Z)Σ O e^(-βE). Take thermodynamic limit.",
     "example":"Derive ideal gas law from canonical ensemble.",
     "applicable_domains":"Statistical mechanics, Thermodynamics",
     "metacognitive_applicability":"High for connecting microscopic to macroscopic"},

    {"name":"Cryptographic reduction","family":"Cryptography",
     "description":"Reduce security of scheme to hard problem.",
     "template":"Assume adversary breaks scheme. Construct solver for hard problem using adversary.",
     "example":"Reduce breaking RSA to factoring.",
     "applicable_domains":"Cryptography, Computational complexity",
     "metacognitive_applicability":"Essential for security proofs"},

    {"name":"Character table computation","family":"Algebra",
     "description":"Use orthogonality relations to construct character tables.",
     "template":"Find conjugacy classes. Use orthogonality to solve for character values. Verify with column sums.",
     "example":"Character table of S₃ or A₄.",
     "applicable_domains":"Representation theory, Group theory",
     "metacognitive_applicability":"Standard in representation theory"},

    {"name":"Model-theoretic forcing","family":"Logic",
     "description":"Extend models to satisfy/deny sentences while preserving consistency.",
     "template":"Build generic filter over forcing poset. Extend model via generic extension. Verify truth lemma.",
     "example":"Prove independence of CH from ZFC.",
     "applicable_domains":"Model theory, Set theory",
     "metacognitive_applicability":"High for independence results"},

    {"name":"Diagram chasing in abelian categories","family":"Algebra",
     "description":"Prove results by following morphisms in commutative diagrams.",
     "template":"Use snake lemma, five lemma, or nine lemma. Chase elements through diagram using exactness.",
     "example":"Prove functoriality of homology.",
     "applicable_domains":"Homological algebra, Category theory",
     "metacognitive_applicability":"Fundamental in homological algebra"},

    {"name":"Spectral sequence analysis","family":"Algebra",
     "description":"Compute homology/cohomology via spectral sequence convergence.",
     "template":"Define E^r page. Compute differentials d^r. Take homology to get E^{r+1}. Repeat until convergence.",
     "example":"Serre spectral sequence for fibration.",
     "applicable_domains":"Algebraic topology, Homological algebra",
     "metacognitive_applicability":"Powerful for complex computations"},

    {"name":"Stochastic calculus with Itô's lemma","family":"Probability",
     "description":"Derive dynamics of functions of stochastic processes.",
     "template":"Apply Itô's lemma: df = f_t dt + f_x dX + (1/2)f_xx d⟨X⟩. Handle quadratic variation term.",
     "example":"Derive Black-Scholes PDE.",
     "applicable_domains":"Financial mathematics, Stochastic processes",
     "metacognitive_applicability":"Essential in quantitative finance"},

    {"name":"Martingale method","family":"Probability",
     "description":"Use martingale properties for convergence and limit theorems.",
     "template":"Show process is martingale. Apply optional stopping or convergence theorem. Extract limit.",
     "example":"Prove Galton-Watson extinction probability.",
     "applicable_domains":"Probability, Stochastic processes",
     "metacognitive_applicability":"Versatile for many limit problems"},

    {"name":"L² harmonic analysis","family":"Analysis",
     "description":"Use Fourier transform and Plancherel theorem for L² estimates.",
     "template":"Transform to frequency domain. Use Plancherel for L² isometry. Estimate in frequency domain. Transform back.",
     "example":"Proof of Hausdorff-Young inequality.",
     "applicable_domains":"Harmonic analysis, PDE theory",
     "metacognitive_applicability":"Standard in modern analysis"},

    {"name":"Geometric measure theory blow-up","family":"Geometry",
     "description":"Analyze local structure by scaling and taking limits.",
     "template":"Blow up at point by rescaling. Take limit of rescaled sets/structures. Identify tangent cone.",
     "example":"Tangent cone analysis in minimal surface theory.",
     "applicable_domains":"Geometric measure theory, Minimal surfaces",
     "metacognitive_applicability":"High for local regularity results"},

    {"name":"Probabilistic method in combinatorics","family":"Combinatorics",
     "description":"Show existence via positive probability in random construction.",
     "template":"Define random structure. Compute probability of desired property. Show probability > 0.",
     "example":"Lower bounds on Ramsey numbers.",
     "applicable_domains":"Combinatorics, Graph theory",
     "metacognitive_applicability":"Powerful for existence proofs"},

    {"name":"K-theoretic argument","family":"Algebra",
     "description":"Use algebraic K-theory for structural information about rings.",
     "template":"Compute K₀ or K₁. Use exact sequences and localization. Deduce ring properties.",
     "example": "Projective module classification via K₀.",
     "applicable_domains":"Algebraic K-theory, Ring theory",
     "metacognitive_applicability":"Sophisticated but powerful"},
]

# ═══════════════════════════════════════════════════════════
# ADDITIONAL CROSS-DOMAIN BRIDGES (14 new)
# ═══════════════════════════════════════════════════════════
CROSS_DOMAIN_BRIDGE_SPECS_V6 = [
    ("Boltzmann distribution", "Shannon entropy",
     "mathematical_foundation",
     "Boltzmann distribution maximizes entropy subject to energy constraint, directly connecting statistical mechanics to information theory.",
     0.95),

    ("RSA encryption", "Euler's totient theorem",
     "mathematical_foundation",
     "RSA security directly relies on Euler's totient theorem for its correctness proof.",
     0.98),

    ("Character orthogonality (first)", "Schur's lemma",
     "mathematical_foundation",
     "Character orthogonality relations are proven using Schur's lemma on intertwiners.",
     0.92),

    ("Compactness theorem", "Completeness theorem",
     "mathematical_foundation",
     "Compactness theorem is model-theoretic dual of completeness theorem in first-order logic.",
     0.90),

    ("Snake lemma", "Five lemma",
     "mathematical_foundation",
     "Five lemma is a direct corollary of the more general snake lemma in homological algebra.",
     0.95),

    ("Poincaré duality", "Alexander duality",
     "structural_analogy",
     "Both are duality theorems in algebraic topology: Poincaré for manifolds, Alexander for complements in spheres.",
     0.88),

    ("Itô's lemma", "Chain rule",
     "generalization",
     "Itô's lemma is the stochastic calculus generalization of the deterministic chain rule, with an additional quadratic variation term.",
     0.94),

    ("Girsanov theorem", "Change of measure",
     "generalization",
     "Girsanov theorem is the stochastic process generalization of classical change of measure in probability theory.",
     0.91),

    ("Lévy's continuity theorem", "Central limit theorem",
     "mathematical_foundation",
     "Continuity theorem provides characteristic function convergence machinery used in proving the central limit theorem.",
     0.93),

    ("Hodge decomposition", "De Rham cohomology",
     "mathematical_foundation",
     "Hodge decomposition gives orthogonal decomposition of De Rham cohomology using harmonic forms.",
     0.89),

    ("Wedderburn's little theorem", "Artin-Wedderburn theorem",
     "generalization",
     "Artin-Wedderburn theorem generalizes Wedderburn's little theorem from finite division rings to semisimple rings.",
     0.96),

    ("Dirichlet's theorem on arithmetic progressions", "Prime number theorem",
     "generalization",
     "Dirichlet's theorem extends prime distribution results from all integers to arithmetic progressions.",
     0.87),

    ("ABC conjecture", "Fermat's last theorem",
     "implication",
     "ABC conjecture implies Fermat's last theorem for sufficiently large exponents (FLT already proven).",
     0.85),

    ("Gibbs entropy formula", "Shannon entropy",
     "mathematical_foundation",
     "Gibbs entropy formula in statistical mechanics is the direct precursor to Shannon's information entropy definition.",
     0.97),
]

# ═══════════════════════════════════════════════════════════
# UPDATED GROWTH DIRECTIVES
# ═══════════════════════════════════════════════════════════
# Mark v5 resolved items, add new frontier items
GROWTH_DIRECTIVES_V6_UPDATES = [
    # Mark previously resolved items
    {"directive":"Add statistical mechanics domain (partition function, Boltzmann distribution)","priority":1,"domain":"Physics","status":"resolved_v6"},
    {"directive":"Add cryptography domain (RSA, discrete log, hash security proofs)","priority":1,"domain":"Cryptography","status":"resolved_v6"},
    {"directive":"Add representation theory domain (character theory, group representations)","priority":2,"domain":"Algebra","status":"resolved_v6"},
    {"directive":"Add model theory domain (compactness, completeness, Löwenheim-Skolem)","priority":2,"domain":"Logic","status":"resolved_v6"},
    {"directive":"Add homological algebra domain (exact sequences, homology/cohomology)","priority":2,"domain":"Algebra","status":"resolved_v6"},
    {"directive":"Add algebraic topology domain (homotopy groups, simplicial homology)","priority":2,"domain":"Topology","status":"resolved_v6"},

    # New frontier items
    {"directive":"Add algebraic geometry domain (schemes, sheaves, varieties)","priority":1,"domain":"Algebraic geometry"},
    {"directive":"Add arithmetic geometry domain (elliptic curves, abelian varieties)","priority":1,"domain":"Arithmetic geometry"},
    {"directive":"Add noncommutative geometry domain (C*-algebras, quantum groups)","priority":2,"domain":"Geometry"},
    {"directive":"Add symplectic topology domain (pseudoholomorphic curves, Floer homology)","priority":2,"domain":"Topology"},
    {"directive":"Add tropical geometry domain (tropical curves, amoebas)","priority":3,"domain":"Geometry"},
    {"directive":"Add derived algebraic geometry domain (derived stacks, infinity categories)","priority":3,"domain":"Algebraic geometry"},
    {"directive":"Add geometric representation theory domain (geometric Langlands, perverse sheaves)","priority":2,"domain":"Representation theory"},
    {"directive":"Add random matrix theory domain (Wigner semicircle, Marchenko-Pastur)","priority":2,"domain":"Probability"},
    {"directive":"Add quantum field theory domain (path integrals, renormalization)","priority":2,"domain":"Physics"},
    {"directive":"Add conformal field theory domain (vertex operator algebras, modular forms)","priority":3,"domain":"Physics"},
]

# ═══════════════════════════════════════════════════════════
# UPDATED KNOWN GAPS
# ═══════════════════════════════════════════════════════════
KNOWN_GAPS_V6_UPDATES = [
    # Close resolved gaps
    {"gap_description":"Statistical mechanics domain has no formulas","domain":"Physics","severity":"high","resolved_at":"v6"},
    {"gap_description":"Cryptography domain has no formulas","domain":"Cryptography","severity":"high","resolved_at":"v6"},
    {"gap_description":"Representation theory domain has no formulas","domain":"Algebra","severity":"high","resolved_at":"v6"},
    {"gap_description":"Model theory domain has no formulas","domain":"Logic","severity":"high","resolved_at":"v6"},
    {"gap_description":"Homological algebra domain has no formulas","domain":"Algebra","severity":"high","resolved_at":"v6"},
    {"gap_description":"Algebraic topology domain has no formulas","domain":"Topology","severity":"high","resolved_at":"v6"},

    # New discovered gaps
    {"gap_description":"Algebraic geometry completely uncovered (schemes, sheaves, varieties, cohomology)","domain":"Algebraic geometry","severity":"high"},
    {"gap_description":"Arithmetic geometry has only elliptic curve entries; missing abelian varieties, motives","domain":"Arithmetic geometry","severity":"high"},
    {"gap_description":"Noncommutative geometry (C*-algebras, quantum groups, cyclic homology) completely uncovered","domain":"Geometry","severity":"high"},
    {"gap_description":"Symplectic topology (pseudoholomorphic curves, Floer homology, Gromov-Witten invariants) completely uncovered","domain":"Topology","severity":"high"},
    {"gap_description":"Deeper coverage in Analysis: pseudodifferential operators, microlocal analysis, wavelets","domain":"Analysis","severity":"medium"},
    {"gap_description":"Deeper coverage in Algebra: Lie theory, algebraic groups, invariant theory","domain":"Algebra","severity":"medium"},
    {"gap_description":"v6 expansion formulas have Lean4/Coq proof coverage of 0%","domain":"Computation","severity":"medium"},
    {"gap_description":"v6 expansion formulas have translations only in English (no multilingual authoring yet)","domain":"Linguistics","severity":"medium"},
    {"gap_description":"No TikZ diagrams added for any v6-expansion formula","domain":"Geometry","severity":"medium"},
    {"gap_description":"Cross-domain bridges not yet extended to include new v6 domains","domain":"All","severity":"medium"},
]

# ═══════════════════════════════════════════════════════════
# INTEGRATION INSTRUCTIONS
# ═══════════════════════════════════════════════════════════
"""
To integrate this v6 expansion into the v5 base script:

1. Add this import at the top if not present:
   from dataclasses import dataclass, field
   from typing import List, Dict, Optional

2. After the existing FORMULAS list, add:
   FORMULAS.extend(FORMULAS_EXPANSION_V6)

3. After the existing PROOF_STRATEGIES list, add:
   PROOF_STRATEGIES.extend(PROOF_STRATEGIES_V6)

4. After the existing CROSS_DOMAIN_BRIDGE_SPECS list, add:
   CROSS_DOMAIN_BRIDGE_SPECS.extend(CROSS_DOMAIN_BRIDGE_SPECS_V6)

5. Update GROWTH_DIRECTIVES:
   for gd in GROWTH_DIRECTIVES:
       if gd["directive"].startswith("Add statistical mechanics"): gd["status"] = "resolved_v6"
       if gd["directive"].startswith("Add cryptography"): gd["status"] = "resolved_v6"
       if gd["directive"].startswith("Add representation theory"): gd["status"] = "resolved_v6"
       if gd["directive"].startswith("Add model theory"): gd["status"] = "resolved_v6"
       if gd["directive"].startswith("Add homological algebra"): gd["status"] = "resolved_v6"
       if gd["directive"].startswith("Add algebraic topology"): gd["status"] = "resolved_v6"
   GROWTH_DIRECTIVES.extend(GROWTH_DIRECTIVES_V6_UPDATES)

6. Update KNOWN_GAPS:
   KNOWN_GAPS = [g for g in KNOWN_GAPS if g["domain"] not in
                 {"Physics","Cryptography","Algebra","Logic","Topology"}]
   for g in KNOWN_GAPS:
       if g["gap_description"].startswith("Chemistry"):
           g["gap_description"] = "Chemistry has 15 formulas but lacks quantum chemistry depth"
   KNOWN_GAPS.extend(KNOWN_GAPS_V6_UPDATES)

7. The script will then generate an atlas with 380 formulas (238 + 142),
   32 proof strategies (20 + 12), 34 cross-domain bridges (20 + 14),
   and updated growth directives and known gaps.

Total new content in v6:
- 142 new formulas (statistical mechanics: 18, cryptography: 18, representation theory: 16,
  model theory: 14, homological algebra: 16, algebraic topology: 18, deeper coverage: 42)
- 12 new proof strategies
- 14 new cross-domain bridges
- 6 resolved growth directives
- 6 new growth directives
- 6 closed known gaps
- 10 new known gaps
"""

print("v6 Expansion loaded successfully")
print(f"Total new formulas: {len(FORMULAS_EXPANSION_V6)}")
print(f"Total new proof strategies: {len(PROOF_STRATEGIES_V6)}")
print(f"Total new cross-domain bridges: {len(CROSS_DOMAIN_BRIDGE_SPECS_V6)}")
print(f"Total updated growth directives: {len(GROWTH_DIRECTIVES_V6_UPDATES)}")
print(f"Total updated known gaps: {len(KNOWN_GAPS_V6_UPDATES)}")
