# Graph Theory Study Notes

These notes are based on the three books in this repository:

| Tag | Book | File |
|---|---|---|
| **[B]** | Yu. B. Burkatovskaya. *Graph Theory. Part 1.* Tomsk: TPU Publishing, 2014 (in Russian, algorithm-oriented) | `graph-theory-books/Textbook_Graph_2013.pdf` |
| **[W]** | R. Wilson. *Introduction to Graph Theory*, 4th ed. (the classic concise introduction) | `graph-theory-books/wilsongraph.pdf` |
| **[G]** | D. Grinberg. *An Introduction to Graph Theory* (graduate course Math 530, Drexel; rigorous proofs) | `graph-theory-books/graphs.pdf` |

---

## 1. Basic notions

*Read: [B] ch. 1; [W] §§1–4; [G] §§2.1–2.8.*

A **graph** `G = (V, E)` is a set of **vertices** `V` and a set of **edges** `E`, where each edge joins a pair of vertices. Variants:

- **Simple graph** — no loops and no multiple edges (an edge is an unordered pair of distinct vertices).
- **Multigraph** — multiple edges allowed; **pseudograph** — loops allowed as well.
- **Directed graph (digraph)** — edges (arcs) are ordered: `(u, v) ≠ (v, u)`.
- **Weighted graph** — numbers (weights, lengths, costs) are assigned to edges.

**Adjacency and incidence.** Two vertices are *adjacent* if joined by an edge; an edge is *incident* to its endpoints. The **degree** `deg(v)` is the number of edges incident to a vertex (a loop counts twice). In a digraph one distinguishes the out-degree `d⁺(v)` and the in-degree `d⁻(v)`.

**Handshake lemma** (the first theorem of graph theory, Euler):

> Σ deg(v) = 2|E| — the sum of all vertex degrees equals twice the number of edges.

Corollary: **the number of vertices of odd degree is always even**.

**Important graph families:**

- `K_n` — the complete graph (all pairs of vertices adjacent), `|E| = n(n−1)/2`;
- `O_n` (the empty graph) — no edges;
- `C_n` — the cycle, `P_n` — the path;
- `K_{m,n}` — the complete bipartite graph; a **bipartite graph** — vertices split into two parts, all edges go between the parts. *Criterion: a graph is bipartite ⇔ it contains no odd cycles.*
- **Regular graph** — all degrees equal `r` (the hypercube `Q_n` and the Petersen graph are classic examples);
- **Kneser graph** `K(n, k)` — vertices are k-subsets, edges are disjoint pairs ([G] §2.6.3).

**Isomorphism.** Graphs are isomorphic if there is a bijection of vertices preserving adjacency. Invariants (necessary conditions): numbers of vertices and edges, degree sequence, number of components, cycle lengths. Matching invariants do not guarantee isomorphism; no efficient general isomorphism test is known.

**Operations on graphs** ([B] §1.6): complement `Ḡ`, union, join, vertex/edge deletion, edge contraction, Cartesian product (e.g. `Q_n = K_2 × … × K_2`).

**Graph representations** ([B] §1.7):

| Representation | Memory | Adjacency check | Neighbor iteration |
|---|---|---|---|
| Adjacency matrix `n×n` | O(n²) | O(1) | O(n) |
| Incidence matrix `n×m` | O(n·m) | — | — |
| Adjacency lists | O(n+m) | O(deg v) | O(deg v) |

---

## 2. Walks and connectivity

*Read: [B] ch. 2; [W] §5; [G] §§2.9–2.12, ch. 3–4.*

A **walk** is an alternating sequence of vertices and edges. A **trail** is a walk without repeated edges. A **path** is a walk without repeated vertices. A **closed walk** ends where it starts; a **cycle** is a closed walk repeating no vertices. Key lemma: *any walk between u and v contains a path between u and v* ([G] §2.9.3).

The **distance** `d(u, v)` is the length of a shortest path. Derived characteristics:

- **eccentricity** `e(v) = max_u d(v, u)`;
- **radius** `r(G) = min_v e(v)`, **diameter** `d(G) = max_v e(v)`;
- **center** — the vertices of minimum eccentricity.

**Connectivity.** A graph is connected if any two vertices are joined by a path. "Joined by a path" is an equivalence relation; its classes are the **connected components**.

**Bounds on the number of edges** ([B] §2.4): for a graph with `n` vertices and `k` components

> n − k ≤ m ≤ (n − k)(n − k + 1)/2.

Corollary: if `m > (n−1)(n−2)/2`, the graph is necessarily connected.

**Numeric connectivity measures:**

- **vertex connectivity** `κ(G)` — the minimum number of vertices whose removal disconnects the graph;
- **edge connectivity** `λ(G)` — same for edges;
- Whitney's inequality: `κ(G) ≤ λ(G) ≤ δ(G)` (the minimum degree).

