import random
import pulp
from influence_maximization import solve_influence_maximization


# -------------------------------------------
# 1. Definition de l'instance
# -------------------------------------------

random.seed(42)

n = 8          # noeuds numerotes 0..7
T = 4          # periodes 0,1,2,3
B = 4.0        # budget

# Couts d'activation de chaque noeud comme seed
costs = {
    0: 4,
    1: 2,
    2: 2,
    3: 1,
    4: 1,
    5: 2,
    6: 1,
    7: 1,
}

# Arcs dans le graphe
all_arcs = [
    (0, 1), (0, 2),
    (1, 3), (1, 4),
    (2, 5),
    (3, 6),
    (4, 7),
    (5, 6),(5, 7)
]

# Voisins sortants et entrants
neighbors_out = {i: [] for i in range(n)}
neighbors_in  = {i: [] for i in range(n)}
for (i, j) in all_arcs:
    neighbors_out[i].append(j)
    neighbors_in[j].append(i)

# -------------------------------------------
# 2. Generation des scenarios stochastiques
# -------------------------------------------
# Chaque arc est actif (aijs=1) avec probabilite p dans chaque scenario.
# On genere S=30 scenarios avec des realisations differentes.

S = 30
p_active = 0.65   # probabilite qu'un arc soit actif dans un scenario

scenarios = []
for s_id in range(S):
    arc_realizations = {}
    for (i, j) in all_arcs:
        arc_realizations[(i, j)] = 1 if random.random() < p_active else 0
    scenarios.append({
        "id": s_id,
        "prob": 1.0 / S,
        "edges": arc_realizations,
    })

# -------------------------------------------
# 3. Affichage de l'instance
# -------------------------------------------

print("=" * 60)
print("   INSTANCE : Reseau Social - 8 noeuds, 30 scenarios, T=4")
print("=" * 60)
print(f"\nNoeuds     : {list(range(n))}")
print(f"Budget B  : {B}")
print(f"Periodes T: {T}")
print(f"\nCouts d'activation des seeds :")
for i, c in costs.items():
    print(f"  Noeud {i} : {c}")

print(f"\nArcs du reseau : {all_arcs}")

print(f"\nScenarios stochastiques ({S} scenarios, pi_s = {1/S:.3f}) :")
for sc in scenarios:
    active = [(i,j) for (i,j), a in sc["edges"].items() if a == 1]
    print(f"  Scenario {sc['id']} - arcs actifs : {active}")

# -------------------------------------------
# 4. Resolution du modele
# -------------------------------------------

print("\n" + "=" * 60)
print("   RESOLUTION DU MODELE MILP")
print("=" * 60)

result = solve_influence_maximization(
    n=n,
    T=T,
    scenarios=scenarios,
    costs=costs,
    budget=B,
    neighbors_out=neighbors_out,
    neighbors_in=neighbors_in,
    M=100,
    verbose=True,
)

# -------------------------------------------
# 5. Affichage des resultats
# -------------------------------------------

print("\n" + "=" * 60)
print("   RESULTATS")
print("=" * 60)

print(f"\nStatut du solveur : {result['status']}")
print(f"Valeur objectif   : {result['objective']:.4f} noeuds actives en moyenne")
print(f"\nSeeds selectionnes : {result['seeds']}")
print(f"Cout total seeds    : {sum(costs[i] for i in result['seeds'])}")

print("\n--- Activation des noeuds par scenario et periode ---")
for s_id in range(S):
    print(f"\n  Scenario {s_id} :")
    for t in range(T + 1):
        activated = [
            i for i in range(n)
            if (result["x"].get((t, i, s_id)) or 0) > 0.5
        ]
        print(f"    t={t} : noeuds actives = {activated}")

print("\n--- Transmissions effectuees ---")
for s_id in range(S):
    print(f"\n  Scenario {s_id} :")
    for t in range(T):
        transmissions = [
            (i, j)
            for (tt, i, j, s), val in result["I"].items()
            if tt == t and s == s_id and (val or 0) > 0.5
        ]
        if transmissions:
            print(f"    t={t} : transmissions {transmissions}")

# -------------------------------------------
# 6. Resume
# -------------------------------------------

print("\n" + "=" * 60)
print("   RESUME")
print("=" * 60)

total_nodes = n
avg_activated = result["objective"]
print(f"\nNoeuds totaux              : {total_nodes}")
print(f"Budget utilise            : {sum(costs[i] for i in result['seeds'])} / {B}")
print(f"Seeds choisies            : {result['seeds']}")
print(f"Esperance d'activation    : {avg_activated:.2f} / {total_nodes} noeuds")
print(f"Taux de noeuds influences moyen : {100 * avg_activated / total_nodes:.1f}%")

print("\nActivation finale par scenario :")
for s_id in range(S):
    count = sum(
        1 for i in range(n)
        if (result["x"].get((T, i, s_id)) or 0) > 0.5
    )
    print(f"  Scenario {s_id} : {count} / {n} noeuds actives")