A **bridge** is an edge whose removal increases the number of components. *An edge is a bridge ⇔ it lies on no cycle* ([G] §2.12). A **cut vertex (articulation point)** is the analogue for a vertex; **blocks** are the maximal subgraphs without cut vertices.

**Menger's theorem** ([B] §2.8; [W] §28; [G] ch. 9):

> The minimum number of vertices separating two non-adjacent vertices `u` and `v` equals the maximum number of vertex-disjoint paths between `u` and `v`.

There is an edge version (min edge cut = max edge-disjoint paths). Menger's theorem is equivalent to the max-flow min-cut theorem (see §10).

**Connectivity of digraphs** ([B] §2.9): one distinguishes **strong** (every vertex reachable from every other), **unilateral** and **weak** connectivity. The **condensation** — the digraph of strongly connected components — is always acyclic.

---

## 3. Trees

*Read: [B] §§2.5–2.7, ch. 5; [W] §§9–11; [G] ch. 5.*

A **tree** is a connected acyclic graph. A **forest** is an acyclic graph. Equivalent definitions of a tree (any one can be taken as the starting point):

1. connected and acyclic;
2. connected and `m = n − 1`;
3. acyclic and `m = n − 1`;
4. any two vertices are joined by a **unique** path;
5. connected, but removing any edge disconnects it (every edge is a bridge);
6. acyclic, but adding any edge creates exactly one cycle.

Every tree with `n ≥ 2` vertices has **at least two leaves** (vertices of degree 1).

A **spanning tree** is a subgraph that is a tree containing all vertices. Every connected graph has one. The **cyclomatic number** `ν(G) = m − n + k` is the number of edges (chords) that must be removed to turn the graph into a forest.

**Fundamental cycles and cuts** ([B] §§2.6–2.7): fix a spanning tree `T`. Every chord `e ∉ T` induces a unique cycle in `T + e` — this gives the **fundamental cycle system** (there are exactly `ν(G)` of them; every cycle of the graph is a symmetric difference of fundamental ones). Dually, every tree edge induces a **fundamental cut**.

**Counting trees:**

- **Cayley's formula:** the number of labeled trees on `n` vertices is `n^{n−2}` (proof via Prüfer codes, [W] §10).
- **Kirchhoff's matrix-tree theorem** ([G] ch. 5): the number of spanning trees equals any cofactor of the Laplacian matrix `L = D − A`.

**Minimum spanning tree (the connector problem, [B] §5.2; [W] §11):**

- **Kruskal's algorithm** — greedily add edges in order of increasing weight, skipping those that create a cycle; `O(m log m)`.
- **Prim's algorithm** — grow the tree from one vertex, each time adding the minimum outgoing edge.

Correctness of both follows from the cut property (the safe edge is the minimum edge of a cut).

**Trees in computer science** ([B] §§5.3–5.6): rooted (directed) trees, ordered and binary trees, **arborescences** (directed spanning trees, [G] §5.9), binary search trees and balancing:

- **AVL trees** — subtree heights differ by at most 1; height `O(log n)`; rotations on insert/delete.
- **Red-black trees** — balancing via node coloring; height ≤ `2·log₂(n+1)`.

---

## 4. Graph traversal and shortest paths

*Read: [B] ch. 3; [W] §8.*

**Traversal strategies:**

- **Breadth-first search (BFS)** — layer-by-layer traversal from the source via a queue; also finds shortest paths by edge count. `O(n + m)`.
- **Depth-first search (DFS)** — go deep via a stack/recursion; the basis of algorithms for bridges, cut vertices, topological sorting, strongly connected components. `O(n + m)`.

**Shortest paths in a weighted graph:**

| Algorithm | Problem | Restriction | Complexity |
|---|---|---|---|
| Dijkstra | single source | weights ≥ 0 | O(n²) or O(m log n) |
| Bellman–Ford | single source | negative weights allowed, detects negative cycles | O(n·m) |
| Floyd–Warshall | all pairs | no negative cycles | O(n³) |

Dijkstra's idea — greedily "close" the nearest vertex and relax its edges; Floyd–Warshall's idea — dynamic programming over the set of allowed intermediate vertices: `d_k(i,j) = min(d_{k−1}(i,j), d_{k−1}(i,k) + d_{k−1}(k,j))`.

**k shortest paths** ([B] §3.4) — a generalization of the algorithms to the space `R^k`: instead of one label per vertex keep the `k` smallest lengths; finding `k` shortest *simple* paths is treated separately.

---

## 5. Facility location: centers and medians

*Read: [B] ch. 4.*

The applied setting: where to place a service facility (hospital, warehouse)?

- The **center** minimizes the *maximum* distance to the vertices (emergency services): a vertex of minimum eccentricity.
- The **median** minimizes the *sum* of (weighted) distances (warehouses, distribution hubs).
- **Multiple centers/medians (p-center, p-median)** — placing `p` facilities; the problems are NP-hard, solved by enumeration schemes and heuristics ([B] §§4.5–4.6).

The computations need the distance matrix — provided by Floyd–Warshall.

---

## 6. Eulerian graphs

*Read: [B] introduction (the bridges problem); [W] §6; [G] §3.3 (multigraphs), ch. 4 (digraphs).*

The historical origin of graph theory — the seven bridges of Königsberg (Euler, 1736).

An **Eulerian circuit** is a closed trail passing through every edge exactly once.

> **Euler's theorem.** A connected (multi)graph has an Eulerian circuit ⇔ all vertex degrees are even.
> An Eulerian (open) trail exists ⇔ exactly two vertices have odd degree.

Construction algorithms: **Fleury's algorithm** (don't cross a bridge while there is a choice) and **Hierholzer's algorithm** (splicing circuits), both `O(m)`.

**For digraphs:** an Eulerian circuit exists ⇔ the digraph is connected and `d⁺(v) = d⁻(v)` for every vertex. The **BEST theorem** ([G] ch. 4) gives the exact number of Eulerian circuits via the number of arborescences.

---

## 7. Hamiltonian graphs

*Read: [W] §7; [G] §2.14.*

A **Hamiltonian cycle** is a cycle through *all vertices* (each exactly once). Unlike Eulerianity, no convenient criterion exists — the problem is NP-complete. Known sufficient conditions:

> **Dirac's theorem.** If `n ≥ 3` and `deg(v) ≥ n/2` for all vertices, the graph is Hamiltonian.
>
> **Ore's theorem.** If `n ≥ 3` and `deg(u) + deg(v) ≥ n` for every pair of non-adjacent vertices, the graph is Hamiltonian.

(Dirac is a special case of Ore; the proof is the "longest path trick", [G] §2.11.)

**Necessary condition:** if the graph is Hamiltonian, then for every `S ⊆ V` the number of components of `G − S` is at most `|S|`.

Examples: the hypercube `Q_n` is Hamiltonian (Gray codes, [G] §2.14.4); the Petersen graph is not. Related is the **traveling salesman problem** (shortest Hamiltonian cycle in a weighted graph) — solved by branch and bound and heuristics.

---

## 8. Digraphs, tournaments, Markov chains

*Read: [W] §§22–24; [G] ch. 4.*

A **tournament** is a digraph in which every pair of vertices is joined by exactly one arc (the results of a round-robin tournament).

- **Rédei's theorem:** every tournament has a Hamiltonian path.
- **Camion's theorem:** every strongly connected tournament has a Hamiltonian cycle.

**Markov chains** ([W] §24) — probabilistic walks on a digraph with probability weights on the arcs; the connectivity of the digraph determines the chain's behavior (irreducibility, absorbing states).

---

## 9. Matchings and Hall's theorem

*Read: [W] §§25–27; [G] ch. 8 (+ ch. 7 on independent sets).*

A **matching** is a set of edges without common vertices. A **perfect matching** covers all vertices.

> **Hall's ("marriage") theorem.** In a bipartite graph with parts `X, Y` there is a matching saturating `X` ⇔ for every `S ⊆ X` the neighborhood `N(S)` satisfies `|N(S)| ≥ |S|`.

Defect form: a maximum matching saturates `|X| − max_S (|S| − |N(S)|)` vertices.

> **Kőnig's theorem.** In a bipartite graph the size of a maximum matching equals the size of a minimum vertex cover.

Applications ([W] §27): systems of distinct representatives (**transversals**), completing Latin squares, decomposing a regular bipartite graph into perfect matchings.

Finding a maximum matching — **augmenting paths**: a matching is maximum ⇔ there is no augmenting path (Berge's theorem).

---

## 10. Network flows

*Read: [W] §29; [G] ch. 9.*

A **network** is a digraph with a source `s`, a sink `t` and arc capacities. A **flow** is a function on the arcs not exceeding the capacities, with flow conservation at intermediate vertices.

> **Ford–Fulkerson (max-flow min-cut) theorem.** The value of a maximum flow equals the capacity of a minimum cut.

The Ford–Fulkerson algorithm: while an augmenting path exists in the residual network, push flow along it. With integer capacities the maximum flow is integral.

Both Menger's theorem and Hall's theorem follow from max-flow min-cut ([G] proves Hall exactly via flows) — these are "three faces" of one duality.

---

## 11. Planarity

*Read: [W] §§12–16.*

A **planar graph** can be drawn in the plane without edge crossings.

> **Euler's formula.** For a connected planar graph: `n − m + f = 2` (vertices − edges + faces).

Corollaries for simple planar graphs with `n ≥ 3`:

- `m ≤ 3n − 6`; if triangle-free (incl. bipartite) — `m ≤ 2n − 4`;
- every planar graph has a vertex of degree ≤ 5;
- `K₅` (10 > 9) and `K_{3,3}` (9 > 8) are **not planar** — the two minimal obstructions.

> **Kuratowski's theorem.** A graph is planar ⇔ it contains no subgraph homeomorphic to `K₅` or `K_{3,3}` (Wagner's equivalent — via minors).

The **dual graph** `G*` ([W] §15): its vertices are the faces of `G`; cycles of `G` correspond to cuts of `G*` and vice versa. For non-planar graphs the **genus** of a surface is introduced ([W] §14): `K₅` and `K₇` embed on the torus.

---

## 12. Graph coloring

*Read: [W] §§17–21; [G] ch. 6–7.*

A **proper vertex coloring** — adjacent vertices get different colors. The **chromatic number** `χ(G)` is the minimum number of colors. `χ = 2` ⇔ the graph is bipartite (and non-empty).

- Greedy bound: `χ(G) ≤ Δ(G) + 1`.
- **Brooks' theorem:** `χ(G) ≤ Δ(G)`, except complete graphs and odd cycles.
- **Four color theorem:** every planar graph is 4-colorable (proved with computer assistance, 1976). The **five** and six color theorems are proved in the textbooks ([W] §19).

**Edge coloring** (adjacent edges get different colors), the chromatic index `χ′(G)`:

> **Vizing's theorem:** `Δ ≤ χ′(G) ≤ Δ + 1` (all graphs fall into two classes).
> **Kőnig's edge coloring theorem:** for bipartite graphs `χ′ = Δ`.

The **chromatic polynomial** `P(G, k)` — the number of proper colorings in `k` colors ([W] §21). Computed by deletion–contraction: `P(G, k) = P(G − e, k) − P(G/e, k)`. Examples: `P(K_n,k) = k(k−1)…(k−n+1)`, for a tree `P = k(k−1)^{n−1}`.

**Extremal results** ([G] §§2.3, ch. 6–7):

- **Mantel's theorem:** a triangle-free graph has at most `n²/4` edges.
- **Turán's theorem:** the generalization to graphs without `K_{r+1}`.
- **Ramsey numbers:** `R(3, 3) = 6` — among any 6 people there are 3 mutual acquaintances or 3 mutual strangers.
- An **independent set** — pairwise non-adjacent vertices; the independence number `α(G)`; relation: `χ(G) ≥ n/α(G)`.

---

## 13. Matroids

*Read: [W] §§30–33.*

A **matroid** is a pair (a set `E`, a family of "independent" subsets) satisfying the hereditary and exchange axioms. It generalizes simultaneously linear independence of vectors and acyclicity of subgraphs:

- the **graphic (cycle) matroid**: independent sets are forests;
- the **transversal matroid** — partial transversals of a set family.

Key property: **the greedy algorithm solves the optimization problem exactly ⇔ the structure is a matroid** — this is why Kruskal's algorithm works. Matroids tie trees, matchings and transversals into a single theory.

---

## 14. Algorithm summary

| Problem | Algorithm | Complexity |
|---|---|---|
| Traversal, components, shortest paths (unweighted) | BFS / DFS | O(n + m) |
| Shortest paths (weights ≥ 0) | Dijkstra | O(n²) / O(m log n) |
| Shortest paths (negative weights) | Bellman–Ford | O(n·m) |
| All-pairs shortest paths | Floyd–Warshall | O(n³) |
| Minimum spanning tree | Kruskal / Prim | O(m log n) |
| Eulerian circuit | Fleury / Hierholzer | O(m) |
| Maximum flow / matching | Ford–Fulkerson | O(m·|f|) |
| Hamiltonian cycle, TSP, p-center, χ(G) | NP-hard: enumeration, branch and bound, heuristics | exponential |

---

## 15. Recommended study order

1. **Basics** (definitions, degrees, connectivity): [W] §§1–5 — the shortest introduction; in parallel [B] ch. 1–2 (in Russian).
2. **Trees and algorithms**: [B] ch. 3–5 (its strong side: Dijkstra, Floyd, MST, search trees in detail with examples); [W] §§8–11.
3. **The classics — Euler and Hamilton**: [W] §§6–7; rigorous proofs — [G] §2.14, ch. 3–4 (the BEST theorem).
4. **Matchings, Menger, flows**: [W] §§25–29, then [G] ch. 8–9 for full proofs.
5. **Planarity and coloring**: [W] §§12–21; additions on coloring and extremal theory — [G] ch. 6–7.
6. **Broadening**: matroids [W] §§30–33; Markov chains [W] §24; counting trees and the BEST theorem [G] ch. 5.

[B] and [G] have exercises at the end of each chapter; [W] provides solutions to some problems (p. 150+). Solving a few exercises per topic is recommended.
